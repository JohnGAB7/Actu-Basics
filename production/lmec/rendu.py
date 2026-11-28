"""Dessin des scènes (images) avec Pillow, communes à la vidéo et au carrousel."""
from __future__ import annotations

import math

import os
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

from .fiche import Fiche, Scene
from . import logo as _logo
from .scenes_pedagogiques import ScenesPedagogiques
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
OPERATEURS = {"+", "−", "-", "×", "÷", "x"}
UNITES_CALCUL = {"%", "€", "min", "minutes", "ans", "cm", "pts", "points"}
TERME_CALCUL = re.compile(r"^[(\[]*[−\-+]?(\d[\d\u00a0\u202f\s,.]*|[½⅓⅔¼¾⅕⅙⅛])[)\]]*[%€]?[,;:.)]*$")
_BLANCS = re.compile(r"[ \t\n]+")


def _mots(texte: str) -> list[str]:
    """Découpe sur les espaces ordinaires seulement : les espaces insécables restent dans le mot."""
    return [m for m in _BLANCS.split(texte) if m]


def insecables_nombres(texte: str) -> str:
    """« 1 600 € » -> « 1\u00a0600\u00a0€ » : les espaces internes d'un nombre deviennent insécables."""
    texte = re.sub(r"(?<=\d) (?=\d{3}(?!\d))", "\u00a0", texte)
    return re.sub(r"(?<=\d) (?=(?:[€$£]|(?:min|minutes?|h|s|km|kg|points?|millions?|milliards?|billions?|°C|K)\b))", "\u00a0", texte)


def mots_riches(texte: str) -> list[tuple[str, bool, bool]]:
    """« Plus de *8 milliards*, vite » -> [(Plus, F, F), (de, F, F), (8, V, F), (milliards, V, F), (",", F, V), (vite, F, F)].

    Troisième valeur : le morceau est collé au précédent (ponctuation juste après une mise en valeur).
    """
    # Pas de coupure de ligne dans une expression : ni entre parenthèses (« n(n − 1) »), ni juste
    # après un opérateur (« ÷ 2 », « − P₀ » restent avec leur opérande).
    texte = re.sub(r"\(([^()]{1,12})\)", lambda m: "(" + m.group(1).replace(" ", "\u00a0") + ")", texte)
    texte = re.sub(r"(?<=\s)([−÷×=+–<>≈≤≥]) (?=\S)", "\\1\u00a0", texte)
    # Multiplications, divisions et comparaisons restent aussi avec leur opérande de gauche
    # (« 780 ÷ 365 > 2 » sur une ligne) ; les longues sommes « 22 + 21 + … » restent coupables.
    texte = re.sub(r"(?<=[\w)]) (?=[÷×=<>≈≤≥]\u00a0)", "\u00a0", texte)
    # Un nombre ne se coupe pas : ni entre ses groupes de milliers (« 1 600 », « 200 000 »),
    # ni avant son unité (« 2 200 € », « 5 min », « 1 point »).
    texte = insecables_nombres(texte)
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
        # Une espace insécable (« *90 %* ? ») colle aussi la ponctuation au mot mis en valeur.
        colle = (bool(mots) and bool(contenu) and not _BLANCS.match(contenu[0])
                 and bool(precedent) and not precedent[-1].isspace())
        precedent = contenu or precedent
        for i, w in enumerate(_mots(contenu)):
            mots.append((w, fort, colle and i == 0))
    return mots


# Durée des animations d'entrée (s) ; au-delà, l'image de la scène est fixe.
DECALAGE_MOT = 0.07
ENTREE_MOT = 0.25


