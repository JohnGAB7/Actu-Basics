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
    if isinstance(valeur, dt.date):
        return valeur
    try:
        return dt.date.fromisoformat(str(valeur).strip())
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
    return [ed.titre, ed.legende] + [s.texte for s in ed.scenes] + [s.voix_off for s in ed.scenes if s.voix_off]


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
        for t in SCENES_OBLIGATOIRES:
            r.verifier(t in types, f"Scène « {t} » présente", f"Scène obligatoire « {t} » absente", langue=langue)
        if types and types[0] != "accroche":
            r.avertir("La vidéo ne commence pas par l'accroche", langue)
        if types and types[-1] != "fin":
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

    nb = {l: len(e.scenes) for l, e in fiche.editions.items()}
    r.verifier(len(set(nb.values())) == 1, "FR et EN ont le même nombre de scènes",
               f"Nombre de scènes différent FR/EN {nb} (adaptation volontaire ?)", AVERTISSEMENT)


def controler_coherence(fiche: Fiche, r: Rapport) -> None:
    ch = fiche.chiffre
    for cle in ("unite", "suffixe", "prefixe"):
        v = ch.get(cle)
        if isinstance(v, dict) and bool(v.get("fr")) != bool(v.get("en")):
            r.bloquant(f"chiffre_cle.{cle} renseigné dans une seule langue")
    for cle in ("periode", "perimetre", "definition"):
        for langue in LANGUES:
            if not fiche.contexte(cle, langue).strip():
                r.bloquant(f"contexte.{cle} vide", langue)

    if fiche.donnees:
        points = fiche.donnees["points"]
        valeur = float(ch["valeur"])
        en_avant = [p for p in points if p.get("mis_en_avant")]
        if en_avant and all(abs(float(p["valeur"]) - valeur) > 1e-9 for p in en_avant):
            r.avertir(f"Le point mis en avant du graphique ({en_avant[0]['valeur']}) diffère du chiffre clé "
                      f"({ch['valeur']}) : même grandeur, même unité ?")
        elif not any(abs(float(p["valeur"]) - valeur) < 1e-9 for p in points):
            r.avertir("Le chiffre clé n'apparaît dans aucun point du graphique (normal seulement s'il "
                      "s'agit d'une autre grandeur)")
        else:
            r.ok.append("Chiffre clé présent dans le graphique")
        u = fiche.donnees.get("unite")
        if isinstance(u, dict) and bool(u.get("fr")) != bool(u.get("en")):
            r.bloquant("donnees.unite renseignée dans une seule langue")
        if any(p["valeur"] < 0 for p in points):
            r.avertir("Valeurs négatives : le graphique en barres ne les représente pas correctement")
        # Années des libellés comprises dans la période annoncée
        annees_periode = [int(a) for a in ANNEE.findall(fiche.contexte("periode", "fr"))]
        if len(annees_periode) >= 1:
            debut, fin = min(annees_periode), max(annees_periode)
            for p in points:
                for langue in LANGUES:
                    lab = p.get("label")
                    lab = lab.get(langue, "") if isinstance(lab, dict) else str(lab)
                    hors = [int(a) for a in ANNEE.findall(lab) if not debut <= int(a) <= fin]
                    if hors:
                        r.avertir(f"Libellé « {lab} » hors de la période {debut}–{fin}", langue)
                        break

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
    aujourd_hui = aujourd_hui or dt.date.today()
    if fiche.chemin.stem != fiche.id:
        r.avertir(f"L'identifiant « {fiche.id} » diffère du nom du fichier « {fiche.chemin.stem} »")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", fiche.id):
        r.bloquant(f"Identifiant « {fiche.id} » : minuscules, chiffres et tirets uniquement")
    controler_validation(fiche, r, aujourd_hui)
    controler_sources(fiche, r, aujourd_hui)
    controler_editions(fiche, r)
    controler_coherence(fiche, r)


# --------------------------------------------------------------------------- rendus
def controler_plateformes(langue: str, duree: float, legende: str, titre: str, nb_hashtags: int,
                          charte: dict, plateformes: dict, r: Rapport) -> None:
    zone = charte["zones_securite_video"]
    for cle in plateformes["cibles"]:
        p = plateformes["plateformes"][cle]
        nom = p["nom"]
        notes = []
        if duree > p["duree_max_s"]:
            r.bloquant(f"{nom} : durée {duree:.0f} s > maximum {p['duree_max_s']} s", langue)
            notes.append("❌ durée")
        else:
            lo, hi = p.get("duree_conseillee_s", [0, 1e9])
            if not lo <= duree <= hi:
                r.avertir(f"{nom} : durée {duree:.0f} s hors de la fourchette conseillée {lo}–{hi} s", langue)
                notes.append("⚠️ durée")
        if len(legende) > p.get("legende_max", 1e9):
            r.bloquant(f"{nom} : légende de {len(legende)} caractères > {p['legende_max']}", langue)
            notes.append("❌ légende")
        if "titre_max" in p and len(titre) > p["titre_max"]:
            r.bloquant(f"{nom} : titre de {len(titre)} caractères > {p['titre_max']}", langue)
            notes.append("❌ titre")
        if nb_hashtags > p.get("hashtags_max", 1e9):
            r.bloquant(f"{nom} : {nb_hashtags} hashtags > {p['hashtags_max']}", langue)
            notes.append("❌ hashtags")
        elif nb_hashtags > p.get("hashtags_conseilles", 1e9):
            notes.append(f"⚠️ {nb_hashtags} hashtags (≤ {p['hashtags_conseilles']} conseillés)")
        ui = p["zone_ui"]
        cote = [c for c in ("haut", "bas", "gauche", "droite") if zone[c] < ui[c]]
        if cote:
            r.avertir(f"{nom} : la zone de texte empiète sur l'interface ({', '.join(cote)})", langue)
            notes.append("⚠️ zone de sécurité")
        r.plateformes.append([langue.upper(), nom, f"{duree:.1f} s", "✅" if not notes else " ; ".join(notes)])


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
