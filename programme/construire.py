"""Construit le programme éditorial et pédagogique ACTU-BASICS.

Lit le catalogue (programme/catalogue/*.txt) et les sections rédigées
(programme/sections/*.md), contrôle la cohérence du programme, puis écrit :

- programme/sortie/programme.html : le document complet ;
- programme/sortie/controles.md : le rapport des contrôles ;
- le PDF, si l'option --pdf est donnée (impression par Chromium, voir imprimer_pdf.js).

Contrôles (un échec bloque la construction) :
- identifiants uniques, champs obligatoires présents ;
- chaque prérequis cité existe, et le graphe des prérequis n'a pas de cycle ;
- dans le tronc commun, aucun prérequis ne renvoie vers une vidéo placée plus loin ;
- un prérequis ne vient jamais d'un niveau plus élevé que la vidéo qui le demande ;
- la durée indiquée est compatible avec le format (mêmes plages que le moteur) ;
- chaque réponse chiffrée annoncée dans un exercice est recalculée par la machine
  avec l'évaluateur du moteur de production (production/lmec/pedagogie.py).

Usage : python programme/construire.py [--pdf]
"""
from __future__ import annotations

import datetime as dt
import html
import math
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import markdown

RACINE = Path(__file__).resolve().parent
DEPOT = RACINE.parent
sys.path.insert(0, str(DEPOT / "production"))
from lmec.pedagogie import evaluer, tolerance_par_defaut  # noqa: E402

VERSION = "1.2 — projet en revue"
NOM_PDF = "PROGRAMME_EDITORIAL_ACTU-BASICS_v1-2.pdf"

FICHIERS = [
    "boite-a-outils.txt",
    "statistiques-1-decouverte.txt",
    "statistiques-2-fondamentaux.txt",
    "statistiques-3-inference-modeles.txt",
    "statistiques-4-branches.txt",
    "econometrie.txt",
    "quotidien.txt",
]

PILIERS = {
    "S": "Statistiques",
    "E": "Économétrie",
    "Q": "Phénomènes du quotidien",
    "M": "Boîte à outils mathématique",
}

NIVEAUX = {
    1: ("Découverte", "decouverte", "Grand public, aucun prérequis au-delà du collège"),
    2: ("Fondamentaux", "lycee", "Niveau lycée, curieux motivés, début d'études supérieures"),
    3: ("Inférence et modèles", "licence", "Licence, professionnels qui utilisent des données"),
    4: ("Branches avancées", "master", "Master, spécialistes, data scientists, économistes"),
}

# Plages de durée en minutes, identiques à celles du moteur (docs/technique/fiches-pedagogiques.md).
FORMATS = {
    "short": ("SHORT", 0.25, 1.5),
    "educational": ("EDUCATIONAL", 1.5, 10),
    "youtube_lesson": ("YOUTUBE_LESSON", 5, 60),
}
# Un SHORT de cours est souvent une capsule de 2 à 4 min : tolérée, mais signalée.
FORMES = {
    "lecon": "Leçon",
    "demonstration": "Démonstration",
    "simulation": "Simulation",
    "paradoxe": "Paradoxe",
    "etude_de_cas": "Étude de cas",
    "rappel": "Rappel",
}

CHAMPS_UNITE = {
    "S": ["titre", "titre_en", "question", "pre", "obj", "intuition", "exemple", "maths", "erreurs", "exercice", "duree", "format", "forme"],
    "E": ["titre", "titre_en", "question", "pre", "obj", "intuition", "exemple", "maths", "erreurs", "exercice", "duree", "format", "forme"],
    "Q": ["titre", "titre_en", "question", "renvoi", "obj", "intuition", "exemple", "erreurs", "sources", "duree", "format", "forme"],
    "M": ["titre", "titre_en", "question", "pre", "obj", "duree", "format", "forme"],
}
CHAMPS_MODULE = ["niveau", "titre", "titre_en", "pre", "maths", "but"]

