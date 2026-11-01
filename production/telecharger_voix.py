#!/usr/bin/env python3
"""Télécharge les modèles de voix Piper listés dans production/tts.yaml vers production/voix/.

    python production/telecharger_voix.py
"""
from __future__ import annotations

import io
import sys
import tarfile
import urllib.request
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent
DOSSIER = RACINE / "voix"


def main() -> int:
    config = yaml.safe_load((RACINE / "tts.yaml").read_text(encoding="utf-8"))
    DOSSIER.mkdir(exist_ok=True)
    for modele, url in (config.get("piper_telechargements") or {}).items():
        if (DOSSIER / modele).exists() and (DOSSIER / f"{modele}.json").exists():
            print(f"✓ {modele} déjà présent")
            continue
        print(f"↓ {modele} ({url})")
        with urllib.request.urlopen(url, timeout=600) as rep:
            archive = tarfile.open(fileobj=io.BytesIO(rep.read()), mode="r:gz")
        base = modele[:-len(".onnx")]
        voulus = {f"{base}.onnx": modele, f"{base}.onnx.json": f"{modele}.json", "MODEL_CARD": f"{base}.LISEZMOI"}
        for membre in archive.getmembers():
            nom = Path(membre.name).name           # jamais de chemin : pas d'écriture hors du dossier
            if membre.isfile() and nom in voulus:
                (DOSSIER / voulus[nom]).write_bytes(archive.extractfile(membre).read())
        if not (DOSSIER / modele).exists():
            print(f"❌ {modele} absent de l'archive")
            return 1
    print(f"Voix disponibles dans {DOSSIER}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
