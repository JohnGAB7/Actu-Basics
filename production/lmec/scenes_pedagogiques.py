"""Scènes des fiches pédagogiques : titre de chapitre, formule, étapes, courbe, animation, exercice, correction.

Mêmes couleurs, polices et animations que les scènes d'actualité (charte.yaml) : seule la mise en page
change. Les étapes apparaissent quand la voix les annonce (repères de phrases fournis après la
narration), sinon à intervalle régulier.

Deux dispositions :
- vertical (video, carrousel) : titre en haut, contenu centré dessous, blocs aérés ;
- leçon 16:9 (lecon) : deux colonnes, titre à gauche, contenu (formule, étapes, courbe…) à droite.
"""
from __future__ import annotations

import math

from .animations import Animations
from .formatage import formater_nombre, typographie

LIBELLES_PEDAGOGIE = {
    "fr": {"exercice": "À VOUS", "correction": "CORRECTION", "chapitre": "CHAPITRE", "paires": "paires"},
    "en": {"exercice": "YOUR TURN", "correction": "ANSWER", "chapitre": "CHAPTER", "paires": "pairs"},
}
INTERVALLE_ETAPES = 1.1     # s entre deux étapes sans repères de voix
TRACE_COURBE = 2.2          # s pour tracer la courbe


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


