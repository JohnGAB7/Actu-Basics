"""Animations pédagogiques : le raisonnement construit à l'image, phase par phase.

Une scène « animation » a un modèle et, en option, une légende par phase (champ `etapes`). Chaque
phase démarre sur une phrase de la voix (repères fournis après la narration), sinon à la suite de
la précédente. Une seule légende est visible à la fois : la voix raconte, l'image démontre.

Modèles :
- foule       : n silhouettes qui apparaissent (le groupe dont on parle) ;
- paires      : n personnes sur un cercle ; phases « apparition », « personne » (les nouvelles paires
                de la personne suivante), « vous » (une personne face aux autres), « reste », « total ».
                Jusqu'à 6 personnes : lettres A, B, C… et liste des paires sous le cercle ;
- doublon     : A choisit B, B choisit A, c'est la même paire (pourquoi on divise par 2) ;
- calendrier  : 365 cases ; chaque personne prend un jour, la fraction de jours encore libres
                et la probabilité « tous différents » se mettent à jour ;
- complement  : une barre de 100 % partagée entre un événement et son contraire ;
- selection   : n icônes (avions ou entreprises) ; « depart » les montre, « selection » estompe
                celles qui disparaissent, « echantillon » fait descendre les survivantes dans le cadre
                des données observées, « filtre » trace la flèche « sélection par la survie ».
"""
from __future__ import annotations

import math
import random

from .formatage import formater_nombre

MODELES = ("foule", "paires", "doublon", "calendrier", "complement", "selection")
PHASES = {
    "foule": ("apparition",),
    "paires": ("apparition", "personne", "vous", "reste", "total"),
    "doublon": ("aller", "retour", "fusion", "legende"),
    "calendrier": ("personne", "reste"),
    "complement": ("gauche", "droite", "total"),
    "selection": ("depart", "selection", "echantillon", "filtre"),
}
PHASES_DEFAUT = {
    "foule": ["apparition"],
    "paires": ["apparition", "reste", "total"],
    "doublon": ["aller", "retour", "fusion"],
    "calendrier": ["personne", "personne", "personne", "reste"],
    "complement": ["gauche", "droite"],
    "selection": ["depart", "selection", "echantillon", "filtre"],
}
LIBELLES = {
    "fr": {"paires": "paires", "paire": "paire", "jours": "jours libres", "tous": "Tous différents"},
    "en": {"paires": "pairs", "paire": "pair", "jours": "days still free", "tous": "All different"},
}
# Modèle « selection » : libellés selon l'icône et la langue.
LIBELLES_SELECTION = {
    ("avion", "fr"): {"depart": "au départ", "restants": "revenus", "absents": "absents",
                      "donnees": "Données observées", "filtre": "sélection par la survie"},
    ("avion", "en"): {"depart": "set out", "restants": "returned", "absents": "missing",
                      "donnees": "Observed data", "filtre": "selection by survival"},
    ("entreprise", "fr"): {"depart": "créées", "restants": "encore actives", "absents": "disparues",
                           "donnees": "Témoignages recueillis", "filtre": "sélection par la survie"},
    ("entreprise", "en"): {"depart": "founded", "restants": "still active", "absents": "closed",
                           "donnees": "Stories we hear", "filtre": "selection by survival"},
}
ICONES_SELECTION = ("avion", "entreprise")
LETTRES = "ABCDEF"
PAUSE_PHASES = 0.5          # s entre deux phases quand la voix ne donne pas de repères


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def _groupes(n: int) -> list[list[tuple[int, int]]]:
    """Paires regroupées par personne : la personne k forme ses paires avec les suivantes."""
    return [[(i, j) for j in range(i + 1, n)] for i in range(n)]


