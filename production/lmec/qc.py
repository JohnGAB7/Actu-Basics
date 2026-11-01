"""Contrôles qualité automatiques + liste de contrôles humains -> rapport-qc.md."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .fiche import Fiche

LIMITES = {
    "titre_youtube": 100,
    "legende": 2200,        # Instagram ; TikTok accepte davantage
    "hashtags_max": 30,     # limite Instagram
    "hashtags_conseilles": 5,
    "duree_max_s": 60,      # au-delà : plus un « Short » partout
    "duree_min_s": 8,
}
MARQUEURS_INCOMPLETS = re.compile(r"\b(TODO|TBD|XXX|à compléter|to be completed)\b|\[\s*\.\.\.\s*\]", re.I)


@dataclass
class Rapport:
    erreurs: list[str] = field(default_factory=list)
    alertes: list[str] = field(default_factory=list)
    ok: list[str] = field(default_factory=list)

    def verifier(self, condition: bool, message_ok: str, message_ko: str, bloquant: bool = True):
        if condition:
            self.ok.append(message_ok)
        else:
            (self.erreurs if bloquant else self.alertes).append(message_ko)


def controler_fiche(fiche: Fiche, rapport: Rapport, brouillon_autorise: bool) -> None:
    if fiche.est_validee:
        rapport.ok.append(f"Fiche validée par {fiche.valide_par} ({fiche.date_validation or 'date ?'})")
    elif brouillon_autorise:
        rapport.alertes.append("Fiche NON validée : rendu en mode brouillon (filigrane), ne pas publier")
    else:
        rapport.erreurs.append("Fiche non validée (validation.statut ≠ « valide » ou valide_par vide)")

    for s in fiche.sources:
        rapport.verifier(str(s.get("url", "")).startswith(("http://", "https://")),
                         f"URL de source valide : {s['nom']}", f"URL de source invalide : {s['nom']}")
        rapport.verifier(bool(s.get("date_consultation")), f"Date de consultation : {s['nom']}",
                         f"Date de consultation manquante : {s['nom']}", bloquant=False)

    nb = {l: len(e.scenes) for l, e in fiche.editions.items()}
    rapport.verifier(len(set(nb.values())) == 1, "FR et EN ont le même nombre de scènes",
                     f"Nombre de scènes différent FR/EN {nb} (adaptation volontaire ?)", bloquant=False)

    for langue, ed in fiche.editions.items():
        textes = [ed.titre, ed.legende] + [s.texte for s in ed.scenes] + [s.voix_off for s in ed.scenes]
        incomplets = [t for t in textes if t and MARQUEURS_INCOMPLETS.search(t)]
        rapport.verifier(not incomplets, f"[{langue}] Aucun marqueur « à compléter »",
                         f"[{langue}] Texte incomplet : « {incomplets[0][:60] if incomplets else ''} »")
        rapport.verifier(len(ed.titre) <= LIMITES["titre_youtube"], f"[{langue}] Titre ≤ 100 caractères",
                         f"[{langue}] Titre trop long pour YouTube ({len(ed.titre)} car.)")
        types = [s.type for s in ed.scenes]
        rapport.verifier("source" in types, f"[{langue}] Scène source présente",
                         f"[{langue}] Aucune scène « source » : la source doit être visible", bloquant=True)
        rapport.verifier(len(ed.hashtags) <= LIMITES["hashtags_max"], f"[{langue}] Hashtags ≤ 30",
                         f"[{langue}] Trop de hashtags ({len(ed.hashtags)})")
        rapport.verifier(len(ed.hashtags) <= LIMITES["hashtags_conseilles"],
                         f"[{langue}] Hashtags ≤ {LIMITES['hashtags_conseilles']} (conseillé)",
                         f"[{langue}] {len(ed.hashtags)} hashtags : 3 à 5 conseillés", bloquant=False)


def controler_legende(langue: str, legende: str, rapport: Rapport) -> None:
    rapport.verifier(len(legende) <= LIMITES["legende"], f"[{langue}] Légende ≤ 2200 caractères",
                     f"[{langue}] Légende trop longue ({len(legende)} car.)")


def controler_video(langue: str, sonde: dict, attendu: dict, avec_voix: bool, rapport: Rapport) -> None:
    flux = {s["codec_type"]: s for s in sonde.get("streams", [])}
    v, a = flux.get("video", {}), flux.get("audio")
    duree = float(sonde.get("format", {}).get("duration", 0))
    rapport.verifier(v.get("width") == attendu["largeur"] and v.get("height") == attendu["hauteur"],
                     f"[{langue}] Vidéo {attendu['largeur']}x{attendu['hauteur']}",
                     f"[{langue}] Résolution inattendue {v.get('width')}x{v.get('height')}")
    rapport.verifier(v.get("codec_name") == "h264", f"[{langue}] Codec H.264",
                     f"[{langue}] Codec {v.get('codec_name')}")
    rapport.verifier(a is not None, f"[{langue}] Piste audio présente", f"[{langue}] Pas de piste audio")
    rapport.verifier(LIMITES["duree_min_s"] <= duree <= LIMITES["duree_max_s"],
                     f"[{langue}] Durée {duree:.1f} s (8–60 s)",
                     f"[{langue}] Durée {duree:.1f} s hors de 8–60 s", bloquant=False)
    if not avec_voix:
        rapport.alertes.append(f"[{langue}] Pas de voix off : piste silencieuse (ajouter une musique "
                               "libre de droits dans l'application de publication si souhaité)")


CONTROLES_HUMAINS = """\
## Contrôles humains (≈ 3 minutes)

Cocher avant de programmer la publication. Détail : `docs/technique/controles-qualite.md`.

- [ ] Planche `apercu-carrousel.png` FR et EN : aucun texte coupé, chevauchant ou illisible
- [ ] Le chiffre affiché est identique à la fiche validée (valeur, unité, période)
- [ ] FR et EN : formats des nombres corrects (8,2 / 8.2 ; 1 000 / 1,000)
- [ ] Vidéo regardée en entier au moins une fois, son activé
- [ ] Voix off (si présente) : prononciation des chiffres et des noms propres, volume
- [ ] Sous-titres synchronisés et sans faute
- [ ] Légende : source et période présentes, pas de faute, bon compte cible
- [ ] Aucun élément important sous l'interface des applications (bas / droite de l'écran)
"""


def ecrire_rapport(fiche: Fiche, rapport: Rapport, destination: Path, extras: list[str]) -> None:
    etat = "❌ BLOQUÉ" if rapport.erreurs else ("⚠️ À VÉRIFIER" if rapport.alertes else "✅ PRÊT")
    lignes = [f"# Rapport qualité — {fiche.id}", "", f"**État : {etat}**", ""]
    if rapport.erreurs:
        lignes += ["## Erreurs bloquantes", ""] + [f"- ❌ {e}" for e in rapport.erreurs] + [""]
    if rapport.alertes:
        lignes += ["## Alertes", ""] + [f"- ⚠️ {a}" for a in rapport.alertes] + [""]
    lignes += ["## Contrôles automatiques réussis", ""] + [f"- ✅ {o}" for o in rapport.ok] + [""]
    lignes += extras + [CONTROLES_HUMAINS]
    destination.write_text("\n".join(lignes), encoding="utf-8")