# Réponses chiffrées annoncées dans les exercices et exemples : recalculées à chaque construction.
# (unité, expression, valeur annoncée, libellé). La tolérance est celle du moteur :
# la moitié de la dernière décimale écrite.
VERIFICATIONS = [
    ("S1.08", "100 * (1.2 * 0.8 - 1)", -4, "+20 % puis −20 % : effet total en %"),
    ("S2.04", "(10 * 12 + 30 * 8) / 40", 9, "moyenne générale de deux classes"),
    ("S2.10", "(15 - 12) / 2", 1.5, "score z en maths"),
    ("S2.10", "(14 - 10) / 3", 1.33, "score z en philosophie"),
    ("S4.05", "100 * (1 - (5 / 6) ** 4)", 51.8, "au moins un 6 en 4 lancers, en %"),
    ("S4.06", "min(n for n in range(2, 100) if 1 - prod((365 - k) / 365 for k in range(n)) >= 0.9)", 41, "seuil des 90 %"),
    ("S4.06", "23 * 22 / 2", 253, "paires dans un groupe de 23"),
    ("S4.10", "100 * 0.01 * 0.9 / (0.01 * 0.9 + 0.99 * 0.05)", 15.4, "valeur prédictive positive, en %"),
    ("S5.02", "0.1 * 15 - 2", -0.50, "espérance du gain net, en €"),
    ("S5.04", "100 * 0.9 ** 10", 34.9, "les 10 passagers viennent, en %"),
    ("S5.06", "100 * exp(-2)", 13.5, "aucun appel en une minute, en %"),
    ("S5.08", "0.5 ** 3", 0.125, "part restante après 3 demi-vies"),
    ("S5.09", "100 * (1 - (1 + erf(2 / sqrt(2))) / 2)", 2.3, "part au-delà de +2 écarts-types, en %"),
    ("S5.11", "sqrt(3 ** 2 + 4 ** 2)", 5, "écart-type d'une somme"),
    ("S6.03", "sqrt(0.5 * 0.5 / 1000)", 0.016, "erreur standard"),
    ("S6.05", "100 * 1.96 * sqrt(0.25 / 1000)", 3.1, "marge d'erreur, en points"),
    ("S7.07", "32 - 2.064 * 10 / sqrt(25)", 27.9, "borne basse de l'IC"),
    ("S7.07", "32 + 2.064 * 10 / sqrt(25)", 36.1, "borne haute de l'IC"),
    ("S7.08", "100 * 3 / 300", 1, "règle de trois, en %"),
    ("S7.09", "ceil(1.96 ** 2 * 0.25 / 0.02 ** 2)", 2401, "taille d'échantillon"),
    ("S8.09", "100 * (1 - 0.95 ** 20)", 64, "au moins un faux positif sur 20 tests, en %"),
    ("S8.09", "0.05 / 10", 0.005, "seuil de Bonferroni"),
    ("S10.02", "0.2 / 0.8", 0.25, "cote"),
    ("S10.04", "exp(0.3)", 1.35, "facteur multiplicatif du taux"),
    ("S10.06", "0.08 * 2500", 200, "prime pure, en €"),
    ("S11.03", "comb(12, 6)", 924, "répartitions en deux groupes de 6"),
    ("S12.02", "(2 + 7) / (2 + 2 + 10)", 0.64, "moyenne a posteriori"),
    ("S16.01", "sqrt(100)", 10, "écart typique après 100 pas"),
    ("S16.03", "0.9 / (1 - 0.9)", 9, "clients dans le système à 90 % d'occupation"),
    ("E1.02", "1500 * 120 / 80", 2250, "euros constants"),
    ("E1.03", "-0.3 * 20", -6, "variation de la demande, en %"),
    ("Q1.02", "log(2) / log(1.05)", 14, "années pour doubler à 5 %"),
    ("Q1.03", "100 * (1 - 0.7 * 0.8)", 44, "réduction totale, en %"),
    ("Q6.03", "600 * sum(1 / k for k in range(1, 601))", 4200, "achats pour un album de 600 images"),
]
# Tolérances explicites quand le texte arrondit volontairement (« environ »).
TOLERANCES = {("Q6.03", 4200): 50, ("Q1.02", 14): 0.5, ("S8.09", 64): 0.5}


ILLUSTRATIONS: dict[str, list[str]] = defaultdict(list)


@dataclass
class Unite:
    id: str
    module: str
    champs: dict
    rang: int = 0

    @property
    def pilier(self) -> str:
        return self.id[0]

    def liste(self, cle: str) -> list[str]:
        v = self.champs.get(cle, "").strip()
        if not v or v == "-":
            return []
        return [x.strip() for x in v.split("|") if x.strip()]

    @property
    def prerequis(self) -> list[str]:
        return self.liste("pre")

    @property
    def duree(self) -> tuple[float, float]:
        a, _, b = self.champs["duree"].partition("-")
        return float(a), float(b or a)

    @property
    def optionnelle(self) -> bool:
        return self.champs.get("option", "").lower() in ("oui", "true")


@dataclass
class Module:
    id: str
    fichier: str
    champs: dict
    unites: list[Unite] = field(default_factory=list)

    @property
    def niveau(self) -> int:
        return int(self.champs["niveau"])


def lire_catalogue() -> tuple[list[Module], dict[str, Unite], list[str]]:
    modules: list[Module] = []
    unites: dict[str, Unite] = {}
    erreurs: list[str] = []
    rang = 0
    for nom in FICHIERS:
        courant: dict | None = None
        for n, ligne in enumerate((RACINE / "catalogue" / nom).read_text(encoding="utf-8").splitlines(), 1):
            if m := re.match(r"^# MODULE (\S+)\s*$", ligne):
                modules.append(Module(m.group(1), nom, {}))
                courant = modules[-1].champs
            elif m := re.match(r"^## (\S+)\s*$", ligne):
                uid = m.group(1)
                if uid in unites:
                    erreurs.append(f"{nom}:{n} identifiant en double : {uid}")
                rang += 1
                u = Unite(uid, modules[-1].id, {}, rang)
                unites[uid] = u
                modules[-1].unites.append(u)
                courant = u.champs
            elif ligne.startswith("#") or not ligne.strip():
                continue
            elif m := re.match(r"^([a-z_]+):\s?(.*)$", ligne):
                if courant is None:
                    erreurs.append(f"{nom}:{n} champ hors module")
                    continue
                courant[m.group(1)] = m.group(2).strip()
            else:
                erreurs.append(f"{nom}:{n} ligne illisible : {ligne[:60]}")
    return modules, unites, erreurs


