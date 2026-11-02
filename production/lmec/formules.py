"""Formules mathématiques (notation LaTeX) rendues en image, sans installation de LaTeX.

Utilise le moteur « mathtext » de matplotlib (fractions, indices, exposants, sommes, lettres grecques,
\\binom, \\approx…). Les environnements LaTeX complets (align, tableaux) ne sont pas pris en charge.
"""
from __future__ import annotations

import io
from functools import lru_cache

from PIL import Image


def _mpl():
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["mathtext.fontset"] = "stix"     # rendu proche de LaTeX
    from matplotlib.figure import Figure
    return Figure


def formule_valide(formule: str) -> str | None:
    """None si la formule est rendue, sinon le message d'erreur."""
    try:
        _image(formule, 40, (255, 255, 255))
        return None
    except ImportError:
        return "matplotlib absent : pip install -r production/requirements.txt"
    except Exception as exc:  # ValueError de mathtext : syntaxe
        return str(exc).strip().splitlines()[-1][:160]


@lru_cache(maxsize=64)
def _image(formule: str, taille: int, couleur: tuple) -> Image.Image:
    Figure = _mpl()
    fig = Figure(figsize=(0.01, 0.01), dpi=100)
    fig.text(0, 0, f"${formule}$", fontsize=taille, color=tuple(c / 255 for c in couleur))
    tampon = io.BytesIO()
    fig.savefig(tampon, format="png", transparent=True, bbox_inches="tight", pad_inches=0.04, dpi=100)
    tampon.seek(0)
    im = Image.open(tampon)
    im.load()
    return im.convert("RGBA")


def image_formule(formule: str, couleur: tuple, largeur_max: int, hauteur_max: int,
                  taille_max: int = 110, taille_min: int = 28) -> Image.Image:
    """Plus grande formule qui tient dans largeur_max × hauteur_max."""
    taille = taille_max
    while True:
        im = _image(formule, taille, tuple(couleur))
        if (im.width <= largeur_max and im.height <= hauteur_max) or taille <= taille_min:
            return im
        taille -= 4


def images_formules(lignes: list[str], couleur: tuple, largeur_max: int, hauteur_max: int,
                    interligne: int = 40, taille_max: int = 110, taille_min: int = 28) -> list[Image.Image]:
    """Plusieurs lignes à la MÊME taille (la plus grande qui fait tout tenir)."""
    taille = taille_max
    while True:
        ims = [_image(l, taille, tuple(couleur)) for l in lignes]
        h = sum(im.height for im in ims) + interligne * (len(ims) - 1)
        if (max(im.width for im in ims) <= largeur_max and h <= hauteur_max) or taille <= taille_min:
            return ims
        taille -= 4
