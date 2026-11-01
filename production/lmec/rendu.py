"""Dessin des scènes (images) avec Pillow, communes à la vidéo et au carrousel."""
from __future__ import annotations

import os
import re
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


def ease_back(t: float) -> float:
    """Légère surcote puis retour : effet « pop »."""
    t = max(0.0, min(1.0, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def _melange(a: tuple, b: tuple, k: float) -> tuple[int, int, int]:
    k = max(0.0, min(1.0, k))
    return tuple(round(x + (y - x) * k) for x, y in zip(a, b))


MARQUEUR = re.compile(r"\*([^*]+)\*")
_BLANCS = re.compile(r"[ \t\n]+")


def _mots(texte: str) -> list[str]:
    """Découpe sur les espaces ordinaires seulement : les espaces insécables restent dans le mot."""
    return [m for m in _BLANCS.split(texte) if m]


def mots_riches(texte: str) -> list[tuple[str, bool, bool]]:
    """« Plus de *8 milliards*, vite » -> [(Plus, F, F), (de, F, F), (8, V, F), (milliards, V, F), (",", F, V), (vite, F, F)].

    Troisième valeur : le morceau est collé au précédent (ponctuation juste après une mise en valeur).
    """
    mots: list[tuple[str, bool, bool]] = []
    pos = 0
    morceaux = []
    for m in MARQUEUR.finditer(texte):
        morceaux.append((texte[pos:m.start()], False))
        morceaux.append((m.group(1), True))
        pos = m.end()
    morceaux.append((texte[pos:], False))
    precedent = ""
    for contenu, fort in morceaux:
        colle = (bool(mots) and bool(contenu) and not contenu[0].isspace()
                 and bool(precedent) and not precedent[-1].isspace())
        precedent = contenu or precedent
        for i, w in enumerate(_mots(contenu)):
            mots.append((w, fort, colle and i == 0))
    return mots


# Durée des animations d'entrée (s) ; au-delà, l'image de la scène est fixe.
DECALAGE_MOT = 0.07
ENTREE_MOT = 0.25


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
        self.majuscules = bool(charte.get("accroche_majuscules", True))
        self._fond = self._degrade()

    # ------------------------------------------------------------------ outils
    @lru_cache(maxsize=256)
    def police(self, style: str, taille: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(self.chemins_polices[style]), taille)

    def _degrade(self) -> Image.Image:
        """Fond : dégradé vertical + halo discret de la couleur d'accent en haut à droite."""
        haut, bas = self.c["fond"], self.c.get("fond_bas", self.c["fond"])
        bande = Image.new("RGB", (1, self.hauteur))
        for y in range(self.hauteur):
            bande.putpixel((0, y), _melange(haut, bas, y / self.hauteur))
        fond = bande.resize((self.largeur, self.hauteur))
        halo = Image.new("L", (self.largeur, self.hauteur), 0)
        r = int(self.largeur * 0.75)
        ImageDraw.Draw(halo).ellipse((self.largeur - r, -r, self.largeur + r, r), fill=70)
        halo = halo.resize((self.largeur // 8, self.hauteur // 8)).resize((self.largeur, self.hauteur),
                                                                        Image.BILINEAR)
        from PIL import ImageFilter
        halo = halo.filter(ImageFilter.GaussianBlur(60))
        couleur = Image.new("RGB", (self.largeur, self.hauteur), self.c["barre"])
        return Image.composite(couleur, fond, halo)

    def _couper(self, texte: str, police, largeur_max: int) -> list[str]:
        lignes: list[str] = []
        for paragraphe in texte.split("\n"):
            courante = ""
            for mot in _mots(paragraphe):
                essai = f"{courante} {mot}".strip()
                if police.getlength(essai) <= largeur_max or not courante:
                    courante = essai
                else:
                    lignes.append(courante)
                    courante = mot
            lignes.append(courante)
        return lignes

    def _couper_riche(self, mots, police, largeur_max):
        espace = police.getlength(" ")
        lignes, courante, l = [], [], 0.0
        for mot, fort, colle in mots:
            w = police.getlength(mot)
            # Un morceau collé (ponctuation) ne commence jamais une ligne.
            if courante and not colle and l + espace + w > largeur_max:
                lignes.append(courante)
                courante, l = [], 0.0
            l += (espace if courante and not colle else 0) + w
            courante.append((mot, fort, colle))
        if courante:
            lignes.append(courante)
        return lignes

    @staticmethod
    def _largeur_ligne(ligne, police) -> float:
        espace = police.getlength(" ")
        return sum(police.getlength(m) + (0 if (c or i == 0) else espace)
                   for i, (m, _, c) in enumerate(ligne))

    def ajuster_riche(self, texte, style, largeur, hauteur, taille_max, taille_min,
                      interligne=1.2, contexte="", majuscules=False):
        """Plus grande taille qui fait tenir le texte (avec mots mis en valeur *…*)."""
        texte = typographie(texte, self.langue)
        if majuscules:
            texte = texte.upper()
        mots = mots_riches(texte)
        taille = taille_max
        while True:
            police = self.police(style, taille)
            lignes = self._couper_riche(mots, police, largeur)
            pas = int(taille * interligne)
            h = pas * len(lignes)
            trop_large = any(self._largeur_ligne(l, police) > largeur for l in lignes)
            if (h <= hauteur and not trop_large) or taille <= taille_min:
                if h > hauteur or trop_large:
                    self.alertes.append(f"Texte trop long ({contexte}) : « {texte[:50]}… »")
                return police, lignes, pas, h
            taille -= 4

    def ajuster(self, texte, style, largeur, hauteur, taille_max, taille_min, interligne=1.2, contexte=""):
        police, lignes, pas, h = self.ajuster_riche(texte, style, largeur, hauteur, taille_max,
                                                    taille_min, interligne, contexte)
        return police, ["".join(("" if c or i == 0 else " ") + m for i, (m, _, c) in enumerate(l))
                        for l in lignes], pas, h

    def _visibilite(self, t, depart, i=0, decalage=DECALAGE_MOT, entree=ENTREE_MOT) -> float:
        if t is None:
            return 1.0
        return ease_out((t - depart - i * decalage) / entree)

    def ecrire_riche(self, d, lignes, police, pas, y, couleur, t=None, depart=0.0,
                     centre=True, x_gauche=0, style_fort="texte", decalage=DECALAGE_MOT):
        """Écrit mot à mot ; en vidéo chaque mot glisse et apparaît à son tour.

        style_fort : "texte" -> mot mis en valeur en couleur d'accent ;
                     "surligne" -> mot sur un bandeau d'accent (effet marqueur).
        """
        espace = police.getlength(" ")
        g, _, dr, _ = self.zone
        x_c = (g + dr) / 2
        n = 0
        for ligne in lignes:
            largeur = self._largeur_ligne(ligne, police)
            x = x_c - largeur / 2 if centre else x_gauche
            for j, (mot, fort, colle) in enumerate(ligne):
                if colle and j > 0:
                    x -= espace
                a = self._visibilite(t, depart, n, decalage)
                n += 1
                w = police.getlength(mot)
                if a > 0:
                    dy = (1 - a) * police.size * 0.35
                    fond = self._fond.getpixel((int(min(x, self.largeur - 1)), int(min(y, self.hauteur - 1))))
                    if fort and style_fort == "surligne":
                        marge = police.size * 0.10
                        haut_b = y + police.size * 0.12
                        d.rectangle((x - marge, haut_b + dy, x + w + marge, haut_b + police.size * 1.02 + dy),
                                    fill=_melange(fond, self.c["accent"], a))
                        d.text((x, y + dy), mot, font=police, fill=_melange(fond, self.c["fond"], a))
                    else:
                        c = self.c["accent"] if fort else couleur
                        d.text((x, y + dy), mot, font=police, fill=_melange(fond, c, a))
                x += w + espace
            y += pas
        return y, n

    def _ecrire_gauche(self, d, x, y, lignes, police, pas, couleur, a=1.0):
        for ligne in lignes:
            fond = self._fond.getpixel((int(x), int(min(y, self.hauteur - 1))))
            d.text((x, y + (1 - a) * 20), ligne, font=police, fill=_melange(fond, couleur, a))
            y += pas
        return y

    # ------------------------------------------------------------------ cadre
    def _cadre(self, d: ImageDraw.ImageDraw, index: int, total: int):
        g, h, dr, b = self.zone
        marque = self.charte["marque"][self.langue]
        p = self.police("gras", 30)
        d.rectangle((g, h + 4, g + 14, h + 34), fill=self.c["accent"])
        d.text((g + 30, h), marque, font=p, fill=self.c["texte"])
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
            # Indicateur de progression du carrousel (points).
            for k in range(total):
                cx = g + k * 26
                couleur = self.c["accent"] if k == index else self.c["secondaire"]
                r = 6 if k == index else 4
                d.ellipse((cx - r + 6, h + 80 - r, cx + r + 6, h + 80 + r), fill=couleur)

    def _filigrane(self, image: Image.Image) -> Image.Image:
        calque = Image.new("RGBA", (self.largeur * 2, 200), (0, 0, 0, 0))
        dc = ImageDraw.Draw(calque)
        p = self.police("noir", 80)
        txt = self.lib["brouillon"]
        dc.text(((calque.width - p.getlength(txt)) / 2, 50), txt, font=p, fill=(220, 50, 50, 150))
        calque = calque.rotate(35, expand=True)
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
    def duree_animation(self, scene: Scene) -> float:
        """Temps (s) après lequel l'image de la scène ne bouge plus."""
        n = len(mots_riches(scene.texte))
        return {
            "accroche": 0.15 + n * DECALAGE_MOT + ENTREE_MOT,
            "texte": 0.1 + n * self._decalage_texte(scene) + ENTREE_MOT,
            "chiffre": max(1.9, 1.0 + n * 0.04 + ENTREE_MOT),
            "graphique": 0.4 + len(self.fiche.donnees["points"]) * 0.15 + 1.0 if self.fiche.donnees else 0,
            "source": 1.2,
            "fin": 0.1 + n * DECALAGE_MOT + 0.9,
        }[scene.type]

    def _decalage_texte(self, scene):
        n = max(1, len(mots_riches(scene.texte)))
        return min(DECALAGE_MOT, 1.6 / n)  # un texte long ne met jamais plus d'1,6 s à apparaître

    def dessiner(self, scene: Scene, index: int = 0, total: int = 1, t: float | None = None) -> Image.Image:
        """t : secondes écoulées depuis le début de la scène (None = état final, pour le carrousel)."""
        image = self._fond.copy()
        d = ImageDraw.Draw(image)
        self._cadre(d, index, total)
        g, h, dr, b = self.zone
        haut, bas = h + 130, b - 110  # sous l'en-tête, au-dessus du pied de page
        largeur = dr - g
        x_c = (g + dr) // 2
        ctx = f"{self.langue}/{self.format}/scène {index + 1} {scene.type}"
        getattr(self, f"_scene_{scene.type}")(d, scene, g, haut, dr, bas, largeur, x_c, t, ctx)
        if self.brouillon:
            image = self._filigrane(image)
        return image

    def _scene_accroche(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        p, lignes, pas, hh = self.ajuster_riche(scene.texte, "affichage", largeur, bas - haut, 190, 80,
                                                1.08, ctx, majuscules=self.majuscules)
        self.ecrire_riche(d, lignes, p, pas, haut + (bas - haut - hh) // 2, self.c["texte"], t, 0.15,
                          style_fort="surligne")

    def _scene_texte(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        p, lignes, pas, hh = self.ajuster_riche(scene.texte, "gras", largeur, bas - haut, 80, 42, 1.25, ctx)
        self.ecrire_riche(d, lignes, p, pas, haut + (bas - haut - hh) // 2, self.c["texte"], t, 0.1,
                          decalage=self._decalage_texte(scene))

    def _scene_fin(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        p, lignes, pas, hh = self.ajuster_riche(scene.texte, "gras", largeur, (bas - haut) // 2, 78, 40,
                                                1.25, ctx)
        y = haut + (bas - haut) // 2 - hh
        y, n = self.ecrire_riche(d, lignes, p, pas, y, self.c["texte"], t, 0.1)
        marque = self.charte["marque"][self.langue]
        pm = self.police("affichage", 120)
        lm = self._couper_riche(mots_riches(marque), pm, largeur)
        a = 1.0 if t is None else ease_back((t - 0.1 - n * DECALAGE_MOT - 0.1) / 0.5)
        if a > 0:
            self.ecrire_riche(d, [[(m, True, c) for m, _, c in l] for l in lm], pm, int(120 * 1.05),
                              y + 70 + (1 - min(a, 1)) * 40, self.c["accent"])

    def _chiffre_espace(self, texte: str, police) -> tuple[list[str], float, float]:
        """Groupes de milliers dessinés séparément, avec un écart lisible en très gros corps."""
        groupes = texte.split(ESPACE_MILLIERS)
        ecart = police.size * 0.22
        largeur = sum(police.getlength(gr) for gr in groupes) + ecart * (len(groupes) - 1)
        return groupes, ecart, largeur

    def _scene_chiffre(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        k = 1.0 if t is None else ease_out(t / 1.3)
        valeur = self.chiffre["valeur"] * k
        txt = formater_chiffre(self.chiffre, self.langue, valeur)
        final = formater_chiffre(self.chiffre, self.langue)
        # Taille calculée sur la valeur finale pour éviter que le chiffre « respire ».
        taille = 420
        while True:
            pc = self.police("affichage", taille)
            if self._chiffre_espace(final, pc)[2] <= largeur or taille <= 120:
                break
            taille -= 8
        hc = pas_c = int(taille * 1.12)
        u = unite(self.chiffre, self.langue)
        pu, lu, pas_u, hu = (self.ajuster_riche(u, "gras", largeur, 200, 70, 38, 1.15, ctx) if u
                             else (None, [], 0, 0))
        reste = bas - haut - hc - hu - 140
        pt, lt, pas_t, ht = self.ajuster_riche(scene.texte, "regulier", largeur, max(reste, 100), 56, 34,
                                               1.3, ctx)
        y = haut + (bas - haut - (hc + hu + ht + 120)) // 2
        groupes, ecart, l_txt = self._chiffre_espace(final, pc)
        # Le chiffre final fixe la position : les groupes sont alignés à droite pendant le comptage.
        groupes_courants = txt.split(ESPACE_MILLIERS)
        x_fin = x_c + l_txt / 2
        x = x_fin
        for gr in reversed(groupes_courants):
            x -= pc.getlength(gr)
            d.text((x, y), gr, font=pc, fill=self.c["accent"])
            x -= ecart
        y += pc.getbbox("0123456789")[3] + 28
        # Soulignement qui se trace une fois le compteur arrivé.
        s = 1.0 if t is None else ease_out((t - 1.1) / 0.5)
        if s > 0:
            lg = l_txt * s
            d.rectangle((x_c - lg / 2, y - 6, x_c + lg / 2, y + 6), fill=self.c["texte"])
        y += 50
        if pu:
            y, _ = self.ecrire_riche(d, lu, pu, pas_u, y, self.c["texte"], t, 0.5, decalage=0.04)
        self.ecrire_riche(d, lt, pt, pas_t, y + 60, self.c["texte"], t, 1.0, decalage=0.04)

    def _scene_graphique(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        donnees = self.fiche.donnees
        pt, lt, pas_t, ht = self.ajuster_riche(scene.texte, "affichage", largeur, 300, 96, 50, 1.08, ctx,
                                               majuscules=self.majuscules)
        y, _ = self.ecrire_riche(d, lt, pt, pas_t, haut, self.c["texte"], t, 0.0, centre=False, x_gauche=g)
        y += int(pt.size * 0.25)
        u = _texte_langue(donnees.get("unite"), self.langue)
        if u:
            pu = self.police("regulier", 34)
            self._ecrire_gauche(d, g, y, [u], pu, 40, self.c["secondaire"], self._visibilite(t, 0.3))
            y += 80
        points = donnees["points"]
        vmax = max(p["valeur"] for p in points) or 1
        espace = (bas - y) / len(points)
        epaisseur = int(min(80, espace * 0.48))
        pl = self.police("gras", max(28, min(42, int(espace * 0.25))))
        pv = self.police("affichage", max(36, min(64, int(espace * 0.4))))
        for i, p in enumerate(points):
            k = 1.0 if t is None else ease_out((t - 0.4 - i * 0.15) / 0.9)
            if k <= 0:
                continue
            yy = y + i * espace
            label = typographie(_texte_langue(p.get("label"), self.langue), self.langue)
            self._ecrire_gauche(d, g, yy, [label], pl, 0, self.c["texte"], min(1.0, k * 2))
            yb = yy + pl.size * 1.35
            val_final = formater_nombre(p["valeur"], self.langue, donnees.get("decimales"))
            val_txt = formater_nombre(p["valeur"] * k, self.langue, donnees.get("decimales")
                                      if donnees.get("decimales") is not None
                                      else (0 if float(p["valeur"]).is_integer() else 1))
            l_max = largeur - pv.getlength(val_final) - 30
            l_barre = max(6, l_max * p["valeur"] / vmax * k)
            couleur = self.c["accent"] if p.get("mis_en_avant") else self.c["barre"]
            d.rounded_rectangle((g, yb, g + l_barre, yb + epaisseur), radius=epaisseur // 5, fill=couleur)
            d.text((g + l_barre + 20, yb + (epaisseur - pv.size) / 2 - pv.size * 0.08), val_txt, font=pv,
                   fill=self.c["accent"] if p.get("mis_en_avant") else self.c["texte"])

    def _scene_source(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        deux_points = " :" if self.langue == "fr" else ":"
        blocs = []
        if scene.texte:
            blocs.append(("affichage", 84, scene.texte.upper() if self.majuscules else scene.texte,
                          self.c["texte"]))
        blocs.append(("noir", 44, self.lib["sources"] + deux_points, self.c["accent"]))
        for s in self.fiche.sources:
            ligne = s["nom"] + (f" ({s['publication']})" if s.get("publication") else "")
            blocs.append(("gras", 40, ligne, self.c["texte"]))
        for cle in ("periode", "perimetre", "definition"):
            val = self.fiche.contexte(cle, self.langue)
            blocs.append(("regulier", 36, f"{self.lib[cle]}{deux_points} {val}", self.c["secondaire"]))
        echelle = 1.0
        while True:
            rendus = []
            for style, taille, texte, couleur in blocs:
                tt = max(22, int(taille * echelle))
                p = self.police(style, tt)
                lignes = self._couper(typographie(texte, self.langue), p, largeur)
                rendus.append((p, lignes, int(tt * (1.1 if style == "affichage" else 1.3)), couleur))
            total = sum(len(l) * pas + 30 for _, l, pas, _ in rendus)
            if total <= bas - haut or echelle < 0.55:
                if total > bas - haut:
                    self.alertes.append(f"Texte trop long ({ctx}) : bloc sources")
                break
            echelle -= 0.05
        y = haut + max(0, (bas - haut - total) // 2)
        for i, (p, lignes, pas, couleur) in enumerate(rendus):
            y = self._ecrire_gauche(d, g, y, lignes, p, pas, couleur, self._visibilite(t, 0.0, i, 0.12, 0.3)) + 30