def controler(modules: list[Module], unites: dict[str, Unite]) -> tuple[list[str], list[str], list[str]]:
    erreurs, avertissements, notes = [], [], []
    ids_modules = {m.id for m in modules}
    niveau_module = {m.id: m.niveau for m in modules}
    for m in modules:
        for c in CHAMPS_MODULE:
            if not m.champs.get(c):
                erreurs.append(f"module {m.id} : champ « {c} » manquant")
        for p in [x.strip() for x in m.champs.get("pre", "").split("|") if x.strip() not in ("", "-")]:
            if p not in ids_modules and p not in unites:
                erreurs.append(f"module {m.id} : prérequis inconnu {p}")
    for u in unites.values():
        for c in CHAMPS_UNITE[u.pilier]:
            if not u.champs.get(c):
                erreurs.append(f"{u.id} : champ « {c} » manquant")
        fmt = u.champs.get("format")
        if fmt not in FORMATS:
            erreurs.append(f"{u.id} : format inconnu « {fmt} »")
            continue
        if u.champs.get("forme") not in FORMES:
            erreurs.append(f"{u.id} : forme inconnue « {u.champs.get('forme')} »")
        nom_f, mini, maxi = FORMATS[fmt]
        a, b = u.duree
        if fmt == "short" and b > maxi:
            notes.append(f"{u.id} : capsule courte de {a:g}–{b:g} min, plus longue qu'un SHORT de réseau (90 s) ; à découper ou à publier en EDUCATIONAL")
        elif a < mini or b > maxi:
            erreurs.append(f"{u.id} : durée {a:g}–{b:g} min hors de la plage {nom_f} ({mini:g}–{maxi:g} min)")
        niv = niveau_module[u.module]
        for p in u.liste("renvoi"):
            if p not in unites:
                erreurs.append(f"{u.id} : renvoi inconnu {p}")
        for p in u.prerequis:
            if p not in unites:
                erreurs.append(f"{u.id} : prérequis inconnu {p}")
                continue
            q = unites[p]
            if niveau_module[q.module] > niv:
                erreurs.append(f"{u.id} (niveau {niv}) demande {p}, de niveau {niveau_module[q.module]} plus élevé")
            if u.pilier == "S" and q.pilier == "S" and niv <= 3 and q.rang > u.rang:
                erreurs.append(f"{u.id} demande {p}, placé plus loin dans le tronc commun")
            if q.optionnelle and not u.optionnelle:
                avertissements.append(f"{u.id} (obligatoire) dépend de {p}, marqué optionnel")
    # Cycles
    etat: dict[str, int] = {}

    def visiter(x: str, chemin: list[str]) -> None:
        etat[x] = 1
        for p in unites[x].prerequis:
            if p not in unites:
                continue
            if etat.get(p) == 1:
                erreurs.append("cycle de prérequis : " + " → ".join(chemin + [x, p]))
            elif not etat.get(p):
                visiter(p, chemin + [x])
        etat[x] = 2

    for x in unites:
        if not etat.get(x):
            visiter(x, [])
    # Vidéos du tronc commun sans successeur ni rôle de fin de module : simple information.
    return erreurs, avertissements, notes


def verifier_calculs(unites: dict[str, Unite]) -> tuple[list[str], list[tuple]]:
    erreurs, lignes = [], []
    for uid, expr, attendu, libelle in VERIFICATIONS:
        if uid not in unites:
            erreurs.append(f"vérification : unité inconnue {uid}")
            continue
        valeur = evaluer(expr)
        tol = TOLERANCES.get((uid, attendu), tolerance_par_defaut(attendu))
        ok = abs(valeur - attendu) <= tol + 1e-12
        lignes.append((uid, libelle, attendu, valeur, ok))
        if not ok:
            erreurs.append(f"{uid} : {libelle} annoncé {attendu}, recalculé {valeur:.6g}")
    return erreurs, lignes


def ordre_production(unites: dict[str, Unite]) -> list[str]:
    """Tri topologique stable : respecte les prérequis, puis l'ordre de lecture."""
    restants = dict(unites)
    fait: list[str] = []
    vus: set[str] = set()
    while restants:
        prets = [u for u in restants.values() if all(p in vus or p not in unites for p in u.prerequis)]
        prets.sort(key=lambda u: u.rang)
        u = prets[0]
        fait.append(u.id)
        vus.add(u.id)
        del restants[u.id]
    return fait