class Rendu(ScenesPedagogiques):
    """Dessine les scènes d'une édition (une langue) pour un format donné (video, carrousel, lecon)."""

    def __init__(self, fiche: Fiche, langue: str, charte: dict, format_: str, brouillon: bool):
        self.fiche, self.langue, self.charte, self.format = fiche, langue, charte, format_
        self.brouillon = brouillon
        dims = charte["formats"][format_]
        self.largeur, self.hauteur = dims["largeur"], dims["hauteur"]
        m = {"video": charte["zones_securite_video"], "carrousel": charte["marges_carrousel"],
             "lecon": charte.get("zones_securite_lecon", charte["marges_carrousel"])}[format_]
        self.zone = (m["gauche"], m["haut"], self.largeur - m["droite"], self.hauteur - m["bas"])
        self.c = self._palette(charte["couleurs"])
        # Univers visuels (direction artistique du 22/11/2026) : « editorial » (couleurs de base) et
        # « immersif » (fond sombre pour les démonstrations et les transformations de données). Chaque
        # scène choisit le sien (champ « univers ») ; Rendu bascule couleurs, fond et décor à la volée.
        self._palettes = {"editorial": self.c}
        for nom, couleurs in (charte.get("univers") or {}).items():
            self._palettes[nom] = self._palette({**charte["couleurs"], **couleurs})
        self._univers = "editorial"
        self.chemins_polices = {style: trouver_police(c) for style, c in charte["polices"].items()}
        self.alertes: list[str] = []  # débordements de texte etc. -> rapport QC
        self.tailles: dict[str, int] = {}  # plus petite taille de police par type de scène
        self.lib = LIBELLES[langue]
        # Nombre de décimales figé sur la valeur finale (pour l'animation du compteur).
        ch = dict(fiche.chiffre or {"valeur": 0})
        if ch.get("decimales") is None:
            v = float(ch["valeur"])
            ch["decimales"] = 0 if v.is_integer() else min(len(repr(v).split(".")[1]), 3)
        self.chiffre = ch
        self.majuscules = bool(charte.get("accroche_majuscules", True))
        self._fond = self._degrade()
        self._fonds = {"editorial": self._fond}
        self.logos = _logo.charger_logos(charte.get("logo"), langue)
        self.poses: dict[tuple, _logo.Pose] = {}   # logos posés sur les images finales -> contrôle qualité
        self._image: Image.Image | None = None
        # Début (s, depuis le début de la scène) de chaque phrase prononcée, par scène (clé : id(scène)) :
        # les étapes apparaissent quand la voix les annonce. Renseigné après la narration (produire.py).
        self.reperes: dict[int, list[float]] = {}
        self.fins_voix: dict[int, float] = {}
        # Morceaux de voix (début, fin) : phrases ET propositions (la synthèse coupe aussi sur « : » et « ; »).
        # Sert à faire apparaître un calcul terme à terme pendant qu'il est dit.
        self.morceaux_voix: dict[int, list[tuple[float, float]]] = {}
        self._scene_courante = None

    # ------------------------------------------------------------------ logo
    def conf_logo(self, couverture: bool = False) -> dict:
        conf = self.logos.conf or {}
        return (conf.get("couverture") if couverture else conf.get(self.format)) or {}

    def logo_prevu(self, scene: Scene, couverture: bool = False) -> bool:
        """Le logo doit-il apparaître sur cette image ? (indépendant de la présence des fichiers)"""
        if not self.logos.actif:
            return False
        c = self.conf_logo(couverture)
        if couverture:
            return bool(c.get("actif", True))
        return scene.type in (c.get("scenes") or [])

    def _logo_coin(self, couverture: bool) -> tuple[int, int, int, str]:
        """Logo hors scène de fin : (x, y, largeur, position)."""
        c = self.conf_logo(couverture)
        largeur = int(c.get("largeur_px" if couverture else "largeur_autres_px", 200))
        position = c.get("position", "haut_droite")
        ref = next(iter(self.logos.images.values()), None)
        hauteur = round(ref.height * largeur / ref.width) if ref else largeur
        g, h, d, b = self.zone
        # En bas, le logo reste au-dessus du pied de page (source, numéro de diapositive).
        zone = (g, h, d, b - 110) if position.startswith("bas") else self.zone
        x, y = _logo.boite_position(position, zone, largeur, hauteur, int(c.get("marge_px", 0)))
        return x, y, largeur, position

    # ------------------------------------------------------------------ logo mobile
    def conf_mobile(self) -> dict:
        return (self.logos.conf or {}).get("mobile") or {}

    @staticmethod
    def _palette(couleurs: dict) -> dict:
        c = {k: _rgb(v) for k, v in couleurs.items() if isinstance(v, str) and v.startswith("#")}
        c.setdefault("encre_accent", c["fond"])     # texte posé sur une forme d'accent
        c.setdefault("halo", c["barre"])
        c.setdefault("progression", c["accent"])
        c.setdefault("or", c["accent"])              # surfaces et repères dorés (jamais du texte courant)
        return c

    def univers_de(self, scene: Scene) -> str:
        # Univers choisi par la scène, sinon celui de son type (charte « univers_par_type », design Mixte).
        u = scene.extra.get("univers") or (self.charte.get("univers_par_type") or {}).get(scene.type, "editorial")
        return u if u in self._palettes else "editorial"

    def basculer(self, univers: str) -> None:
        """Couleurs et fond de l'univers demandé (les fonds sont calculés une fois)."""
        if univers == self._univers:
            return
        self._univers = univers
        self.c = self._palettes[univers]
        if univers not in self._fonds:
            self._fonds[univers] = self._degrade()
        self._fond = self._fonds[univers]

    # ------------------------------------------------------------------ décor en mouvement
    def decor_prevu(self, scene: Scene) -> bool:
        """Le décor en mouvement (lmec/decor.py) passe-t-il derrière cette scène ?"""
        c = self.charte.get("decor") or {}
        return bool(c.get("actif")) and self.format in (c.get("formats") or []) \
            and scene.type not in (c.get("sauf_scenes") or ["fin"])

    @property
    def decor(self):
        """Décor de l'univers courant (un par univers, calculé une fois)."""
        decors = self.__dict__.setdefault("_decors", {})
        if self._univers not in decors:
            from .decor import Decor
            bandeau = 0
            if self.logos.actif and self.logos.images and self.conf_mobile().get("actif"):
                _, h, p = self._mobile_taille()
                bandeau = self.zone[1] + h + 2 * p    # bandeau du logo mobile, zone de protection comprise
            conf = dict(self.charte.get("decor") or {})
            conf.update((conf.get("par_univers") or {}).get(self._univers) or {})
            decors[self._univers] = Decor(self._fond, self.c, conf, bandeau)
        return decors[self._univers]

    def mobile_prevu(self, scene: Scene) -> bool:
        """Le logo mobile accompagne-t-il cette scène ? (vidéo et cours 16:9, hors scène de fin)"""
        c = self.conf_mobile()
        if not (self.logos.actif and self.logos.images and c.get("actif")):
            return False
        if self.format not in (c.get("formats") or []):
            return False
        return scene.type not in (c.get("sauf_scenes") or ["fin"])

    def _mobile_taille(self) -> tuple[int, int, int]:
        """(largeur, hauteur, zone de protection) du logo mobile, en pixels."""
        lg = self.conf_mobile().get("largeur_px", 160)
        lg = int(lg.get(self.format, 160) if isinstance(lg, dict) else lg)
        ref = next(iter(self.logos.images.values()))
        return lg, round(ref.height * lg / ref.width), round(lg * float(self.logos.conf.get("zone_protection", 0.08)))

    def mobile_position(self, temps: float) -> tuple[int, int]:
        """Coin haut-gauche du logo mobile à `temps` secondes du début de la vidéo.

        Aller-retour horizontal, doux (cosinus), dans le bandeau du haut de la zone de sécurité :
        rien d'autre n'y est dessiné sur une vidéo, et l'espace sous le logo est réservé (dessiner)."""
        g, h, dr, _ = self.zone
        lg, _, p = self._mobile_taille()
        periode = max(4.0, float(self.conf_mobile().get("periode_s", 40)))
        course = max(0, dr - g - lg - 2 * p)
        k = 0.5 - 0.5 * math.cos(2 * math.pi * temps / periode)
        return g + p + round(course * k), h   # zone de protection au-dessus : marge de sécurité, toujours vide

    def poser_mobile(self, image, temps: float, scene: Scene, index: int, opacite: float = 1.0,
                     mesurer: bool = False):
        x, y = self.mobile_position(temps)
        lg, _, _ = self._mobile_taille()
        return _logo.poser(image, self._fond, self.logos, x=x, y=y, largeur=lg,
                           variante_demandee=self.logos.conf.get("variante", "auto"),
                           sur_fond_clair=self.logos.conf.get("sur_fond_clair", "clair"),
                           protection=float(self.logos.conf.get("zone_protection", 0.08)),
                           support="mobile", scene=scene.type, index=index, opacite=opacite, mesurer=mesurer)

    def mesurer_mobile(self, scene: Scene, index: int, total: int) -> None:
        """Contrôle qualité : pose le logo mobile aux deux extrémités et au milieu de sa course sur
        l'image finale de la scène, et garde la pose la plus défavorable (recouvrement maximal)."""
        if not self.mobile_prevu(scene):
            return
        statique = self.dessiner(scene, index, total, None)
        periode = max(4.0, float(self.conf_mobile().get("periode_s", 40)))
        poses = [self.poser_mobile(statique.copy(), periode * f, scene, index, mesurer=True) for f in (0, 0.25, 0.5)]
        poses = [p for p in poses if p]
        if poses:
            self.poses[("mobile", index)] = max(poses, key=lambda p: p.recouvrement)

    def _poser_logo(self, image, x, y, largeur, scene, index, t, couverture, opacite=1.0):
        support = "couverture" if couverture else self.format
        pose = _logo.poser(image, self._fond, self.logos, x=x, y=y, largeur=largeur,
                           variante_demandee=self.logos.conf.get("variante", "auto"),
                           sur_fond_clair=self.logos.conf.get("sur_fond_clair", "clair"),
                           protection=float(self.logos.conf.get("zone_protection", 0.08)),
                           support=support, scene=scene.type, index=index, opacite=opacite,
                           mesurer=t is None)
        if pose and t is None:
            self.poses[(support, index)] = pose
        return pose

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
        couleur = Image.new("RGB", (self.largeur, self.hauteur), self.c["halo"])
        fond = Image.composite(couleur, fond, halo)
        opacite = float((self.charte.get("decor") or {}).get("grain", 0))
        if opacite > 0 and self.format != "carrousel":   # grain lumineux, fixe (couche 1 du décor)
            from .decor import grain
            fond = ImageChops.overlay(fond, grain(fond.size, opacite).convert("RGB"))   # 128 = neutre
        return fond

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

    def _couper_equilibre(self, mots, police, largeur_max):
        """Même nombre de lignes que la coupe gloutonne, mais des lignes de longueurs voisines
        (pas de mot orphelin en fin de titre)."""
        lignes = self._couper_riche(mots, police, largeur_max)
        if len(lignes) < 2:
            return lignes
        bas, haut = max(police.getlength(m) for m, _, _ in mots), float(largeur_max)
        for _ in range(18):
            milieu = (bas + haut) / 2
            if len(self._couper_riche(mots, police, milieu)) <= len(lignes):
                haut = milieu
            else:
                bas = milieu
        return self._couper_riche(mots, police, haut + 0.5)

    @staticmethod
    def _largeur_ligne(ligne, police) -> float:
        espace = police.getlength(" ")
        return sum(police.getlength(m) + (0 if (c or i == 0) else espace)
                   for i, (m, _, c) in enumerate(ligne))

    def ajuster_riche(self, texte, style, largeur, hauteur, taille_max, taille_min,
                      interligne=1.2, contexte="", majuscules=False, equilibre=False):
        """Plus grande taille qui fait tenir le texte (avec mots mis en valeur *…*).
        equilibre : lignes de longueurs voisines (titres)."""
        texte = typographie(texte, self.langue)
        if majuscules:
            texte = texte.upper()
        mots = mots_riches(texte)
        plafond = ((self.charte.get("typographie") or {}).get(self.format) or {}).get(style)
        if plafond:   # grille typographique de la charte : jamais de texte surdimensionné
            taille_max = min(taille_max, int(plafond))
            taille_min = min(taille_min, taille_max)
        taille = taille_max
        while True:
            police = self.police(style, taille)
            lignes = (self._couper_equilibre if equilibre else self._couper_riche)(mots, police, largeur)
            pas = int(taille * interligne)
            h = pas * len(lignes)
            trop_large = any(self._largeur_ligne(l, police) > largeur for l in lignes)
            if (h <= hauteur and not trop_large) or taille <= taille_min:
                if h > hauteur or trop_large:
                    self.alertes.append(f"Texte trop long ({contexte}) : « {texte[:50]}… »")
                cle = contexte.split()[-1] if contexte else "?"
                self.tailles[cle] = min(self.tailles.get(cle, 10_000), taille)
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
        for n_ligne, ligne in enumerate(lignes):
            largeur = self._largeur_ligne(ligne, police)
            x = x_c - largeur / 2 if centre else x_gauche
            temps_calc = self._temps_calcul(ligne, depart + n_ligne * max(0.18, decalage * 5))
            for j, (mot, fort, colle) in enumerate(ligne):
                if colle and j > 0:
                    x -= espace
                # Par groupes de sens (une ligne à la fois), plus mot à mot (direction artistique 22/11).
                # Un calcul (« 5 + 10 + 6 + 4 = 25 ») apparaît terme à terme, au rythme de la voix (JG, 22/11).
                a = self._visibilite(t, depart, n_ligne, max(0.18, decalage * 5))
                n += 1
                w = police.getlength(mot)
                if j in temps_calc:   # morceau par morceau, chacun à son instant
                    xp = x
                    for piece, t0 in temps_calc[j]:
                        ap = a if t0 is None else self._visibilite(t, t0, 0, 0, ENTREE_MOT)
                        if ap > 0:
                            fond = self._fond.getpixel((int(min(xp, self.largeur - 1)), int(min(y, self.hauteur - 1))))
                            c = self.c["accent"] if fort else couleur
                            d.text((xp, y + (1 - ap) * police.size * 0.35), piece.rstrip("\u00a0\u202f"),
                                   font=police, fill=_melange(fond, c, ap))
                        xp += police.getlength(piece)
                    x += w + espace
                    continue
                if a > 0:
                    dy = (1 - a) * police.size * 0.35
                    fond = self._fond.getpixel((int(min(x, self.largeur - 1)), int(min(y, self.hauteur - 1))))
                    if fort and style_fort == "surligne" and self._univers == "immersif":
                        # Sur le bleu nuit, le mot fort passe simplement en jaune, comme dans les premières
                        # vidéos (design Mixte, JG, 28/11/2026) : une bande claire y paraît terne.
                        d.text((x, y + dy), mot, font=police, fill=_melange(fond, self.c["accent"], a))
                    elif fort and style_fort == "surligne":
                        # Surligneur doux : bande claire dans la moitié basse du mot, mot en couleur d'accent
                        # (plus de pavé plein, jugé trop lourd par JG le 22/11/2026).
                        marge = police.size * 0.06
                        haut_b = y + police.size * 0.62
                        d.rounded_rectangle((x - marge, haut_b + dy, x + w + marge, y + police.size * 1.08 + dy),
                                            radius=max(2, round(police.size * 0.08)),
                                            fill=_melange(fond, self.c["or"], 0.32 * a))
                        d.text((x, y + dy), mot, font=police, fill=_melange(fond, couleur, a))
                    else:
                        c = self.c["accent"] if fort else couleur
                        d.text((x, y + dy), mot, font=police, fill=_melange(fond, c, a))
                x += w + espace
            y += pas
        return y, n

    def _temps_calcul(self, ligne, debut_ligne) -> dict[int, list[tuple[str, float | None]]]:
        """Calcul de la ligne (« 5 + 10 + 6 + 4 = 25 ») : pour chaque mot concerné, ses morceaux (séparés
        par les espaces insécables de la typographie) et l'instant d'apparition de chacun. Vide si la ligne
        ne contient pas de calcul (un opérateur et un « = »). Les termes s'étalent sur le morceau de voix en
        cours quand la ligne apparaît (sinon sur 1,8 s) ; ce qui précède le calcul suit la ligne."""
        decoupe = [re.split(r"([\u00a0\u202f])", m) for m, _, _ in ligne]
        pieces = [p for parts in decoupe for p in parts[::2]]
        if not any(p in OPERATEURS for p in pieces) or not any(p in ("=", "≈") for p in pieces):
            return {}
        calc = lambda p: p in OPERATEURS or p in ("=", "≈") or bool(TERME_CALCUL.match(p))
        ordre, vu_terme = [], False          # (mot, indice du morceau) des termes, dans l'ordre
        for j, parts in enumerate(decoupe):
            for k in range(0, len(parts), 2):
                p = parts[k]
                if TERME_CALCUL.match(p):
                    vu_terme = True
                if vu_terme and (calc(p) or (p in UNITES_CALCUL and ordre)):
                    ordre.append((j, k, p in UNITES_CALCUL))
        if sum(1 for *_, u in ordre if not u) < 3:
            return {}
        fin = debut_ligne + 1.8
        scene = self._scene_courante
        morceaux = self.morceaux_voix.get(id(scene)) if scene is not None else None
        if morceaux:
            en_cours = [m for m in morceaux if m[1] > debut_ligne + 0.1]
            if en_cours:
                d0, f0 = en_cours[0]
                fin = max(debut_ligne + 0.8, f0 - 0.15)
                debut_ligne = max(debut_ligne, d0)
        n_termes = sum(1 for *_, u in ordre if not u)
        pas = (fin - debut_ligne) / max(1, n_termes)
        instants, k_terme = {}, -1
        for j, k, unite in ordre:
            if not unite:
                k_terme += 1
            instants[(j, k)] = debut_ligne + max(0, k_terme) * pas
        sortie = {}
        for j in {j for j, _, _ in ordre}:
            parts = decoupe[j]
            sortie[j] = [(parts[k] + (parts[k + 1] if k + 1 < len(parts) else ""), instants.get((j, k)))
                         for k in range(0, len(parts), 2)]
        return sortie

    def _ecrire_gauche(self, d, x, y, lignes, police, pas, couleur, a=1.0):
        for ligne in lignes:
            fond = self._fond.getpixel((int(x), int(min(y, self.hauteur - 1))))
            d.text((x, y + (1 - a) * 20), ligne, font=police, fill=_melange(fond, couleur, a))
            y += pas
        return y

    # ------------------------------------------------------------------ cadre
    def _cadre(self, d: ImageDraw.ImageDraw, index: int, total: int, nom_marque: bool = True):
        g, h, dr, b = self.zone
        marque = self.charte["marque"][self.langue]
        p = self.police("gras", 30)
        if nom_marque:  # inutile quand le logo est déjà en haut de l'image
            d.rectangle((g, h + 4, g + 14, h + 34), fill=self.c["accent"])
            d.text((g + 30, h), marque, font=p, fill=self.c["texte"])
        # « court » (facultatif) : nom bref pour le pied de page, quand une fiche cite plusieurs pages d'un même site.
        noms_l = list(dict.fromkeys(_texte_langue(s.get("court") or s["nom"], self.langue) for s in self.fiche.sources))
        noms = ", ".join(noms_l)
        if not noms:   # fiche pédagogique sans source : pas de pied de page
            return self._cadre_numero(d, index, total)
        # Pied de page des sources limité à certaines scènes (charte « pied_sources ») : la source de chaque
        # fait reste dans sa note ; le pied de page de chaque image se lisait comme du texte fixe.
        seules = (self.charte.get("pied_sources") or {}).get(self.format)
        scene = getattr(self, "_scene_courante", None)
        if seules is not None and scene is not None and scene.type not in seules:
            return
        lib = self.lib["sources" if len(noms_l) > 1 else "source"]
        pied = typographie(f"{lib} : {noms}" if self.langue == "fr" else f"{lib}: {noms}", self.langue)
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

    def _cadre_numero(self, d, index, total):
        if self.format == "carrousel" and total > 1:
            g, h, dr, b = self.zone
            pp = self.police("regulier", 26)
            num = f"{index + 1}/{total}"
            d.text((dr - pp.getlength(num), b - 34), num, font=pp, fill=self.c["secondaire"])

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
        if scene.type in self.TYPES_PEDAGOGIQUES:
            return self.duree_animation_pedagogique(scene, n)
        return {
            "accroche": 0.0 if self.charte.get("accroche_pleine") else 0.15 + n * DECALAGE_MOT + ENTREE_MOT,
            "texte": 0.1 + n * self._decalage_texte(scene) + ENTREE_MOT,
            "chiffre": max(1.9, 1.0 + n * 0.04 + ENTREE_MOT) + (0.6 if scene.extra.get("valeur") is not None else 0),
            "graphique": 0.4 + len(self.fiche.donnees["points"]) * 0.15 + 1.0 if self.fiche.donnees else 0,
            "source": 1.2,
            "fin": 0.1 + n * DECALAGE_MOT + 1.2,
            "accueil": 0.1 + n * self._decalage_texte(scene) + ENTREE_MOT,
            "cloture": 0.1 + n * self._decalage_texte(scene) + ENTREE_MOT,
        }[scene.type]

    def _decalage_texte(self, scene):
        n = max(1, len(mots_riches(scene.texte)))
        return min(DECALAGE_MOT, 1.6 / n)  # un texte long ne met jamais plus d'1,6 s à apparaître

    def dessiner(self, scene: Scene, index: int = 0, total: int = 1, t: float | None = None,
                 couverture: bool = False) -> Image.Image:
        """t : secondes écoulées depuis le début de la scène (None = état final, pour le carrousel).
        couverture : image de couverture (miniature), avec le logo selon logo.couverture."""
        self.basculer(self.univers_de(scene))
        image = self._fond.copy()
        self._image = image
        self._scene_courante = scene
        d = ImageDraw.Draw(image)
        g, h, dr, b = self.zone
        haut, bas = h + 130, b - 110  # sous l'en-tête, au-dessus du pied de page
        coin = None
        if scene.type != "fin" and self.logo_prevu(scene, couverture) and self.logos.images:
            x, y, lg, position = coin = self._logo_coin(couverture)
            ref = next(iter(self.logos.images.values()))
            hl = round(ref.height * lg / ref.width)
            p = round(lg * float(self.logos.conf.get("zone_protection", 0.08)))
            # On réserve la place du logo : le texte de la scène ne passe jamais dessous.
            if position.startswith("haut"):
                haut = max(haut, y + hl + p + 20)
            elif position.startswith("bas"):
                bas = min(bas, y - p - 20)
        mobile = not couverture and self.mobile_prevu(scene)
        if mobile:   # bandeau du haut réservé au logo mobile : le texte de la scène n'y passe jamais
            _, hm, pm = self._mobile_taille()
            haut = max(haut, h + hm + pm + 20)
        # Plus de nom de marque fixe sur les vidéos (décision de JG, 21/11/2026) : seul le carrousel
        # (images fixes) garde l'en-tête « ACTU-BASICS » quand le logo n'est pas en haut.
        nom_marque = self.format == "carrousel" and not (coin and coin[3].startswith("haut"))
        self._cadre(d, index, total, nom_marque=nom_marque)
        largeur = dr - g
        x_c = (g + dr) // 2
        ctx = f"{self.langue}/{self.format}/scène {index + 1} {scene.type}"
        self._index, self._couverture = index, couverture
        note = scene.extra.get("note")
        if note and scene.type != "fin":
            bas = self._note(d, note, g, dr, bas, t, self.duree_animation_modele(scene) - 0.6 if scene.type == "animation" else 0.9)
        getattr(self, f"_scene_{scene.type}")(d, scene, g, haut, dr, bas, largeur, x_c, t, ctx)
        if coin:
            self._poser_logo(image, coin[0], coin[1], coin[2], scene, index, t, couverture)
        if self.brouillon:
            image = self._filigrane(image)
        return image

    def _note(self, d, note, g, dr, bas, t, depart=0.9) -> int:
        """Petite mention discrète en bas de la zone (hypothèse, précision). Retourne le nouveau bas."""
        p = self.police("regulier", 40 if self.format != "lecon" else 36)
        mots, lignes, ligne = _mots(insecables_nombres(note)), [], ""
        for m in mots:
            essai = f"{ligne} {m}".strip()
            if p.getlength(essai) > (dr - g) * 0.9 and ligne:
                lignes.append(ligne)
                ligne = m
            else:
                ligne = essai
        lignes.append(ligne)
        pas = 52 if self.format != "lecon" else 46
        y = bas - pas * len(lignes)
        a = self._visibilite(t, depart)
        for k, l in enumerate(lignes):
            x = (g + dr - p.getlength(l)) / 2
            fond = self._fond.getpixel((int(x), int(y + k * pas)))
            d.text((x, y + k * pas), l, font=p, fill=_melange(fond, self.c["secondaire"], a))
        return y - 30

    def _scene_accroche(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        p, lignes, pas, hh = self.ajuster_riche(scene.texte, "affichage", largeur, bas - haut, 190, 80,
                                                1.08, ctx, majuscules=self.majuscules)
        # Première image pleine (diagnostic TikTok du 21/11/2026, charte « accroche_pleine ») : la question est
        # lisible dès 00:00 ; le mouvement vient de la caméra lente et du décor.
        if self.charte.get("accroche_pleine"):
            t = None
        self.ecrire_riche(d, lignes, p, pas, haut + (bas - haut - hh) // 2, self.c["texte"], t, 0.15,
                          style_fort="surligne")

    def _scene_texte(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        p, lignes, pas, hh = self.ajuster_riche(scene.texte, "gras", largeur, bas - haut, 80, 42, 1.25, ctx)
        self.ecrire_riche(d, lignes, p, pas, haut + (bas - haut - hh) // 2, self.c["texte"], t, 0.1,
                          decalage=self._decalage_texte(scene))

    def _scene_accueil(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        """Accueil : salutation et remerciement, puis ce que l'épisode va apporter (texte de la fiche)."""
        self._scene_texte(d, scene, g, haut, dr, bas, largeur, x_c, t, ctx)

    def _scene_cloture(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        """Clôture : récapitulatif, orientation (épisode suivant, autres vidéos), invitations à s'abonner,
        aimer et partager. Une ligne par invitation dans la fiche (retours à la ligne)."""
        self._scene_texte(d, scene, g, haut, dr, bas, largeur, x_c, t, ctx)

    def _scene_fin(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        if self.logo_prevu(scene, self._couverture) and self.logos.images:
            return self._scene_fin_logo(d, scene, g, haut, dr, bas, largeur, x_c, t, ctx)
        p, lignes, pas, hh = self.ajuster_riche(scene.texte, "gras", largeur, (bas - haut) // 2, 78, 40,
                                                1.25, ctx)
        y = haut + (bas - haut) // 2 - hh
        y, n = self.ecrire_riche(d, lignes, p, pas, y, self.c["texte"], t, 0.1)
        # Sans logo (désactivé ou fichier absent) : nom de la marque en texte, jamais un logo imité.
        marque = self.charte["marque"][self.langue]
        pm = self.police("affichage", 120)
        lm = self._couper_riche(mots_riches(marque), pm, largeur)
        a = 1.0 if t is None else ease_back((t - 0.1 - n * DECALAGE_MOT - 0.1) / 0.5)
        if a > 0:
            self.ecrire_riche(d, [[(m, True, c) for m, _, c in l] for l in lm], pm, int(120 * 1.05),
                              y + 70 + (1 - min(a, 1)) * 40, self.c["accent"])

    def _scene_fin_logo(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        """Fin : appel à l'action, logo officiel, slogan. Le logo n'est jamais recouvert."""
        c = self.conf_logo()
        protection = float(self.logos.conf.get("zone_protection", 0.08))
        ref = next(iter(self.logos.images.values()))
        ratio = ref.height / ref.width
        p, lignes, pas, hh = self.ajuster_riche(scene.texte, "gras", largeur, (bas - haut) * 2 // 5, 78, 40,
                                                1.25, ctx)
        afficher = c.get("slogan", True)
        if isinstance(afficher, dict):  # réglage par langue
            afficher = afficher.get(self.langue, True)
        slogan = (self.charte.get("slogan") or {}).get(self.langue, "") if afficher else ""
        ps = self.police("gras", 46)
        ls = self._couper_riche(mots_riches(typographie(slogan, self.langue)), ps, largeur) if slogan else []
        hs = int(46 * 1.25) * len(ls)
        lg, lg_min = int(c.get("largeur_px", 420)), int(c.get("largeur_min_px", 280))
        lg = min(lg, largeur)

        def ecarts(w):
            e = max(40, round(w * protection) + 16)   # au-delà de la zone de protection
            return e, (e if ls else 0)

        def total(w):
            e1, e2 = ecarts(w)
            return hh + e1 + round(w * ratio) + e2 + hs

        while total(lg) > bas - haut and lg > lg_min:
            lg -= 10
        if total(lg) > bas - haut:
            self.alertes.append(f"Texte de fin trop long pour laisser la place au logo ({ctx})")
        e1, e2 = ecarts(lg)
        y = haut + max(0, (bas - haut - total(lg)) // 2)
        y, n = self.ecrire_riche(d, lignes, p, pas, y, self.c["texte"], t, 0.1)
        y = max(y, haut + hh)
        depart = 0.1 + n * DECALAGE_MOT + 0.1
        a = 1.0 if t is None else max(0.0, min(1.0, (t - depart) / 0.4))   # fondu simple, sans effet
        y_logo = y + e1
        if ls:  # écrit avant le logo : le contrôle de recouvrement voit tout ce qui l'entoure
            self.ecrire_riche(d, ls, ps, int(46 * 1.25), y_logo + round(lg * ratio) + e2, self.c["texte"],
                              t, depart + 0.3)
        if a > 0:
            self._poser_logo(self._image, x_c - lg // 2, y_logo, lg, scene, self._index, t, False, opacite=a)

    def _chiffre_espace(self, texte: str, police) -> tuple[list[str], float, float]:
        """Groupes de milliers dessinés séparément, avec un écart lisible en très gros corps."""
        groupes = texte.split(ESPACE_MILLIERS)
        ecart = police.size * 0.22
        largeur = sum(police.getlength(gr) for gr in groupes) + ecart * (len(groupes) - 1)
        return groupes, ecart, largeur

    def _scene_chiffre(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        chiffre = self.chiffre
        if scene.extra.get("valeur") is not None:   # fiche pédagogique : chiffre propre à la scène
            chiffre = {k: scene.extra[k] for k in ("valeur", "unite", "prefixe", "suffixe", "decimales")
                       if k in scene.extra}
            if chiffre.get("decimales") is None:
                v = float(chiffre["valeur"])
                chiffre["decimales"] = 0 if v.is_integer() else min(len(repr(v).split(".")[1]), 3)
        k = 1.0 if t is None else ease_out(t / 1.3)
        valeur = chiffre["valeur"] * k
        txt = formater_chiffre(chiffre, self.langue, valeur)
        final = formater_chiffre(chiffre, self.langue)
        # Taille calculée sur la valeur finale pour éviter que le chiffre « respire ».
        taille = 420
        while True:
            pc = self.police("affichage", taille)
            if (self._chiffre_espace(final, pc)[2] <= largeur and taille * 1.12 <= (bas - haut) * 0.55) \
                    or taille <= 120:
                break
            taille -= 8
        hc = pas_c = int(taille * 1.12)
        u = unite(chiffre, self.langue)
        pu, lu, pas_u, hu = (self.ajuster_riche(u, "gras", largeur, 200, 70, 38, 1.15, ctx) if u
                             else (None, [], 0, 0))
        reste = bas - haut - hc - hu - 140
        pt, lt, pas_t, ht = self.ajuster_riche(scene.texte, "regulier", largeur, max(reste, 100), 56, 34,
                                               1.3, ctx)
        y = haut + max(0, (bas - haut - (hc + hu + ht + 120)) // 2)
        groupes, ecart, l_txt = self._chiffre_espace(final, pc)
        # Le chiffre final fixe la position : les groupes sont alignés à droite pendant le comptage.
        groupes_courants = txt.split(ESPACE_MILLIERS)
        x_fin = x_c + l_txt / 2
        x = x_fin
        for gr in reversed(groupes_courants):
            x -= pc.getlength(gr)
            d.text((x, y), gr, font=pc, fill=self.c["accent"])
            x -= ecart
        # Bas réel du chiffre final, virgule comprise (elle descend sous la ligne de base) :
        # le soulignement ne doit jamais couper le nombre.
        y += max(pc.getbbox("0123456789")[3], pc.getbbox(final)[3]) + 28
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
            ligne = _texte_langue(s["nom"], self.langue) + (f" ({s['publication']})" if s.get("publication") else "")
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
