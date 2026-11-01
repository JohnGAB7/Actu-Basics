"""Logo officiel ACTU-BASICS : chargement, choix de la variante, placement.

Règles (assets/brand/actu-basics/BRAND_GUIDELINES.md) :
- seuls les fichiers officiels sont utilisés ; aucun logo n'est dessiné ni « reconstitué » ;
- un logo par langue (chacun porte le slogan de sa langue) ;
- variante claire sur fond clair, variante sombre sur fond sombre ;
- proportions, couleurs et zone de protection préservées : redimensionnement proportionnel
  uniquement (jamais d'étirement, de recadrage, de recoloration ni d'effet) ;
- jamais sur un texte, un graphique ou une zone chargée ; dans les zones de sécurité.

Si un fichier manque, rien n'est dessiné à sa place : le contrôle qualité bloque le rendu final.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageStat

DEPOT = Path(__file__).resolve().parents[2]
VARIANTES = ("clair", "sombre")
LANGUES_LOGO = ("fr", "en")
POSITIONS = ("haut_gauche", "haut_centre", "haut_droite", "centre", "bas_gauche", "bas_centre", "bas_droite")
SEUIL_FOND_CLAIR = 0.5        # luminance moyenne (0–1) au-dessus de laquelle le fond est « clair »
SLOGANS_OFFICIELS = {"fr": "Éveiller par les chiffres.", "en": "Enlightening through numbers."}
ANCIENNES_SIGNATURES = ("le monde en chiffres", "the world in numbers", "un chiffre à la fois",
                        "one number at a time")
LARGEUR_MOBILE_MIN = 90       # px à l'écran d'un téléphone (390 px de large) : en dessous, logo illisible
SEUIL_RECOUVREMENT = 0.02     # part de la zone du logo (avec protection) occupée par autre chose que le fond


@dataclass
class Pose:
    """Un logo posé sur une image (pour le contrôle qualité)."""
    support: str              # video | carrousel | couverture
    scene: str
    index: int
    boite: tuple[int, int, int, int]          # logo seul (x0, y0, x1, y1)
    boite_protection: tuple[int, int, int, int]
    variante: str
    largeur: int
    largeur_native: int
    luminance_fond: float
    recouvrement: float = 0.0  # part de la zone de protection déjà occupée (texte, graphique…)


@dataclass
class Logos:
    conf: dict
    langue: str = "fr"
    images: dict[str, Image.Image] = field(default_factory=dict)
    chemins: dict[str, Path] = field(default_factory=dict)
    manquants: list[str] = field(default_factory=list)

    @property
    def actif(self) -> bool:
        return bool(self.conf.get("actif", False))

    def disponible(self, variante: str) -> bool:
        return variante in self.images


def fichiers_langue(conf: dict | None, langue: str) -> dict:
    """Candidats par variante pour une langue : fichiers.<langue>.<variante> (ou fichiers.<variante>,
    même logo pour toutes les langues)."""
    fichiers = (conf or {}).get("fichiers") or {}
    if any(l in fichiers for l in LANGUES_LOGO):
        return fichiers.get(langue) or {}
    return fichiers


def charger_logos(conf: dict | None, langue: str = "fr") -> Logos:
    conf = conf or {}
    logos = Logos(conf, langue)
    if not logos.actif:
        return logos
    dossier = DEPOT / conf.get("dossier", "assets/brand/actu-basics")
    fichiers = fichiers_langue(conf, langue)
    for variante in VARIANTES:
        candidats = fichiers.get(variante) or []
        trouve = next((dossier / c for c in candidats if (dossier / c).is_file()), None)
        if trouve is None:
            logos.manquants.append(f"[{langue}] {dossier.relative_to(DEPOT) if dossier.is_relative_to(DEPOT) else dossier}/"
                                   f"{' ou '.join(candidats)}")
            continue
        logos.chemins[variante] = trouve
        logos.images[variante] = _ouvrir(str(trouve))
    return logos


@lru_cache(maxsize=8)
def _ouvrir(chemin: str) -> Image.Image:
    im = Image.open(chemin)
    im.load()
    return im.convert("RGBA")


@lru_cache(maxsize=32)
def _redimensionner(chemin: str, largeur: int) -> Image.Image:
    """Redimensionnement PROPORTIONNEL (jamais d'étirement)."""
    im = _ouvrir(chemin)
    if largeur == im.width:
        return im
    hauteur = round(im.height * largeur / im.width)
    return im.resize((largeur, hauteur), Image.LANCZOS)


def luminance(image: Image.Image, boite) -> float:
    zone = image.crop(boite).convert("L")
    return ImageStat.Stat(zone).mean[0] / 255


def choisir_variante(lum_fond: float, demande: str = "auto") -> str:
    if demande in VARIANTES:
        return demande
    return "clair" if lum_fond >= SEUIL_FOND_CLAIR else "sombre"


def boite_position(position: str, zone: tuple[int, int, int, int], largeur: int, hauteur: int,
                   marge: int) -> tuple[int, int]:
    """Coin haut-gauche du logo, ancré dans `zone` (zone de sécurité ou marges) + `marge`."""
    g, h, d, b = zone
    if position not in POSITIONS:
        raise ValueError(f"Position de logo inconnue « {position} » ({', '.join(POSITIONS)})")
    horiz = position.split("_")[-1] if "_" in position else "centre"
    vert = position.split("_")[0] if "_" in position else "centre"
    x = {"gauche": g + marge, "droite": d - marge - largeur}.get(horiz, (g + d - largeur) // 2)
    y = {"haut": h + marge, "bas": b - marge - hauteur}.get(vert, (h + b - hauteur) // 2)
    return int(x), int(y)


def recouvrement(image: Image.Image, fond: Image.Image, boite, tolerance: int = 24) -> float:
    """Part des pixels de `boite` qui diffèrent du fond nu (texte, barre, graphique déjà dessinés)."""
    from PIL import ImageChops
    a = image.crop(boite).convert("L")
    f = fond.crop(boite).convert("L")
    if not a.width or not a.height:
        return 0.0
    masque = ImageChops.difference(a, f).point(lambda v: 255 if v > tolerance else 0)
    return ImageStat.Stat(masque).mean[0] / 255


def poser(image: Image.Image, fond: Image.Image, logos: Logos, *, x: int, y: int, largeur: int,
          variante_demandee: str, protection: float, support: str, scene: str, index: int,
          opacite: float = 1.0, mesurer: bool = True) -> Pose | None:
    """Colle le logo (variante adaptée au fond) à (x, y). Retourne la pose, ou None si indisponible."""
    if not logos.images:
        return None
    ref = next(iter(logos.images.values()))
    hauteur = round(ref.height * largeur / ref.width)
    boite = (x, y, x + largeur, y + hauteur)
    lum = luminance(fond, boite)
    variante = choisir_variante(lum, variante_demandee)
    if not logos.disponible(variante):
        return None
    source = logos.images[variante]
    hauteur = round(source.height * largeur / source.width)
    boite = (x, y, x + largeur, y + hauteur)
    p = round(largeur * protection)
    boite_p = (max(0, x - p), max(0, y - p), min(image.width, x + largeur + p), min(image.height, y + hauteur + p))
    occupe = recouvrement(image, fond, boite_p) if mesurer else 0.0
    im = _redimensionner(str(logos.chemins[variante]), largeur)
    if opacite < 1.0:
        alpha = im.getchannel("A").point(lambda v: round(v * max(0.0, opacite)))
        im = im.copy()
        im.putalpha(alpha)
    image.paste(im, (x, y), im)
    return Pose(support, scene, index, boite, boite_p, variante, largeur, source.width, round(lum, 3),
                round(occupe, 4))