# ---------------------------------------------------------------- rendu HTML

def e(t: str) -> str:
    return html.escape(t, quote=True)


def minutes(a: float, b: float) -> str:
    f = lambda x: f"{x:g}".replace(".", ",")
    return f"{f(a)} min" if a == b else f"{f(a)}–{f(b)} min"


def liens(ids: list[str], unites: dict[str, Unite]) -> str:
    if not ids:
        return "aucun"
    return ", ".join(f'<a href="#{e(i)}">{e(i)}</a>' if i in unites else e(i) for i in ids)


def puces(items: list[str]) -> str:
    if len(items) == 1:
        return e(items[0])
    return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"


VERBES_APPLIQUER = ("Calculer", "Construire", "Appliquer", "Mener", "Estimer", "Réaliser", "Simuler", "Écrire", "Utiliser",
                    "Coder", "Déflater", "Lisser", "Traduire", "Obtenir", "Dérouler", "Compléter", "Retrouver", "Tester",
                    "Approcher", "Convertir", "Simplifier", "Résoudre", "Sommer", "Mettre", "Décomposer", "Classer", "Lire",
                    "Exprimer", "Reproduire", "Interpréter", "Choisir", "Identifier", "Associer", "Représenter", "Formuler")
MARQUEURS_CRITIQUER = ("Distinguer", "Repérer", "Juger", "Discuter", "Réfuter", "Diagnostiquer", "Évaluer", "limite", "Critiquer", "Reconnaître",
                       "contresens", "piège", "ne couvre pas", "biais", "Dire quand", "Dire ce qu", "plausibilité", "crédib", "portée")


def maitrise(u: "Unite") -> list[str]:
    """Niveaux de maîtrise visés, déduits des verbes des objectifs observables."""
    objs = u.liste("obj")
    out = ["comprendre"]
    if any(o.split()[0] in VERBES_APPLIQUER for o in objs if o.split()):
        out.append("appliquer")
    if any(m in o for o in objs for m in MARQUEURS_CRITIQUER):
        out.append("critiquer")
    return out


def niveau_maths(texte: str) -> int:
    t = re.split(r"en option|en intuition", texte)[0]
    niveaux = [int(x) for x in re.findall(r"M(\d)", t)]
    return max(niveaux) if niveaux else 0


def niveaux_maths(u: "Unite") -> tuple[int, int, int]:
    """(comprendre, appliquer, démontrer). Le champ maths donne le niveau pour appliquer ;
    maths_comprendre et maths_demontrer le précisent quand ils diffèrent."""
    c = u.champs
    app = niveau_maths(c.get("maths", ""))
    comp = niveau_maths(c["maths_comprendre"]) if c.get("maths_comprendre") else (
        app - 1 if app >= 2 and c.get("forme") in ("simulation", "demonstration", "paradoxe") else app)
    demo = niveau_maths(c["maths_demontrer"]) if c.get("maths_demontrer") else app
    return comp, app, max(demo, app)


def carte_unite(u: Unite, unites: dict[str, Unite], successeurs: dict[str, list[str]]) -> str:
    c = u.champs
    illustrations = ILLUSTRATIONS
    fmt = FORMATS[c["format"]][0]
    chips = [
        f'<span class="chip fmt-{c["format"]}">{fmt}</span>',
        f'<span class="chip">{e(FORMES[c["forme"]])}</span>',
        f'<span class="chip">{minutes(*u.duree)}</span>',
    ]
    if c.get("maths"):
        comp, app, demo = niveaux_maths(u)
        if comp == app == demo:
            chips.append(f'<span class="chip">Maths M{app}</span>')
        else:
            chips.append(f'<span class="chip">Maths : comprendre M{comp} · appliquer M{app} · démontrer M{demo}</span>')
    if u.pilier != "M":
        chips.append(f'<span class="chip maitrise">Maîtrise : {" · ".join(maitrise(u))}</span>')
    if u.optionnelle:
        chips.append('<span class="chip opt">Optionnel</span>')
    lignes = []

    def ligne(lib: str, val: str) -> None:
        lignes.append(f"<tr><th>{lib}</th><td>{val}</td></tr>")

    if u.pilier != "Q" or u.prerequis:
        ligne("Prérequis", liens(u.prerequis, unites))
    if u.liste("renvoi"):
        ligne("Pour aller plus loin", liens(u.liste("renvoi"), unites))
    if successeurs.get(u.id):
        ligne("Prépare", liens(successeurs[u.id], unites))
    if illustrations.get(u.id):
        ligne("Illustré par", liens(illustrations[u.id], unites))
    ligne("Objectifs", puces(u.liste("obj")))
    if c.get("maths") and c["maths"].rstrip(".") not in ("Aucune", "M0", "M1", "M2", "M3"):
        ligne("Notions mathématiques", e(c["maths"]))
    for cle, lib in [("intuition", "Intuition d'abord"), ("exemple", "Exemple fil rouge"), ("erreurs", "Idées fausses à prévenir"), ("exercice", "Vérification"), ("sources", "Sources à mobiliser")]:
        if c.get(cle):
            ligne(lib, e(c[cle]))
    return (
        f'<article class="unite" id="{e(u.id)}">'
        f'<header><span class="uid">{e(u.id)}</span><div class="titres"><h4>{e(c["titre"])}</h4>'
        f'<p class="en">EN · {e(c["titre_en"])}</p></div></header>'
        f'<p class="question">{e(c["question"])}</p>'
        f'<div class="chips">{"".join(chips)}</div>'
        f'<table class="fiche">{"".join(lignes)}</table></article>'
    )