class Animations:
    """Mélangé à Rendu (polices, couleurs, écriture) via ScenesPedagogiques."""

    # ------------------------------------------------------------------ phases et temps
    def _plan_animation(self, scene) -> list[dict]:
        """Phases de la scène : nature, durée, et contenu propre au modèle."""
        conf = scene.extra["animation"]
        modele, n = conf["modele"], conf.get("n", 0)
        phases = conf.get("phases") or PHASES_DEFAUT[modele]
        plan = []
        if modele == "paires":
            groupes, k = _groupes(n), 0
            for nature in phases:
                if nature == "apparition":
                    plan.append({"nature": nature, "duree": 1.6, "paires": []})
                elif nature == "personne":
                    g = groupes[min(k, n - 1)]
                    k += 1
                    plan.append({"nature": nature, "duree": min(0.55 * max(len(g), 1), 2.6), "paires": g,
                                 "personne": k - 1})
                elif nature == "vous":
                    plan.append({"nature": nature, "duree": 2.2, "paires": groupes[0], "personne": 0})
                    k = max(k, 1)
                elif nature == "reste":
                    g = [p for gg in groupes[k:] for p in gg]
                    k = n
                    plan.append({"nature": nature, "duree": 2.8, "paires": g})
                else:   # total
                    plan.append({"nature": nature, "duree": 0.8, "paires": []})
        elif modele == "calendrier":
            k = 0
            for nature in phases:
                if nature == "personne":
                    plan.append({"nature": nature, "duree": 0.8, "de": k, "a": k + 1})
                    k += 1
                else:
                    plan.append({"nature": nature, "duree": 3.0, "de": k, "a": n})
                    k = n
        else:
            durees = {"apparition": 1.8, "aller": 1.0, "retour": 1.0, "fusion": 1.0, "legende": 0.6,
                      "gauche": 1.2, "droite": 1.2, "total": 0.8,
                      "depart": 1.6, "selection": 1.4, "echantillon": 1.4, "filtre": 1.0}
            plan = [{"nature": nature, "duree": durees.get(nature, 1.0)} for nature in phases]
        debuts = self._debuts_phases(scene, plan)
        for p, debut in zip(plan, debuts):
            p["debut"] = debut
        return plan

    def _debuts_phases(self, scene, plan) -> list[float]:
        if self.reperes.get(id(scene)):
            debuts = self._debuts_etapes(scene, len(plan))
        else:
            debuts, t = [], 0.8
            for p in plan:
                debuts.append(t)
                t += p["duree"] + PAUSE_PHASES + 0.8
        return debuts

    def duree_animation_modele(self, scene) -> float:
        plan = self._plan_animation(scene)
        return max(p["debut"] + p["duree"] for p in plan) + 0.8

    @staticmethod
    def _avancee(p, t) -> float:
        """0 avant la phase, 1 après, progression pendant."""
        if t is None:
            return 1.0
        return max(0.0, min(1.0, (t - p["debut"]) / p["duree"]))

    def _phase_courante(self, plan, t) -> int:
        if t is None:
            return len(plan) - 1
        courante = -1
        for i, p in enumerate(plan):
            if t >= p["debut"]:
                courante = i
        return courante

    # ------------------------------------------------------------------ éléments communs
    def _ecrire_centre(self, d, texte, style, cx, y, largeur, hauteur, taille_max, taille_min, t, depart, ctx,
                       couleur=None):
        """Texte riche centré sur cx (et non sur la zone). Retourne le bas."""
        if not texte:
            return y
        p, lignes, pas, h = self.ajuster_riche(texte, style, largeur, hauteur, taille_max, taille_min, 1.18, ctx,
                                               equilibre=True)
        for ligne in lignes:
            w = self._largeur_ligne(ligne, p)
            self.ecrire_riche(d, [ligne], p, pas, y, couleur or self.c["texte"], t, depart, centre=False,
                              x_gauche=cx - w / 2, decalage=0.03)
            y += pas
        return y

    def _legende_phase(self, d, scene, plan, zone, y_bas, t, ctx):
        """Légende de la phase en cours, centrée en bas de la zone de contenu (une seule à la fois)."""
        legendes = scene.extra.get("etapes") or []
        i = self._phase_courante(plan, t)
        if i < 0 or i >= len(legendes):
            return
        g, _, dr, _ = zone
        hauteur = 170 if not self.colonnes else 150
        self._ecrire_centre(d, legendes[i], "gras", (g + dr) / 2, y_bas - hauteur, dr - g, hauteur,
                            64 if not self.colonnes else 58, 40, t, plan[i]["debut"], ctx)

    def _personne(self, d, cx, cy, r, couleur):
        """Silhouette simple : tête et épaules."""
        d.ellipse((cx - r * 0.42, cy - r, cx + r * 0.42, cy - r * 0.16), fill=couleur)
        d.pieslice((cx - r * 0.8, cy - r * 0.05, cx + r * 0.8, cy + r * 1.5), 180, 360, fill=couleur)

    # ------------------------------------------------------------------ dispatch
    def _scene_animation(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        zt, zc = self._zones(g, haut, dr, bas)
        y = self._titre_scene(d, scene, zt, t, ctx, hauteur_max=(bas - haut) // 5, taille=84)
        haut_c = zc[1] if self.colonnes else y + 10
        plan = self._plan_animation(scene)
        reserve = 190 if (scene.extra.get("etapes")) else 0
        zone = (zc[0], haut_c, zc[2], bas - reserve)
        getattr(self, "_anim_" + scene.extra["animation"]["modele"])(d, scene, plan, zone, t, ctx)
        self._legende_phase(d, scene, plan, (zc[0], haut_c, zc[2], bas), bas, t, ctx)

    # ------------------------------------------------------------------ foule
    def _anim_foule(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        n = scene.extra["animation"]["n"]
        g, haut, dr, bas = zone
        cols = max(1, round(math.sqrt(n * (dr - g) / max(bas - haut, 1))))
        rangs = math.ceil(n / cols)
        pas = min((dr - g) / cols, (bas - haut) / rangs)
        r = pas * 0.36
        x0 = (g + dr) / 2 - pas * cols / 2
        y0 = (haut + bas) / 2 - pas * rangs / 2
        p = plan[0]
        fond = self._fond.getpixel((int((g + dr) / 2), int((haut + bas) / 2)))
        for k in range(n):
            a = 1.0 if t is None else _ease((t - p["debut"] - k * p["duree"] / n) / 0.35)
            if a <= 0:
                continue
            c, l = k % cols, k // cols
            dernier_rang = l == rangs - 1 and n % cols
            decal = (cols - n % cols) * pas / 2 if dernier_rang else 0
            cx, cy = x0 + decal + (c + 0.5) * pas, y0 + (l + 0.5) * pas + (1 - a) * 20
            self._personne(d, cx, cy, r, _melange(fond, self.c["texte"], a))

    # ------------------------------------------------------------------ paires
    def _anim_paires(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        conf = scene.extra["animation"]
        n = conf["n"]
        depuis = conf.get("depuis") or 0
        lettres = n <= len(LETTRES)
        g, haut, dr, bas = zone
        lib = LIBELLES[self.langue]
        pc = self.police("affichage", 104 if not self.colonnes else 120)
        p_liste = self.police("gras", 56 if not self.colonnes else 50)
        pas_liste = int(p_liste.size * 1.5)
        if lettres:
            # Petit groupe : cercle à gauche, liste des paires à droite (lisible sur mobile).
            l_cercle = (dr - g) * 0.56
            rayon = min(l_cercle / 2 - 50, (bas - haut) / 2 - 45)
            cx = g + l_cercle / 2
            cy = (haut + bas) / 2
            x_liste = g + l_cercle + 10
        else:
            rayon = min((dr - g) / 2 - 30, (bas - haut - pc.size - 70) / 2)
            cx = (g + dr) / 2
            cy = haut + 20 + rayon
        rayon = max(rayon, 80)
        depart = -math.pi / 2 if n != 4 else -3 * math.pi / 4      # 4 personnes : un carré bien posé
        points = [(cx + rayon * math.cos(depart + 2 * math.pi * k / n),
                   cy + rayon * math.sin(depart + 2 * math.pi * k / n)) for k in range(n)]
        fond = self._fond.getpixel((int(cx), int(cy)))
        epais = 7 if lettres else 2
        normal = _melange(fond, self.c["texte"] if lettres else self.c["barre"], 0.55 if lettres else 0.5)
        courante = self._phase_courante(plan, t)
        # Paires tracées : phase par phase, la dernière tracée en accent.
        dessinees, vous, derniere = [], set(), None
        for i, p in enumerate(plan):
            k = self._avancee(p, t)
            if p["nature"] in ("personne", "vous", "reste") and k > 0:
                visibles = p["paires"][: math.ceil(len(p["paires"]) * k)]
                dessinees += visibles
                if p["nature"] == "vous":
                    vous.update(visibles)
                if visibles and k < 1:
                    derniere = visibles[-1]
        total = plan[courante]["nature"] == "total" if courante >= 0 else False
        k_total = self._avancee(plan[courante], t) if total else 0
        # Personne en cours : ses paires déjà comptées (avec les précédentes) en pointillés discrets.
        en_cours = plan[courante] if courante >= 0 and plan[courante]["nature"] == "personne" else None
        if en_cours and lettres and t is not None:
            b = en_cours["personne"]
            for a in range(b):
                self._pointilles(d, points[a], points[b], _melange(fond, self.c["secondaire"], 0.8), 4)
        for (i, j) in dessinees:
            if (i, j) in vous:
                couleur = self.c["accent"]
            elif total:
                couleur = _melange(normal, self.c["accent"], k_total)
            else:
                couleur = normal
            d.line((*points[i], *points[j]), fill=couleur, width=epais if (i, j) not in vous else max(epais, 4))
        if derniere:
            d.line((*points[derniere[0]], *points[derniere[1]]), fill=self.c["accent"], width=epais + 3)
        # Personnes (points), lettres.
        p_lettre = self.police("noir", 58 if not self.colonnes else 52)
        apparition = next((p for p in plan if p["nature"] == "apparition"), None)
        r_point = 34 if lettres else 13
        for idx, (px, py) in enumerate(points):
            if apparition and idx >= depuis:
                a = 1.0 if t is None else _ease((t - apparition["debut"]
                                                 - (idx - depuis) * apparition["duree"] / max(n - depuis, 1)) / 0.3)
            else:
                a = 1.0 if t is None else _ease((t - 0.1 - idx * 0.08) / 0.3)
            if a <= 0:
                continue
            actif = en_cours is not None and idx == en_cours["personne"]
            couleur = self.c["accent"] if actif or (vous and idx == 0) else self.c["texte"]
            r = r_point * a * (1.15 if actif else 1)
            d.ellipse((px - r, py - r, px + r, py + r), fill=_melange(fond, couleur, a))
            if lettres:
                lettre = LETTRES[idx]
                d.text((px - p_lettre.getlength(lettre) / 2, py - p_lettre.size * 0.62), lettre, font=p_lettre,
                       fill=_melange(fond, self.c["fond"], a))
        # Liste des paires (petits groupes) ou compteur (grands groupes).
        nb = len(dessinees)
        if lettres:
            y = cy - pas_liste * (n - 1) / 2
            for a in range(n - 1):
                mots = [f"{LETTRES[a]}–{LETTRES[b]}" for b in range(a + 1, n) if (a, b) in dessinees]
                if mots:
                    couleur = self.c["accent"] if en_cours and en_cours["personne"] == a else self.c["texte"]
                    d.text((x_liste, y), "  ".join(mots), font=p_liste, fill=couleur)
                y += pas_liste
        elif nb:
            texte = f"{formater_nombre(nb, self.langue, 0)} {lib['paires'] if nb != 1 else lib['paire']}"
            fini = nb == n * (n - 1) // 2
            d.text((cx - pc.getlength(texte) / 2, cy + rayon + 26), texte, font=pc,
                   fill=self.c["accent"] if fini or vous and nb == len(vous) else self.c["texte"])

    def _pointilles(self, d, a, b, couleur, largeur, pas=18):
        lg = math.dist(a, b)
        if lg == 0:
            return
        ux, uy = (b[0] - a[0]) / lg, (b[1] - a[1]) / lg
        s = 0.0
        while s < lg:
            e = min(lg, s + pas * 0.55)
            d.line((a[0] + ux * s, a[1] + uy * s, a[0] + ux * e, a[1] + uy * e), fill=couleur, width=largeur)
            s += pas

    # ------------------------------------------------------------------ doublon
    def _anim_doublon(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        g, haut, dr, bas = zone
        cy = (haut + bas) / 2
        ecart = min((dr - g) * 0.32, 340)
        cx = (g + dr) / 2
        A, B = (cx - ecart, cy), (cx + ecart, cy)
        fond = self._fond.getpixel((int(cx), int(cy)))
        par_nature = {p["nature"]: p for p in plan}
        fusion = self._avancee(par_nature["fusion"], t) if "fusion" in par_nature else 0.0
        for nom, (de, vers), signe in (("aller", (A, B), -1), ("retour", (B, A), 1)):
            p = par_nature.get(nom)
            if not p:
                continue
            k = self._avancee(p, t)
            if k <= 0:
                continue
            courbure = 150 * (1 - fusion) * signe
            couleur = self.c["accent"] if nom == "aller" else self.c["texte"]
            if fusion > 0:
                couleur = _melange(couleur, self.c["accent"], fusion)
            self._fleche(d, de, vers, courbure, k, couleur, 9, fleche=fusion < 0.6)
        p_lettre = self.police("noir", 72)
        for lettre, (px, py) in (("A", A), ("B", B)):
            r = 56
            d.ellipse((px - r, py - r, px + r, py + r), fill=self.c["texte"])
            d.text((px - p_lettre.getlength(lettre) / 2, py - p_lettre.size * 0.62), lettre, font=p_lettre,
                   fill=self.c["fond"])
        if fusion > 0:
            pe = self.police("affichage", 96)
            texte = "A–B = B–A"
            d.text((cx - pe.getlength(texte) / 2, cy + 120), texte, font=pe,
                   fill=_melange(fond, self.c["accent"], fusion))

    def _fleche(self, d, de, vers, courbure, k, couleur, largeur, fleche=True):
        """Arc de `de` vers `vers` (bombé de `courbure` px), tracé jusqu'à la fraction k."""
        mx, my = (de[0] + vers[0]) / 2, (de[1] + vers[1]) / 2 + courbure
        pts = []
        for s in range(0, 41):
            u = s / 40 * k
            x = (1 - u) ** 2 * de[0] + 2 * (1 - u) * u * mx + u ** 2 * vers[0]
            y = (1 - u) ** 2 * de[1] + 2 * (1 - u) * u * my + u ** 2 * vers[1]
            pts.append((x, y))
        # On s'arrête au bord du disque d'arrivée.
        pts = [p for p in pts if math.dist(p, vers) > 64 and math.dist(p, de) > 64] or pts[-1:]
        if len(pts) >= 2:
            d.line(pts, fill=couleur, width=largeur, joint="curve")
            if fleche and k > 0.2:
                (x1, y1), (x2, y2) = pts[-2], pts[-1]
                ang = math.atan2(y2 - y1, x2 - x1)
                tete = 30
                d.polygon([(x2 + 6 * math.cos(ang), y2 + 6 * math.sin(ang)),
                           (x2 - tete * math.cos(ang - 0.45), y2 - tete * math.sin(ang - 0.45)),
                           (x2 - tete * math.cos(ang + 0.45), y2 - tete * math.sin(ang + 0.45))], fill=couleur)

    # ------------------------------------------------------------------ calendrier
    def _anim_calendrier(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        n = scene.extra["animation"]["n"]
        jours = scene.extra["animation"].get("jours", 365)
        g, haut, dr, bas = zone
        lib = LIBELLES[self.langue]
        p_prob = self.police("gras", 56 if not self.colonnes else 50)
        h_texte = p_prob.size + 50
        # Nombre de colonnes qui donne les plus grandes cases dans la place disponible.
        cote, cols = max((min((dr - g) / c, (bas - haut - h_texte - 20) / math.ceil(jours / c)), c)
                         for c in range(10, 60))
        rangs = math.ceil(jours / cols)
        x0 = (g + dr) / 2 - cote * cols / 2
        y0 = haut + 10
        fond = self._fond.getpixel((int((g + dr) / 2), int(y0)))
        libre = _melange(fond, self.c["barre"], 0.45)
        pris = random.Random(2026).sample(range(jours), min(n, jours))
        # Nombre de personnes placées à l'instant t (fractionnaire pendant une phase).
        places, courante = 0.0, self._phase_courante(plan, t)
        for p in plan:
            k = self._avancee(p, t)
            if k > 0:
                places = p["de"] + (p["a"] - p["de"]) * k
        entiers = int(places + 1e-9)
        for jour in range(jours):
            c, l = jour % cols, jour // cols
            x, y = x0 + c * cote, y0 + l * cote
            d.rectangle((x + 2, y + 2, x + cote - 2, y + cote - 2), fill=libre)
        for k, jour in enumerate(pris[:entiers]):
            c, l = jour % cols, jour // cols
            x, y = x0 + c * cote, y0 + l * cote
            neuf = courante >= 0 and k == entiers - 1 and t is not None
            marge = -3 if neuf else 1
            d.rectangle((x + marge, y + marge, x + cote - marge, y + cote - marge), fill=self.c["accent"])
        y = y0 + rangs * cote + 30
        if entiers == 0:
            return
        cx = (g + dr) / 2
        prob = math.prod((jours - k) / jours for k in range(entiers))
        pct = formater_nombre(prob * 100, self.langue, 1) + (" %" if self.langue == "fr" else "%")
        sep = " : " if self.langue == "fr" else ": "
        debut, fin = f"{lib['tous']}{sep}", pct
        lg = p_prob.getlength(debut) + p_prob.getlength(fin)
        d.text((cx - lg / 2, y), debut, font=p_prob, fill=self.c["texte"])
        d.text((cx - lg / 2 + p_prob.getlength(debut), y), fin, font=p_prob, fill=self.c["accent"])

    # ------------------------------------------------------------------ complément
    def _anim_complement(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        v = float(scene.extra["animation"]["valeur"])
        g, haut, dr, bas = zone
        h_barre = 200 if not self.colonnes else 180
        y = (haut + bas) / 2 - h_barre / 2
        fond = self._fond.getpixel((int(g), int(y)))
        d.rounded_rectangle((g, y, dr, y + h_barre), radius=24, outline=_melange(fond, self.c["secondaire"], 0.6),
                            width=4)
        par_nature = {p["nature"]: p for p in plan}
        p_pct = self.police("affichage", 110 if not self.colonnes else 100)
        x_sep = g + (dr - g) * v
        for nom, x_a, x_b, couleur, encre in (("gauche", g, x_sep, self.c["texte"], self.c["fond"]),
                                              ("droite", x_sep, dr, self.c["accent"], self.c["fond"])):
            p = par_nature.get(nom)
            if not p:
                continue
            k = _ease(self._avancee(p, t))
            if k <= 0:
                continue
            fin = x_a + (x_b - x_a) * k
            d.rounded_rectangle((x_a + 6, y + 6, max(x_a + 7, fin - 6), y + h_barre - 6), radius=18,
                                fill=_melange(fond, couleur, 0.95))
            part = v if nom == "gauche" else 1 - v
            texte = formater_nombre(part * 100, self.langue, 1) + (" %" if self.langue == "fr" else "%")
            if fin - x_a > p_pct.getlength(texte) + 30:
                d.text(((x_a + fin) / 2 - p_pct.getlength(texte) / 2, y + h_barre / 2 - p_pct.size * 0.62), texte,
                       font=p_pct, fill=_melange(couleur, encre, k))
        if "total" in par_nature and self._avancee(par_nature["total"], t) > 0:
            # Accolade au-dessus de la barre : les deux parts forment un tout.
            k = _ease(self._avancee(par_nature["total"], t))
            c = _melange(fond, self.c["accent"], k)
            yb = y - 40
            d.line((g + 10, yb + 24, g + 10, yb, dr - 10, yb, dr - 10, yb + 24), fill=c, width=6)

    # ------------------------------------------------------------------ sélection par la survie
    @staticmethod
    def _disparues(n: int, restants: int) -> set[int]:
        """Indices des icônes qui disparaissent, réparties dans la rangée (pas toutes au bout)."""
        absents = n - restants
        return {round((j + 0.5) * n / absents - 0.5) for j in range(absents)} if absents else set()

    def _avion(self, d, cx, cy, r, couleur, contour=False):
        """Avion vu de dessus, nez vers le haut : fuselage, ailes, empennage. Pictogramme générique."""
        fuselage = [(cx, cy - r), (cx + r * 0.13, cy - r * 0.75), (cx + r * 0.13, cy + r * 0.75),
                    (cx, cy + r * 0.9), (cx - r * 0.13, cy + r * 0.75), (cx - r * 0.13, cy - r * 0.75)]
        ailes = [(cx - r * 0.12, cy - r * 0.25), (cx - r, cy + r * 0.2), (cx - r, cy + r * 0.38),
                 (cx - r * 0.12, cy + r * 0.12), (cx + r * 0.12, cy + r * 0.12), (cx + r, cy + r * 0.38),
                 (cx + r, cy + r * 0.2), (cx + r * 0.12, cy - r * 0.25)]
        queue = [(cx - r * 0.1, cy + r * 0.55), (cx - r * 0.42, cy + r * 0.82), (cx - r * 0.42, cy + r * 0.95),
                 (cx, cy + r * 0.82), (cx + r * 0.42, cy + r * 0.95), (cx + r * 0.42, cy + r * 0.82),
                 (cx + r * 0.1, cy + r * 0.55)]
        for forme in (ailes, queue, fuselage):
            if contour:
                d.polygon(forme, outline=couleur, width=3)
            else:
                d.polygon(forme, fill=couleur)

    def _entreprise(self, d, cx, cy, r, couleur, contour=False):
        """Immeuble simple : bloc et toit plat, trois rangées de fenêtres."""
        x0, x1, y0, y1 = cx - r * 0.62, cx + r * 0.62, cy - r * 0.85, cy + r * 0.9
        if contour:
            d.rectangle((x0, y0, x1, y1), outline=couleur, width=3)
            return
        d.rectangle((x0, y0, x1, y1), fill=couleur)
        fond = self.c["fond"]
        for li in range(3):
            for co in range(2):
                fx = x0 + r * (0.22 + co * 0.6)
                fy = y0 + r * (0.25 + li * 0.5)
                d.rectangle((fx, fy, fx + r * 0.34, fy + r * 0.28), fill=fond)

    def _anim_selection(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        conf = scene.extra["animation"]
        n, restants, icone = conf["n"], conf["restants"], conf.get("icone", "avion")
        lib = LIBELLES_SELECTION[(icone, self.langue)]
        dessiner = self._avion if icone == "avion" else self._entreprise
        g, haut, dr, bas = zone
        par_nature = {p["nature"]: p for p in plan}
        k_de = {nom: (_ease(self._avancee(par_nature[nom], t)) if nom in par_nature else 0.0)
                for nom in PHASES["selection"]}
        if t is None:
            k_de = {nom: (1.0 if nom in par_nature else 0.0) for nom in k_de}
        fond = self._fond.getpixel((int((g + dr) / 2), int((haut + bas) / 2)))
        p_cpt = self.police("gras", 46 if not self.colonnes else 42)
        p_lbl = self.police("regulier", 38 if not self.colonnes else 34)
        # Mise en page calculée sur la hauteur disponible : rangée, compteur, flèche, cadre.
        h_cpt, fleche_min, marge_cadre = p_cpt.size + 20, 110, 80
        pas = min((dr - g) / n, 150)
        r = max(18.0, min(pas * 0.4, (bas - haut - h_cpt - fleche_min - marge_cadre - 60) / 4))
        x0 = (g + dr) / 2 - pas * n / 2
        y_pop = haut + r + 20
        disparues = self._disparues(n, restants)
        survivantes = [i for i in range(n) if i not in disparues]
        hauteur_cadre = 2 * r + marge_cadre
        y_cadre = max(y_pop + r + h_cpt + fleche_min + 20, bas - hauteur_cadre - 10)
        demi_largeur = max(pas * restants / 2 + 40, p_lbl.getlength(lib["donnees"]) / 2 + 30)
        x_cadre0, x_cadre1 = (g + dr) / 2 - demi_largeur, (g + dr) / 2 + demi_largeur
        y_obs = y_cadre + marge_cadre - 20 + r
        p_dep = par_nature.get("depart")
        for i in range(n):
            cx = x0 + (i + 0.5) * pas
            a = 1.0 if t is None or not p_dep else _ease((t - p_dep["debut"] - i * p_dep["duree"] / n) / 0.35)
            if a <= 0:
                continue
            if i in disparues:
                # L'icône s'estompe et monte : elle ne reviendra pas dans les données.
                k = k_de["selection"]
                dessiner(d, cx, y_pop - 24 * k, r, _melange(fond, self.c["texte"], a * (1 - 0.8 * k)))
            elif k_de["echantillon"] <= 0:
                dessiner(d, cx, y_pop, r, _melange(fond, self.c["texte"], a))
        # Compteurs sous la rangée.
        y_txt = y_pop + r + 14
        if k_de["selection"] > 0:
            texte = f"{restants} {lib['restants']} · {n - restants} {lib['absents']}"
            couleur = _melange(fond, self.c["accent"], k_de["selection"])
        elif k_de["depart"] > 0:
            texte, couleur = f"{n} {lib['depart']}", _melange(fond, self.c["texte"], k_de["depart"])
        else:
            texte = ""
        if texte:
            d.text(((g + dr) / 2 - p_cpt.getlength(texte) / 2, y_txt), texte, font=p_cpt, fill=couleur)
        # Les survivantes descendent dans le cadre des données observées.
        k = k_de["echantillon"]
        if k > 0:
            d.rounded_rectangle((x_cadre0, y_cadre, x_cadre1, y_cadre + hauteur_cadre), radius=26,
                                outline=_melange(fond, self.c["accent"], k), width=5)
            d.text((x_cadre0 + 24, y_cadre + 10), lib["donnees"], font=p_lbl,
                   fill=_melange(fond, self.c["accent"], k))
            for rang, i in enumerate(survivantes):
                xa, xb = x0 + (i + 0.5) * pas, (g + dr) / 2 - pas * restants / 2 + (rang + 0.5) * pas
                dessiner(d, xa + (xb - xa) * k, y_pop + (y_obs - y_pop) * k, r, _melange(fond, self.c["texte"], k))
        # Flèche : de la population de départ aux données, filtrée par la survie.
        k = k_de["filtre"]
        if k > 0:
            couleur = _melange(fond, self.c["accent"], k)
            xa, ya, yb = (g + dr) / 2, y_txt + p_cpt.size + 24, y_cadre - 14
            self._fleche(d, (xa, ya - 60), (xa, yb + 60), 0, k, couleur, 8)   # _fleche rogne 64 px aux bouts
            lbl = lib["filtre"]
            d.text((xa + 24, (ya + yb) / 2 - p_lbl.size / 2), lbl, font=p_lbl, fill=couleur)

