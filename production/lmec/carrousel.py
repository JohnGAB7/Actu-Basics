"""Carrousel 1080x1350 (4:5) : une image PNG par scène + planche d'aperçu."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from .fiche import Edition
from .rendu import Rendu


def produire_carrousel(rendu: Rendu, edition: Edition, dossier: Path) -> list[Path]:
    dossier.mkdir(parents=True, exist_ok=True)
    for ancien in dossier.glob("*.png"):
        ancien.unlink()
    chemins = []
    total = len(edition.scenes)
    for i, scene in enumerate(edition.scenes):
        chemin = dossier / f"{i + 1:02d}-{scene.type}.png"
        rendu.dessiner(scene, i, total).save(chemin, optimize=True)
        chemins.append(chemin)
    return chemins


def planche_apercu(images: list[Path], destination: Path, colonnes: int = 4, largeur_vignette: int = 360) -> None:
    """Toutes les diapositives sur une seule image : relecture en un coup d'œil."""
    vignettes = []
    for chemin in images:
        im = Image.open(chemin)
        h = round(im.height * largeur_vignette / im.width)
        vignettes.append(im.resize((largeur_vignette, h)))
    if not vignettes:
        return
    marge = 16
    lignes = -(-len(vignettes) // colonnes)
    h = vignettes[0].height
    planche = Image.new("RGB", (colonnes * (largeur_vignette + marge) + marge,
                                lignes * (h + marge) + marge), "white")
    for i, v in enumerate(vignettes):
        planche.paste(v, (marge + (i % colonnes) * (largeur_vignette + marge),
                          marge + (i // colonnes) * (h + marge)))
    planche.save(destination, optimize=True)