def bloc_module(m: Module, unites: dict[str, Unite], successeurs) -> str:
    c = m.champs
    total = sum(sum(u.duree) / 2 for u in m.unites)
    niv = NIVEAUX[m.niveau][0]
    pre = [x.strip() for x in c["pre"].split("|") if x.strip() not in ("", "-")]
    sommaire = "".join(
        f'<tr><td><a href="#{e(u.id)}">{e(u.id)}</a></td><td>{e(u.champs["titre"])}{" <em>(optionnel)</em>" if u.optionnelle else ""}</td>'
        f'<td>{FORMATS[u.champs["format"]][0]}</td><td class="num">{minutes(*u.duree)}</td></tr>'
        for u in m.unites
    )
    return (
        f'<section class="module" id="{e(m.id)}"><div class="module-entete"><div class="module-tete">'
        f'<span class="mid">{e(m.id)}</span><div><h3>{e(c["titre"])}</h3><p class="en">EN · {e(c["titre_en"])}</p></div></div>'
        f'<p class="meta">Niveau {m.niveau} · {e(niv)} · Prérequis : {liens(pre, unites) if pre else "aucun"} · Mathématiques : {e(c["maths"])} · '
        f'{len(m.unites)} vidéos · environ {round(total)} min</p>'
        f'<p class="but">{e(c["but"])}</p>'
        f'<table class="sommaire"><thead><tr><th>N°</th><th>Vidéo</th><th>Format</th><th>Durée</th></tr></thead><tbody>{sommaire}</tbody></table></div>'
        + "".join(carte_unite(u, unites, successeurs) for u in m.unites)
        + "</section>"
    )


def syllabus(pilier: str, modules, unites, successeurs) -> str:
    out = []
    niveau_courant = None
    for m in modules:
        if m.id[0] != pilier:
            continue
        if pilier in "SE" and m.niveau != niveau_courant:
            niveau_courant = m.niveau
            nom, cle, public = NIVEAUX[m.niveau]
            out.append(f'<h2 class="niveau">Niveau {m.niveau} — {e(nom)}<span>{e(public)}</span></h2>')
        out.append(bloc_module(m, unites, successeurs))
    return "".join(out)


