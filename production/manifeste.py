"""Manifeste d'un rendu final : ce qui a été rendu, avec quoi, et qui l'a autorisé.

Usage (workflow « Validation finale », après les rendus) :
    python production/manifeste.py <fiche> --sortie sortie [--voix kokoro]

Le champ « valide_par » d'une fiche est une métadonnée éditoriale, pas une preuve d'autorisation :
n'importe qui peut l'écrire. La preuve, c'est l'approbation de l'environnement GitHub
« production » (relecteur requis) sur ce run précis, donc sur ce commit précis. Ce manifeste
consigne le commit, les empreintes SHA-256 de la fiche, de la charte, du moteur, des modèles de voix
et des rapports QC, ainsi que l'acteur GitHub du run (revue ChatGPT, PR #50, issue #51).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PRODUCTION = RACINE / "production"


def sha256(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def sha256_ensemble(fichiers: list[Path], base: Path) -> str:
    """Empreinte d'un ensemble de fichiers : chemins relatifs et contenus, dans l'ordre trié."""
    h = hashlib.sha256()
    for f in sorted(fichiers):
        h.update(str(f.relative_to(base)).encode() + b"\0" + sha256(f).encode() + b"\n")
    return h.hexdigest()


def _commande(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def construire(fiche: Path, sortie: Path, voix: str = "") -> dict:
    moteur = [*(PRODUCTION / "lmec").glob("*.py"), PRODUCTION / "produire.py"]
    configs = {n: sha256(PRODUCTION / n) for n in ("charte.yaml", "tts.yaml", "plateformes.yaml")
               if (PRODUCTION / n).exists()}
    modeles = {}
    dossier_voix = PRODUCTION / "voix"
    if dossier_voix.is_dir():
        modeles = {str(f.relative_to(dossier_voix)): sha256(f)
                   for f in sorted(dossier_voix.rglob("*")) if f.is_file()}
    rapports = {str(f.relative_to(sortie)): sha256(f) for f in sorted(sortie.rglob("rapport-qc.md"))} \
        if sortie.is_dir() else {}
    medias = {str(f.relative_to(sortie)): sha256(f) for f in sorted(sortie.rglob("*.mp4"))} \
        if sortie.is_dir() else {}
    ffmpeg = _commande(["ffmpeg", "-version"]).splitlines()
    return {
        "version_manifeste": 1,
        "cree_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": os.environ.get("GITHUB_SHA") or _commande(["git", "-C", str(RACINE), "rev-parse", "HEAD"]),
        "ref": os.environ.get("GITHUB_REF", ""),
        "autorisation": {
            # Seule preuve d'autorisation : l'approbation de l'environnement « production » sur ce run.
            "environnement": os.environ.get("ENVIRONNEMENT_GITHUB", ""),
            "lance_par": os.environ.get("GITHUB_TRIGGERING_ACTOR") or os.environ.get("GITHUB_ACTOR", ""),
            "run": (f"{os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}"
                    f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}") if os.environ.get("GITHUB_RUN_ID") else "",
        },
        "fiche": {"chemin": str(fiche), "sha256": sha256(fiche)},
        "configuration": configs,
        "moteur_sha256": sha256_ensemble(moteur, RACINE),
        "voix": {"fournisseur": voix, "modeles_sha256": modeles},
        "rapports_qc_sha256": rapports,
        "medias_sha256": medias,
        "environnement": {"python": platform.python_version(), "ffmpeg": ffmpeg[0] if ffmpeg else "",
                          "systeme": platform.platform()},
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("fiche", type=Path)
    p.add_argument("--sortie", type=Path, default=Path("sortie"))
    p.add_argument("--voix", default="")
    a = p.parse_args(argv)
    if not a.fiche.is_file():
        print(f"Fiche introuvable : {a.fiche}", file=sys.stderr)
        return 1
    m = construire(a.fiche, a.sortie, a.voix)
    a.sortie.mkdir(parents=True, exist_ok=True)
    (a.sortie / "manifeste.json").write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Manifeste écrit : {a.sortie / 'manifeste.json'} (commit {m['commit'][:12]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
