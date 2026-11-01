"""Scènes des fiches pédagogiques : titre de chapitre, formule, étapes, courbe, exercice, correction.

Mêmes couleurs, polices et animations que les scènes d'actualité (charte.yaml) : seule la mise en page
change. Les étapes apparaissent quand la voix les annonce (repères de phrases fournis après la
narration), sinon à intervalle régulier.
"""
from __future__ import annotations

import math

from PIL import ImageDraw

from .formatage import formater_nombre, typographie

LIBELLES_PEDAGOGIE = {
    "fr": {"exercice": "À VOUS", "correction": "CORRECTION", "chapitre": "CHAPITRE", "reponse": "Réponse"},
    "en": {"exercice": "YOUR TURN", "correction": "ANSWER", "chapitre": "CHAPTER", "reponse": "Answer"},
}
INTERVALLE_ETAPES = 1.1     # s entre deux étapes sans repères de voix
TRACE_COURBE = 2.2          # s pour tracer la courbe


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


class ScenesPedagogiques:
    """Mélangé à Rendu : utilise ses polices, couleurs, zone et fonctions d'écriture."""

    TYPES_PEDAGOGIQUES = ("titre", "formule", "etapes", "courbe", "exercice", "correction")

    # ------------------------------------------------------------------ temps
    def _debuts_etapes(self, scene, n: int, depart: float = 0.6) -> list[float]:
        """Instant d'apparition de chaque étape : sur les phrases de la voix si elles sont connues."""
        reperes = self.reperes.get(id(scene))
        if reperes and n:
            if len(reperes) == n + 1:          # une phrase d'introduction, puis une par étape
                return reperes[1:]
            if len(reperes) == n:
                return reperes
            return [reperes[min(len(reperes) - 1, i * len(reperes) // n)] for i in range(n)]
        return [depart + i * INTERVALLE_ETAPES for i in range(n)]

    def duree_animation_pedagogique(self, scene, n_mots: int) -> float:
        etapes = scene.extra.get("etapes", [])
        if scene.type == "titre":
            return 0.3 + n_mots * 0.07 + 0.5
        if scene.type == "formule":
            n = len(scene.extra.get("formule", [])) or 1
            return (self._debuts_etapes(scene, n, depart=0.5)[-1] if n > 1 else 0.5) + 1.0
        if scene.type == "courbe":
            return 0.6 + TRACE_COURBE + 0.8
        if scene.type in ("etapes", "correction"):
            fin = (self._debuts_etapes(scene, len(etapes))[-1] + 0.5) if etapes else 0.8
            if scene.type == "correction" and scene.extra.get("reponse"):
                fin = max(fin, self._debut_reponse(scene)) + 0.6
            return fin
        if scene.type == "exercice":
            fin_voix = self.fins_voix.get(id(scene))
            depart = fin_voix if fin_voix is not None else 0.3 + n_mots * 0.05 + 0.4
            return depart + scene.extra.get("pause", 3) + 0.3
        return 1.0

    def _debut_reponse(self, scene) -> float:
        etapes = scene.extra.get("etapes", [])
        reperes = self.reperes.get(id(scene))
        if reperes:
            return reperes[-1]
        return (self._debuts_etapes(scene, len(etapes))[-1] + INTERVALLE_ETAPES) if etapes else 0.6

    # ------------------------------------------------------------------ éléments communs
    def _badge(self, d, x, y, texte, a=1.0, centre=False):
        p = self.police("noir", 40)
        w = p.getlength(texte) + 56
        x0 = x - w / 2 if centre else x
        fond = self._fond.getpixel((int(min(max(x0, 0), self.largeur - 1)), int(min(y, self.hauteur - 1))))
        from .rendu import _melange
        d.rounded_rectangle((x0, y, x0 + w, y + 76), radius=38, fill=_melange(fond, self.c["accent"], a))
        d.text((x0 + 28, y + 12), texte, font=p, fill=_melange(fond, self.c["fond"], a))
        return y + 76

    def _titre_scene(self, d, scene, g, haut, largeur, t, ctx, hauteur_max=300, taille=88):
        if not scene.texte:
            return haut
        pt, lt, pas_t, _ = self.ajuster_riche(scene.texte, "affichage", largeur, hauteur_max, taille, 48, 1.08,
                                              ctx, majuscules=self.majuscules)
        y, _ = self.ecrire_riche(d, lt, pt, pas_t, haut, self.c["texte"], t, 0.0, centre=False, x_gauche=g)
        return y + int(pt.size * 0.35)

    def _lignes_etapes(self, d, etapes, debuts, g, y, largeur, bas, t, ctx, derniere_accent=False):
        """Étapes numérotées qui apparaissent une à une."""
        from .rendu import _melange
        n = len(etapes)
        place = (bas - y) / max(n, 1)
        taille = int(max(40, min(64, place * 0.36)))
        pastille = int(taille * 1.25)
        x_txt = g + pastille + 34
        for i, (etape, debut) in enumerate(zip(etapes, debuts)):
            a = 1.0 if t is None else _ease((t - debut) / 0.45)
            if a <= 0:
                continue
            pt, lt, pas_t, ht = self.ajuster_riche(etape, "gras", largeur - (x_txt - g), place - 24, taille,
                                                   34, 1.2, ctx)
            yy = y + i * place + (place - max(ht, pastille)) / 2
            fond = self._fond.getpixel((g, int(min(yy, self.hauteur - 1))))
            accent = derniere_accent and i == n - 1
            couleur_p = self.c["accent"]
            dx = (1 - a) * 40
            d.ellipse((g + dx, yy, g + pastille + dx, yy + pastille), fill=_melange(fond, couleur_p, a))
            pn = self.police("noir", int(pastille * 0.55))
            num = str(i + 1)
            d.text((g + dx + (pastille - pn.getlength(num)) / 2, yy + pastille * 0.18), num, font=pn,
                   fill=_melange(fond, self.c["fond"], a))
            couleur = self.c["accent"] if accent else self.c["texte"]
            self.ecrire_riche(d, lt, pt, pas_t, yy + max(0, (pastille - ht) / 2), couleur,
                              None if a >= 1 else t, debut, centre=False, x_gauche=x_txt, decalage=0.02)
        return y + n * place

    # ------------------------------------------------------------------ scènes
    def _scene_titre(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        from .rendu import _melange
        lib = LIBELLES_PEDAGOGIE[self.langue]
        numero = scene.extra.get("numero")
        pt, lt, pas_t, ht = self.ajuster_riche(scene.texte, "affichage", largeur, (bas - haut) // 2, 150, 70,
                                               1.05, ctx, majuscules=self.majuscules)
        hn = 0
        if numero:
            pn = self.police("affichage", 260)
            hn = int(pn.size * 1.05) + 40
        y = haut + (bas - haut - ht - hn - 60) // 2
        if numero:
            a = 1.0 if t is None else _ease(t / 0.5)
            fond = self._fond.getpixel((g, int(y)))
            pl = self.police("noir", 38)
            d.text((g, y), lib["chapitre"], font=pl,
                   fill=_melange(fond, self.c["secondaire"], a))
            d.text((g, y + 50 + (1 - a) * 30), numero, font=pn, fill=_melange(fond, self.c["accent"], a))
            y += hn
        s = 1.0 if t is None else _ease((t - 0.2) / 0.6)
        d.rectangle((g, y, g + 160 * s, y + 14), fill=self.c["accent"])
        self.ecrire_riche(d, lt, pt, pas_t, y + 50, self.c["texte"], t, 0.3, centre=False, x_gauche=g)

    def _scene_formule(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        """Une ou plusieurs lignes de formule, à la même taille, qui apparaissent une à une."""
        from .formules import images_formules
        y = self._titre_scene(d, scene, g, haut, largeur, t, ctx, hauteur_max=(bas - haut) // 3)
        lignes = scene.extra["formule"]
        try:
            ims = images_formules(lignes, self.c["texte"], largeur, max(120, bas - y - 40))
        except Exception as exc:   # signalé par le contrôle qualité (formule illisible)
            self.alertes.append(f"Formule non rendue ({ctx}) : {exc}")
            return
        if ims and ims[0].height < 60:
            self.alertes.append(f"Formule petite sur mobile ({ctx}) : la couper en plusieurs lignes")
        ecart = 40
        total = sum(im.height for im in ims) + ecart * (len(ims) - 1)
        yy = y + (bas - y - total) / 2
        debuts = self._debuts_etapes(scene, len(ims), depart=0.5) if len(ims) > 1 else [0.5]
        for im, debut in zip(ims, debuts):
            a = 1.0 if t is None else _ease((t - debut) / 0.7)
            if a > 0:
                if a < 1:
                    im = im.copy()
                    im.putalpha(im.getchannel("A").point(lambda v, a=a: round(v * a)))
                self._image.paste(im, (int(x_c - im.width / 2), int(yy + (1 - a) * 30)), im)
            yy += im.height + ecart

    def _scene_etapes(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        y = self._titre_scene(d, scene, g, haut, largeur, t, ctx)
        etapes = scene.extra.get("etapes", [])
        self._lignes_etapes(d, etapes, self._debuts_etapes(scene, len(etapes)), g, y + 20, largeur, bas, t, ctx,
                            derniere_accent=bool(scene.extra.get("derniere_en_valeur", False)))

    def _scene_exercice(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        from .rendu import _melange
        lib = LIBELLES_PEDAGOGIE[self.langue]
        a = 1.0 if t is None else _ease(t / 0.4)
        y = self._badge(d, g, haut, scene.extra.get("etiquette") or lib["exercice"], a) + 60
        anneau = 220
        pq, lq, pas_q, hq = self.ajuster_riche(scene.texte, "gras", largeur, bas - y - anneau - 80, 86, 44, 1.2, ctx)
        self.ecrire_riche(d, lq, pq, pas_q, y, self.c["texte"], t, 0.3, centre=False, x_gauche=g, decalage=0.05)
        # Compte à rebours : temps de réflexion après la question.
        pause = scene.extra.get("pause", 3)
        if pause <= 0:
            return
        fin_voix = self.fins_voix.get(id(scene))
        depart = fin_voix if fin_voix is not None else 0.3 + len(scene.texte.split()) * 0.05 + 0.4
        if t is not None and t < depart:
            return
        ecoule = pause if t is None else min(pause, t - depart)
        reste = max(0.0, 1 - ecoule / pause)
        cy = bas - anneau / 2 - 20
        boite = (x_c - anneau / 2, cy - anneau / 2, x_c + anneau / 2, cy + anneau / 2)
        d.ellipse(boite, outline=self.c["barre"], width=14)
        if reste > 0:
            d.arc(boite, -90, -90 + 360 * reste, fill=self.c["accent"], width=14)
        pn = self.police("affichage", 110)
        num = str(math.ceil(pause - ecoule)) if reste > 0 else "?"
        d.text((x_c - pn.getlength(num) / 2, cy - pn.size * 0.62), num, font=pn, fill=self.c["texte"])

    def _scene_correction(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        from .rendu import _melange
        lib = LIBELLES_PEDAGOGIE[self.langue]
        a = 1.0 if t is None else _ease(t / 0.4)
        y = self._badge(d, g, haut, lib["correction"], a) + 50
        if scene.texte:
            pt, lt, pas_t, ht = self.ajuster_riche(scene.texte, "gras", largeur, 260, 70, 40, 1.2, ctx)
            y, _ = self.ecrire_riche(d, lt, pt, pas_t, y, self.c["texte"], t, 0.2, centre=False, x_gauche=g,
                                     decalage=0.04)
            y += 30
        etapes = scene.extra.get("etapes", [])
        reponse = scene.extra.get("reponse")
        bas_etapes = bas - (260 if reponse else 0)
        if etapes:
            self._lignes_etapes(d, etapes, self._debuts_etapes(scene, len(etapes)), g, y, largeur, bas_etapes, t, ctx)
        if reponse:
            debut = self._debut_reponse(scene)
            k = 1.0 if t is None else _ease((t - debut) / 0.5)
            if k <= 0:
                return
            pr, lr, pas_r, hr = self.ajuster_riche(reponse, "affichage", largeur - 80, 260, 130, 56, 1.05, ctx)
            yb = bas - hr - 80 if etapes else y + (bas - y - hr - 60) / 2 - 60
            fond = self._fond.getpixel((g, int(yb)))
            d.rounded_rectangle((g, yb, dr, yb + hr + pr.size * 0.25 + 60), radius=28,
                                fill=_melange(fond, self.c["accent"], k))
            self.ecrire_riche(d, lr, pr, pas_r, yb + 30, _melange(fond, self.c["fond"], k), None, 0,
                              centre=True)

    def _scene_courbe(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        from .rendu import _melange
        c = scene.extra["courbe"]
        pts = c["_points"]
        y = self._titre_scene(d, scene, g, haut, largeur, t, ctx, hauteur_max=280, taille=80)
        pourcent = c.get("format_y") == "pourcent"
        p_axe = self.police("regulier", 32)
        p_lbl = self.police("gras", 34)

        def fmt_y(v):
            return (formater_nombre(v * 100, self.langue, 0) + (" %" if self.langue == "fr" else "%")) if pourcent \
                else formater_nombre(v, self.langue, c.get("decimales_y"))

        ymin = c.get("y_min", 0.0)
        ymax = c.get("y_max", max(v for _, v in pts) or 1.0)
        xmin, xmax = pts[0][0], pts[-1][0]
        gauche = g + int(max(p_axe.getlength(fmt_y(ymax)), p_axe.getlength(fmt_y(ymin)))) + 24
        droite = dr - 20
        haut_g = y + 40
        bas_g = bas - 110
        if c.get("axe_y"):
            self._ecrire_gauche(d, g, y - 10, [typographie(c["axe_y"], self.langue)], p_axe, 40, self.c["secondaire"],
                                1.0 if t is None else _ease(t / 0.4))
            haut_g += 30

        def X(v):
            return gauche + (v - xmin) / ((xmax - xmin) or 1) * (droite - gauche)

        def Y(v):
            return bas_g - (v - ymin) / ((ymax - ymin) or 1) * (bas_g - haut_g)

        a_axes = 1.0 if t is None else _ease(t / 0.5)
        fond = self._fond.getpixel((g, int(bas_g)))
        grille = _melange(fond, self.c["secondaire"], 0.35 * a_axes)
        for k in range(5):
            v = ymin + (ymax - ymin) * k / 4
            yy = Y(v)
            d.line((gauche, yy, droite, yy), fill=grille, width=2)
            lbl = fmt_y(v)
            d.text((gauche - 18 - p_axe.getlength(lbl), yy - p_axe.size * 0.6), lbl, font=p_axe,
                   fill=_melange(fond, self.c["secondaire"], a_axes))
        pas_x = next(p for p in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000, 10 ** 9)
                     if (xmax - xmin) / p <= 6)
        v = math.ceil(xmin / pas_x) * pas_x
        while v <= xmax + 1e-9:
            lbl = formater_nombre(v, self.langue, 0)
            d.text((X(v) - p_axe.getlength(lbl) / 2, bas_g + 16), lbl, font=p_axe,
                   fill=_melange(fond, self.c["secondaire"], a_axes))
            v += pas_x
        if c.get("axe_x"):
            lbl = typographie(c["axe_x"], self.langue)
            d.text((droite - p_axe.getlength(lbl), bas_g + 60), lbl, font=p_axe,
                   fill=_melange(fond, self.c["secondaire"], a_axes))
        # Courbe tracée progressivement.
        k = 1.0 if t is None else _ease((t - 0.6) / TRACE_COURBE)
        if k <= 0:
            return
        x_lim = xmin + (xmax - xmin) * k
        trace = [(X(x), Y(v)) for x, v in pts if x <= x_lim + 1e-9]
        if len(trace) >= 2:
            d.line(trace, fill=self.c["accent"], width=9, joint="curve")
        # Repères : point, pointillés, étiquette (quand la courbe les atteint).
        for rep in c.get("reperes", []):
            xr = rep["x"]
            if xr > x_lim + 1e-9:
                continue
            yr = rep.get("y")
            if yr is None:
                yr = min(pts, key=lambda p: abs(p[0] - xr))[1]
            px, py = X(xr), Y(yr)
            for yy in range(int(py), int(bas_g), 22):
                d.line((px, yy, px, min(yy + 11, bas_g)), fill=self.c["texte"], width=3)
            d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=self.c["texte"], outline=self.c["accent"], width=5)
            lbl = typographie(rep.get("label") or fmt_y(yr), self.langue)
            lx = px + 26 if px + 26 + p_lbl.getlength(lbl) <= droite else px - 26 - p_lbl.getlength(lbl)
            d.text((lx, py - p_lbl.size * 1.5), lbl, font=p_lbl, fill=self.c["texte"])
