"""Sous-titres SRT, script de voix off et métadonnées de publication."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .fiche import Edition, Fiche, Scene
from .formatage import formater_chiffre, typographie, unite

CARACTERES_PAR_SOUS_TITRE = 84  # 2 lignes de ~42 caractères


def texte_parle(scene: Scene, fiche: Fiche, langue: str) -> str:
    """Ce qui est dit (voix off) ou, à défaut, ce qui est lu à l'écran."""
    if scene.voix_off:
        return scene.voix_off
    if scene.type == "chiffre":
        chiffre = f"{formater_chiffre(fiche.chiffre, langue)} {unite(fiche.chiffre, langue)}".strip()
        return f"{chiffre}. {scene.texte}".strip()
    if scene.type == "source":
        noms = ", ".join(s["nom"] for s in fiche.sources)
        return f"Source : {noms}" if langue == "fr" else f"Source: {noms}"
    return scene.texte


def _decouper(texte: str) -> list[str]:
    phrases = re.split(r"(?<=[.!?…])\s+", texte.replace("\n", " ").strip())
    morceaux: list[str] = []
    for phrase in phrases:
        courant = ""
        for mot in phrase.split():
            if len(courant) + len(mot) + 1 > CARACTERES_PAR_SOUS_TITRE and courant:
                morceaux.append(courant)
                courant = mot
            else:
                courant = f"{courant} {mot}".strip()
        if courant:
            morceaux.append(courant)
    return morceaux


def _horodatage(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ecrire_srt(fiche: Fiche, edition: Edition, durees: list[float], destination: Path) -> None:
    blocs, t, n = [], 0.0, 1
    for scene, duree in zip(edition.scenes, durees):
        morceaux = _decouper(typographie(texte_parle(scene, fiche, edition.langue), edition.langue))
        longueur = sum(len(m) for m in morceaux) or 1
        debut = t
        for m in morceaux:
            fin = debut + duree * len(m) / longueur
            blocs.append(f"{n}\n{_horodatage(debut)} --> {_horodatage(fin - 0.05)}\n{m}\n")
            n, debut = n + 1, fin
        t += duree
    destination.write_text("\n".join(blocs), encoding="utf-8")


def ecrire_script_voix(fiche: Fiche, edition: Edition, durees: list[float], destination: Path) -> None:
    lignes = [f"# Script voix off — {fiche.id} — {edition.langue.upper()}",
              "# À enregistrer (ou synthétiser) tel quel ; durées indicatives.", ""]
    for i, (scene, duree) in enumerate(zip(edition.scenes, durees), 1):
        lignes.append(f"[{i}] {scene.type} (~{duree:.1f} s)")
        lignes.append(texte_parle(scene, fiche, edition.langue))
        lignes.append("")
    destination.write_text("\n".join(lignes), encoding="utf-8")


def legende_complete(fiche: Fiche, edition: Edition) -> str:
    langue = edition.langue
    noms = ", ".join(s["nom"] for s in fiche.sources)
    source = (f"Source : {noms} ({fiche.contexte('periode', langue)})" if langue == "fr"
              else f"Source: {noms} ({fiche.contexte('periode', langue)})")
    morceaux = [edition.legende.strip(), typographie(source, langue)]
    if edition.hashtags:
        morceaux.append(" ".join(edition.hashtags))
    return "\n\n".join(morceaux)


def ecrire_metadonnees(fiche: Fiche, edition: Edition, durees: list[float], dossier: Path) -> dict:
    legende = legende_complete(fiche, edition)
    (dossier / "legende.txt").write_text(legende + "\n", encoding="utf-8")
    meta = {
        "id": fiche.id, "langue": edition.langue, "theme": fiche.theme,
        "titre": edition.titre, "legende": legende, "hashtags": edition.hashtags,
        "sources": fiche.sources, "periode": fiche.contexte("periode", edition.langue),
        "perimetre": fiche.contexte("perimetre", edition.langue),
        "validation": {"statut": fiche.statut, "valide_par": fiche.valide_par,
                       "date": fiche.date_validation},
        "duree_video_s": round(sum(durees), 2),
        "fichiers": {"video": "video.mp4", "sous_titres": "sous-titres.srt",
                     "carrousel": "carrousel/", "legende": "legende.txt"},
        # Rempli à la main (ou par l'orchestrateur) après publication.
        "publication": {"statut": "a_publier", "plateformes": {}},
    }
    (dossier / "metadonnees.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8")
    return meta
