"""Sous-titres SRT, script de voix off et métadonnées de publication."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .fiche import Edition, Fiche, Scene
from .formatage import _texte_langue, formater_chiffre, typographie, unite

CARACTERES_PAR_SOUS_TITRE = 84  # 2 lignes de ~42 caractères


def sans_marqueurs(texte: str) -> str:
    """Retire les astérisques de mise en valeur (*mot*)."""
    return texte.replace("*", "")


def texte_parle(scene: Scene, fiche: Fiche, langue: str) -> str:
    """Ce qui est dit (voix off) ou, à défaut, ce qui est lu à l'écran."""
    return sans_marqueurs(_texte_parle(scene, fiche, langue))


def _texte_parle(scene: Scene, fiche: Fiche, langue: str) -> str:
    if scene.voix_off:
        return scene.voix_off
    if scene.type == "chiffre":
        source = scene.extra if scene.extra.get("valeur") is not None else fiche.chiffre
        chiffre = f"{formater_chiffre(source, langue)} {unite(source, langue)}".strip()
        return f"{chiffre}. {scene.texte}".strip()
    if scene.type == "source":
        noms = ", ".join(_texte_langue(s["nom"], langue) for s in fiche.sources)
        return f"Source : {noms}" if langue == "fr" else f"Source: {noms}"
    if scene.type == "etapes" or (scene.type == "correction" and scene.extra.get("etapes")):
        lignes = [scene.texte] + scene.extra.get("etapes", []) + [scene.extra.get("reponse", "")]
        return ". ".join(l.rstrip(".") for l in lignes if l)
    if scene.type == "correction" and scene.extra.get("reponse"):
        return f"{scene.texte} {scene.extra['reponse']}".strip()
    return scene.texte


LIGNE_SOUS_TITRE = 42   # caractères par ligne, lisibles sur mobile


def deux_lignes(texte: str) -> str:
    """Coupe un sous-titre trop long en deux lignes équilibrées, à l'espace le plus proche du milieu."""
    if len(texte) <= LIGNE_SOUS_TITRE or " " not in texte:
        return texte
    milieu = len(texte) / 2
    espaces = [i for i, c in enumerate(texte) if c == " " and texte[i + 1:i + 2] not in ("?", "!", ":", ";", "»")]
    i = min(espaces or [texte.index(" ")], key=lambda k: abs(k - milieu))
    return texte[:i] + "\n" + texte[i + 1:]


def decouper_sous_titres(texte: str) -> list[str]:
    """Phrases, puis morceaux équilibrés de ≤ 84 caractères (pas de petit reste orphelin)."""
    phrases = re.split(r"(?<=[.!?…])\s+", texte.replace("\n", " ").strip())
    morceaux: list[str] = []
    for phrase in phrases:
        mots = phrase.split()
        if not mots:
            continue
        n = -(-len(phrase) // CARACTERES_PAR_SOUS_TITRE)
        cible = len(phrase) / n
        courant, coupes = "", 0
        for mot in mots:
            essai = f"{courant} {mot}".strip()
            if courant and (len(essai) > CARACTERES_PAR_SOUS_TITRE or (len(courant) >= cible and coupes < n - 1)):
                morceaux.append(courant)
                courant, coupes = mot, coupes + 1
            else:
                courant = essai
        if courant:
            morceaux.append(courant)
    return morceaux


def _horodatage(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def ecrire_srt(fiche: Fiche, edition: Edition, durees: list[float], destination: Path,
               reperes: list[tuple[float, float, str]] | None = None) -> None:
    """Sous-titres : calés sur la voix réelle si `reperes` est fourni, sinon répartis sur les scènes."""
    if reperes is None:
        reperes, t = [], 0.0
        for scene, duree in zip(edition.scenes, durees):
            morceaux = decouper_sous_titres(texte_parle(scene, fiche, edition.langue))
            longueur = sum(len(m) for m in morceaux) or 1
            debut = t
            for m in morceaux:
                fin = debut + duree * len(m) / longueur
                reperes.append((debut, fin, m))
                debut = fin
            t += duree
    blocs = []
    for n, (debut, fin, texte) in enumerate(reperes, 1):
        texte = deux_lignes(typographie(texte, edition.langue))
        blocs.append(f"{n}\n{_horodatage(debut)} --> {_horodatage(max(debut + 0.3, fin - 0.04))}\n{texte}\n")
    destination.write_text("\n".join(blocs), encoding="utf-8")


def ecrire_script_voix(fiche: Fiche, edition: Edition, durees: list[float], destination: Path,
                       lexique: dict | None = None) -> None:
    from .narration import preparer_pour_voix
    lignes = [f"# Script voix off — {fiche.id} — {edition.langue.upper()}",
              "# Un fichier par scène si vous enregistrez vous-même : 01.mp3, 02.mp3…",
              "# « Dit » = texte envoyé à la synthèse vocale (après lexique de prononciation).", ""]
    for i, (scene, duree) in enumerate(zip(edition.scenes, durees), 1):
        ecrit = texte_parle(scene, fiche, edition.langue)
        dit = preparer_pour_voix(ecrit, edition.langue, lexique or {})
        lignes.append(f"[{i:02d}] {scene.type} (~{duree:.1f} s)")
        lignes.append(ecrit)
        if dit != ecrit.replace("\u202f", " ").replace("\u00a0", " "):
            lignes.append(f"    Dit : {dit}")
        lignes.append("")
    destination.write_text("\n".join(lignes), encoding="utf-8")


def legende_complete(fiche: Fiche, edition: Edition) -> str:
    langue = edition.langue
    noms = ", ".join(_texte_langue(s["nom"], langue) for s in fiche.sources)
    periode = (fiche.contexte('periode', langue) or "").strip()
    suite = f" ({periode})" if periode else ""
    source = (f"Source : {noms}{suite}" if langue == "fr" else f"Source: {noms}{suite}")
    morceaux = [edition.legende.strip()] + ([typographie(source, langue)] if noms else [])
    if edition.hashtags:
        morceaux.append(" ".join(edition.hashtags))
    return "\n\n".join(morceaux)


def ecrire_metadonnees(fiche: Fiche, edition: Edition, durees: list[float], dossier: Path,
                       voix: dict | None = None, mode: str = "apercu") -> dict:
    legende = legende_complete(fiche, edition)
    (dossier / "legende.txt").write_text(legende + "\n", encoding="utf-8")
    meta = {
        "id": fiche.id, "langue": edition.langue, "theme": fiche.theme,
        "type_fiche": fiche.type_fiche, "famille": fiche.famille, "format": fiche.format, "image": fiche.format_image,
        "titre": edition.titre, "legende": legende, "hashtags": edition.hashtags,
        "sources": fiche.sources, "periode": fiche.contexte("periode", edition.langue),
        "perimetre": fiche.contexte("perimetre", edition.langue),
        "validation": {"statut": fiche.statut, "valide_par": fiche.valide_par,
                       "date": fiche.date_validation},
        "duree_video_s": round(sum(durees), 2),
        "durees_scenes_s": [round(d, 2) for d in durees],
        "mode": mode,
        "voix": voix or {"fournisseur": None},
        "fichiers": {"video": "video.mp4", "sous_titres": "sous-titres.srt",
                     "carrousel": "carrousel/", "legende": "legende.txt"},
        # Rempli à la main (ou par l'orchestrateur) après publication.
        "publication": {"statut": "a_publier", "plateformes": {}},
    }
    (dossier / "metadonnees.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2, default=str) + "\n",
                                             encoding="utf-8")
    return meta