class ScenesPedagogiques(Animations):
    """Mélangé à Rendu : utilise ses polices, couleurs, zone et fonctions d'écriture."""

    TYPES_PEDAGOGIQUES = ("titre", "formule", "etapes", "courbe", "animation", "exercice", "correction")

    # ------------------------------------------------------------------ disposition
    @property
    def colonnes(self) -> bool:
        return self.format == "lecon"

    def _zones(self, g, haut, dr, bas):
        """(zone du titre, zone du contenu) : empilées en vertical, côte à côte en 16:9."""
        if self.colonnes:
            l = dr - g
            return (g, haut, g + int(l * 0.36), bas), (g + int(l * 0.42), haut, dr, bas)
        return (g, haut, dr, bas), (g, haut, dr, bas)

    # ------------------------------------------------------------------ temps
    def _debuts_etapes(self, scene, n: int, depart: float = 0.6) -> list[float]:
        """Instant d'apparition de chaque étape : sur les phrases de la voix si elles sont connues.
        Correction avec réponse : la dernière phrase annonce la réponse, les étapes prennent les précédentes."""
        reperes = self.reperes.get(id(scene))
        if reperes and n and scene.type == "correction" and scene.extra.get("reponse") and len(reperes) > n:
            return reperes[:n]
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
            reperes = scene.extra["courbe"].get("reperes", [])
            fin_reperes = (self._debuts_etapes(scene, len(reperes))[-1] + 0.6) \
                if reperes and self.reperes.get(id(scene)) else 0
            return max(0.6 + TRACE_COURBE + 0.8, fin_reperes)
        if scene.type == "animation":
            return self.duree_animation_modele(scene)
        if scene.type == "etapes" and scene.extra.get("disposition") == "cartes":
            return self._debuts_etapes(scene, len(etapes))[-1] + 0.8
        if scene.type in ("etapes", "correction"):
            fin = (self._debuts_etapes(scene, len(etapes))[-1] + 0.5) if etapes else 0.8
            if scene.type == "correction" and scene.extra.get("reponse"):
                fin = max(fin, self._debut_reponse(scene)) + 0.6
            return fin
        if scene.type == "exercice":
            return self._debut_compte(scene) + scene.extra.get("pause", 3) + 0.3
        return 1.0

    def _debut_compte(self, scene) -> float:
        fin_voix = self.fins_voix.get(id(scene))
        return fin_voix if fin_voix is not None else 0.3 + len(scene.texte.split()) * 0.05 + 0.4

    def _debut_reponse(self, scene) -> float:
        etapes = scene.extra.get("etapes", [])
        reperes = self.reperes.get(id(scene))
        if reperes:
            return reperes[-1]
        return (self._debuts_etapes(scene, len(etapes))[-1] + INTERVALLE_ETAPES) if etapes else 0.6

    def reperes_sonores(self, scenes, durees) -> list[tuple[float, str]]:
        """Instants (secondes depuis le début de la vidéo) des repères sonores : un tic par seconde
        du compte à rebours, un carillon quand un chiffre s'arrête ou qu'une réponse apparaît."""
        reperes, debut = [], 0.0
        for scene, duree in zip(scenes, durees):
            if scene.type == "exercice" and scene.extra.get("pause", 3) > 0:
                depart = self._debut_compte(scene)
                reperes += [(debut + depart + k, "tic") for k in range(int(scene.extra.get("pause", 3)))]
            elif scene.type == "chiffre":
                reperes.append((debut + 1.2, "revele"))
            elif scene.type == "correction" and scene.extra.get("reponse"):
                reperes.append((debut + self._debut_reponse(scene), "revele"))
            debut += duree
        return [(t, n) for t, n in reperes if t < debut]

    # ------------------------------------------------------------------ éléments communs
    def _badge(self, d, x, y, texte, a=1.0):
        from .rendu import _melange
        p = self.police("noir", 40)
        w = p.getlength(texte) + 56
        fond = self._fond.getpixel((int(min(max(x, 0), self.largeur - 1)), int(min(y, self.hauteur - 1))))
        d.rounded_rectangle((x, y, x + w, y + 76), radius=38, fill=_melange(fond, self.c["accent"], a))
        d.text((x + 28, y + 12), texte, font=p, fill=_melange(fond, self.c["fond"], a))
        return y + 76

    def _mesurer_titre(self, texte, largeur, hauteur_max, taille, ctx):
        return self.ajuster_riche(texte, "affichage", largeur, hauteur_max, taille, 48, 1.08, ctx,
                                  majuscules=self.majuscules, equilibre=True)

    def _titre_scene(self, d, scene, zone, t, ctx, hauteur_max=300, taille=92):
        """Titre de la scène. En 16:9, centré verticalement dans la colonne de gauche. Retourne le bas du titre."""
        g, haut, dr, bas = zone
        if not scene.texte:
            return haut
        pt, lt, pas_t, ht = self._mesurer_titre(scene.texte, dr - g, hauteur_max if not self.colonnes else bas - haut,
                                                taille if not self.colonnes else 110, ctx)
        y0 = haut if not self.colonnes else haut + (bas - haut - ht) // 2
        y, _ = self.ecrire_riche(d, lt, pt, pas_t, y0, self.c["texte"], t, 0.0, centre=False, x_gauche=g)
        if self.colonnes:   # filet d'accent sous le titre, rappel de la carte de chapitre
            s = 1.0 if t is None else _ease((t - 0.2) / 0.6)
            d.rectangle((g, y + 20, g + 120 * s, y + 30), fill=self.c["accent"])
        return y + int(pt.size * 0.45)

    def _mesurer_etapes(self, etapes, largeur, hauteur, ctx):
        """Taille commune, hauteur de chaque ligne, hauteur totale (lignes aérées, jamais étirées)."""
        n = max(len(etapes), 1)
        taille = int(max(40, min(66, hauteur / n * 0.34)))
        # Une étape tient de préférence sur une ligne : on accepte de réduire jusqu'à 75 % pour cela.
        largeur_txt = largeur - int(taille * 1.25) - 34
        bruts = [typographie(e.replace("*", ""), self.langue) for e in etapes]
        for essai in range(taille, int(taille * 0.75) - 1, -2):
            pe = self.police("gras", essai)
            if all(pe.getlength(b) <= largeur_txt for b in bruts):
                taille = essai
                break
        pastille = int(taille * 1.25)
        mesures = []
        for e in etapes:
            pt, lt, pas_t, ht = self.ajuster_riche(e, "gras", largeur - pastille - 34, hauteur / n, taille, 34, 1.2, ctx)
            mesures.append((pt, lt, pas_t, ht))
        hauteurs = [max(ht, pastille) for *_, ht in mesures]
        ecart = int(taille * 0.9)
        return mesures, hauteurs, pastille, sum(hauteurs) + ecart * (n - 1), ecart

    def _lignes_etapes(self, d, etapes, debuts, g, y, largeur, hauteur, t, ctx, derniere_accent=False,
                       mesure=None):
        """Étapes numérotées qui apparaissent une à une, bloc centré dans la hauteur donnée.
        Retourne le bas de la dernière étape. `mesure` : résultat de _mesurer_etapes déjà calculé."""
        from .rendu import _melange
        mesures, hauteurs, pastille, total, ecart = mesure or self._mesurer_etapes(etapes, largeur, hauteur, ctx)
        yy = y + max(0, (hauteur - total) / 2)
        x_txt = g + pastille + 34
        for i, ((pt, lt, pas_t, ht), h, debut) in enumerate(zip(mesures, hauteurs, debuts)):
            a = 1.0 if t is None else _ease((t - debut) / 0.45)
            if a > 0:
                fond = self._fond.getpixel((g, int(min(yy, self.hauteur - 1))))
                dx = (1 - a) * 40
                d.ellipse((g + dx, yy, g + pastille + dx, yy + pastille), fill=_melange(fond, self.c["accent"], a))
                pn = self.police("noir", int(pastille * 0.55))
                num = str(i + 1)
                d.text((g + dx + (pastille - pn.getlength(num)) / 2, yy + pastille * 0.18), num, font=pn,
                       fill=_melange(fond, self.c["fond"], a))
                couleur = self.c["accent"] if derniere_accent and i == len(etapes) - 1 else self.c["texte"]
                self.ecrire_riche(d, lt, pt, pas_t, yy + max(0, (pastille - ht) / 2), couleur,
                                  None if a >= 1 else t, debut, centre=False, x_gauche=x_txt, decalage=0.02)
            yy += h + ecart
        return yy - ecart

    def _cartes(self, d, etapes, debuts, zone, t, ctx):
        """Étapes en cartes (grille de deux colonnes) : chaque idée a sa place, sans bloc de texte dense."""
        from .rendu import _melange
        g, haut, dr, bas = zone
        n = len(etapes)
        cols = 2 if n > 1 else 1
        rangs = math.ceil(n / cols)
        ecart = 36
        lc = (dr - g - ecart * (cols - 1)) / cols
        hc = min((bas - haut - ecart * (rangs - 1)) / rangs, lc * 0.9 if not self.colonnes else lc * 0.62)
        y0 = haut + (bas - haut - (hc * rangs + ecart * (rangs - 1))) / 2
        pn = self.police("affichage", 96 if not self.colonnes else 84)

        def _zone(i, x, y):
            if self.colonnes:   # 16:9 : cartes basses, numéro à gauche du texte pour lui laisser la hauteur
                return (x + 34 + d.textlength(str(i + 1), font=pn) + 30, y + 26, x + lc - 30, y + hc - 26)
            return (x + 34, y + 56 + pn.size, x + lc - 34, y + hc - 26)

        # Même taille de texte sur toutes les cartes : la plus grande qui convient à la plus longue.
        commune = 58
        for i, texte in enumerate(etapes):
            z = _zone(i, 0, 0)
            commune = min(commune, self.ajuster_riche(texte, "gras", z[2] - z[0], z[3] - z[1], 58, 36, 1.15, ctx)[0].size)
        for i, (texte, debut) in enumerate(zip(etapes, debuts)):
            a = 1.0 if t is None else _ease((t - debut) / 0.45)
            if a <= 0:
                continue
            c, l = i % cols, i // cols
            x = g + c * (lc + ecart)
            y = y0 + l * (hc + ecart) + (1 - a) * 30
            fond = self._fond.getpixel((int(x + 5), int(min(y + 5, self.hauteur - 1))))
            d.rounded_rectangle((x, y, x + lc, y + hc), radius=28, fill=_melange(fond, self.c["barre"], 0.35 * a),
                                outline=_melange(fond, self.c["accent"], a), width=4)
            num = str(i + 1)
            pos_num = (x + 34, y + (hc - pn.size) / 2 - 8) if self.colonnes else (x + 34, y + 22)
            d.text(pos_num, num, font=pn, fill=_melange(fond, self.c["accent"], a))
            zone_txt = _zone(i, x, y)
            pt, lt, pas_t, ht = self.ajuster_riche(texte, "gras", zone_txt[2] - zone_txt[0],
                                                   zone_txt[3] - zone_txt[1], commune, 36, 1.15, ctx)
            y_txt = zone_txt[1] + (max(0, zone_txt[3] - zone_txt[1] - ht) / 2 if self.colonnes else 0)
            self.ecrire_riche(d, lt, pt, pas_t, y_txt, self.c["texte"], None if a >= 1 else t, debut,
                              centre=False, x_gauche=zone_txt[0], decalage=0.02)

    # ------------------------------------------------------------------ scènes
    def _scene_titre(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        from .rendu import _melange
        lib = LIBELLES_PEDAGOGIE[self.langue]
        numero = scene.extra.get("numero")
        a = 1.0 if t is None else _ease(t / 0.5)
        pn = self.police("affichage", 300 if not self.colonnes else 420)
        pl = self.police("noir", 38)
        if self.colonnes and numero:   # numéro géant à gauche, titre à droite
            (gg, hh, dg, bg), (gc, hc, dc, bc) = self._zones(g, haut, dr, bas)
            fond = self._fond.getpixel((gg, int(hh)))
            yn = hh + (bg - hh - pn.size) // 2
            d.text((gg, yn - 40), lib["chapitre"], font=pl, fill=_melange(fond, self.c["secondaire"], a))
            d.text((gg, yn + (1 - a) * 30), numero, font=pn, fill=_melange(fond, self.c["accent"], a))
            pt, lt, pas_t, ht = self._mesurer_titre(scene.texte, dc - gc, bc - hc, 140, ctx)
            y = hc + (bc - hc - ht) // 2
            s = 1.0 if t is None else _ease((t - 0.2) / 0.6)
            d.rectangle((gc, y - 50, gc + 160 * s, y - 36), fill=self.c["accent"])
            self.ecrire_riche(d, lt, pt, pas_t, y, self.c["texte"], t, 0.3, centre=False, x_gauche=gc)
            return
        pt, lt, pas_t, ht = self._mesurer_titre(scene.texte, largeur, (bas - haut) // 2, 150, ctx)
        # Hauteur réelle du numéro (bas du glyphe), pas la taille nominale de la police : sinon la
        # barre d'accent mordait sur le bas du grand chiffre.
        bas_numero = d.textbbox((0, 0), numero, font=pn)[3] if numero else 0
        hn = 50 + bas_numero + 48 if numero else 0
        y = haut + (bas - haut - ht - hn - 64) // 2
        if numero:
            fond = self._fond.getpixel((g, int(y)))
            d.text((g, y), lib["chapitre"], font=pl, fill=_melange(fond, self.c["secondaire"], a))
            d.text((g, y + 50 + (1 - a) * 30), numero, font=pn, fill=_melange(fond, self.c["accent"], a))
            y += hn
        s = 1.0 if t is None else _ease((t - 0.2) / 0.6)
        d.rectangle((g, y, g + 160 * s, y + 14), fill=self.c["accent"])
        self.ecrire_riche(d, lt, pt, pas_t, y + 50, self.c["texte"], t, 0.3, centre=False, x_gauche=g)

    def _scene_formule(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        """Lignes de formule à la même taille, qui apparaissent une à une ; le résultat en couleur d'accent."""
        from .formules import images_formules
        zt, zc = self._zones(g, haut, dr, bas)
        y = self._titre_scene(d, scene, zt, t, ctx, hauteur_max=(bas - haut) // 4)
        haut_c = zc[1] if self.colonnes else y + 30
        lignes = scene.extra["formule"]
        resultat = scene.extra.get("resultat_en_valeur", len(lignes) > 1)
        ecart = 56
        # Les images de formule ne dépendent pas du temps : calculées une fois par scène et réutilisées
        # pour chaque image de la vidéo. Sans ce cache, chaque image recalculait le rendu mathtext
        # (environ 4,5 s par image), soit plus d'une heure et demie pour les deux formules longues.
        cle = (tuple(lignes), resultat, zc[2] - zc[0], max(120, bas - haut_c - 40), ecart,
               self.c["texte"], self.c["accent"])
        cache = self.__dict__.setdefault("_cache_formules", {})
        if cle not in cache:
            try:
                ims = images_formules(lignes, self.c["texte"], zc[2] - zc[0], max(120, bas - haut_c - 40),
                                      interligne=ecart, taille_max=150)
                if resultat:
                    ims[-1] = self._formule_couleur(lignes, ims, zc[2] - zc[0], max(120, bas - haut_c - 40), ecart)
                cache[cle] = ims
            except Exception as exc:   # signalé par le contrôle qualité (formule illisible)
                cache[cle] = exc
        if isinstance(cache[cle], Exception):
            self.alertes.append(f"Formule non rendue ({ctx}) : {cache[cle]}")
            return
        ims = list(cache[cle])
        if ims and min(im.height for im in ims) < 70 and not self.colonnes:
            self.alertes.append(f"Formule petite sur mobile ({ctx}) : la couper en plusieurs lignes")
        total = sum(im.height for im in ims) + ecart * (len(ims) - 1)
        yy = haut_c + (bas - haut_c - total) / 2
        x_centre = (zc[0] + zc[2]) / 2
        debuts = self._debuts_etapes(scene, len(ims), depart=0.5) if len(ims) > 1 else [0.5]
        for im, debut in zip(ims, debuts):
            a = 1.0 if t is None else _ease((t - debut) / 0.7)
            if a > 0:
                if a < 1:
                    im = im.copy()
                    im.putalpha(im.getchannel("A").point(lambda v, a=a: round(v * a)))
                self._image.paste(im, (int(x_centre - im.width / 2), int(yy + (1 - a) * 30)), im)
            yy += im.height + ecart

    def _formule_couleur(self, lignes, ims, largeur, hauteur, ecart):
        """Dernière ligne (le résultat) en couleur d'accent, à la même taille que les autres."""
        from .formules import images_formules
        taille = 150
        while True:
            essai = images_formules(lignes, self.c["texte"], largeur, hauteur, interligne=ecart,
                                    taille_max=taille, taille_min=taille)
            if [im.size for im in essai] == [im.size for im in ims] or taille <= 28:
                break
            taille -= 4
        return images_formules([lignes[-1]], self.c["accent"], largeur, 10_000, taille_max=taille,
                               taille_min=taille)[0]

    def _scene_etapes(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        zt, zc = self._zones(g, haut, dr, bas)
        y = self._titre_scene(d, scene, zt, t, ctx)
        haut_c = zc[1] if self.colonnes else y + 20
        etapes = scene.extra.get("etapes", [])
        if scene.extra.get("disposition") == "cartes":
            return self._cartes(d, etapes, self._debuts_etapes(scene, len(etapes)), (zc[0], haut_c, zc[2], bas), t, ctx)
        self._lignes_etapes(d, etapes, self._debuts_etapes(scene, len(etapes)), zc[0], haut_c, zc[2] - zc[0],
                            bas - haut_c, t, ctx, derniere_accent=bool(scene.extra.get("derniere_en_valeur", False)))

    def _scene_exercice(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        lib = LIBELLES_PEDAGOGIE[self.langue]
        a = 1.0 if t is None else _ease(t / 0.4)
        zt, zc = self._zones(g, haut, dr, bas)
        anneau = 240 if not self.colonnes else 340
        if self.colonnes:   # 16:9 : la question prend les deux tiers de la largeur, le compte à rebours le reste
            l = dr - g
            zt, zc = (g, haut, g + int(l * 0.64), bas), (g + int(l * 0.70), haut, dr, bas)
        pq, lq, pas_q, hq = self.ajuster_riche(scene.texte, "gras", zt[2] - zt[0],
                                               (bas - haut - 140 - (anneau + 120 if not self.colonnes else 0)),
                                               92 if not self.colonnes else 84, 44, 1.2, ctx, equilibre=True)
        bloc = 76 + 50 + hq
        y0 = haut + (bas - haut - bloc - (anneau + 100 if not self.colonnes else 0)) // 2
        y = self._badge(d, zt[0], y0, scene.extra.get("etiquette") or lib["exercice"], a) + 50
        self.ecrire_riche(d, lq, pq, pas_q, y, self.c["texte"], t, 0.3, centre=False, x_gauche=zt[0], decalage=0.05)
        # Compte à rebours : temps de réflexion après la question.
        pause = scene.extra.get("pause", 3)
        if pause <= 0:
            return
        depart = self._debut_compte(scene)
        if t is not None and t < depart:
            return
        ecoule = pause if t is None else min(pause, t - depart)
        reste = max(0.0, 1 - ecoule / pause)
        if self.colonnes:
            cx, cy = (zc[0] + zc[2]) / 2, (haut + bas) / 2
        else:
            cx, cy = x_c, y + hq + 100 + anneau / 2
        boite = (cx - anneau / 2, cy - anneau / 2, cx + anneau / 2, cy + anneau / 2)
        epaisseur = 16 if not self.colonnes else 24
        d.ellipse(boite, outline=self.c["barre"], width=epaisseur)
        if reste > 0:
            d.arc(boite, -90, -90 + 360 * reste, fill=self.c["accent"], width=epaisseur)
        pn = self.police("affichage", int(anneau * 0.5))
        num = str(math.ceil(pause - ecoule)) if reste > 0 else "?"
        d.text((cx - pn.getlength(num) / 2, cy - pn.size * 0.62), num, font=pn, fill=self.c["texte"])

    def _scene_correction(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        """Badge, phrase d'introduction, étapes, puis la réponse dans un encadré mesuré sur son texte."""
        from .rendu import _melange
        lib = LIBELLES_PEDAGOGIE[self.langue]
        a = 1.0 if t is None else _ease(t / 0.4)
        # Une seule colonne, aussi en 16:9 (centrée) : les étapes ont besoin de largeur.
        marge = int((dr - g) * 0.18) if self.colonnes else 0
        zone = (g + marge, haut, dr - marge, bas)
        etapes = scene.extra.get("etapes", [])
        reponse = scene.extra.get("reponse")
        # Mesures, pour centrer l'ensemble verticalement (respiration au-dessus et au-dessous).
        intro = self.ajuster_riche(scene.texte, "gras", zone[2] - zone[0], 260, 76, 40, 1.2, ctx) \
            if scene.texte else None
        l_rep = zone[2] - zone[0]
        rep = self.ajuster_riche(reponse, "affichage", l_rep - 100, 210, 150, 60, 1.05, ctx, equilibre=True) \
            if reponse else None
        h_rep = 0
        if rep:
            pr, lr, pas_r, hr = rep
            marge_v = int(pr.size * 0.32)
            h_rep = hr + 2 * marge_v
        h_etapes, m_etapes = 0, None
        if etapes:
            m_etapes = self._mesurer_etapes(etapes, zone[2] - zone[0], (bas - haut) * 0.45, ctx)
            h_etapes = m_etapes[3]
        h_intro = intro[3] + 40 if intro else 0
        bloc = 76 + 50 + h_intro + h_etapes + (70 if etapes and rep else 0) + h_rep
        y = haut + max(0, (bas - haut - bloc) // 2)
        y = self._badge(d, zone[0], y, lib["correction"], a) + 50
        if intro:
            pt, lt, pas_t, ht = intro
            y, _ = self.ecrire_riche(d, lt, pt, pas_t, y, self.c["texte"], t, 0.2, centre=False, x_gauche=zone[0],
                                     decalage=0.04)
            y += 40
        if etapes:
            y = self._lignes_etapes(d, etapes, self._debuts_etapes(scene, len(etapes)), zone[0], y,
                                    zone[2] - zone[0], h_etapes, t, ctx, mesure=m_etapes) + 70
        if rep:
            debut = self._debut_reponse(scene)
            k = 1.0 if t is None else _ease((t - debut) / 0.5)
            if k <= 0:
                return
            yb = y
            x0, x1 = zone[0], zone[2]
            echelle = 0.92 + 0.08 * k            # l'encadré « se pose » légèrement
            cxr, cyr = (x0 + x1) / 2, yb + h_rep / 2
            boite = (cxr - (x1 - x0) / 2 * echelle, cyr - h_rep / 2 * echelle,
                     cxr + (x1 - x0) / 2 * echelle, cyr + h_rep / 2 * echelle)
            fond = self._fond.getpixel((int(x0), int(min(yb, self.hauteur - 1))))
            d.rounded_rectangle(boite, radius=32, fill=_melange(fond, self.c["accent"], k))
            # Texte centré dans l'encadré, d'après sa boîte d'encre réelle.
            y_txt = cyr - hr / 2 - (pr.getbbox("Hg")[1]) / 2
            for ligne in lr:
                lg = self._largeur_ligne(ligne, pr)
                x = cxr - lg / 2
                for j, (mot, _, colle) in enumerate(ligne):
                    if colle and j:
                        x -= pr.getlength(" ")
                    d.text((x, y_txt), mot, font=pr, fill=_melange(fond, self.c["fond"], k))
                    x += pr.getlength(mot) + pr.getlength(" ")
                y_txt += pas_r

    def _scene_courbe(self, d, scene, g, haut, dr, bas, largeur, x_c, t, ctx):
        from .rendu import _melange
        c = scene.extra["courbe"]
        pts = c["_points"]
        zt, zc = self._zones(g, haut, dr, bas)
        y = self._titre_scene(d, scene, zt, t, ctx, hauteur_max=300, taille=84)
        g, dr = zc[0], zc[2]
        haut_c = zc[1] if self.colonnes else y
        pourcent = c.get("format_y") == "pourcent"
        p_axe = self.police("regulier", 34 if not self.colonnes else 30)
        p_lbl = self.police("noir", 42 if not self.colonnes else 38)

        def fmt_y(v):
            return (formater_nombre(v * 100, self.langue, 0) + (" %" if self.langue == "fr" else "%")) if pourcent \
                else formater_nombre(v, self.langue, c.get("decimales_y"))

        ymin = c.get("y_min", 0.0)
        ymax = c.get("y_max", max(v for _, v in pts) or 1.0)
        style = c.get("style", "ligne")
        # Barres : une par catégorie, centrée sur son rang (0, 1, 2…), étiquetée par « etiquettes ».
        # Histogramme : chaque point est [début de classe, hauteur] ; une classe s'arrête au début de la
        # suivante, la dernière a la largeur « largeur_classe » (par défaut celle de l'avant-dernière).
        # Classes contiguës, éventuellement inégales : la surface compte, donc aucune espace entre les barres.
        if style in ("barres", "boites"):
            xmin, xmax = -0.5, len(pts) - 0.5
        elif style == "histogramme":
            lc = float(c.get("largeur_classe") or ((pts[-1][0] - pts[-2][0]) if len(pts) > 1 else 1.0))
            bornes = [x for x, _ in pts] + [pts[-1][0] + lc]
            xmin, xmax = bornes[0], bornes[-1]
        else:   # « x_min » / « x_max » : cadrage d'un nuage de points qui ne commence pas à son premier point
            xmin, xmax = float(c.get("x_min", pts[0][0])), float(c.get("x_max", pts[-1][0]))
        gauche = g + int(max(p_axe.getlength(fmt_y(ymax)), p_axe.getlength(fmt_y(ymin)))) + 24
        droite = dr - 20
        # « serie_2 » : seconde courbe avec son propre axe vertical, à droite (double échelle, S1.09).
        s2 = c.get("serie_2")
        if s2:
            pts2 = [(float(x), float(v)) for x, v in s2["points"]]
            y2min = float(s2.get("y_min", 0.0))
            y2max = float(s2.get("y_max", max(v for _, v in pts2) or 1.0))

            def fmt_y2(v):
                return formater_nombre(v, self.langue, s2.get("decimales_y"))
            droite = dr - 20 - int(max(p_axe.getlength(fmt_y2(y2max)), p_axe.getlength(fmt_y2(y2min)))) - 24
        haut_g = haut_c + 80
        bas_g = bas - 120
        if not self.colonnes:   # graphique carré et centré : plus lisible qu'un graphique étiré
            h_max = (droite - gauche) * 1.05
            if bas_g - haut_g > h_max:
                marge = (bas_g - haut_g - h_max) / 2
                haut_g, bas_g = haut_g + marge, bas_g - marge

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
            if s2:
                lbl2 = fmt_y2(y2min + (y2max - y2min) * k / 4)
                d.text((droite + 18, yy - p_axe.size * 0.6), lbl2, font=p_axe,
                       fill=_melange(fond, self.c["texte"], a_axes))
        pas_x = next(p for p in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000, 10 ** 9)
                     if (xmax - xmin) / p <= 6)
        if style in ("barres", "boites"):   # étiquette de catégorie sous chaque barre, sur deux lignes au plus
            etiq = c.get("etiquettes") or [formater_nombre(x, self.langue, None) for x, _ in pts]
            l_cat = (droite - gauche) / len(pts) - 8
            for n_b, lbl in enumerate(etiq):
                lignes = self._couper(typographie(str(lbl), self.langue), p_axe, l_cat)[:2]
                for n_l, ligne in enumerate(lignes):
                    d.text((X(n_b) - p_axe.getlength(ligne) / 2, bas_g + 16 + n_l * (p_axe.size + 6)), ligne,
                           font=p_axe, fill=_melange(fond, self.c["secondaire"], a_axes))
            pas_x = None
        elif style == "histogramme" and len(bornes) <= 9:   # graduations aux bornes des classes
            # Une borne sur deux si les étiquettes se chevauchent (revenus « 1 000 », « 2 000 »… sur mobile).
            l_max = max(p_axe.getlength(formater_nombre(b, self.langue, None)) for b in bornes)
            saut = 2 if min(X(b1) - X(b0) for b0, b1 in zip(bornes, bornes[1:])) < l_max + 16 else 1
            for b in bornes[::saut]:
                lbl = formater_nombre(b, self.langue, None)
                d.text((X(b) - p_axe.getlength(lbl) / 2, bas_g + 16), lbl, font=p_axe,
                       fill=_melange(fond, self.c["secondaire"], a_axes))
            pas_x = None
        v = math.ceil(xmin / pas_x) * pas_x if pas_x else xmax + 1
        # Des années (2019, 2023) s'écrivent sans séparateur de milliers : « 2 019 » se lirait comme un nombre.
        annees = all(float(x).is_integer() and 1000 <= x <= 2999 for x, _ in pts)
        while v <= xmax + 1e-9:
            lbl = str(int(round(v))) if annees else formater_nombre(v, self.langue, 0)
            d.text((X(v) - p_axe.getlength(lbl) / 2, bas_g + 16), lbl, font=p_axe,
                   fill=_melange(fond, self.c["secondaire"], a_axes))
            v += pas_x
        if c.get("axe_x"):
            lbl = typographie(c["axe_x"], self.langue)
            d.text((droite - p_axe.getlength(lbl), bas_g + 64), lbl, font=p_axe,
                   fill=_melange(fond, self.c["secondaire"], a_axes))
        # Titre de l'axe vertical (« Hauteur (cm) ») au-dessus des graduations : l'unité se lit sur l'axe.
        if c.get("axe_y"):
            lbl = typographie(c["axe_y"], self.langue)
            d.text((g, haut_g - p_axe.size * 1.6 - 22), lbl, font=p_axe,
                   fill=_melange(fond, self.c["accent"] if s2 else self.c["secondaire"], a_axes))
        if s2 and s2.get("axe_y"):   # titre de l'axe de droite, dans la couleur de sa courbe
            lbl = typographie(s2["axe_y"], self.langue)
            d.text((dr - p_axe.getlength(lbl), haut_g - p_axe.size * 1.6 - 22), lbl, font=p_axe,
                   fill=_melange(fond, self.c["texte"], a_axes))
        # Seuils horizontaux en pointillés : « seuil » (ex. 0.9, étiqueté par sa valeur) et/ou « seuils »,
        # liste de {valeur, label} (ex. moyenne et médiane affichées ensemble). Couleurs : accent, puis texte.
        seuils = ([{"valeur": c["seuil"]}] if c.get("seuil") is not None else []) + list(c.get("seuils") or [])
        for n_s, seuil in enumerate(seuils):
            ys = Y(float(seuil["valeur"]))
            couleur = self.c["accent"] if n_s % 2 == 0 else self.c["texte"]
            xx = gauche
            while xx < droite:
                d.line((xx, ys, min(xx + 16, droite), ys), fill=_melange(fond, couleur, 0.8 * a_axes), width=4)
                xx += 30
            lbl = typographie(seuil.get("label") or fmt_y(float(seuil["valeur"])), self.langue)
            # Seuils pairs à gauche, impairs à droite : deux seuils proches ne se chevauchent pas.
            lx = gauche + 16 if n_s % 2 == 0 else droite - 16 - p_axe.getlength(lbl)
            ly = ys - p_axe.size - 12
            if len(seuils) > 1:   # fond sous l'étiquette : les pointillés voisins ne la traversent pas
                d.rectangle((lx - 8, ly - 2, lx + p_axe.getlength(lbl) + 8, ly + p_axe.size + 8), fill=fond)
            d.text((lx, ly), lbl, font=p_axe, fill=_melange(fond, couleur, a_axes))
        # Courbe tracée progressivement, ou points posés un à un (« style: points », pour des valeurs
        # individuelles comme dix salaires rangés : un trait suggérerait une continuité qui n'existe pas).
        k = 1.0 if t is None else _ease((t - 0.6) / TRACE_COURBE)
        if k <= 0:
            return
        x_lim = xmin + (xmax - xmin) * k
        trace = [(X(x), Y(v)) for x, v in pts if x <= x_lim + 1e-9]
        if style in ("barres", "histogramme"):
            avant = set(c.get("mis_en_avant") or [])
            for n_b, (x, v_b) in enumerate(pts):
                # Les barres poussent l'une après l'autre, de gauche à droite.
                kb = min(1.0, max(0.0, k * len(pts) - n_b))
                if kb <= 0:
                    continue
                x0, x1 = (X(n_b - 0.32), X(n_b + 0.32)) if style == "barres" else (X(x), X(bornes[n_b + 1]))
                y_haut = Y(ymin + (v_b - ymin) * kb)
                couleur = self.c["accent"] if (n_b in avant or not avant) else self.c["barre"]
                d.rectangle((x0, y_haut, x1, bas_g), fill=couleur,
                            outline=fond if style == "histogramme" else None, width=3 if style == "histogramme" else 0)
                if c.get("valeurs") and kb >= 1.0:
                    lbl = fmt_y(v_b)
                    d.text(((x0 + x1) / 2 - p_axe.getlength(lbl) / 2, y_haut - p_axe.size - 14), lbl, font=p_axe,
                           fill=self.c["texte"])
        elif style == "boites":
            # Boîtes à moustaches posées l'une après l'autre : moustaches (min et max hors atypiques), boîte de
            # Q1 à Q3, trait épais à la médiane, valeurs atypiques en points creux.
            avant = set(c.get("mis_en_avant") or [])
            demi = 0.18 if len(pts) == 1 else 0.3
            for n_b, b in enumerate(c["boites"]):
                kb = min(1.0, max(0.0, k * len(pts) - n_b))
                if kb <= 0:
                    continue
                mn, q1, me, q3, mx = (float(z) for z in b["valeurs"])
                couleur = self.c["accent"] if (n_b in avant or not avant) else self.c["barre"]
                trait = _melange(fond, couleur, kb)
                xc, x0, x1 = X(n_b), X(n_b - demi), X(n_b + demi)
                xm0, xm1 = X(n_b - demi / 2), X(n_b + demi / 2)
                d.line((xc, Y(mn), xc, Y(q1)), fill=trait, width=6)
                d.line((xc, Y(q3), xc, Y(mx)), fill=trait, width=6)
                d.line((xm0, Y(mn), xm1, Y(mn)), fill=trait, width=6)
                d.line((xm0, Y(mx), xm1, Y(mx)), fill=trait, width=6)
                d.rectangle((x0, Y(q3), x1, Y(q1)), fill=_melange(fond, couleur, 0.35 * kb), outline=trait, width=6)
                d.line((x0, Y(me), x1, Y(me)), fill=_melange(fond, self.c["texte"], kb), width=10)
                for v_a in b.get("atypiques", []):
                    ya = Y(float(v_a))
                    d.ellipse((xc - 14, ya - 14, xc + 14, ya + 14), outline=trait, width=6)
                # « valeurs: true » : les cinq nombres écrits à droite de la boîte (une seule boîte, ou peu).
                if c.get("valeurs") and kb >= 1.0:
                    noms = {"fr": ("min", "Q1", "médiane", "Q3", "max"), "en": ("min", "Q1", "median", "Q3", "max")}
                    # Étiquettes écartées les unes des autres (Q1 et min proches), de haut en bas.
                    lignes = sorted(((Y(v_b) - p_axe.size * 0.6, f"{nom} {fmt_y(v_b)}", nom in ("médiane", "median"))
                                     for nom, v_b in zip(noms.get(self.langue, noms["en"]), (mn, q1, me, q3, mx))))
                    pas_l = p_axe.size + 10
                    ys_l = [lignes[0][0]]
                    for y_l, _, _ in lignes[1:]:
                        ys_l.append(max(y_l, ys_l[-1] + pas_l))
                    depasse = ys_l[-1] - (bas_g - p_axe.size * 0.6)
                    if depasse > 0:
                        ys_l = [v - depasse for v in ys_l]
                    for y_l, (_, lbl, med) in zip(ys_l, lignes):
                        d.text((x1 + 22, y_l), lbl, font=p_axe, fill=self.c["texte"] if med else self.c["secondaire"])
        elif style == "points":
            avant = set(c.get("mis_en_avant") or [])
            rangs = [n_p for n_p, (x, _) in enumerate(pts) if x <= x_lim + 1e-9]
            for n_p, (px, py) in zip(rangs, trace):
                couleur = self.c["accent"] if (n_p in avant or not avant) else self.c["barre"]
                d.ellipse((px - 14, py - 14, px + 14, py + 14), fill=couleur)
        elif len(trace) >= 2:
            d.line(trace, fill=self.c["accent"], width=10, joint="curve")
        if s2:
            def Y2(v):
                return bas_g - (v - y2min) / ((y2max - y2min) or 1) * (bas_g - haut_g)
            trace2 = [(X(x), Y2(v)) for x, v in pts2 if x <= x_lim + 1e-9]
            if len(trace2) >= 2:
                d.line(trace2, fill=self.c["texte"], width=10, joint="curve")
        # Repères : point, pointillés, étiquette. Ils apparaissent quand la courbe les atteint et, si la
        # voix est connue, sur la phrase qui les annonce (une phrase d'introduction, puis une par repère).
        reperes = c.get("reperes", [])
        debuts = self._debuts_etapes(scene, len(reperes)) if self.reperes.get(id(scene)) and reperes \
            else [0.0] * len(reperes)
        places = []
        for rep, debut in zip(reperes, debuts):
            xr = rep["x"]
            if xr > x_lim + 1e-9 or (t is not None and t < debut):
                continue
            a = 1.0 if t is None else _ease((t - debut) / 0.4) if debut else 1.0
            yr = rep.get("y")
            if yr is None:
                yr = min(pts, key=lambda p: abs(p[0] - xr))[1]
            px, py = X(xr), Y(yr)
            for yy in range(int(py), int(bas_g), 22):
                d.line((px, yy, px, min(yy + 11, bas_g)), fill=_melange(fond, self.c["texte"], a), width=3)
            # « guide_y: true » : second pointillé vers l'axe vertical, pour lire les deux coordonnées.
            if rep.get("guide_y"):
                for xx in range(int(px), int(gauche), -22):
                    d.line((max(xx - 11, gauche), py, xx, py), fill=_melange(fond, self.c["texte"], a), width=3)
            r = 15 * (0.6 + 0.4 * a)
            d.ellipse((px - r, py - r, px + r, py + r), fill=self.c["texte"], outline=self.c["accent"], width=6)
            places.append((typographie(rep.get("label") or fmt_y(yr), self.langue), px, py, a))
        # Étiquettes : à droite et sous le point (la courbe, croissante, passe au-dessus), sinon à gauche et
        # au-dessus ; décalées si elles en chevauchent une autre (repères voisins comme 40 et 41).
        occupes = []
        hl = p_lbl.size
        if len(reperes) > 2:
            # Repères nombreux et voisins (40 et 41) : légende rangée en haut à gauche du graphique,
            # vide au-dessus d'une courbe croissante. Chaque ligne commence par son abscisse.
            y_leg = Y(ymin + (ymax - ymin) * 0.86)
            for lbl, px, py, a in places:
                d.text((gauche + 24, y_leg), lbl, font=p_lbl, fill=_melange(fond, self.c["texte"], a))
                y_leg += hl + 14
            places = []
        for lbl, px, py, a in places:
            lg_l = p_lbl.getlength(lbl)
            a_droite = px + 28 + lg_l <= droite
            lx = px + 28 if a_droite else px - 28 - lg_l
            ly = py + 20 if a_droite else py - 28 - hl
            for _ in range(8):
                rect = (lx - 10, ly - 6, lx + lg_l + 10, ly + hl + 12)
                if not any(rect[0] < o[2] and o[0] < rect[2] and rect[1] < o[3] and o[1] < rect[3] for o in occupes):
                    break
                ly += (hl + 22) if a_droite else -(hl + 22)
            occupes.append(rect)
            d.rounded_rectangle(rect, radius=8, fill=self._fond.getpixel((int(min(max(lx, 0), self.largeur - 1)),
                                                                          int(min(max(ly, 0), self.hauteur - 1)))))
            d.text((lx, ly), lbl, font=p_lbl, fill=_melange(fond, self.c["texte"], a))
