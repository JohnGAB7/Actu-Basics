"""Inventaire vérifié d'un dossier de sortie (artefact CI) : chaque fichier, sa taille, son SHA-256,
et pour les vidéos et narrations la durée, la résolution, la cadence et l'audio (ffprobe).

Échoue (code 1) si une langue rendue n'a pas de vidéo, si une vidéo n'a pas de piste audio,
ou si un fichier attendu manque. C'est ce qui aurait signalé l'artefact sans vidéo anglaise.

Usage : python production/inventaire.py sortie/ [--sortie sortie/INVENTAIRE.md]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ATTENDUS = ("video.mp4", "sous-titres.srt", "script-voix-off.txt", "miniature.jpg", "metadonnees.json")
LANGUES = ("fr", "en")


def sonder(chemin: Path) -> dict:
    sortie = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
                             "-of", "json", str(chemin)], capture_output=True, text=True)
    if sortie.returncode:
        return {}
    return json.loads(sortie.stdout or "{}")


def decrire(info: dict) -> str:
    if not info:
        return "illisible"
    morceaux = [f"{float(info.get('format', {}).get('duration', 0)):.1f} s"]
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            n, _, d = s.get("r_frame_rate", "0/1").partition("/")
            morceaux.append(f"{s.get('codec_name')} {s.get('width')}×{s.get('height')} {float(n) / float(d or 1):g} i/s")
        elif s.get("codec_type") == "audio":
            morceaux.append(f"audio {s.get('codec_name')} {s.get('sample_rate')} Hz, {s.get('channels')} canal(aux)")
    return ", ".join(morceaux)


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def inventorier(racine: Path) -> tuple[str, list[str]]:
    erreurs, lignes = [], ["# Inventaire de l'artefact", ""]
    fiches = sorted(p for p in racine.iterdir() if p.is_dir() and any((p / l).is_dir() for l in LANGUES))
    for fiche in fiches:
        lignes += [f"## {fiche.name}", ""]
        for langue in LANGUES:
            dossier = fiche / langue
            if not dossier.is_dir():
                continue
            attendus = list(ATTENDUS)
            try:
                meta = json.loads((dossier / "metadonnees.json").read_text(encoding="utf-8"))
            except (OSError, ValueError):
                meta = {}
            fournisseur = (meta.get("voix") or {}).get("fournisseur")
            if fournisseur and fournisseur != "aucune":
                attendus.append("narration.wav")   # une voix a été produite : sa piste doit être livrée
            lignes.append(f"- {langue} : voix {fournisseur or 'aucune'}"
                          f"{' (' + (meta.get('voix') or {}).get('config', {}).get('voix', '') + ')' if fournisseur else ''}")
            for nom in attendus:
                if not (dossier / nom).is_file():
                    erreurs.append(f"{fiche.name}/{langue}/{nom} manquant")
            video = dossier / "video.mp4"
            if video.is_file():
                info = sonder(video)
                if not any(s.get("codec_type") == "audio" for s in info.get("streams", [])):
                    erreurs.append(f"{fiche.name}/{langue}/video.mp4 sans piste audio")
                if float(info.get("format", {}).get("duration", 0) or 0) <= 0:
                    erreurs.append(f"{fiche.name}/{langue}/video.mp4 de durée nulle")
        lignes += ["", "| Fichier | Taille | Contenu | SHA-256 |", "|---|---|---|---|"]
        for f in sorted(p for p in fiche.rglob("*") if p.is_file()):
            contenu = decrire(sonder(f)) if f.suffix in (".mp4", ".wav", ".mp3") else ""
            taille = f"{f.stat().st_size:,}".replace(",", " ")
            lignes.append(f"| `{f.relative_to(fiche)}` | {taille} o | {contenu} | `{sha256(f)}` |")
        lignes.append("")
    if not fiches:
        erreurs.append("aucune fiche rendue")
    lignes += ["## Contrôle", ""] + ([f"- ❌ {e}" for e in erreurs] or
                                     ["- ✅ chaque langue rendue a sa vidéo avec piste audio, et tous les fichiers attendus"])
    return "\n".join(lignes) + "\n", erreurs


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("dossier", type=Path)
    p.add_argument("--sortie", type=Path)
    a = p.parse_args()
    texte, erreurs = inventorier(a.dossier)
    print(texte)
    if a.sortie:
        a.sortie.write_text(texte, encoding="utf-8")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
