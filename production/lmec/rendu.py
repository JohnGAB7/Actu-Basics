"""Dessin des scènes (images) avec Pillow, communes à la vidéo et au carrousel."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .fiche import Fiche, Scene
from .formatage import ESPACE_MILLIERS, formater_chiffre, formater_nombre, typographie, unite, _texte_langue

RACINE_PRODUCTION = Path(__file__).resolve().parent.parent

LIBELLES = {
    "fr": {"source": "Source", "sources": "Sources", "periode": "Période", "perimetre": "Périmètre",
           "definition": "Définition", "brouillon": "BROUILLON · NON VALIDÉ"},
    "en": {"source": "Source", "sources": "Sources", "periode": "Period", "perimetre": "Scope",
           "definition": "Definition", "brouillon": "DRAFT · NOT VALIDATED"},
}

_REPERTOIRES_POLICES = [
    RACINE_PRODUCTION / "polices",
    Path("/usr/share/fonts"), Path("/usr/local/share/fonts"), Path.home() / ".local/share/fonts",
    Path.home() / "Library/Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts"),
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts",
]


@lru_cache(maxsize=1)
def _index_polices() -> dict[str, Path]:
    index: dict[str, Path] = {}
    for rep in _REPERTOIRES_POLICES:
        if rep.is_dir():
            for f in rep.rglob("*"):
                if f.suffix.lower() in (".ttf", ".otf"):
                    index.setdefault(f.name.lower(), f)
    return index


def trouver_police(candidats: list[str]) -> Path:
    index = _index_polices()
    for nom in candidats:
        if nom.lower() in index:
            return index[nom.lower()]
    raise FileNotFoundError(
        f"Aucune police trouvée parmi {candidats}. Installez Inter (https://rsms.me/inter/) "
        "ou déposez les fichiers dans production/polices/.")


def _rgb(hexa: str) -> tuple[int, int, int]:
    hexa = hexa.lstrip("#")
    return tuple(int(hexa[i:i + 2], 16) for i in (0, 2, 4))


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


class Rendu:
    """Dessine les scènes d'une édition (une langue) pour un format donné."""

    def __init__(self, fiche: Fiche, langue: str, charte: dict, format_: str, brouillon: bool):
        self.fiche, self.langue, self.charte, self.format = fiche, langue, charte, format_
        self.brouillon = brouillon
        dims = charte["formats"][format_]
        self.largeur, self.hauteur = dims["largeur"], dims["hauteur"]
        m = charte["zones_securite_video"] if format_ == "video" else charte["marges_carrousel"]
        self.zone = (m["gauche"], m["haut"], self.largeur - m["droite"], self.hauteur - m["bas"])
        self.c = {k: _rgb(v) for k, v in charte["couleurs"].items()}
        self.chemins_polices = {style: trouver_police(c) for style, c in charte["polices"].items()}
        self.alertes: list[str] = []  # débordements de texte etc. -> rapport QC
        self.lib = LIBELLES[langue]
        # Nombre de décimales figé sur la valeur finale (pour l'animation du compteur).
        ch = dict(fiche.chiffre)
        if ch.get("decimales") is None:
            v = float(ch["valeur"])
            ch["decimales"] = 0 if v.is_integer() else min(len(repr(v).split(".")[1]), 3)
        self.chiffre = ch

    # ------------------------------------------------------------------ outils
    @lru_cache(maxsize=256)
    def police(self, style: str, taille: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(self.chemins_polices[style]), taille)

    def _couper(self, texte: str, police, largeur_max: int) -> list[str]:
        lignes: list[str] = []
        for paragraphe in texte.split("\n"):
            courante = ""
            for mot in paragraphe.split():
                essai = f"{courante} {mot}".strip()
                if police.getlength(essai) <= largeur_max or not courante:
                    courante = essai
                else:
                    lignes.append(courante)
                    courante = mot
            lignes.append(courante)
        return lignes

    def ajuster(self, texte: str, style: str, largeur: int, hauteur: int,
                taille_max: int, taille_min: int, interligne: float = 1.2, contexte: str = ""):
        """Plus grande taille de police qui fait tenir le texte dans la boîte."""
        texte = typographie(texte, self.langue)
        taille = taille_max
        while True:
            police = self.police(style, taille)
            lignes = self._couper(texte, police, largeur)
            pas = int(taille * interligne)
            h = pas * len(lignes)
            trop_large = any(police.getlength(l) > largeur for l in lignes)
            if (h <= hauteur and not trop_large) or taille <= taille_min:
                if h > hauteur or trop_large:
                    self.alertes.append(f"Texte trop long ({contexte}) : « {texte[:50]}… »")
                return police, lignes, pas, h
            taille -= 4

    def _ecrire(self, d: ImageDraw.ImageDraw, x_centre: int, y: int, lignes, police, pas, couleur):
        for ligne in lignes:
            w = police.getlength(ligne)
            d.text((x_centre - w / 2, y), ligne, font=police, fill=couleur)
            y += pas
        return y

    def _ecrire_gauche(self, d, x, y, lignes, police, pas, couleur):
        for ligne in lignes:
            d.text((x, y), ligne, font=police, fill=couleur)
            y += pas
        return y

    # ------------------------------------------------------------------ cadre
    def _cadre(self, d: ImageDraw.ImageDraw, index: int, total: int):
        g, h, dr, b = self.zone
        marque = self.charte["marque"][self.langue]
        p = self.police("gras", 30)
        d.text((g, h), marque, font=p, fill=self.c["secondaire"])
        d.rectangle((g, h + 48, g + 90, h + 54), fill=self.c["accent"])
        noms = ", ".join(s["nom"] for s in self.fiche.sources)
        pied = typographie(f"{self.lib['source']} : {noms}" if self.langue == "fr"
                           else f"{self.lib['source']}: {noms}", self.langue)
        pp = self.police("regulier", 26)
        lignes = self._couper(pied, pp, dr - g - (110 if self.format == "carrousel" else 0))[:2]
        y = b - 34 * len(lignes)
        self._ecrire_gauche(d, g, y, lignes, pp, 34, self.c["secondaire"])
        if self.format == "carrousel" and total > 1:
            num = f"{index + 1}/{total}"
            d.text((dr - pp.getlength(num), b - 34), num, font=pp, fill=self.c["secondaire"])

    def _filigrane(self, image: Image.Image) -> Image.Image:
        calque = Image.new("RGBA", (self.largeur * 2, 200), (0, 0, 0, 0))
        dc = ImageDraw.Draw(calque)
        p = self.police("noir", 80)
        txt = self.lib["brouillon"]
        dc.text(((calque.width - p.getlength(txt)) / 2, 50), txt, font=p, fill=(220, 50, 50, 150))
        calque = calque.rotate(35, expand=True)
        # Recadre le calque tourné au centre, à la taille de l'image.
        x0 = (calque.width - self.largeur) // 2
        y0 = (calque.height - self.hauteur) // 2
        if x0 < 0 or y0 < 0:
            grand = Image.new("RGBA", (max(calque.width, self.largeur), max(calque.height, self.hauteur)))
            grand.paste(calque, (max(-x0, 0), max(-y0, 0)))
            calque, x0, y0 = grand, max(x0, 0), max(y0, 0)
        calque = calque.crop((x0, y0, x0 + self.largeur, y0 + self.hauteur))
        base = image.convert("RGBA")
        base.alpha_composite(calque)
        return base.convert("RGB")

    # ------------------------------------------------------------------ scènes
    def dessiner(self, scene: Scene, index: int = 0, total: int = 1, progression: float = 1.0) -> Image.Image:
        image = Image.new("RGB", (self.largeur, self.hauteur), self.c["fond"])
        d = ImageDraw.Draw(image)
        self._cadre(d, index, total)
        g, h, dr, b = self.zone
        haut, bas = h + 110, b - 110  # sous l'en-tête, au-dessus du pied de page
        largeur = dr - g
        x_c = (g + dr) // 2
        ctx = f"{self.langue}/{self.format}/scène {index + 1} {scene.type}"
        getattr(self, f"_scene_{scene.type}")(d, scene, g, haut, dr, bas, largeur, x_c, progression, ctx)
        if self.brouillon:
            image = self._filigrane(image)
        return image

    def _scene_accroche(self, d, scene, g, haut, dr, bas, largeur, x_c, prog, ctx):
        p, lignes, pas, hh = self.ajuster(scene.texte, "noir", largeur, bas - haut, 112, 56, 1.15, ctx)
        self._ecrire(d, x_c, haut + (bas - haut - hh) // 2, lignes, p, pas, self.c["texte"])

    def _scene_texte(self, d, scene, g, haut, dr, bas, largeur, x_c, prog, ctx):
        p, lignes, pas, hh = self.ajuster(scene.texte, "gras", largeur, bas - haut, 76, 40, 1.25, ctx)
        self._ecrire(d, x_c, haut + (bas - haut - hh) // 2, lignes, p, pas, self.c["texte"])

    def _scene_fin(self, d, scene, g, haut, dr, bas, largeur, x_c, prog, ctx):
        p, lignes, pas, hh = self.ajuster(scene.texte, "gras", largeur, (bas - haut) // 2, 76, 40, 1.25, ctx)
        y = haut + (bas - haut) // 2 - hh
        y = self._ecrire(d, x_c, y, lignes, p, pas, self.c["texte"])
        marque = self.charte["marque"][self.langue]
        pm = self.police("noir", 64)
        lm = self._couper(marque, pm, largeur)
        self._ecrire(d, x_c, y + 60, lm, pm, 76, self.c["accent"])

    def _chiffre_espace(self, texte: str, police) -> tuple[list[str], float, float]:
        """Groupes de milliers dessinés séparément, avec un écart lisible en très gros corps."""
        groupes = texte.split(ESPACE_MILLIERS)
        ecart = police.size * 0.28
        largeur = sum(police.getlength(gr) for gr in groupes) + ecart * (len(groupes) - 1)
        return groupes, ecart, largeur

    def _scene_chiffre(self, d, scene, g, haut, dr, bas, largeur, x_c, prog, ctx):
        valeur = self.chiffre["valeur"] * ease_out(prog)
        txt = formater_chiffre(self.chiffre, self.langue, valeur)
        final = formater_chiffre(self.chiffre, self.langue)
        # Taille calculée sur la valeur finale pour éviter que le chiffre « respire ».
        taille = 300
        while True:
            pc = self.police("noir", taille)
            if self._chiffre_espace(final, pc)[2] <= largeur or taille <= 100:
                break
            taille -= 8
        hc = pas_c = int(taille * 1.05)
        u = unite(self.chiffre, self.langue)
        pu, lu, pas_u, hu = (self.ajuster(u, "gras", largeur, 160, 64, 36, 1.15, ctx) if u
                             else (None, [], 0, 0))
        reste = bas - haut - hc - hu - 120
        pt, lt, pas_t, ht = self.ajuster(scene.texte, "regulier", largeur, max(reste, 100), 54, 34, 1.3, ctx)
        y = haut + (bas - haut - (hc + hu + ht + 100)) // 2
        groupes, ecart, l_txt = self._chiffre_espace(txt, pc)
        x = x_c - l_txt / 2
        for gr in groupes:
            d.text((x, y), gr, font=pc, fill=self.c["accent"])
            x += pc.getlength(gr) + ecart
        y += pas_c + 20
        if pu:
            y = self._ecrire(d, x_c, y, lu, pu, pas_u, self.c["texte"])
        self._ecrire(d, x_c, y + 80, lt, pt, pas_t, self.c["texte"])

    def _scene_graphique(self, d, scene, g, haut, dr, bas, largeur, x_c, prog, ctx):
        donnees = self.fiche.donnees
        pt, lt, pas_t, ht = self.ajuster(scene.texte, "gras", largeur, 260, 60, 36, 1.2, ctx)
        y = self._ecrire_gauche(d, g, haut, lt, pt, pas_t, self.c["texte"]) + 20
        u = _texte_langue(donnees.get("unite"), self.langue)
        if u:
            pu = self.police("regulier", 34)
            d.text((g, y), u, font=pu, fill=self.c["secondaire"])
            y += 70
        points = donnees["points"]
        vmax = max(p["valeur"] for p in points) or 1
        espace = (bas - y) / len(points)
        epaisseur = int(min(70, espace * 0.45))
        pl = self.police("gras", max(28, min(40, int(espace * 0.25))))
        pv = self.police("noir", max(30, min(48, int(espace * 0.3))))
        for i, p in enumerate(points):
            yy = y + i * espace
            label = typographie(_texte_langue(p.get("label"), self.langue), self.langue)
            d.text((g, yy), label, font=pl, fill=self.c["texte"])
            yb = yy + pl.size * 1.35
            val_txt = formater_nombre(p["valeur"], self.langue, donnees.get("decimales"))
            l_max = largeur - pv.getlength(val_txt) - 30
            l_barre = max(6, l_max * p["valeur"] / vmax * ease_out(prog))
            couleur = self.c["accent"] if p.get("mis_en_avant") else self.c["barre"]
            d.rectangle((g, yb, g + l_barre, yb + epaisseur), fill=couleur)
            d.text((g + l_barre + 20, yb + (epaisseur - pv.size) / 2 - 4), val_txt, font=pv,
                   fill=self.c["texte"])

    def _scene_source(self, d, scene, g, haut, dr, bas, largeur, x_c, prog, ctx):
        deux_points = " :" if self.langue == "fr" else ":"
        blocs = []
        if scene.texte:
            blocs.append(("gras", 54, scene.texte, self.c["texte"]))
        blocs.append(("noir", 46, self.lib["sources"] + deux_points, self.c["accent"]))
        for s in self.fiche.sources:
            ligne = s["nom"] + (f" ({s['publication']})" if s.get("publication") else "")
            blocs.append(("regulier", 40, ligne, self.c["texte"]))
        for cle in ("periode", "perimetre", "definition"):
            val = self.fiche.contexte(cle, self.langue)
            blocs.append(("regulier", 36, f"{self.lib[cle]}{deux_points} {val}", self.c["secondaire"]))
        # Réduit l'ensemble proportionnellement jusqu'à ce que tout tienne.
        echelle = 1.0
        while True:
            rendus = []
            for style, taille, texte, couleur in blocs:
                t = max(22, int(taille * echelle))
                p = self.police(style, t)
                lignes = self._couper(typographie(texte, self.langue), p, largeur)
                rendus.append((p, lignes, int(t * 1.3), couleur))
            total = sum(len(l) * pas + 28 for _, l, pas, _ in rendus)
            if total <= bas - haut or echelle < 0.55:
                if total > bas - haut:
                    self.alertes.append(f"Texte trop long ({ctx}) : bloc sources")
                break
            echelle -= 0.05
        y = haut + max(0, (bas - haut - total) // 2)
        for p, lignes, pas, couleur in rendus:
            y = self._ecrire_gauche(d, g, y, lignes, p, pas, couleur) + 28