def carte_dependances(modules: list[Module], pilier_filtre: str) -> str:
    """Schéma SVG des modules et de leurs dépendances, en couches par niveau."""
    mods = [m for m in modules if m.id[0] in pilier_filtre]
    ids = {m.id for m in mods}
    unite_vers_module = {u.id: m.id for m in modules for u in m.unites}
    deps: dict[str, set[str]] = defaultdict(set)
    for m in mods:
        for x in [x.strip() for x in m.champs["pre"].split("|") if x.strip() not in ("", "-")]:
            cible = x if x in ids else unite_vers_module.get(x)
            if cible in ids and cible != m.id:
                deps[m.id].add(cible)
    par_niveau: dict[int, list[Module]] = defaultdict(list)
    for m in mods:
        par_niveau[m.niveau].append(m)
    largeur, haut_bande, bh = 1000, 140, 60
    niveaux = sorted(par_niveau)
    plus_large = max(len(par_niveau[n]) for n in niveaux)
    bw = min(150, (largeur - 40) / plus_large - 12)
    pos, col = {}, {}
    for i, n in enumerate(niveaux):
        rang = par_niveau[n]
        pas = (largeur - 40) / len(rang)
        for j, m in enumerate(rang):
            pos[m.id] = (20 + pas * (j + 0.5), 10 + i * haut_bande)  # (centre x, haut de bande)
            col[m.id] = j
    h = 10 + len(niveaux) * haut_bande
    svg = [f'<svg viewBox="0 0 {largeur} {h}" class="carte" xmlns="http://www.w3.org/2000/svg">',
           '<defs><marker id="fl" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#8a97a8"/></marker></defs>']
    for i, n in enumerate(niveaux):
        t = 10 + i * haut_bande
        svg.append(f'<rect x="0" y="{t}" width="{largeur}" height="{haut_bande - 10}" rx="10" fill="{"#f3f6fa" if i % 2 == 0 else "#fbfcfe"}"/>')
        svg.append(f'<text x="12" y="{t + 15}" class="bande">NIVEAU {n} · {e(NIVEAUX[n][0].upper())}</text>')
    haut_boite = lambda t: t + 28
    for m in mods:
        for d in sorted(deps[m.id]):
            x1, t1 = pos[d]
            x2, t2 = pos[m.id]
            if t1 == t2:
                if abs(col[d] - col[m.id]) == 1:
                    sens = 1 if x2 > x1 else -1
                    yy = haut_boite(t1) + bh / 2
                    svg.append(f'<path d="M{x1 + sens * bw / 2},{yy} L{x2 - sens * bw / 2},{yy}" class="arc" marker-end="url(#fl)"/>')
                else:
                    y0 = haut_boite(t1)
                    svg.append(f'<path d="M{x1},{y0} C{x1},{y0 - 22} {x2},{y0 - 22} {x2},{y0}" class="arc pointille" marker-end="url(#fl)"/>')
            else:
                y1 = haut_boite(t1) + bh
                y2 = haut_boite(t2)
                my = (y1 + y2) / 2
                svg.append(f'<path d="M{x1},{y1} C{x1},{my} {x2},{my} {x2},{y2}" class="arc" marker-end="url(#fl)"/>')
    for m in mods:
        x, t = pos[m.id]
        y = haut_boite(t)
        couleur = {"S": "#1685D5", "E": "#FF8500", "M": "#5b6b80", "Q": "#2a9d8f"}[m.id[0]]
        titre = m.champs.get("titre_court") or m.champs["titre"].split(" — ")[-1]
        largeur_car = max(12, int(bw / 5.6))
        mots, lignes_t, l = titre.split(), [], ""
        for w in mots:
            if len(l) + len(w) + 1 > largeur_car and l:
                lignes_t.append(l)
                l = w
            else:
                l = (l + " " + w).strip()
        lignes_t.append(l)
        if len(lignes_t) > 3:
            lignes_t = lignes_t[:2] + [" ".join(lignes_t[2:])]
        svg.append(f'<g><rect x="{x - bw / 2}" y="{y}" width="{bw}" height="{bh}" rx="8" fill="#fff" stroke="{couleur}" stroke-width="2"/>')
        svg.append(f'<text x="{x}" y="{y + 15}" class="mid" fill="{couleur}">{e(m.id)}</text>')
        for k, t_ in enumerate(lignes_t):
            svg.append(f'<text x="{x}" y="{y + 29 + k * 10.5}" class="mt">{e(t_)}</text>')
        svg.append("</g>")
    svg.append("</svg>")
    return "".join(svg)


def tableau_volumes(modules, unites) -> str:
    lignes = []
    tot_n = tot_min = 0
    for p, nom in PILIERS.items():
        us = [u for u in unites.values() if u.pilier == p]
        if not us:
            continue
        n = len(us)
        mins = sum(sum(u.duree) / 2 for u in us)
        fm = Counter(u.champs["format"] for u in us)
        opt = sum(u.optionnelle for u in us)
        tot_n += n
        tot_min += mins
        lignes.append(f"<tr><td>{e(nom)}</td><td class='num'>{n}</td><td class='num'>{opt}</td><td class='num'>{fm.get('short', 0)}</td><td class='num'>{fm.get('educational', 0)}</td><td class='num'>{fm.get('youtube_lesson', 0)}</td><td class='num'>{mins / 60:.1f} h</td></tr>")
    lignes.append(f"<tr class='total'><td>Total</td><td class='num'>{tot_n}</td><td></td><td></td><td></td><td></td><td class='num'>{tot_min / 60:.1f} h</td></tr>")
    tete = ("<table class='donnees'><thead><tr><th>Pilier</th><th>Vidéos</th><th>dont optionnelles</th><th>SHORT</th>"
            "<th>EDUCATIONAL</th><th>YOUTUBE_LESSON</th><th>Durée totale<br>(milieu de fourchette)</th></tr></thead><tbody>")
    return tete + "".join(lignes).replace(".", ",") + "</tbody></table>"


def tableau_niveaux(modules, unites) -> str:
    lignes = []
    for n, (nom, cle, public) in NIVEAUX.items():
        mods = [m for m in modules if m.niveau == n and m.id[0] == "S"]
        us = [u for m in mods for u in m.unites]
        mins = sum(sum(u.duree) / 2 for u in us)
        lignes.append(f"<tr><td>{n}</td><td>{e(nom)}<br><code>{cle}</code></td><td>{e(public)}</td><td>{', '.join(m.id for m in mods)}</td><td class='num'>{len(us)}</td><td class='num'>{mins / 60:.1f} h</td></tr>".replace(".", ","))
    return ("<table class='donnees'><thead><tr><th>Niv.</th><th>Nom<br>(clé moteur)</th><th>Public visé</th><th>Modules</th><th>Vidéos</th><th>Durée</th></tr></thead><tbody>"
            + "".join(lignes) + "</tbody></table>")


