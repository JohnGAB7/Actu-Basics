"""Décor en mouvement : des ondes de données qui glissent lentement au bas de l'image, derrière le contenu.

Les plateformes pénalisent les images figées, et un fond qui respire garde l'œil attentif. Ce décor
anime chaque image, même pendant une explication posée, sans jamais toucher au contenu (texte,
formules, graphiques, logo) :
- il n'est peint que là où l'image montre encore le fond, et s'estompe en douceur à l'approche du
  contenu (masque adouci, marge `ecart_px`) ;
- il ne passe jamais dans le bandeau du logo mobile (zone de protection du logo libre) ;
- ses couleurs sont celles de la charte, à faible opacité.

Chaque onde est une couche périodique (sa longueur d'onde) calculée une fois : à chaque image, un simple
recadrage la fait glisser, chacune à sa vitesse, ce qui donne l'impression de profondeur. Seule la bande
du bas où passent les ondes est recomposée ; le masque du contenu est calculé à quart de définition
et réutilisé tel quel pour les images fixes d'une scène.
"""
from __future__ import annotations

import math

from PIL import Image, ImageChops, ImageDraw, ImageFilter

REDUCTION = 4   # le masque du contenu est calculé sur une image 4 fois plus petite

ONDES_DEFAUT = [
    {"couleur": "barre", "opacite": 0.10, "amplitude": 0.035, "longueur": 0.75, "niveau": 0.76, "vitesse": 22},
    {"couleur": "barre", "opacite": 0.07, "amplitude": 0.05, "longueur": 1.05, "niveau": 0.83, "vitesse": -14},
    {"couleur": "accent", "opacite": 0.07, "amplitude": 0.025, "longueur": 0.6, "niveau": 0.9, "vitesse": 30},
]


class Onde:
    """Une couche : surface sous une courbe périodique, avec une crête un peu plus marquée."""

    def __init__(self, conf: dict, couleurs: dict, largeur: int, hauteur: int, haut_bande: int):
        self.longueur = max(200, round(float(conf.get("longueur", 0.8)) * largeur))
        self.vitesse = float(conf.get("vitesse", 20))
        couleur = conf.get("couleur", "barre")
        rgb = couleurs.get(couleur, couleurs["barre"]) if isinstance(couleur, str) else tuple(couleur)
        self.couleur = rgb
        opacite = max(0.0, min(0.5, float(conf.get("opacite", 0.08))))
        amplitude = float(conf.get("amplitude", 0.04)) * hauteur
        niveau = float(conf.get("niveau", 0.8)) * hauteur - haut_bande
        h_bande = hauteur - haut_bande
        w = largeur + self.longueur
        k = 2 * math.pi / self.longueur
        crete = [(x, niveau + amplitude * math.sin(k * x) + 0.35 * amplitude * math.sin(2 * k * x + 1.3))
                 for x in range(0, w + 1, 6)]
        alpha = Image.new("L", (w, h_bande), 0)
        d = ImageDraw.Draw(alpha)
        d.polygon(crete + [(w, h_bande), (0, h_bande)], fill=round(255 * opacite))
        d.line(crete, fill=round(255 * min(0.6, opacite * 2.6)), width=3)   # trait de crête, net
        self.alpha = alpha

    def decalage(self, temps: float) -> int:
        return int(temps * self.vitesse) % self.longueur


class Decor:
    def __init__(self, fond: Image.Image, couleurs: dict, conf: dict, bandeau_px: int = 0):
        self.fond = fond
        self.largeur, self.hauteur = fond.size
        self.ecart = max(0, int(conf.get("ecart_px", 24)))
        self.bandeau = max(0, int(bandeau_px))
        ondes = conf.get("ondes") or ONDES_DEFAUT
        # Haut de la bande animée : au-dessus de la plus haute crête, jamais dans le bandeau du logo.
        haut = min(float(o.get("niveau", 0.8)) - 1.4 * float(o.get("amplitude", 0.04)) for o in ondes)
        self.haut_bande = max(self.bandeau, int(haut * self.hauteur))
        self.ondes = [Onde(o, couleurs, self.largeur, self.hauteur, self.haut_bande) for o in ondes]
        self.fond_bande = fond.crop((0, self.haut_bande, self.largeur, self.hauteur))
        self._unis = {o.couleur: Image.new("RGB", self.fond_bande.size, o.couleur) for o in self.ondes}

    def masque_libre(self, image: Image.Image) -> Image.Image:
        """Bande du bas : 255 là où le décor peut passer (fond intact), adouci à l'approche du contenu."""
        bande = image.crop((0, self.haut_bande, self.largeur, self.hauteur))
        petit = (max(1, bande.width // REDUCTION), max(1, bande.height // REDUCTION))
        ecart = ImageChops.difference(bande, self.fond_bande).convert("L").resize(petit, Image.BOX)
        contenu = ecart.point(lambda v: 255 if v > 0 else 0)
        r = max(1, round(self.ecart / REDUCTION))
        contenu = contenu.filter(ImageFilter.MaxFilter(1 + 2 * r)).filter(ImageFilter.GaussianBlur(r))
        return ImageChops.invert(contenu).resize(bande.size, Image.BILINEAR)

    def appliquer(self, image: Image.Image, temps: float, libre: Image.Image | None = None) -> Image.Image:
        """Nouvelle image : `image` avec les ondes à `temps` secondes (temps global de la vidéo)."""
        if libre is None:
            libre = self.masque_libre(image)
        bande = image.crop((0, self.haut_bande, self.largeur, self.hauteur))
        w, h = bande.size
        for o in self.ondes:
            dx = o.decalage(temps)
            a = ImageChops.multiply(o.alpha.crop((dx, 0, dx + w, h)), libre)
            bande = Image.composite(self._unis[o.couleur], bande, a)
        sortie = image.copy()
        sortie.paste(bande, (0, self.haut_bande))
        return sortie
