"""Mouvement d'ambiance : un fond qui respire, presque imperceptible, derrière le contenu.

Direction artistique du 22/11/2026 (revue ChatGPT retenue par JG) : le meilleur mouvement reste celui
des données ; le décor ne doit jamais leur faire concurrence. Trois couches :
1. grain lumineux : grain très fin et fixe, mêlé au fond (Rendu._degrade), opacité 1 à 2 % ;
2. courant de données : quelques points de 2 à 4 px qui dérivent lentement dans les zones vides, sur
   deux plans à vitesses différentes (parallaxe), opacité 3 à 5 % ;
3. accent de profondeur : une lumière diffuse sarcelle qui se déplace très lentement, opacité 2 à 3 %.

Règles tenues par construction :
- rien n'est peint sur le contenu : masque d'exclusion de `ecart_px` autour des textes et graphiques,
  adouci pour qu'aucun bord ne se voie ;
- rien dans le bandeau réservé en haut (`bandeau_px`) ;
- aucun clignotement : positions continues, couleurs fixes, cycles de 35 à 60 s.

Coût : motifs périodiques calculés une fois ; par image, deux recadrages et deux compositions. Le masque
est calculé à quart de définition et réutilisé tel quel pour les images fixes d'une scène.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

REDUCTION = 4   # le masque du contenu est calculé sur une image 4 fois plus petite


def grain(taille: tuple[int, int], opacite: float, graine: int = 3) -> Image.Image:
    """Grain fin (L, centré sur 128) à mêler au fond : ±opacité × 255 au plus."""
    hasard = random.Random(graine)
    petit = (max(1, taille[0] // 2), max(1, taille[1] // 2))
    amplitude = 255 * max(0.0, min(0.05, opacite))
    donnees = bytes(int(128 + amplitude * (hasard.random() * 2 - 1)) for _ in range(petit[0] * petit[1]))
    return Image.frombytes("L", petit, donnees).resize(taille, Image.NEAREST)


class Decor:
    def __init__(self, fond: Image.Image, couleurs: dict, conf: dict, bandeau_px: int = 0):
        self.fond = fond
        self.largeur, self.hauteur = fond.size
        self.ecart = max(0, int(conf.get("ecart_px", 32)))
        self.bandeau = max(0, int(bandeau_px))
        c = conf.get("courant") or {}
        self.periode = max(120, int(c.get("periode_px", 360)))
        opacite = max(0.0, min(0.2, float(c.get("opacite", 0.045))))
        self.plans = []
        for k, plan in enumerate(c.get("plans") or [{"vitesse": [8, 1.5], "points": 5, "rayon": [2, 3]},
                                                     {"vitesse": [12, 2.5], "points": 3, "rayon": [3, 4]}]):
            self.plans.append((tuple(plan["vitesse"]), self._motif(plan, opacite, 11 + k)))
        self.couleur_points = Image.new("RGB", fond.size, couleurs.get(c.get("couleur", "barre"), couleurs["barre"]))
        lum = conf.get("lumiere") or {}
        self.cycle = max(10.0, float(lum.get("cycle_s", 50)))
        self.rayon_lumiere = int(float(lum.get("rayon", 0.33)) * self.largeur)
        self.lumiere = self._lumiere(max(0.0, min(0.1, float(lum.get("opacite", 0.025)))))
        self.couleur_lumiere = Image.new("RGB", fond.size, couleurs.get(lum.get("couleur", "barre"), couleurs["barre"]))

    # ------------------------------------------------------------------ motifs (calculés une fois)
    def _motif(self, plan: dict, opacite: float, graine: int) -> Image.Image:
        """Points sur une tuile périodique, répétée sur l'image plus une période (dérive sans couture)."""
        p = self.periode
        tuile = Image.new("L", (p, p), 0)
        d = ImageDraw.Draw(tuile)
        hasard = random.Random(graine)
        r_min, r_max = plan.get("rayon", [2, 4])
        for _ in range(int(plan.get("points", 4))):
            x, y = hasard.uniform(0, p), hasard.uniform(0, p)
            r = hasard.uniform(r_min, r_max)
            a = round(255 * opacite * 6 * hasard.uniform(0.6, 1.0))   # cœur du point ; le flou l'adoucit
            for dx in (-p, 0, p):
                for dy in (-p, 0, p):
                    d.ellipse((x + dx - r, y + dy - r, x + dx + r, y + dy + r), fill=min(255, a))
        tuile = tuile.filter(ImageFilter.GaussianBlur(0.8))
        motif = Image.new("L", (self.largeur + p, self.hauteur + p), 0)
        for x in range(0, self.largeur + p, p):
            for y in range(0, self.hauteur + p, p):
                motif.paste(tuile, (x, y))
        return motif

    def _lumiere(self, opacite: float) -> Image.Image:
        """Halo diffus (gaussien), plus grand que l'image pour pouvoir glisser."""
        r = self.rayon_lumiere
        cote = 2 * r
        petit = Image.new("L", (cote // 8, cote // 8), 0)
        ImageDraw.Draw(petit).ellipse((cote // 32, cote // 32, cote // 8 - cote // 32, cote // 8 - cote // 32),
                                      fill=round(255 * opacite))
        petit = petit.filter(ImageFilter.GaussianBlur(cote // 64))
        return petit.resize((cote, cote), Image.BILINEAR)

    # ------------------------------------------------------------------ par image
    def masque_libre(self, image: Image.Image) -> Image.Image:
        """255 là où le décor peut passer (fond intact), adouci à l'approche du contenu."""
        petit = (max(1, self.largeur // REDUCTION), max(1, self.hauteur // REDUCTION))
        ecart = ImageChops.difference(image, self.fond).convert("L").resize(petit, Image.BOX)
        contenu = ecart.point(lambda v: 255 if v > 0 else 0)
        r = max(1, round(self.ecart / REDUCTION))
        contenu = contenu.filter(ImageFilter.MaxFilter(1 + 2 * r)).filter(ImageFilter.GaussianBlur(r / 2))
        libre = ImageChops.invert(contenu).resize(image.size, Image.BILINEAR)
        if self.bandeau:
            ImageDraw.Draw(libre).rectangle((0, 0, self.largeur, self.bandeau), fill=0)
        return libre

    def _points(self, temps: float) -> Image.Image:
        alpha = None
        for (vx, vy), motif in self.plans:
            dx, dy = int(temps * vx) % self.periode, int(temps * vy) % self.periode
            couche = motif.crop((dx, dy, dx + self.largeur, dy + self.hauteur))
            alpha = couche if alpha is None else ImageChops.lighter(alpha, couche)
        return alpha

    def _position_lumiere(self, temps: float) -> tuple[int, int]:
        """Trajet lent et fermé (courbe de Lissajous) : jamais d'à-coup, retour au départ en `cycle` s."""
        w = 2 * math.pi * temps / self.cycle
        cx = self.largeur * (0.5 + 0.32 * math.sin(w))
        cy = self.hauteur * (0.5 + 0.22 * math.sin(2 * w + 0.7))
        return round(cx - self.rayon_lumiere), round(cy - self.rayon_lumiere)

    def appliquer(self, image: Image.Image, temps: float, libre: Image.Image | None = None) -> Image.Image:
        """Nouvelle image : `image` avec le décor à `temps` secondes (temps global de la vidéo)."""
        if libre is None:
            libre = self.masque_libre(image)
        x, y = self._position_lumiere(temps)
        halo = Image.new("L", image.size, 0)
        halo.paste(self.lumiere, (x, y))
        sortie = Image.composite(self.couleur_lumiere, image, ImageChops.multiply(halo, libre))
        return Image.composite(self.couleur_points, sortie, ImageChops.multiply(self._points(temps), libre))