def premier_catalogue(unites: dict[str, Unite], ordre: list[str]) -> str:
    """Les vidéos des vagues 1 et 2, dans l'ordre de production (voir section 7)."""
    vagues = vagues_production(unites, ordre)
    out = []
    for nom, ids in vagues:
        mins = sum(sum(unites[i].duree) / 2 for i in ids)
        rows = "".join(
            f"<tr><td>{k}</td><td><a href='#{i}'>{i}</a></td><td>{e(unites[i].champs['titre'])}</td><td>{e(PILIERS[unites[i].pilier])}</td><td>{FORMATS[unites[i].champs['format']][0]}</td><td class='num'>{minutes(*unites[i].duree)}</td></tr>"
            for k, i in enumerate(ids, 1)
        )
        out.append(f"<h3>{e(nom)} — {len(ids)} vidéos, environ {mins / 60:.1f} h</h3>".replace(".", ",")
                   + f"<table class='donnees serre'><thead><tr><th>#</th><th>N°</th><th>Vidéo</th><th>Pilier</th><th>Format</th><th>Durée</th></tr></thead><tbody>{rows}</tbody></table>")
    return "".join(out)


# Composition proposée des deux premières vagues (voir sections/07-feuille-de-route.md).
VAGUE_1_MODULES = {"S1", "S2", "S3"}
VAGUE_1_EXTRA = ["M0.01", "M0.02", "M0.03", "S4.01", "S4.02", "S4.05", "E1.01", "E1.02",
                 "Q1.01", "Q1.02", "Q1.03", "Q2.01", "Q2.04", "Q3.01", "Q3.02", "Q3.03", "Q4.02", "Q4.04"]
VAGUE_2_MODULES = {"S4", "S5"}
VAGUE_2_EXTRA = ["M1.01", "M1.02", "M1.03", "M1.04", "M1.05", "M2.01", "M2.02", "E1.03", "E1.04",
                 "Q1.05", "Q2.02", "Q2.03", "Q2.05", "Q3.04", "Q4.01", "Q4.03", "Q6.03"]


def vagues_production(unites, ordre):
    v1 = [i for i in ordre if (unites[i].module in VAGUE_1_MODULES) or i in VAGUE_1_EXTRA]
    v2 = [i for i in ordre if i not in v1 and ((unites[i].module in VAGUE_2_MODULES) or i in VAGUE_2_EXTRA)]
    deja = set()
    for nom, v in (("Vague 1", v1), ("Vague 2", v2)):
        for i in v:
            for p in unites[i].prerequis:
                if p in unites and p not in deja and p not in v:
                    raise SystemExit(f"{nom} : {i} demande {p}, qui n'est pas produit avant")
            deja.add(i)
    return [("Vague 1 · « Lire un chiffre sans se faire avoir »", v1), ("Vague 2 · « Le hasard apprivoisé »", v2)]


def rapport_controles(stats, lignes_calc, avertissements, notes) -> str:
    rows = "".join(
        f"<tr><td><a href='#{u}'>{u}</a></td><td>{e(lib)}</td><td class='num'>{str(att).replace('.', ',')}</td><td class='num'>{f'{val:.4g}'.replace('.', ',')}</td><td>{'✔' if ok else '✘'}</td></tr>"
        for u, lib, att, val, ok in lignes_calc
    )
    av = "".join(f"<li>{e(a)}</li>" for a in avertissements + notes) or "<li>Aucun.</li>"
    return (
        f"<p>Construction du {dt.date.today().strftime('%d/%m/%Y')} : {stats['unites']} vidéos, {stats['modules']} modules, "
        f"{stats['liens']} liens de prérequis contrôlés, aucun cycle, aucun prérequis manquant, aucun prérequis placé après la vidéo qui le demande dans le tronc commun. "
        f"{len(lignes_calc)} réponses chiffrées recalculées par l'évaluateur du moteur de production.</p>"
        f"<h3>Réponses chiffrées recalculées</h3><table class='donnees serre'><thead><tr><th>Vidéo</th><th>Calcul</th><th>Annoncé</th><th>Recalculé</th><th></th></tr></thead><tbody>{rows}</tbody></table>"
        f"<h3>Points signalés (non bloquants)</h3><ul>{av}</ul>"
    )


def rendre_sections(contexte: dict[str, str]) -> str:
    md = markdown.Markdown(extensions=["tables", "attr_list", "toc", "sane_lists", "md_in_html", "fenced_code"])
    out = []
    for f in sorted((RACINE / "sections").glob("*.md")):
        md.reset()
        h = md.convert(f.read_text(encoding="utf-8"))
        for cle, val in contexte.items():
            h = h.replace(f"<p>{{{{{cle}}}}}</p>", val).replace(f"{{{{{cle}}}}}", val)
        reste = re.findall(r"\{\{[A-Z_:]+\}\}", h)
        if reste:
            raise SystemExit(f"{f.name} : marqueurs inconnus {reste}")
        out.append(f'<div class="section" data-fichier="{f.name}">{h}</div>')
    return "".join(out)


