"""Contrôles qualité automatiques et rapport.

Trois niveaux, toujours séparés dans le rapport :
- BLOQUANT      : la production finale est refusée ;
- AVERTISSEMENT : à regarder, n'empêche pas la production ;
- contrôles HUMAINS : ce que la machine ne sait pas vérifier, dont la véracité des chiffres.

La machine vérifie la structure, la cohérence interne et la conformité technique.
Elle ne vérifie JAMAIS qu'un chiffre est vrai : c'est la vérification factuelle humaine.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from .fiche import Fiche, LANGUES
from .formatage import _texte_langue
from . import logo as _logo

BLOQUANT, AVERTISSEMENT = "bloquant", "avertissement"
SCENES_OBLIGATOIRES = ("accroche", "chiffre", "source", "fin")
MARQUEURS_INCOMPLETS = re.compile(r"\b(TODO|TBD|XXX|à compléter|to be completed|lorem ipsum)\b|\[\s*\.\.\.\s*\]", re.I)
ANNEE = re.compile(r"(?<!\d)(1[5-9]\d\d|2[0-2]\d\d)(?!\d)")
TAILLE_TEXTE_MIN_PX = 34   # en dessous, illisible sur téléphone (image 1080 px de large)
ECART_LONGUEUR_FR_EN = 0.35


@dataclass
class Constat:
    niveau: str
    message: str
    langue: str = ""

    def __str__(self):
        return f"[{self.langue}] {self.message}" if self.langue else self.message


@dataclass
class Rapport:
    constats: list[Constat] = field(default_factory=list)
    ok: list[str] = field(default_factory=list)
    plateformes: list[list[str]] = field(default_factory=list)   # lignes du tableau de compatibilité
    production: list[str] = field(default_factory=list)          # infos de rendu (durées, voix…)
    a_verifier: list[str] = field(default_factory=list)          # cohérences que la machine n'a pas pu établir

    def bloquant(self, message, langue=""):
        self.constats.append(Constat(BLOQUANT, message, langue))

    def avertir(self, message, langue=""):
        self.constats.append(Constat(AVERTISSEMENT, message, langue))

    def verifier(self, condition, message_ok, message_ko, niveau=BLOQUANT, langue=""):
        if condition:
            self.ok.append(f"[{langue}] {message_ok}" if langue else message_ok)
        else:
            self.constats.append(Constat(niveau, message_ko, langue))
        return condition

    @property
    def bloquants(self):
        return [c for c in self.constats if c.niveau == BLOQUANT]

    @property
    def avertissements(self):
        return [c for c in self.constats if c.niveau == AVERTISSEMENT]


# --------------------------------------------------------------------------- outils
def _date(valeur) -> dt.date | None:
    """Toute date de la fiche ramenée à un `date` simple (jamais un `datetime`).

    YAML peut produire un `datetime` (« 2026-11-01 10:30:00 ») qui hérite de `date` :
    le comparer à un `date` lèverait une exception. On garde le jour, on ignore l'heure.
    """
    if isinstance(valeur, dt.datetime):
        return valeur.date()
    if isinstance(valeur, dt.date):
        return valeur
    texte = str(valeur or "").strip()
    if not texte:
        return None
    try:
        return dt.date.fromisoformat(texte)
    except ValueError:
        pass
    try:
        return dt.datetime.fromisoformat(texte.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def nombres(texte: str, langue: str) -> list[float]:
    """Nombres écrits dans un texte, normalisés (« 8,2 » fr = « 8.2 » en ; « 1 000 » = « 1,000 »)."""
    texte = texte.replace(" ", " ").replace(" ", " ")
    if langue == "fr":
        motif = r"(?<![\d,])\d{1,3}(?: \d{3})+(?:,\d+)?|\d+(?:,\d+)?"
    else:
        motif = r"(?<![\d.])\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
    valeurs = []
    for m in re.findall(motif, texte):
        brut = m.replace(" ", "") if langue == "fr" else m.replace(",", "")
        brut = brut.replace(",", ".")
        try:
            valeurs.append(float(brut))
        except ValueError:
            pass
    return valeurs


def _textes_edition(ed) -> list[str]:
    return ([ed.titre, ed.legende] + [s.texte for s in ed.scenes] + [s.voix_off for s in ed.scenes if s.voix_off]
            + [e for s in ed.scenes for e in s.extra.get("etapes", [])]
            + [s.extra["reponse"] for s in ed.scenes if s.extra.get("reponse")]
            + [s.extra["note"] for s in ed.scenes if s.extra.get("note")])


# --------------------------------------------------------------------------- fiche
def controler_validation(fiche: Fiche, r: Rapport, aujourd_hui: dt.date) -> None:
    date_val = _date(fiche.date_validation) if fiche.date_validation else None
    if fiche.statut == "valide":
        r.verifier(bool(fiche.valide_par.strip()), f"Validée par {fiche.valide_par}",
                   "Statut « valide » mais « valide_par » est vide")
        if not fiche.date_validation:
            r.bloquant("Statut « valide » mais la date de validation est absente")
        elif date_val is None:
            r.bloquant(f"Date de validation illisible « {fiche.date_validation} » (format attendu AAAA-MM-JJ)")
        elif date_val > aujourd_hui:
            r.bloquant(f"Date de validation dans le futur ({date_val})")
        else:
            r.ok.append(f"Date de validation : {date_val}")
            for s in fiche.sources:
                consult = _date(s.get("date_consultation"))
                if consult and consult > date_val:
                    r.avertir(f"Source « {_texte_langue(s['nom'], 'fr')} » consultée ({consult}) après la validation ({date_val}) : "
                              "la fiche a-t-elle été revalidée ?")
    else:
        r.bloquant("Fiche non validée (statut « brouillon ») : aucun rendu final possible")
        if fiche.valide_par or fiche.date_validation:
            r.avertir("Statut « brouillon » mais « valide_par » ou « date » renseigné : incohérent")


def controler_sources(fiche: Fiche, r: Rapport, aujourd_hui: dt.date) -> None:
    for s in fiche.sources:
        url = urlparse(str(s.get("url", "")))
        r.verifier(url.scheme in ("http", "https") and "." in url.netloc,
                   f"URL de source bien formée : {_texte_langue(s['nom'], 'fr')}", f"URL de source invalide : {s.get('url')}")
        consult = _date(s.get("date_consultation"))
        if not s.get("date_consultation"):
            r.avertir(f"Date de consultation manquante : {_texte_langue(s['nom'], 'fr')}")
        elif consult is None:
            r.bloquant(f"Date de consultation illisible pour {_texte_langue(s['nom'], 'fr')} : « {s.get('date_consultation')} »")
        elif consult > aujourd_hui:
            r.bloquant(f"Date de consultation dans le futur pour {_texte_langue(s['nom'], 'fr')} ({consult})")
        elif (aujourd_hui - consult).days > 365:
            r.avertir(f"Source consultée il y a plus d'un an ({consult}) : vérifier qu'il n'existe pas de version plus récente")


def controler_editions(fiche: Fiche, r: Rapport) -> None:
    for langue in LANGUES:
        ed = fiche.editions[langue]
        types = [s.type for s in ed.scenes]
        for t in (SCENES_OBLIGATOIRES if not fiche.pedagogique else ("fin",)):
            r.verifier(t in types, f"Scène « {t} » présente", f"Scène obligatoire « {t} » absente", langue=langue)
        if types and types[0] != "accroche" and not fiche.pedagogique:
            r.avertir("La vidéo ne commence pas par l'accroche", langue)
        if types and types[-1] != "fin" and not fiche.pedagogique:
            r.avertir("La vidéo ne se termine pas par la scène de fin", langue)
        r.verifier(len(ed.legende.strip()) >= 40, "Légende renseignée",
                   "Légende trop courte pour être utile (< 40 caractères)", AVERTISSEMENT, langue)
        r.verifier(bool(ed.hashtags), "Hashtags présents", "Aucun hashtag", AVERTISSEMENT, langue)
        mauvais = [h for h in ed.hashtags if " " in h or len(h) < 2]
        r.verifier(not mauvais, "Hashtags bien formés", f"Hashtags mal formés : {mauvais}", BLOQUANT, langue)
        incomplets = [t for t in _textes_edition(ed) if t and MARQUEURS_INCOMPLETS.search(t)]
        r.verifier(not incomplets, "Aucun marqueur « à compléter »",
                   f"Texte incomplet : « {incomplets[0][:60] if incomplets else ''} »", BLOQUANT, langue)
        asterisques = [t for t in (ed.titre, ed.legende) if "*" in t]
        r.verifier(not asterisques, "Pas d'astérisque dans le titre ni la légende",
                   "Astérisques de mise en valeur dans le titre ou la légende (ils seraient publiés tels quels)",
                   BLOQUANT, langue)
        impairs = [s.texte for s in ed.scenes if s.texte.count("*") % 2]
        r.verifier(not impairs, "Mises en valeur *…* bien fermées",
                   f"Astérisque non fermé : « {impairs[0][:50] if impairs else ''} »", BLOQUANT, langue)
        if not ed.narration:
            r.avertir("Vidéo sans voix par choix éditorial (narration: false)", langue)
        anciens = sorted({a for t in _textes_edition(ed) for a in _logo.ANCIENNES_SIGNATURES if a in t.lower()})
        r.verifier(not anciens, "Aucun ancien nom ni ancienne signature de la marque",
                   f"Ancien nom ou ancienne signature de la marque dans les textes ({', '.join(anciens)}) : "
                   f"la marque est ACTU-BASICS, slogan « {_logo.SLOGANS_OFFICIELS[langue]} » "
                   "(correction éditoriale)", AVERTISSEMENT, langue)

    nb = {l: len(e.scenes) for l, e in fiche.editions.items()}
    r.verifier(len(set(nb.values())) == 1, "FR et EN ont le même nombre de scènes",
               f"Nombre de scènes différent FR/EN {nb} (adaptation volontaire ?)", AVERTISSEMENT)


# Mots d'échelle reconnus dans les unités (« milliards » fr = « billion » en ; « billion » fr = 10^12).
_ECHELLES = {
    "fr": [(r"\bmilliers?\b", 1e3), (r"\bmillions?\b", 1e6), (r"\bmilliards?\b", 1e9),
           (r"\bbillions?\b", 1e12)],
    "en": [(r"\bthousands?\b", 1e3), (r"\bmillions?\b", 1e6), (r"\bbillions?\b", 1e9),
           (r"\btrillions?\b", 1e12)],
}
_POURCENT = re.compile(r"%|\bpour ?cents?\b|\bper ?cent\b|\bpercent(age)?\b|\bpoints? de pourcentage\b|"
                       r"\bpercentage points?\b", re.I)
_POUR_MILLE = re.compile(r"‰|\bpour (1 ?000|mille)\b|\bper (1,?000|thousand)\b", re.I)


def lire_unite(texte: str, langue: str) -> tuple[str, float | None]:
    """Nature et échelle d'une unité écrite : (« pourcentage » | « pour_mille » | « valeur », facteur).

    Le facteur vaut None quand aucun mot d'échelle n'est reconnu (on ne sait pas : 1 n'est pas supposé).
    """
    t = texte.replace("\u00a0", " ").replace("\u202f", " ")
    if _POURCENT.search(t):
        return "pourcentage", 1.0
    if _POUR_MILLE.search(t):
        return "pour_mille", 1.0
    for motif, facteur in _ECHELLES[langue]:
        if re.search(motif, t, re.I):
            return "valeur", facteur
    return "valeur", None


def _unite_chiffre(ch: dict, langue: str) -> str:
    return " ".join(_texte_langue(ch.get(c), langue) for c in ("prefixe", "suffixe", "unite"))


def _annees(texte: str) -> set[int]:
    return {int(a) for a in ANNEE.findall(texte or "")}


def _decimales_reelles(v: float) -> int:
    return 0 if float(v).is_integer() else len(repr(float(v)).split(".")[1])


def _decrire(unite: tuple[str, float | None]) -> str:
    nature, facteur = unite
    if nature != "valeur":
        return nature.replace("_", " ")
    return {None: "sans mot d'échelle", 1e3: "milliers", 1e6: "millions", 1e9: "milliards",
            1e12: "billions (10^12)"}.get(facteur, str(facteur))


def _coherence_graphique(fiche: Fiche, r: Rapport, unite_ch: dict, debut, fin) -> None:
    d, ch = fiche.donnees, fiche.chiffre
    points = d["points"]
    unite_d = {l: lire_unite(_texte_langue(d.get("unite"), l), l) for l in LANGUES}
    u = d.get("unite")
    if isinstance(u, dict) and bool(str(u.get("fr") or "").strip()) != bool(str(u.get("en") or "").strip()):
        r.bloquant("donnees.unite renseignée dans une seule langue")
    if unite_d["fr"] != unite_d["en"]:
        r.bloquant(f"Unité du graphique différente entre FR ({_decrire(unite_d['fr'])}) et EN "
                   f"({_decrire(unite_d['en'])}) : erreur de traduction probable")
    if any(p["valeur"] < 0 for p in points):
        r.avertir("Valeurs négatives : le graphique en barres ne les représente pas correctement")
    if unite_d["fr"][0] == "pourcentage" and any(not 0 <= p["valeur"] <= 100 for p in points):
        r.avertir("Graphique en pourcentage avec une valeur hors de 0–100")
    dec_d = d.get("decimales")
    if isinstance(dec_d, int):
        arrondis = [p["valeur"] for p in points if _decimales_reelles(p["valeur"]) > dec_d]
        if arrondis:
            r.avertir(f"Valeurs du graphique affichées arrondies à {dec_d} décimale(s) : {arrondis}")

    # Chiffre clé ↔ point mis en avant, après conversion d'échelle quand elle est connue
    en_avant = [p for p in points if p.get("mis_en_avant")]
    if len(en_avant) > 1:
        r.avertir(f"{len(en_avant)} points mis en avant dans le graphique : un seul attendu")
    nat_c, fac_c = unite_ch["fr"]
    nat_d, fac_d = unite_d["fr"]
    v = float(ch["valeur"])
    if nat_c != nat_d:
        r.avertir(f"Le chiffre clé ({_decrire(unite_ch['fr'])}) et le graphique ({_decrire(unite_d['fr'])}) "
                  "n'ont pas la même nature d'unité : le chiffre clé n'a pas pu être retrouvé dans le graphique")
        return
    if (fac_c is None) != (fac_d is None):
        # Une seule des deux unités a un mot d'échelle : on suppose « unités simples » pour l'autre,
        # mais on le dit.
        fac_c, fac_d = fac_c or 1.0, fac_d or 1.0
        hypothese = " (en supposant des unités simples là où aucune échelle n'est écrite)"
    else:
        fac_c, fac_d = fac_c or 1.0, fac_d or 1.0
        hypothese = ""

    def tolerance(dec, facteur, val):
        dec = dec if isinstance(dec, int) else _decimales_reelles(val)
        return 0.5 * 10 ** -dec * facteur

    def egal(p):
        ecart = abs(v * fac_c - float(p["valeur"]) * fac_d)
        return ecart <= tolerance(ch.get("decimales"), fac_c, v) + tolerance(dec_d, fac_d, p["valeur"]) + 1e-9

    cibles = en_avant or points
    trouves = [p for p in cibles if egal(p)]
    if trouves:
        conv = "" if fac_c == fac_d else " après conversion d'échelle"
        quoi = "au point mis en avant" if en_avant else "à un point"
        r.ok.append(f"Chiffre clé égal {quoi} du graphique{conv}{hypothese}")
    elif en_avant:
        r.avertir(f"Le point mis en avant du graphique ({en_avant[0]['valeur']}, {_decrire(unite_d['fr'])}) ne "
                  f"correspond pas au chiffre clé ({ch['valeur']}, {_decrire(unite_ch['fr'])}){hypothese}")
    else:
        r.avertir("Le chiffre clé n'apparaît dans aucun point du graphique (normal seulement s'il "
                  f"s'agit d'une autre grandeur){hypothese}")

    # Années des libellés : identiques en FR et EN, comprises dans la période
    hors, avec_annee = [], False
    for i, p in enumerate(points):
        par_langue = {l: _texte_langue(p.get("label"), l) for l in LANGUES}
        annees = {l: _annees(t) for l, t in par_langue.items()}
        if annees["fr"] != annees["en"]:
            r.bloquant(f"Libellé du point {i + 1} : années différentes entre FR ({par_langue['fr']}) et EN "
                       f"({par_langue['en']})")
        avec_annee = avec_annee or bool(annees["fr"])
        if debut is not None:
            hors += [(par_langue["fr"], a) for a in annees["fr"] if not debut <= a <= fin]
    for lab, a in hors:
        r.avertir(f"Libellé du graphique « {lab} » : {a} hors de la période annoncée {debut}–{fin}")
    if avec_annee and debut is not None and not hors:
        r.ok.append(f"Années des libellés du graphique comprises dans la période {debut}–{fin}")


def controler_coherence(fiche: Fiche, r: Rapport) -> None:
    """Cohérence interne : chiffre clé, graphique, unités, périodes, FR/EN.

    Ne conclut « cohérent » que sur ce qui est réellement comparé. Ce qui ne peut pas l'être
    (même grandeur ? même définition ?) est renvoyé à la vérification humaine (r.a_verifier).
    """
    ch = fiche.chiffre
    for cle in ("unite", "suffixe", "prefixe"):
        v = ch.get(cle)
        if isinstance(v, dict) and bool(str(v.get("fr") or "").strip()) != bool(str(v.get("en") or "").strip()):
            r.bloquant(f"chiffre_cle.{cle} renseigné dans une seule langue")
    for cle in ("periode", "perimetre", "definition"):
        for langue in LANGUES:
            if not fiche.contexte(cle, langue).strip():
                r.bloquant(f"contexte.{cle} vide", langue)

    # --- Unités : même nature et même échelle en FR et en EN
    unite_ch = {l: lire_unite(_unite_chiffre(ch, l), l) for l in LANGUES}
    if unite_ch["fr"] != unite_ch["en"]:
        r.bloquant(f"Unité du chiffre clé différente entre FR et EN (FR : {_decrire(unite_ch['fr'])}, "
                   f"EN : {_decrire(unite_ch['en'])}) : erreur de traduction probable "
                   "(rappel : « milliard » = « billion », « billion » français = « trillion »)")
    else:
        r.ok.append(f"Unité du chiffre clé de même nature et même échelle en FR et EN ({_decrire(unite_ch['fr'])})")
    if unite_ch["fr"][0] == "pourcentage" and not 0 <= float(ch["valeur"]) <= 100:
        r.avertir(f"Chiffre clé en pourcentage hors de 0–100 ({ch['valeur']}) : variation en points ?")
    dec = ch.get("decimales")
    if isinstance(dec, int) and _decimales_reelles(ch["valeur"]) > dec:
        r.avertir(f"Chiffre clé {ch['valeur']} affiché arrondi à {dec} décimale(s) : arrondi voulu ?")

    # --- Périodes : mêmes années en FR et en EN
    annees_periode = {l: _annees(fiche.contexte("periode", l)) for l in LANGUES}
    if annees_periode["fr"] != annees_periode["en"]:
        r.bloquant(f"Période différente entre FR ({sorted(annees_periode['fr'])}) et EN "
                   f"({sorted(annees_periode['en'])})")
    periode = annees_periode["fr"] | annees_periode["en"]
    debut, fin = (min(periode), max(periode)) if periode else (None, None)
    if not periode:
        r.avertir("La période ne contient aucune année : la cohérence des années n'a pas pu être contrôlée")
        r.a_verifier.append("Les années citées (chiffre, graphique, textes) correspondent à la période annoncée "
                            "(non contrôlable automatiquement : période sans année)")
    else:
        hors = []
        for l in LANGUES:
            textes = [_unite_chiffre(ch, l)] + [s.texte for s in fiche.editions[l].scenes if s.type == "chiffre"]
            hors += [(l, a) for t in textes for a in _annees(t) if not debut <= a <= fin]
        for l, a in hors:
            r.avertir(f"Année {a} citée avec le chiffre clé, hors de la période annoncée {debut}–{fin}", l)
        if not hors:
            r.ok.append(f"Années citées avec le chiffre clé comprises dans la période {debut}–{fin}")

    if fiche.donnees:
        _coherence_graphique(fiche, r, unite_ch, debut, fin)
    r.a_verifier.append("Le chiffre clé et le graphique mesurent la même grandeur, avec la même définition "
                        "(la machine compare seulement les nombres et les mots d'échelle des unités)")

    _coherence_textes(fiche, r)


def _coherence_textes(fiche: Fiche, r: Rapport) -> None:
    # Mêmes nombres en FR et en EN (une adaptation ne change pas les chiffres)
    ensembles = {}
    for langue in LANGUES:
        vals = []
        for t in _textes_edition(fiche.editions[langue]):
            vals += nombres(t, langue)
        ensembles[langue] = sorted(set(round(v, 6) for v in vals))
    seulement_fr = sorted(set(ensembles["fr"]) - set(ensembles["en"]))
    seulement_en = sorted(set(ensembles["en"]) - set(ensembles["fr"]))
    if seulement_fr or seulement_en:
        r.avertir(f"Nombres différents entre FR et EN — seulement FR : {seulement_fr or '∅'} ; "
                  f"seulement EN : {seulement_en or '∅'}")
    else:
        r.ok.append("Les mêmes nombres figurent en FR et en EN")

    # Format des nombres propre à chaque langue
    for t in _textes_edition(fiche.editions["fr"]):
        m = re.search(r"\b\d+\.\d+\b", t)
        if m:
            r.avertir(f"Nombre au format anglais dans le texte français : « {m.group()} »", "fr")
            break
    for t in _textes_edition(fiche.editions["en"]):
        m = re.search(r"\b\d+,\d{1,2}\b(?!\d)", t)
        if m:
            r.avertir(f"Virgule décimale dans le texte anglais : « {m.group()} »", "en")
            break


def controler_fiche(fiche: Fiche, r: Rapport, aujourd_hui: dt.date | None = None) -> None:
    aujourd_hui = _date(aujourd_hui) or dt.date.today()
    if fiche.chemin.stem != fiche.id:
        r.avertir(f"L'identifiant « {fiche.id} » diffère du nom du fichier « {fiche.chemin.stem} »")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fiche.id):
        r.bloquant(f"Identifiant « {fiche.id} » : minuscules, chiffres et tirets uniquement")
    controler_validation(fiche, r, aujourd_hui)
    controler_sources(fiche, r, aujourd_hui)
    controler_editions(fiche, r)
    if fiche.pedagogique:
        from .pedagogie import controler_pedagogie
        _coherence_textes(fiche, r)
        controler_pedagogie(fiche, r)
    else:
        controler_coherence(fiche, r)


# --------------------------------------------------------------------------- rendus
def _officielle(p: dict, champ: str) -> bool:
    return ((p.get("references") or {}).get(champ) or {}).get("statut") == "officiel"


def _depassement(r: Rapport, p: dict, champ: str, message: str, langue: str, notes: list, etiquette: str) -> None:
    """Limite officielle dépassée = bloquant. Plafond non officiel = avertissement, présenté comme
    un choix interne de production (voir plateformes.yaml, « references »)."""
    if _officielle(p, champ):
        r.bloquant(message, langue)
        notes.append(f"❌ {etiquette}")
    else:
        r.avertir(f"{message} — plafond interne de production, non confirmé par une source officielle "
                  f"(production/plateformes.yaml, références de « {champ} ») : vérifier la limite actuelle "
                  "avant de publier", langue)
        notes.append(f"⚠️ {etiquette} (plafond interne)")


def controler_plateformes(langue: str, duree: float, legende: str, titre: str, nb_hashtags: int,
                          charte: dict, plateformes: dict, r: Rapport) -> None:
    zone = charte["zones_securite_video"]
    for cle in plateformes["cibles"]:
        p = plateformes["plateformes"][cle]
        nom = p["nom"]
        notes = []
        if duree > p["duree_max_s"]:
            _depassement(r, p, "duree_max_s", f"{nom} : durée {duree:.0f} s > maximum {p['duree_max_s']} s",
                         langue, notes, "durée")
        else:
            lo, hi = p.get("duree_conseillee_s", [0, 1e9])
            if not lo <= duree <= hi:
                r.avertir(f"{nom} : durée {duree:.0f} s hors de la fourchette conseillée {lo}–{hi} s", langue)
                notes.append("⚠️ durée")
        if len(legende) > p.get("legende_max", 1e9):
            _depassement(r, p, "legende_max", f"{nom} : légende de {len(legende)} caractères > {p['legende_max']}",
                         langue, notes, "légende")
        if "titre_max" in p and len(titre) > p["titre_max"]:
            _depassement(r, p, "titre_max", f"{nom} : titre de {len(titre)} caractères > {p['titre_max']}",
                         langue, notes, "titre")
        if nb_hashtags > p.get("hashtags_max", 1e9):
            _depassement(r, p, "hashtags_max", f"{nom} : {nb_hashtags} hashtags > {p['hashtags_max']}",
                         langue, notes, "hashtags")
        elif nb_hashtags > p.get("hashtags_conseilles", 1e9):
            notes.append(f"⚠️ {nb_hashtags} hashtags (≤ {p['hashtags_conseilles']} conseillés)")
        ui = p["zone_ui"]
        cote = [c for c in ("haut", "bas", "gauche", "droite") if zone[c] < ui[c]]
        if cote:
            r.avertir(f"{nom} : la zone de texte empiète sur l'interface ({', '.join(cote)})", langue)
            notes.append("⚠️ zone de sécurité")
        r.plateformes.append([langue.upper(), nom, f"{duree:.1f} s", "✅" if not notes else " ; ".join(notes)])


def controler_marque(charte: dict, r: Rapport) -> None:
    """Avant tout rendu : fichiers du logo présents et slogans exacts (le mode final refuse sinon)."""
    for langue in LANGUES:
        logos = _logo.charger_logos(charte.get("logo"), langue)
        if not logos.actif:
            if langue == LANGUES[0]:
                r.avertir("Logo désactivé dans production/charte.yaml (logo.actif: false)")
            continue
        for m in logos.manquants:
            r.bloquant(f"Logo officiel introuvable : {m}. Aucun logo de substitution n'est dessiné ; déposer le "
                       "fichier d'origine (voir assets/brand/actu-basics/LISEZMOI.md)")
        if not logos.manquants:
            r.ok.append(f"Logo officiel {langue.upper()} présent : " + ", ".join(
                f"{v} = {c.name}" for v, c in logos.chemins.items()))
    for langue in LANGUES:
        slogan = (charte.get("slogan") or {}).get(langue, "")
        r.verifier(slogan == _logo.SLOGANS_OFFICIELS[langue], f"Slogan {langue.upper()} conforme à la marque",
                   f"Slogan {langue.upper()} « {slogan} » différent du slogan officiel "
                   f"« {_logo.SLOGANS_OFFICIELS[langue]} » (production/charte.yaml)", BLOQUANT)


def controler_logo(langue: str, rendu, attendus: list[tuple[str, int, str]], charte: dict,
                   plateformes: dict, r: Rapport) -> None:
    """Logo officiel : présent, variante adaptée au fond, net, dégagé, dans les zones de sécurité.

    attendus : (support, index, type de scène) des images qui doivent porter le logo.
    """
    logos = rendu.logos
    if not logos.actif or not logos.images:
        return  # signalé avant le rendu par controler_marque
    r.verifier(logos.langue == langue, f"[{langue}] Logo de la bonne langue",
               f"[{langue}] Logo de la langue « {logos.langue} » utilisé pour la version {langue.upper()}", BLOQUANT)
    noms = {"video": "vidéo", "lecon": "vidéo 16:9", "carrousel": "carrousel", "couverture": "couverture"}
    horizontal = getattr(rendu, "format", "") == "lecon"   # cours 16:9 : pas d'interface d'application par-dessus
    zone_c = charte["marges_carrousel"]
    for support, index, type_ in attendus:
        pose = rendu.poses.get((support, index))
        lieu = f"{noms[support]}, scène {index + 1} ({type_})"
        if pose is None:
            r.bloquant(f"Logo absent ({lieu}) alors que la charte le prévoit", langue)
            continue
        x0, y0, x1, y1 = pose.boite
        w, h = rendu.largeur, rendu.hauteur
        if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
            r.bloquant(f"Logo coupé par le bord de l'image ({lieu})", langue)
        attendue = _logo.choisir_variante(pose.luminance_fond)
        if pose.variante != attendue:
            r.bloquant(f"Logo {pose.variante} sur un fond {'clair' if attendue == 'clair' else 'sombre'} "
                       f"({lieu}) : utiliser la variante {attendue}", langue)
        if pose.recouvrement > _logo.SEUIL_RECOUVREMENT:
            r.bloquant(f"Le logo touche un texte ou un graphique ({lieu} : {pose.recouvrement:.0%} de sa zone "
                       "de protection occupée)", langue)
        if pose.largeur > pose.largeur_native:
            r.avertir(f"Logo agrandi au-delà de sa résolution ({pose.largeur} px pour un fichier de "
                      f"{pose.largeur_native} px, {lieu}) : risque de flou, fournir un fichier plus grand", langue)
        ecran_tel = 844 if horizontal else 390   # téléphone tenu à l'horizontale pour un cours 16:9
        if pose.largeur * ecran_tel / w < _logo.LARGEUR_MOBILE_MIN:
            r.avertir(f"Logo petit sur téléphone ({round(pose.largeur * ecran_tel / w)} px à l'écran, {lieu})", langue)
        lis = (charte.get("logo") or {}).get("lisibilite") or {}
        if lis.get(langue):
            ecran = pose.largeur * ecran_tel / w
            nom, slogan = ecran * lis[langue]["nom"], ecran * lis[langue]["slogan"]
            if nom < lis.get("nom_min_px", 8):
                r.avertir(f"Nom ACTU-BASICS du logo peu lisible sur téléphone ({nom:.1f} px de haut, {lieu})",
                          langue)
            elif support != "couverture" and slogan < lis.get("slogan_min_px", 4):
                r.avertir(f"Slogan du logo peu lisible sur téléphone ({slogan:.1f} px de haut, {lieu}) : "
                          "agrandir le logo (largeur_px)", langue)
        if support == "carrousel":
            hors = (x0 < zone_c["gauche"] or y0 < zone_c["haut"] or x1 > w - zone_c["droite"]
                    or y1 > h - zone_c["bas"])
            if hors:
                r.avertir(f"Logo hors des marges du carrousel ({lieu})", langue)
        elif not horizontal:
            for cle in plateformes["cibles"]:
                p = plateformes["plateformes"][cle]
                z = p["zone_ui"]
                if x0 < z["gauche"] or y0 < z["haut"] or x1 > w - z["droite"] or y1 > h - z["bas"]:
                    r.avertir(f"{p['nom']} : le logo passe sous l'interface de l'application ({lieu})", langue)
        r.ok.append(f"[{langue}] Logo {pose.variante} ({lieu}) : {pose.largeur} px, fond "
                    f"{'clair' if attendue == 'clair' else 'sombre'} (luminance {pose.luminance_fond:.2f}), "
                    f"zone de protection libre, dans les zones de sécurité")


def controler_video(langue: str, sonde: dict, attendu: dict, r: Rapport) -> None:
    flux = {s["codec_type"]: s for s in sonde.get("streams", [])}
    v, a = flux.get("video", {}), flux.get("audio")
    r.verifier(v.get("width") == attendu["largeur"] and v.get("height") == attendu["hauteur"],
               f"Vidéo {attendu['largeur']}×{attendu['hauteur']}",
               f"Résolution inattendue {v.get('width')}×{v.get('height')}", langue=langue)
    r.verifier(v.get("codec_name") == "h264", "Codec H.264", f"Codec {v.get('codec_name')}", langue=langue)
    r.verifier(a is not None, "Piste audio présente", "Pas de piste audio", langue=langue)


def controler_lisibilite(langue: str, tailles: dict, r: Rapport) -> None:
    petits = {k: v for k, v in tailles.items() if v < TAILLE_TEXTE_MIN_PX}
    if petits:
        r.avertir("Texte principal petit sur mobile : " + ", ".join(f"{k} {v}px" for k, v in petits.items()), langue)
    else:
        r.ok.append(f"[{langue}] Texte principal ≥ {TAILLE_TEXTE_MIN_PX} px partout")


def controler_longueurs(durees: dict[str, list[float]], fiche: Fiche, r: Rapport) -> None:
    if set(durees) != set(LANGUES):
        return
    fr, en = durees["fr"], durees["en"]
    tf, te = sum(fr), sum(en)
    if abs(tf - te) / max(tf, te) > ECART_LONGUEUR_FR_EN:
        r.avertir(f"Durées FR ({tf:.0f} s) et EN ({te:.0f} s) très différentes")
    for i, (a, b) in enumerate(zip(fr, en)):
        if max(a, b) > 3 and abs(a - b) / max(a, b) > 0.5:
            r.avertir(f"Scène {i + 1} : {a:.1f} s en FR contre {b:.1f} s en EN")


# --------------------------------------------------------------------------- rapport
VERIFICATION_FACTUELLE = """\
## 1. Vérification factuelle — humaine, NON automatisable

La machine a seulement vérifié que les champs sont présents, bien formés et cohérents entre eux.
**Elle n'a pas vérifié que les chiffres sont vrais.** Avant validation, une personne doit :

- [ ] Ouvrir chaque source et retrouver chaque chiffre affiché ou prononcé (valeur, unité, année)
- [ ] Confirmer la période, le périmètre et la définition de l'indicateur
- [ ] Vérifier qu'il n'existe pas d'édition plus récente de la source
- [ ] Vérifier que la formulation (accroche, légende) ne déforme pas le chiffre
"""

CONTROLES_HUMAINS = """\
## 5. Contrôles humains visuels et audio (≈ 5 minutes)

- [ ] `inspection/planche-video.png` : aucun texte coupé, chevauchant ou illisible
- [ ] `inspection/apercu-mobile.png` : tout se lit à taille réelle de téléphone
- [ ] `inspection/zones-*.png` : rien d'important sous l'interface TikTok / Reels / Shorts
- [ ] Vidéo regardée en entier, son activé, FR puis EN
- [ ] Voix : prononciation des nombres, sigles et noms propres ; rythme ; volume
- [ ] Sous-titres synchronisés avec la voix, sans faute
- [ ] Légende : source et période présentes, bon compte (FR ou EN)
- [ ] Voix de synthèse : activer la mention « contenu généré par IA » sur chaque plateforme
"""


def ecrire_rapport(fiche: Fiche, r: Rapport, destination: Path, mode: str) -> str:
    if r.bloquants:
        etat = "❌ BLOQUÉ — ne pas publier"
    elif r.avertissements:
        etat = "⚠️ À VÉRIFIER"
    else:
        etat = "✅ Contrôles automatiques OK — vérifications humaines à faire"
    if mode == "apercu":
        etat += " · rendu d'APERÇU (jamais publiable)"
    lignes = [f"# Rapport qualité — {fiche.id}", "", f"**État : {etat}**", "",
              f"Mode : `{mode}` · statut de la fiche : `{fiche.statut}`", ""]
    lignes += [VERIFICATION_FACTUELLE]
    if r.a_verifier:
        lignes += ["Points que la machine n'a **pas** pu vérifier elle-même :", ""]
        lignes += [f"- [ ] {a}" for a in dict.fromkeys(r.a_verifier)] + [""]
    lignes += ["## 2. Erreurs bloquantes", ""]
    lignes += [f"- ❌ {c}" for c in r.bloquants] or ["Aucune."]
    lignes += ["", "## 3. Avertissements", ""]
    lignes += [f"- ⚠️ {c}" for c in r.avertissements] or ["Aucun."]
    if r.plateformes:
        lignes += ["", "## 4. Compatibilité plateformes", "", "| Langue | Plateforme | Durée | État |",
                   "|---|---|---|---|"] + [f"| {' | '.join(l)} |" for l in r.plateformes]
    lignes += ["", CONTROLES_HUMAINS]
    if r.production:
        lignes += ["## 6. Production", ""] + r.production + [""]
    lignes += ["## 7. Contrôles automatiques réussis", "", f"<details><summary>{len(r.ok)} contrôles</summary>", ""]
    lignes += [f"- ✅ {o}" for o in r.ok] + ["", "</details>", ""]
    texte = "\n".join(lignes)
    destination.write_text(texte, encoding="utf-8")
    return etat