def main() -> int:
    modules, unites, erreurs = lire_catalogue()
    e2, avertissements, notes = controler(modules, unites)
    erreurs += e2
    e3, lignes_calc = verifier_calculs(unites)
    erreurs += e3
    if erreurs:
        print("ÉCHEC des contrôles :")
        for x in erreurs:
            print("  ✘", x)
        return 1
    ordre = ordre_production(unites)
    successeurs: dict[str, list[str]] = defaultdict(list)
    for u in unites.values():
        for p in u.prerequis:
            successeurs[p].append(u.id)
        for p in u.liste("renvoi"):
            ILLUSTRATIONS[p].append(u.id)
    stats = {
        "unites": len(unites),
        "modules": len(modules),
        "liens": sum(len(u.prerequis) + len(u.liste("renvoi")) for u in unites.values()),
    }
    s_us = [u for u in unites.values() if u.pilier == "S"]
    contexte = {
        "VERSION": e(VERSION),
        "DATE": dt.date.today().strftime("%d/%m/%Y"),
        "NB_VIDEOS": str(len(unites)),
        "NB_STATS": str(len(s_us)),
        "NB_STATS_TRONC": str(sum(1 for u in s_us if int([m for m in modules if m.id == u.module][0].champs["niveau"]) <= 3)),
        "NB_ECO": str(sum(1 for u in unites.values() if u.pilier == "E")),
        "NB_QUOTIDIEN": str(sum(1 for u in unites.values() if u.pilier == "Q")),
        "NB_MATHS": str(sum(1 for u in unites.values() if u.pilier == "M")),
        "NB_MODULES": str(len(modules)),
        "HEURES_TOTAL": f"{sum(sum(u.duree) / 2 for u in unites.values()) / 60:.0f}",
        "NB_CALCULS": str(len(lignes_calc)),
        "TABLEAU_VOLUMES": tableau_volumes(modules, unites),
        "TABLEAU_NIVEAUX": tableau_niveaux(modules, unites),
        "CARTE_STATS": carte_dependances(modules, "S"),
        "CARTE_ECO": carte_dependances([m for m in modules if m.id[0] == "E" or m.id in ("S1", "S3", "S9", "S10", "S14")], "SE"),
        "SYLLABUS_STATS": syllabus("S", modules, unites, successeurs),
        "SYLLABUS_ECO": syllabus("E", modules, unites, successeurs),
        "SYLLABUS_QUOTIDIEN": syllabus("Q", modules, unites, successeurs),
        "SYLLABUS_MATHS": syllabus("M", modules, unites, successeurs),
        "PREMIER_CATALOGUE": premier_catalogue(unites, ordre),
        "RAPPORT_CONTROLES": rapport_controles(stats, lignes_calc, avertissements, notes),
    }
    v = vagues_production(unites, ordre)
    contexte["NB_V1"] = str(len(v[0][1]))
    contexte["NB_V2"] = str(len(v[1][1]))
    contexte["H_V1"] = f"{sum(sum(unites[i].duree) / 2 for i in v[0][1]) / 60:.0f}"
    contexte["H_V2"] = f"{sum(sum(unites[i].duree) / 2 for i in v[1][1]) / 60:.0f}"
    for k, (_, ids) in enumerate(v, 1):
        for p in "SEQM":
            contexte[f"V{k}_{p}"] = str(sum(1 for i in ids if unites[i].pilier == p))
    n1 = len(v[0][1])
    contexte["CHARGE_V1"] = f"{n1 * 4.5:.0f} et {n1 * 9:.0f}"
    contexte["CHARGE_V1_JG"] = f"{n1 * 0.5:.0f} à {n1 * 1:.0f}"
    for p in "SEQM":
        contexte[f"H_{p}"] = f"{sum(sum(u.duree) / 2 for u in unites.values() if u.pilier == p) / 60:.0f}"
    corps = rendre_sections(contexte)
    for cle, val in contexte.items():
        corps = corps.replace(f"{{{{{cle}}}}}", val)
    gabarit = (RACINE / "gabarit.html").read_text(encoding="utf-8")
    logo = (DEPOT / "assets/brand/actu-basics/logo-dark.png").as_uri()
    police = (DEPOT / "production/polices/Anton-Regular.ttf").as_uri()
    page = gabarit.replace("{{CORPS}}", corps).replace("{{LOGO}}", logo).replace("{{POLICE_ANTON}}", police).replace("{{VERSION}}", e(VERSION)).replace("{{DATE}}", contexte["DATE"])
    sortie = RACINE / "sortie"
    sortie.mkdir(exist_ok=True)
    (sortie / "programme.html").write_text(page, encoding="utf-8")
    print(f"OK : {stats['unites']} vidéos, {stats['modules']} modules, {stats['liens']} liens de prérequis, {len(lignes_calc)} calculs vérifiés.")
    for a in avertissements + notes:
        print("  ⚠", a)
    if "--pdf" in sys.argv:
        pdf = sortie / NOM_PDF
        subprocess.run(["node", str(RACINE / "imprimer_pdf.js"), str(sortie / "programme.html"), str(pdf)], check=True)
        print("PDF :", pdf)
    return 0


if __name__ == "__main__":
    sys.exit(main())
