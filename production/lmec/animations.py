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
- surface     : un carré de côté 1, puis un carré de côté 2 ; « decoupe » montre qu'il contient
                quatre petits carrés (doubler hauteur et largeur multiplie l'aire par 4) ;
- grille      : n cases (combinaisons) ; « personnes » réparties au hasard (graine fixe) ;
                « isoles » met en couleur les cases qui ne contiennent qu'une seule personne ;
- pastilles   : une pastille par valeur (« valeurs », « largeur_classe », « origine », « unite ») ;
                « points » les pose sur l'axe, « tri » les range en piles par classe, « barres » fait
                monter l'histogramme derrière les piles avec les effectifs ;
- curseur     : la série en pastilles ; « mediane » et « moyenne » les marquent sous l'axe ; « curseur »
                fait glisser la valeur « indice » (la plus grande par défaut) jusqu'à « vers » : la moyenne
                suit, la médiane bouge à peine (laboratoire LAB-2) ;
- equilibre   : la moyenne comme point d'appui ; « serie » pose les valeurs sur une planche, « appui »
                fait glisser l'appui jusqu'à la moyenne (la planche se redresse), « ecarts » trace les
                écarts à la moyenne et leur somme nulle ;
- elimination : la médiane par élimination ; « rangement » aligne les valeurs triées, « elimination »
                barre la plus petite et la plus grande, deux à deux, « milieu » désigne la médiane ;
                avec « ajout », une valeur entre, puis « pair » recommence : il reste deux valeurs ;
- densite     : classes inégales (« bornes », « effectifs ») ; « effectif » monte les barres à hauteur
                d'effectif, « densite » les ramène à la densité (les pastilles prennent le même
                espacement partout), « surface » affiche densité × largeur = effectif ;
- apercu      : bande-annonce de l'épisode ; une carte par compétence (« cartes » : icone, texte), qui
                apparaît quand la voix l'annonce (une proposition par carte, après l'annonce) ;
- cumul       : fréquences cumulées ; une barre de 100 % qui se remplit catégorie par catégorie
                (« categories », « frequences » en %), le cumul écrit à chaque palier ;
- partage     : la moyenne comme partage égal ; « montants » en briques, versés dans la « cagnotte »,
                puis « partage » en parts égales ;
- ponderee    : moyenne pondérée ; « notes » (valeur, coef, libelle) en pastilles, « poids » ajoute une
                pastille par point de coefficient, « ponderee » fait glisser la moyenne simple vers la pondérée ;
- decoupages  : les mêmes « valeurs » en histogrammes côte à côte, une « largeur » de classes par panneau ;
- asymetrie   : trois distributions (traîne à droite, symétrique, traîne à gauche), médiane et moyenne
                calculées sur les courbes ; présenté comme une tendance fréquente, pas une loi ;
- melange     : un histogramme à deux bosses (« groupes » : deux listes d'effectifs), puis deux
                sous-distributions colorées, à titre d'hypothèse (« prudence » : l'histogramme ne le prouve pas) ;
- questions   : deux questions côte à côte (question, reponse, icone), chacune mène à son indicateur ; « deux »
                les relie ;
- capitalisation : intérêt simple ou composé, année par année (« capital », « taux », « annees ») ;
                « capital » pose le capital (axe coupé, signalé), « simple » empile les intérêts du capital
                (une marche égale par an), « compose » ajoute les intérêts des intérêts, qui font boule de neige ;
- echeancier  : des versements (« montants », « dates ») sur une frise du temps, au « taux » donné ; « flux »
                les pose, « actualisation » fait glisser chacun vers la date 0 en le rétrécissant de vᵗ,
                « somme » empile les valeurs actuelles et écrit le total ;
- escompte    : une facture de « nominal » payable dans un an, au « taux » d'intérêt i ; « facture » la pose,
                « retenue » la ramène à aujourd'hui en coupant l'escompte (d = i / (1 + i)), « interet » montre
                que la même somme vaut d du nominal et i du montant versé ;
- frequences  : un an, un « taux » annuel effectif, « m » périodes ; « annuel » trace un seul saut en fin
                d'année, « mensuel » les m petits sauts au taux équivalent, « egalite » montre l'arrivée commune
                et le piège du taux proportionnel (m × j < i) ;
- selection   : n icônes (avions ou entreprises) ; « depart » les montre, « selection » estompe
                celles qui disparaissent, « echantillon » fait descendre les survivantes dans le cadre
                des données observées, « filtre » trace la flèche « sélection par la survie ».
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from .formatage import formater_nombre

MODELES = ("foule", "paires", "doublon", "calendrier", "complement", "selection", "surface", "grille",
           "pastilles", "curseur", "equilibre", "elimination", "densite", "apercu",
           "cumul", "partage", "ponderee", "decoupages", "asymetrie", "melange", "questions",
           "capitalisation", "echeancier", "escompte", "frequences")
PHASES = {
    "foule": ("apparition",),
    "paires": ("apparition", "personne", "vous", "reste", "total"),
    "doublon": ("aller", "retour", "fusion", "legende"),
    "calendrier": ("personne", "reste"),
    "complement": ("gauche", "droite", "total"),
    "selection": ("depart", "selection", "echantillon", "filtre"),
    "surface": ("petit", "grand", "decoupe"),
    "grille": ("cases", "remplissage", "isoles"),
    "pastilles": ("points", "tri", "barres"),
    "curseur": ("serie", "mediane", "moyenne", "curseur"),
    "equilibre": ("serie", "appui", "ecarts"),
    "elimination": ("rangement", "elimination", "milieu", "ajout", "pair"),
    "densite": ("effectif", "densite", "surface"),
    "apercu": ("carte",),
    "cumul": ("palier",),
    "partage": ("montants", "cagnotte", "partage"),
    "ponderee": ("notes", "poids", "ponderee"),
    "decoupages": ("decoupage",),
    "asymetrie": ("queue_droite", "symetrique", "queue_gauche"),
    "melange": ("global", "hypothese", "prudence"),
    "questions": ("question", "deux"),
    "capitalisation": ("capital", "simple", "compose"),
    "echeancier": ("flux", "actualisation", "somme"),
    "escompte": ("facture", "retenue", "interet"),
    "frequences": ("annuel", "mensuel", "egalite"),
}
ICONES_APERCU = ("tableau", "histogramme", "forme", "equilibre", "mediane", "laboratoire")
PHASES_DEFAUT = {
    "foule": ["apparition"],
    "paires": ["apparition", "reste", "total"],
    "doublon": ["aller", "retour", "fusion"],
    "calendrier": ["personne", "personne", "personne", "reste"],
    "complement": ["gauche", "droite"],
    "selection": ["depart", "selection", "echantillon", "filtre"],
    "surface": ["petit", "grand", "decoupe"],
    "grille": ["cases", "remplissage", "isoles"],
    "pastilles": ["points", "tri", "barres"],
    "curseur": ["serie", "mediane", "moyenne", "curseur"],
    "equilibre": ["serie", "appui", "ecarts"],
    "elimination": ["rangement", "elimination", "milieu", "ajout", "pair"],
    "densite": ["effectif", "densite", "surface"],
    "apercu": ["carte"],
    "cumul": ["palier"],
    "partage": ["montants", "cagnotte", "partage"],
    "ponderee": ["notes", "poids", "ponderee"],
    "decoupages": ["decoupage", "decoupage"],
    "asymetrie": ["queue_droite", "symetrique", "queue_gauche"],
    "melange": ["global", "hypothese", "prudence"],
    "questions": ["question", "question", "deux"],
    "capitalisation": ["capital", "simple", "compose"],
    "echeancier": ["flux", "actualisation", "somme"],
    "escompte": ["facture", "retenue", "interet"],
    "frequences": ["annuel", "mensuel", "egalite"],
}
LIBELLES = {
    "fr": {"paires": "paires", "paire": "paire", "jours": "jours libres", "tous": "Tous différents",
           "aire": "aire", "cote": "côté"},
    "en": {"paires": "pairs", "paire": "pair", "jours": "days still free", "tous": "All different",
           "aire": "area", "cote": "side"},
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
                      "depart": 1.6, "selection": 1.4, "echantillon": 1.4, "filtre": 1.0,
                      "petit": 1.0, "grand": 1.4, "decoupe": 1.4, "cases": 1.2, "remplissage": 2.4,
                      "isoles": 1.2, "points": 2.4, "tri": 1.8, "barres": 1.2,
                      "serie": 1.8, "mediane": 1.0, "moyenne": 1.0, "curseur": 4.0,
                      "appui": 2.4, "ecarts": 2.4, "rangement": 1.6, "elimination": 3.0, "milieu": 1.0,
                      "ajout": 1.6, "pair": 3.4, "effectif": 1.6, "densite": 2.4, "surface": 1.4,
                      "carte": 0.9, "palier": 1.0, "montants": 1.4, "cagnotte": 1.8, "partage": 1.8,
                      "notes": 1.2, "poids": 1.6, "ponderee": 1.6, "decoupage": 1.6, "queue_droite": 2.0,
                      "symetrique": 2.0, "queue_gauche": 2.0, "global": 1.6, "hypothese": 2.0, "prudence": 1.0,
                      "question": 1.2, "deux": 0.8,
                      "capital": 1.4, "simple": 2.6, "compose": 2.6, "flux": 1.6, "actualisation": 3.2,
                      "somme": 1.2, "facture": 1.2, "retenue": 2.2, "interet": 1.6, "annuel": 1.6,
                      "mensuel": 3.2, "egalite": 1.0}
            plan = [{"nature": nature, "duree": durees.get(nature, 1.0)} for nature in phases]
        debuts = self._debuts_phases(scene, plan)
        for p, debut in zip(plan, debuts):
            p["debut"] = debut
        return plan

    def _debuts_phases(self, scene, plan) -> list[float]:
        morceaux = getattr(self, "morceaux_voix", {}).get(id(scene))
        if scene.extra["animation"]["modele"] == "apercu" and morceaux:
            # Une carte par proposition annoncée (« … : construire un tableau ; choisir… ; … ») :
            # la première proposition est l'annonce, les suivantes les cartes.
            debuts = [m[0] for m in morceaux[-len(plan):]] if len(morceaux) > len(plan) else \
                [m[0] for m in morceaux[1:1 + len(plan)]]   # les dernières propositions : une par carte
            dernier = morceaux[-1][1]
            while len(debuts) < len(plan):
                debuts.append(min(dernier, (debuts[-1] if debuts else 0.6) + 1.2))
            return debuts
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
                                              ("droite", x_sep, dr, self.c["accent"], self.c["encre_accent"])):
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



def repartition_grille(n: int, personnes: int, graine: int) -> list[int]:
    """Effectif de chaque case quand « personnes » tombent au hasard, uniformément, dans n cases."""
    r = random.Random(graine)
    comptes = [0] * n
    for _ in range(personnes):
        comptes[r.randrange(n)] += 1
    return comptes


class _AnimationsAires:
    # ------------------------------------------------------------------ surface
    def _anim_surface(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        g, haut, dr, bas = zone
        par = {p["nature"]: p for p in plan}
        lib = LIBELLES[self.langue]
        p_lbl = self.police("noir", 46 if not self.colonnes else 40)
        p_txt = self.police("regulier", 36 if not self.colonnes else 32)
        ecart = 70
        cote = min((dr - g - ecart) / 3, (bas - haut - 160) / 2)
        x1 = (g + dr) / 2 - (3 * cote + ecart) / 2
        y_bas = (haut + bas) / 2 + cote
        fond = self._fond.getpixel((int(g), int(y_bas)))
        carres = (("petit", x1, cote, "1"), ("grand", x1 + cote + ecart, 2 * cote, "2"))
        for nom, x, c_, lbl in carres:
            p = par.get(nom)
            if not p:
                continue
            k = _ease(self._avancee(p, t))
            if k <= 0:
                continue
            c_k = c_ * (0.6 + 0.4 * k)
            d.rectangle((x, y_bas - c_k, x + c_k, y_bas), fill=_melange(fond, self.c["accent"], 0.9 * k),
                        outline=_melange(fond, self.c["texte"], k), width=4)
            txt = f"{lib['cote']} {lbl}"
            d.text((x + c_k / 2 - p_txt.getlength(txt) / 2, y_bas + 18), txt, font=p_txt,
                   fill=_melange(fond, self.c["texte"], k))
        p = par.get("decoupe")
        if p and par.get("grand") and self._avancee(p, t) > 0:
            k = _ease(self._avancee(p, t))
            x, c_ = x1 + cote + ecart, 2 * cote
            ligne = _melange(self.c["accent"], self.c["fond"], k)
            d.line((x + cote, y_bas - c_, x + cote, y_bas), fill=ligne, width=6)
            d.line((x, y_bas - cote, x + c_, y_bas - cote), fill=ligne, width=6)
            for nom, xx, cc, aire in (("petit", x1, cote, "1"), ("grand", x, c_, "4")):
                txt = f"{lib['aire']} {aire}"
                d.text((xx + cc / 2 - p_lbl.getlength(txt) / 2, y_bas - c_ - p_lbl.size - 40), txt, font=p_lbl,
                       fill=_melange(fond, self.c["texte"], k))

    # ------------------------------------------------------------------ grille de combinaisons
    def _anim_grille(self, d, scene, plan, zone, t, ctx):
        from .rendu import _melange
        conf = scene.extra["animation"]
        n = conf["n"]
        comptes = repartition_grille(n, conf["personnes"], conf.get("graine", 1))
        g, haut, dr, bas = zone
        par = {p["nature"]: p for p in plan}
        reserve = 20   # le décompte des cases est dans la légende de phase
        cols = conf.get("colonnes") or max(1, round(math.sqrt(n * (dr - g) / max(bas - haut - reserve, 1))))
        rangs = math.ceil(n / cols)
        pas = min((dr - g) / cols, (bas - haut - reserve) / rangs)
        x0 = (g + dr) / 2 - pas * cols / 2
        y0 = (haut + bas - reserve) / 2 - pas * rangs / 2
        fond = self._fond.getpixel((int(g), int(y0)))
        a_c = _ease(self._avancee(par["cases"], t)) if "cases" in par else 1.0
        k_r = _ease(self._avancee(par["remplissage"], t)) if "remplissage" in par else 1.0
        k_i = _ease(self._avancee(par["isoles"], t)) if "isoles" in par else 0.0
        for i, nb in enumerate(comptes):
            c_, l_ = i % cols, i // cols
            x, y = x0 + c_ * pas, y0 + l_ * pas
            boite = (x + 2, y + 2, x + pas - 2, y + pas - 2)
            d.rectangle(boite, outline=_melange(fond, self.c["secondaire"], 0.5 * a_c), width=2)
            if nb == 0 or i >= n * k_r:
                continue
            base = min(1.0, 0.25 + 0.2 * nb)
            couleur = _melange(fond, self.c["texte"], base * (1 - 0.6 * k_i))
            if nb == 1:
                couleur = _melange(couleur, self.c["accent"], k_i)
            d.rectangle((x + 4, y + 4, x + pas - 4, y + pas - 4), fill=couleur)


Animations._anim_surface = _AnimationsAires._anim_surface
Animations._anim_grille = _AnimationsAires._anim_grille


# ---------------------------------------------------------------------- données : pastilles et curseur
class AnimationsDonnees:
    """Modèles qui montrent les données elles-mêmes (une pastille par individu), calculés par
    lmec/laboratoires.py : la vidéo et le laboratoire du site affichent les mêmes nombres."""

    def _axe(self, d, g, dr, y, mini, maxi, graduations, unite, fond, k=1.0, eviter=()):
        """Axe gradué ; pas de libellé de graduation à moins de 45 px d'un repère `eviter` (valeurs)."""
        from .rendu import _melange
        p = self.police("regulier", 34)
        d.line((g, y, dr, y), fill=_melange(fond, self.c["secondaire"], 0.8 * k), width=3)
        x_de = lambda v: g + (v - mini) / (maxi - mini) * (dr - g)
        for v in graduations:
            x = x_de(v)
            d.line((x, y, x, y + 14), fill=_melange(fond, self.c["secondaire"], k), width=3)
            lib = formater_nombre(v, self.langue)
            if any(abs(x - x_de(e)) < 45 for e in eviter):
                continue
            d.text((x - p.getlength(lib) / 2, y + 22), lib, font=p, fill=_melange(fond, self.c["secondaire"], k))
        if unite:   # sous le début de l'axe : la droite reste libre pour les repères et les flèches
            d.text((g, y + 66), unite, font=p, fill=_melange(fond, self.c["secondaire"], k))
        return x_de

    def _anim_pastilles(self, d, scene, plan, zone, t, ctx):
        """Une pastille par individu : posée sur l'axe à sa valeur, puis rangée dans sa classe ; les
        barres de l'histogramme montent derrière les piles et chaque effectif s'affiche."""
        from .laboratoires import classes_regulieres
        from .rendu import _melange
        conf = scene.extra["animation"]
        valeurs = conf["valeurs"]
        classes = classes_regulieres(valeurs, conf["largeur_classe"], conf.get("origine", 0.0))
        g, haut, dr, bas = zone
        y_axe = bas - 110
        mini, maxi = classes[0].debut, classes[-1].fin
        fond = self._fond.getpixel((int(g), int(min(y_axe, self.hauteur - 1))))
        x_de = self._axe(d, g, dr, y_axe, mini, maxi, [c.debut for c in classes] + [maxi],
                         conf.get("unite", ""), fond)
        n_max = max(c.effectif for c in classes)
        larg_px = (dr - g) / len(classes)
        # Piles sur une ou plusieurs colonnes : on garde le choix qui donne les plus grosses pastilles.
        h_dispo = y_axe - haut - 70
        r, cols = max(((min((larg_px - 12) / (c * 2.25 + 0.3), h_dispo / (math.ceil(n_max / c) * 2.25 + 0.6), 30.0), c)
                       for c in range(1, 5)), key=lambda rc: rc[0])
        r = max(7.0, r)
        par_nature = {p["nature"]: p for p in plan}
        k_tri = _ease(self._avancee(par_nature["tri"], t)) if "tri" in par_nature else 0.0
        k_bar = _ease(self._avancee(par_nature["barres"], t)) if "barres" in par_nature else 0.0
        p_pts = par_nature.get("points")
        # Barres derrière les piles.
        if k_bar > 0:
            pe = self.police("gras", 40)
            for c in classes:
                x0, x1 = x_de(c.debut) + 6, x_de(c.fin) - 6
                h = (math.ceil(c.effectif / cols) * 2.25 * r + r * 0.5) * k_bar
                if c.effectif and h > 4:      # début de la montée : rien à dessiner
                    d.rounded_rectangle((x0, y_axe - h, x1, y_axe - 2), radius=12,
                                        fill=_melange(fond, self.c["barre"], 0.22 * k_bar + 0.0))
                lib = str(c.effectif)
                d.text(((x0 + x1) / 2 - pe.getlength(lib) / 2, y_axe - h - 58), lib, font=pe,
                       fill=_melange(fond, self.c["texte"], k_bar))
        # Pastilles : position sur l'axe (rang alterné pour ne pas se cacher) puis dans la pile.
        rangs = {}
        ordre = sorted(range(len(valeurs)), key=lambda i: valeurs[i])
        for i in ordre:
            v = valeurs[i]
            ci = next(j for j, c in enumerate(classes) if c.debut <= v < c.fin)
            rangs[i] = (ci, sum(1 for j in rangs if rangs[j][0] == ci))
        n = len(valeurs)
        for i, v in enumerate(valeurs):
            a = 1.0 if (t is None or not p_pts) else _ease((t - p_pts["debut"] - i * p_pts["duree"] / n) / 0.4)
            if a <= 0:
                continue
            ci, j = rangs[i]
            xa, ya = x_de(v), y_axe - r * 1.3 - (i % 3) * r * 0.9
            n_ci = classes[ci].effectif
            dans_rang = min(cols, n_ci - (j // cols) * cols)      # pastilles de ce rang (dernier rang centré)
            xb = (x_de(classes[ci].debut) + x_de(classes[ci].fin)) / 2 + ((j % cols) - (dans_rang - 1) / 2) * 2.25 * r
            yb = y_axe - r * 1.25 - (j // cols) * 2.25 * r
            k = _ease(min(1.0, max(0.0, k_tri * 1.25 - 0.25 * (i / n)))) if k_tri < 1 else 1.0
            x, y = xa + (xb - xa) * k, ya + (yb - ya) * k - (1 - a) * 80
            couleur = self.c["barre"] if k < 1 or k_bar <= 0 else _melange(self.c["barre"], self.c["texte"], 0.25 * k_bar)
            d.ellipse((x - r, y - r, x + r, y + r), fill=_melange(fond, couleur, a))

    def _anim_curseur(self, d, scene, plan, zone, t, ctx):
        """Une série en pastilles ; la médiane (bleu) et la moyenne (orange) marquées sous l'axe. Puis une
        valeur glisse : la moyenne la suit, la médiane bouge à peine. Hors de l'axe, une flèche et la valeur."""
        from .laboratoires import mediane, moyenne, remplacer
        from .rendu import _melange
        conf = scene.extra["animation"]
        valeurs = conf["valeurs"]
        indice = conf.get("indice", max(range(len(valeurs)), key=lambda i: valeurs[i]))
        g, haut, dr, bas = zone
        par_nature = {p["nature"]: p for p in plan}
        k_c = _ease(self._avancee(par_nature["curseur"], t)) if "curseur" in par_nature else 0.0
        courante = valeurs[indice] + (conf["vers"] - valeurs[indice]) * k_c
        serie = remplacer(valeurs, indice, courante)
        mini = min(0.0, min(valeurs))
        autres = [v for i, v in enumerate(valeurs) if i != indice]
        maxi = conf.get("axe_max") or max(max(autres), valeurs[indice]) * 1.15
        y_axe = haut + (bas - haut) * 0.42
        fond = self._fond.getpixel((int(g), int(min(y_axe, self.hauteur - 1))))
        pas_grad = _pas_rond((maxi - mini) / 5)
        grads = [mini + k * pas_grad for k in range(int((maxi - mini) / pas_grad) + 1)]
        dr_axe = dr - 150   # place pour la flèche « hors de l'axe »
        reperes = [f(serie) for nom, f in (("mediane", mediane), ("moyenne", moyenne))
                   if nom in par_nature and self._avancee(par_nature[nom], t) > 0]
        x_de = self._axe(d, g, dr_axe, y_axe, mini, maxi, grads, conf.get("unite", ""), fond,
                         eviter=[min(v, maxi) for v in reperes])
        x_lim = lambda v: min(x_de(v), dr_axe + 40)
        r = 19
        p_pts = par_nature.get("serie")
        n = len(serie)
        pv = self.police("gras", 38)
        for i, v in enumerate(serie):
            a = 1.0 if (t is None or not p_pts) else _ease((t - p_pts["debut"] - i * p_pts["duree"] / n) / 0.4)
            if a <= 0:
                continue
            x, y = x_lim(v), y_axe - r * 1.5 - (i % 3) * r * 1.7 - (1 - a) * 60
            moving = i == indice and k_c > 0
            couleur = self.c["or"] if moving else self.c["barre"]
            d.ellipse((x - r, y - r, x + r, y + r), fill=_melange(fond, couleur, a))
            if moving:
                lib = formater_nombre(round(v), self.langue)
                if x_de(v) > dr_axe + 40:   # hors de l'axe : flèche et valeur
                    d.line((dr_axe + 60, y, dr - 10, y), fill=self.c["or"], width=4)
                    d.polygon(((dr, y), (dr - 22, y - 14), (dr - 22, y + 14)), fill=self.c["or"])
                d.text((min(x, dr - pv.getlength(lib)) - pv.getlength(lib) / 2, y - r - 56), lib, font=pv,
                       fill=self.c["accent"])
        # Repères sous l'axe : médiane puis moyenne (étiquettes décalées pour ne pas se chevaucher).
        lib = LIBELLES_DONNEES[self.langue]
        pl = self.police("gras", 36)
        for nom, valeur, couleur, dy in (("mediane", mediane(serie), self.c["barre"], 110),
                                         ("moyenne", moyenne(serie), self.c["or"], 175)):
            p = par_nature.get(nom)
            if not p:
                continue
            k = _ease(self._avancee(p, t))
            if k <= 0:
                continue
            x = x_lim(valeur)
            yt = y_axe + dy
            d.polygon(((x, y_axe + 8), (x - 16, y_axe + 36), (x + 16, y_axe + 36)), fill=_melange(fond, couleur, k))
            d.line((x, y_axe + 36, x, yt - 6), fill=_melange(fond, couleur, k), width=3)
            dec = conf.get("decimales", 0)
            v = round(valeur, dec)
            texte = f"{lib[nom]} {formater_nombre(v, self.langue, 0 if float(v).is_integer() else dec)}"
            xt = max(g, min(x - pl.getlength(texte) / 2, dr - pl.getlength(texte)))
            encre = self.c["accent"] if nom == "moyenne" else couleur   # texte doré : or foncé lisible
            d.text((xt, yt), texte, font=pl, fill=_melange(fond, encre, k))

    # ------------------------------------------------------------------ équilibre, élimination, densité
    def _montant(self, v, unite, dec=0):
        """Nombre avec son unité : « 2 200 € » (fr), « €2,200 » (en), « 15 min »."""
        txt = formater_nombre(round(v, dec), self.langue, 0 if float(round(v, dec)).is_integer() else dec)
        if unite == "€":
            return txt + " €" if self.langue == "fr" else "€" + txt
        return f"{txt} {unite}" if unite else txt

    def _anim_equilibre(self, d, scene, plan, zone, t, ctx):
        """La moyenne, point d'équilibre : les valeurs posées sur une planche ; l'appui glisse jusqu'à la
        moyenne et la planche se redresse ; puis les écarts à la moyenne, dont la somme vaut zéro."""
        from .laboratoires import moyenne
        from .rendu import _melange
        conf = scene.extra["animation"]
        valeurs, unite, dec = conf["valeurs"], conf.get("unite", ""), conf.get("decimales", 0)
        m = moyenne(valeurs)
        g, haut, dr, bas = zone
        mini = min(0.0, min(valeurs))
        pas = _pas_rond((max(valeurs) - mini) / 5)
        maxi = math.ceil(max(valeurs) * 1.05 / pas) * pas
        grads = [mini + k * pas for k in range(int(round((maxi - mini) / pas)) + 1)]
        y_b = haut + (bas - haut) * 0.60          # planche (au repos)
        y_sol = y_b + 74                          # sol gradué : l'appui glisse dessus
        fond = self._fond.getpixel((int(g), int(min(y_b, self.hauteur - 1))))
        lib = LIBELLES_DONNEES[self.langue]
        par = {p["nature"]: p for p in plan}
        k_ap = _ease(self._avancee(par["appui"], t)) if "appui" in par else 1.0
        k_ec = _ease(self._avancee(par["ecarts"], t)) if "ecarts" in par else 0.0
        x_de = self._axe(d, g, dr, y_sol, mini, maxi, grads, unite, fond,
                         eviter=[m] if k_ap >= 1 else [])
        depart = conf.get("appui_depart", (min(valeurs) + max(valeurs)) / 2)
        a = depart + (m - depart) * k_ap
        xa = x_de(a)
        # Inclinaison : le côté le plus « chargé » descend ; nulle quand l'appui est sous la moyenne.
        couple = sum(v - a for v in valeurs) / max(1e-9, (maxi - mini))
        angle = max(-0.12, min(0.12, couple * 0.12))
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        def sur_planche(x, h=0.0):   # point de la planche (abscisse x au repos), à h px au-dessus
            dx = x - xa
            return xa + dx * cos_a + h * sin_a, y_b + dx * sin_a - h * cos_a

        # Appui (triangle) et planche.
        d.polygon(((xa, y_b + 8), (xa - 34, y_sol - 2), (xa + 34, y_sol - 2)), fill=self.c["or"])
        p0, p1 = sur_planche(g - 10), sur_planche(dr + 10)
        d.line((p0, p1), fill=_melange(fond, self.c["texte"], 0.75), width=8)
        # Valeurs : pastilles posées sur la planche (empilées si égales).
        r = 24
        p_s = par.get("serie")
        pv = self.police("gras", 34)
        vus: dict[float, int] = {}
        for i, v in enumerate(valeurs):
            al = 1.0 if (t is None or not p_s) else _ease((t - p_s["debut"] - i * p_s["duree"] / len(valeurs)) / 0.4)
            if al <= 0:
                continue
            j = vus.get(v, 0)
            vus[v] = j + 1
            x, y = sur_planche(x_de(v), r + 4 + j * 2.1 * r + (1 - al) * 70)
            d.ellipse((x - r, y - r, x + r, y + r), fill=_melange(fond, self.c["barre"], al))
            txt = formater_nombre(v, self.langue)
            if j == 0:
                d.text((x - pv.getlength(txt) / 2, y - r - 46), txt, font=pv,
                       fill=_melange(fond, self.c["texte"], al))
        # Repère « moyenne » sous le sol, une fois l'équilibre atteint.
        pl = self.police("gras", 36)
        if k_ap >= 1:
            k = 1.0 if (t is None or "appui" not in par) else _ease((t - par["appui"]["debut"] - par["appui"]["duree"]) / 0.5)
            txt = f"{lib['moyenne']} {self._montant(m, '', dec)}"
            d.line((xa, y_sol + 4, xa, y_sol + 58), fill=_melange(fond, self.c["or"], k), width=3)
            d.text((xa - pl.getlength(txt) / 2, y_sol + 64), txt, font=pl, fill=_melange(fond, self.c["accent"], k))
        if k_ec <= 0:
            return
        # Écarts : flèches depuis la moyenne, rangées par côté (la plus courte en bas).
        cotes = {-1: sorted([v for v in valeurs if v < m], reverse=True), 1: sorted(v for v in valeurs if v > m)}
        haut_fleches = y_b - 2 * r - 96
        pe = self.police("gras", 32)
        n_ec = sum(len(c) for c in cotes.values())
        rang = 0
        for signe, liste in cotes.items():
            for j, v in enumerate(liste):
                k = _ease((k_ec - 0.6 * rang / max(1, n_ec)) / 0.25) if t is not None else 1.0
                rang += 1
                if k <= 0:
                    continue
                y = haut_fleches - j * 48
                x0, x1 = xa, xa + (x_de(v) - xa) * k
                couleur = self.c["barre"] if signe < 0 else self.c["or"]
                d.line((x0, y, x1, y), fill=couleur, width=4)
                d.polygon(((x1, y), (x1 - signe * 16, y - 10), (x1 - signe * 16, y + 10)), fill=couleur)
                d.line((x_de(v), y + 12, x_de(v), sur_planche(x_de(v), 2 * r + 8)[1]),
                       fill=_melange(fond, couleur, 0.35 * k), width=2)
                ecart = v - m
                txt = ("+" if ecart > 0 else "−") + formater_nombre(round(abs(ecart), dec), self.langue)
                xt = (x0 + x_de(v)) / 2 - pe.getlength(txt) / 2
                d.text((xt, y - 44), txt, font=pe, fill=_melange(fond, self.c["accent"] if signe > 0 else couleur, k))
        # Somme des écarts : zéro.
        if t is None or k_ec >= 0.85:
            k = 1.0 if t is None else (k_ec - 0.85) / 0.15
            termes = [v - m for v in valeurs]
            txt = " ".join((("+ " if e >= 0 else "− ") if i else ("" if e >= 0 else "−"))
                           + formater_nombre(round(abs(e), dec), self.langue) for i, e in enumerate(termes)) + " = 0"
            ps = self.police("gras", 44)
            y = haut_fleches - max(len(c) for c in cotes.values()) * 48 - 40
            d.text(((g + dr) / 2 - ps.getlength(txt) / 2, max(haut, y - 30)), txt, font=ps,
                   fill=_melange(fond, self.c["texte"], k))

    def _anim_elimination(self, d, scene, plan, zone, t, ctx):
        """La médiane par élimination : valeurs rangées, on barre la plus petite et la plus grande, deux à
        deux, jusqu'au milieu. Avec « ajout », une valeur entre et l'on recommence : il en reste deux."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        base = sorted(conf["valeurs"])
        unite, dec = conf.get("unite", ""), conf.get("decimales", 0)
        ajout = conf.get("ajout")
        g, haut, dr, bas = zone
        fond = self._fond.getpixel((int(g), int(min((haut + bas) / 2, self.hauteur - 1))))
        par = {p["nature"]: p for p in plan}
        av = lambda nom, defaut=0.0: (_ease(self._avancee(par[nom], t)) if nom in par else defaut)
        k_rg, k_el, k_mi = av("rangement", 1.0), av("elimination"), av("milieu")
        k_aj = av("ajout") if ajout is not None else 0.0
        k_pa = self._avancee(par["pair"], t) if (ajout is not None and "pair" in par) else 0.0
        second = sorted(base + [ajout]) if k_aj > 0 else None
        gap = 10
        y_t = haut + (bas - haut) * 0.34
        h_t = 104

        def disposition(n):
            w = min(190.0, (dr - g - (n - 1) * gap) / n)
            x0 = (g + dr) / 2 - (n * w + (n - 1) * gap) / 2
            return w, [x0 + i * (w + gap) for i in range(n)]

        def barres(n, k):    # nombre de tuiles barrées à chaque bout (progression k de l'élimination)
            paires = (n - 1) // 2
            return paires * k

        def dessiner(liste, xs, w, alpha, k_elim, k_milieu, entree=None):
            n = len(liste)
            def taille_pour(v):
                tl = 44
                while tl > 20 and self.police("gras", tl).getlength(formater_nombre(v, self.langue)) > w - 14:
                    tl -= 2
                return tl
            tailles = [taille_pour(v) for v in liste]
            commune = sorted(tailles)[len(tailles) // 2]      # une valeur hors norme se réduit seule
            pr = self.police("regulier", 28)
            elim = barres(n, k_elim)
            milieu = [n // 2] if n % 2 else [n // 2 - 1, n // 2]
            for i, v in enumerate(liste):
                a = alpha * (entree(i) if entree else 1.0)
                if a <= 0:
                    continue
                x, y = xs[i], y_t
                pos = min(i, n - 1 - i)          # distance au bord : 0 pour les extrêmes
                barre = max(0.0, min(1.0, elim - pos))
                estompe = 1 - 0.7 * barre
                choisi = i in milieu and k_milieu > 0
                fill = _melange(fond, self.c["or"] if choisi else self.c["barre"],
                                (0.38 * k_milieu if choisi else 0.16) * a * estompe + 0.0)
                contour = _melange(fond, self.c["or"] if choisi else self.c["barre"], (1.0 if choisi else 0.55) * a * estompe)
                d.rounded_rectangle((x, y, x + w, y + h_t), radius=16, fill=fill, outline=contour,
                                    width=4 if choisi else 2)
                txt = formater_nombre(v, self.langue)
                tl = min(commune, tailles[i])
                pv = self.police("gras", tl)
                d.text((x + w / 2 - pv.getlength(txt) / 2, y + h_t / 2 - tl * 0.62), txt, font=pv,
                       fill=_melange(fond, self.c["texte"], a * estompe))
                rangtxt = (("1er" if i == 0 else f"{i + 1}e") if self.langue == "fr" else _ordinal_en(i + 1))
                d.text((x + w / 2 - pr.getlength(rangtxt) / 2, y - 44), rangtxt, font=pr,
                       fill=_melange(fond, self.c["secondaire"], a * (0.4 + 0.6 * estompe)))
                if barre > 0:   # trait qui barre la tuile, tracé de gauche à droite
                    xb = x + 10 + (w - 20) * barre
                    d.line((x + 10, y + h_t - 14, xb, y + 14 + (h_t - 28) * (1 - barre)),
                           fill=_melange(fond, self.c["secondaire"], a), width=4)
            if k_milieu > 0:
                lib = LIBELLES_DONNEES[self.langue]
                if len(milieu) == 1:
                    txt = f"{lib['mediane']} : {self._montant(liste[milieu[0]], unite, dec)}" if self.langue == "fr" \
                        else f"{lib['mediane']}: {self._montant(liste[milieu[0]], unite, dec)}"
                else:
                    v1, v2 = liste[milieu[0]], liste[milieu[1]]
                    txt = (f"({formater_nombre(v1, self.langue)} + {formater_nombre(v2, self.langue)}) ÷ 2 = "
                           f"{self._montant((v1 + v2) / 2, unite, dec)}")
                pl = self.police("gras", 46)
                cx = (xs[milieu[0]] + xs[milieu[-1]] + w) / 2
                xt = max(g, min(cx - pl.getlength(txt) / 2, dr - pl.getlength(txt)))
                d.line((cx, y_t + h_t + 10, cx, y_t + h_t + 56), fill=_melange(fond, self.c["or"], k_milieu * alpha), width=3)
                d.text((xt, y_t + h_t + 68), txt, font=pl, fill=_melange(fond, self.c["accent"], k_milieu * alpha))

        w1, xs1 = disposition(len(base))
        if second is None:
            n = len(base)
            entree = (lambda i: _ease(k_rg * (n + 2) / 2 - i / 2)) if t is not None and "rangement" in par else None
            dessiner(base, xs1, w1, 1.0, k_el, k_mi, entree)
            return
        # Ajout : la première série s'efface, la nouvelle (une valeur de plus) se met en place.
        w2, xs2 = disposition(len(second))
        if k_aj < 1:
            dessiner(base, xs1, w1, 1 - k_aj, k_el, k_mi)
        k_el2, k_mi2 = min(1.0, k_pa / 0.75), max(0.0, (k_pa - 0.75) / 0.25)
        j_new = second.index(ajout)
        dessiner(second, xs2, w2, k_aj, _ease(k_el2), _ease(k_mi2),
                 entree=lambda i: 1.0 if i != j_new else _ease(k_aj * 1.4 - 0.4))

    def _anim_densite(self, d, scene, plan, zone, t, ctx):
        """Classes inégales : barres à hauteur d'effectif (image trompeuse), puis à hauteur de densité ; une
        pastille par individu, au même espacement partout une fois en densité ; aire = effectif."""
        from .laboratoires import classes_depuis_effectifs
        from .rendu import _melange
        conf = scene.extra["animation"]
        classes = classes_depuis_effectifs(conf["bornes"], conf["effectifs"])
        unite = conf.get("unite", "")
        g, haut, dr, bas = zone
        y_axe = bas - 110
        fond = self._fond.getpixel((int(g), int(min(y_axe, self.hauteur - 1))))
        x_de = self._axe(d, g, dr, y_axe, conf["bornes"][0], conf["bornes"][-1], conf["bornes"], unite, fond)
        par = {p["nature"]: p for p in plan}
        av = lambda nom, defaut=0.0: (_ease(self._avancee(par[nom], t)) if nom in par else defaut)
        k_ef, k_de, k_su = av("effectif", 1.0), av("densite"), av("surface")
        h_max = y_axe - haut - 100
        e_max = max(c.effectif for c in classes) or 1
        d_max = max(c.densite_effectif() for c in classes) or 1
        lib = LIBELLES_DONNEES[self.langue]
        # Légende de la hauteur, en haut à gauche : effectif puis densité (fondu croisé).
        ph = self.police("gras", 34)
        for txt, k in ((lib["hauteur_effectif"], 1 - k_de), (lib["hauteur_densite"], k_de)):
            if k > 0.02:
                d.text((g, haut), txt, font=ph, fill=_melange(fond, self.c["secondaire"], k))

        def grille(x0, x1, h, n, pas=None):
            """n pastilles dans le rectangle (x0, y_axe - h, x1, y_axe), rangées par le bas. Avec `pas` : même
            espacement imposé (état « densité », où l'aire par pastille est la même dans chaque barre)."""
            if n == 0 or h <= 0:
                return [], 0.0
            lw = x1 - x0
            s = pas or math.sqrt(lw * h / n)
            cols = max(1, min(n, round(lw / s)))
            rangs = math.ceil(n / cols)
            sx, sy = lw / cols, h / rangs
            if pas:   # espacement imposé, réduit seulement si la barre est trop petite
                sx, sy = min(pas, sx), min(pas, sy)
            pts = []
            for i in range(n):
                rang, j = divmod(i, cols)
                dans = min(cols, n - rang * cols)
                cx = (x0 + x1) / 2 + (j - (dans - 1) / 2) * sx
                pts.append((cx, y_axe - sy * (rang + 0.5)))
            return pts, min(sx, sy) * 0.34

        pe = self.police("gras", 40)
        n_tot = sum(c.effectif for c in classes) or 1
        aire_d = sum((x_de(c.fin) - x_de(c.debut) - 22) * (c.densite_effectif() / d_max * h_max - 8) for c in classes)
        pas_d = math.sqrt(max(1.0, aire_d) / n_tot)
        r_commun = min((grille(x_de(c.debut) + 11, x_de(c.fin) - 11, c.densite_effectif() / d_max * h_max - 8,
                               c.effectif, pas_d)[1] for c in classes if c.effectif), default=0.0)
        for c in classes:
            x0, x1 = x_de(c.debut) + 5, x_de(c.fin) - 5
            h_e = c.effectif / e_max * h_max
            h_d = c.densite_effectif() / d_max * h_max
            h = (h_e + (h_d - h_e) * k_de) * k_ef
            if c.effectif and h > 4:          # début de croissance : rien à dessiner
                fill = _melange(fond, self.c["or"] if k_su > 0 else self.c["barre"], 0.20 + 0.06 * k_su)
                d.rounded_rectangle((x0, y_axe - h, x1, y_axe - 2), radius=10, fill=fill,
                                    outline=_melange(fond, self.c["barre"], 0.6 * k_ef), width=2)
            pts_e, r_e = grille(x0 + 6, x1 - 6, h_e - 8, c.effectif)
            pts_d, _ = grille(x0 + 6, x1 - 6, h_d - 8, c.effectif, pas_d)
            r_d = r_commun                       # même taille de pastille partout en densité
            r = (r_e + (r_d - r_e) * k_de)
            for (xa, ya), (xb, yb) in zip(pts_e, pts_d):
                x, y = xa + (xb - xa) * k_de, ya + (yb - ya) * k_de
                y = y_axe - (y_axe - y) * k_ef
                d.ellipse((x - r, y - r, x + r, y + r), fill=_melange(fond, self.c["barre"], k_ef))
            # Étiquette au-dessus : effectif, puis densité, puis densité × largeur = effectif.
            dens_v = c.densite_effectif()
            exacte = abs(round(dens_v, 2) - dens_v) < 1e-9
            dens = formater_nombre(round(dens_v, 2), self.langue)
            frac = Fraction(c.effectif, 1) / Fraction(c.largeur).limit_denominator(1000)
            fraction = FRACTIONS.get((frac.numerator, frac.denominator), f"{frac.numerator}/{frac.denominator}")
            larg = formater_nombre(c.largeur, self.langue)
            eff = str(c.effectif)
            for txt, k, couleur in ((eff, k_ef * (1 - k_de), self.c["texte"]),
                                    (dens if exacte else "≈ " + dens, k_de * (1 - k_su), self.c["texte"]),
                                    (f"{dens if exacte else fraction} × {larg} = {eff}", k_su, self.c["accent"])):
                if k <= 0.02:
                    continue
                lignes = [txt]
                taille, p = 40, pe
                while taille > 28 and p.getlength(txt) > x1 - x0 - 4:
                    taille -= 2
                    p = self.police("gras", taille)
                if p.getlength(txt) > x1 - x0 - 4 and " = " in txt:   # trop étroit : « a × b » sur « = c »
                    lignes = [txt.split(" = ")[0], "= " + txt.split(" = ")[1]]
                for n_l, ligne in enumerate(lignes):
                    y = y_axe - h - 56 - (len(lignes) - 1 - n_l) * (taille + 8)
                    d.text(((x0 + x1) / 2 - p.getlength(ligne) / 2, y), ligne, font=p, fill=_melange(fond, couleur, k))

    # ------------------------------------------------------------------ aperçu de l'épisode
    def _anim_apercu(self, d, scene, plan, zone, t, ctx):
        """Bande-annonce de l'épisode : une carte par compétence (vignette dessinée et phrase courte), qui
        apparaît quand la voix l'annonce. Prépare le spectateur à ce qu'il va voir (JG, 22/11/2026)."""
        from .rendu import _melange
        cartes = scene.extra["animation"]["cartes"]
        g, haut, dr, bas = zone
        n = len(cartes)
        cols = 3 if n > 4 else n if n <= 3 else 2
        rangs = math.ceil(n / cols)
        gap = 26
        w = (dr - g - (cols - 1) * gap) / cols
        h = min(330.0, (bas - haut - (rangs - 1) * gap) / rangs)
        y0 = haut + (bas - haut - (rangs * h + (rangs - 1) * gap)) / 2
        fond = self._fond.getpixel((int(g), int(min(y0, self.hauteur - 1))))
        carte_fond = _melange(fond, (255, 255, 255), 0.75) if sum(fond) > 380 else _melange(fond, self.c["barre"], 0.12)
        pt = self.police("gras", 34)
        pn = self.police("affichage", 30)
        actuelle = self._phase_courante(plan, t)
        for i, c in enumerate(cartes):
            p = plan[i] if i < len(plan) else None
            k = _ease(self._avancee(p, t)) if p else 1.0
            if k <= 0:
                continue
            x = g + (i % cols) * (w + gap)
            y = y0 + (i // cols) * (h + gap) + (1 - k) * 30
            vive = t is None or i == actuelle
            contour = _melange(fond, self.c["or"] if vive and t is not None else self.c["barre"], (0.9 if vive else 0.45) * k)
            d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=_melange(fond, carte_fond, k), outline=contour,
                                width=3 if vive and t is not None else 2)
            # Numéro discret en haut à gauche.
            num = str(i + 1)
            d.text((x + 20, y + 12), num, font=pn, fill=_melange(fond, self.c["accent"], k))
            # Vignette dessinée dans la moitié haute.
            vx0, vy0, vx1, vy1 = x + 36, y + 30, x + w - 36, y + h * 0.60
            self._vignette(d, c["icone"], (vx0, vy0, vx1, vy1), k, fond)
            # Phrase courte, centrée, deux lignes au plus.
            p_t, lignes, pas, hh = self.ajuster_riche(c["texte"], "gras", w - 36, h * 0.34, 34, 24, 1.15, ctx,
                                                      equilibre=True)
            yt = y + h * 0.62 + (h * 0.36 - hh) / 2
            for ligne in lignes:
                lw = self._largeur_ligne(ligne, p_t)
                self.ecrire_riche(d, [ligne], p_t, pas, yt, self.c["texte"], None if k >= 1 else t,
                                  p["debut"] if p else 0.0, centre=False, x_gauche=x + w / 2 - lw / 2)
                yt += pas

    def _vignette(self, d, icone, boite, k, fond):
        """Petits dessins des notions de l'épisode, tracés à mesure que k va de 0 à 1."""
        from .rendu import _melange
        x0, y0, x1, y1 = boite
        w, h = x1 - x0, y1 - y0
        barre, orr, encre = self.c["barre"], self.c["or"], self.c["secondaire"]
        trait = _melange(fond, encre, 0.7 * k)
        if icone == "tableau":
            cols, rangs = 3, 4
            cw, rh = w / cols, h / rangs
            d.rounded_rectangle((x0, y0, x1, y0 + rh), radius=6, fill=_melange(fond, barre, 0.25 * k))
            for r in range(rangs):
                if r / rangs > k:
                    break
                yy = y0 + r * rh
                for c in range(cols):
                    lx = x0 + c * cw + cw * 0.2
                    lg = cw * (0.6 if c else 0.35)
                    d.rounded_rectangle((lx, yy + rh * 0.38, lx + lg, yy + rh * 0.62), radius=4,
                                        fill=_melange(fond, orr if (c == 2 and r) else encre, 0.8 * k))
            d.line((x0, y1, x1, y1), fill=trait, width=2)
        elif icone == "histogramme":
            hauteurs = [0.3, 0.75, 0.6, 0.35, 0.15]
            bw = w / len(hauteurs)
            for i, hh in enumerate(hauteurs):
                bh = h * hh * k
                if bh > 3:
                    d.rounded_rectangle((x0 + i * bw + 3, y1 - bh, x0 + (i + 1) * bw - 3, y1), radius=5,
                                        fill=_melange(fond, orr if i == 1 else barre, 0.85))
            d.line((x0, y1, x1, y1), fill=trait, width=3)
        elif icone == "forme":
            pts = []
            n = 40
            for j in range(int(n * k) + 1):
                u = j / n
                v = (u * 6) ** 1.6 * math.exp(-u * 6) / 1.25   # bosse à gauche, longue queue à droite
                pts.append((x0 + u * w, y1 - v * h * 0.95))
            if len(pts) > 1:
                d.polygon(pts + [(pts[-1][0], y1), (x0, y1)], fill=_melange(fond, barre, 0.22))
                d.line(pts, fill=barre, width=4)
            d.line((x0, y1, x1, y1), fill=trait, width=3)
        elif icone == "equilibre":
            yb = y0 + h * 0.62
            xa = x0 + w * 0.42
            d.polygon(((xa, yb + 4), (xa - 18, y1), (xa + 18, y1)), fill=_melange(fond, orr, k))
            d.line((x0, yb, x1, yb), fill=_melange(fond, self.c["texte"], 0.8 * k), width=5)
            for u in (0.08, 0.25, 0.42, 0.85):
                if u <= k + 0.05:
                    cx = x0 + u * w
                    d.ellipse((cx - 11, yb - 25, cx + 11, yb - 3), fill=_melange(fond, barre, k))
        elif icone == "mediane":
            n = 5
            tw = (w - (n - 1) * 8) / n
            th = min(h * 0.6, tw * 1.1)
            yy = y0 + (h - th) / 2
            for i in range(n):
                xx = x0 + i * (tw + 8)
                milieu = i == n // 2
                d.rounded_rectangle((xx, yy, xx + tw, yy + th), radius=6,
                                    fill=_melange(fond, orr if milieu else barre, (0.55 if milieu else 0.2) * k),
                                    outline=_melange(fond, orr if milieu else barre, 0.8 * k), width=2)
                barre_k = max(0.0, min(1.0, k * 3 - (1 if i in (0, n - 1) else 2)))
                if not milieu and barre_k > 0:
                    d.line((xx + 5, yy + th - 5, xx + 5 + (tw - 10) * barre_k, yy + th - 5 - (th - 10) * barre_k),
                           fill=_melange(fond, encre, 0.9), width=3)
        elif icone == "laboratoire":
            ya = y0 + h * 0.7
            d.line((x0, ya, x1 - 30, ya), fill=trait, width=3)
            for u in (0.08, 0.16, 0.22, 0.3, 0.37, 0.45):
                cx = x0 + u * w
                d.ellipse((cx - 9, ya - 22, cx + 9, ya - 4), fill=_melange(fond, barre, k))
            cx = x0 + (0.5 + 0.38 * k) * w
            d.ellipse((cx - 11, ya - 26, cx + 11, ya - 4), fill=orr)
            d.line((cx - w * 0.38 * k, ya - 15, cx - 14, ya - 15), fill=_melange(fond, orr, 0.6), width=3)
            xm = x0 + 0.27 * w
            d.polygon(((xm, ya + 6), (xm - 9, ya + 22), (xm + 9, ya + 22)), fill=barre)

    # ------------------------------------------------------------------ revue du 22/11/2026 : sept modèles
    def _fond_a(self, x, y):
        return self._fond.getpixel((int(max(0, min(x, self.largeur - 1))), int(max(0, min(y, self.hauteur - 1)))))

    def _pct(self, v):
        return formater_nombre(round(v, 1), self.langue) + (" %" if self.langue == "fr" else "%")

    def _texte_centre(self, d, txt, police, cx, y, couleur, g=None, dr=None):
        w = police.getlength(txt)
        x = cx - w / 2
        if g is not None:
            x = max(g, min(x, dr - w))
        d.text((x, y), txt, font=police, fill=couleur)

    def _panneaux(self, zone, n, gap=48):
        """n sous-zones côte à côte si la zone est large, empilées sinon."""
        g, haut, dr, bas = zone
        if (dr - g) >= 1.25 * (bas - haut) or n == 1:
            w = (dr - g - (n - 1) * gap) / n
            return [(g + i * (w + gap), haut, g + i * (w + gap) + w, bas) for i in range(n)]
        h = (bas - haut - (n - 1) * gap * 0.6) / n
        return [(g, haut + i * (h + gap * 0.6), dr, haut + i * (h + gap * 0.6) + h) for i in range(n)]

    def _anim_cumul(self, d, scene, plan, zone, t, ctx):
        """Fréquences cumulées : une barre de 100 % qui se remplit catégorie après catégorie ; le cumul
        s'inscrit à chaque palier (20 %, 60 %, 84 %, 100 %)."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        cats, freqs = conf["categories"], conf["frequences"]
        g, haut, dr, bas = zone
        hb = min(170.0, (bas - haut) * 0.26)
        yb = haut + (bas - haut) * 0.36
        fond = self._fond_a(g, yb)
        x_de = lambda p: g + (dr - g) * p / 100
        d.rounded_rectangle((g, yb, dr, yb + hb), radius=14, outline=_melange(fond, self.c["secondaire"], 0.6), width=3)
        pc, pf, pk = self.police("gras", 42), self.police("regulier", 34), self.police("gras", 46)
        courante = self._phase_courante(plan, t)
        cumul = 0.0
        paliers = []
        for i, (c, f) in enumerate(zip(cats, freqs)):
            p = plan[i] if i < len(plan) else None
            k = _ease(self._avancee(p, t)) if p else 1.0
            if k <= 0:
                break
            x0, x1 = x_de(cumul), x_de(cumul + f * k)
            vive = t is not None and i == courante
            if x1 - x0 > 6:
                couleur = self.c["or"] if vive else self.c["barre"]
                d.rectangle((x0 + 3, yb + 5, x1 - 3, yb + hb - 5),
                            fill=_melange(fond, couleur, 0.85 if vive else (0.55 if i % 2 == 0 else 0.38)))
            cx = (x_de(cumul) + x_de(cumul + f)) / 2
            encre = _melange(fond, self.c["texte"], k)
            self._texte_centre(d, c, pc, cx, yb + hb + 18, encre, g, dr)
            self._texte_centre(d, "+" + self._pct(f) if i else self._pct(f), pf, cx, yb + hb + 72,
                               _melange(fond, self.c["secondaire"], k), g, dr)
            cumul += f
            # Palier : le cumul au-dessus de la frontière.
            xk = x_de(cumul)
            a = k * (1.0 if (vive or t is None or i == len(cats) - 1) else 0.55)
            txt = self._pct(cumul)
            w_t = pk.getlength(txt)
            x_t = max(g, min(xk - w_t / 2, dr - w_t))
            monte = bool(paliers) and x_t < paliers[-1][0] + paliers[-1][1] + 16 and not paliers[-1][2]
            paliers.append((x_t, w_t, monte))
            y_t = yb - 80 - (58 if monte else 0)
            d.line((xk, y_t + 54, xk, yb + hb + 4), fill=_melange(fond, self.c["or"], a), width=4)
            d.text((x_t, y_t), txt, font=pk,
                   fill=_melange(fond, self.c["accent"] if vive or t is None else self.c["texte"], a))

    def _anim_partage(self, d, scene, plan, zone, t, ctx):
        """La moyenne, un partage égal : chaque montant en briques, toutes versées dans la cagnotte, puis
        redistribuées en parts égales (la cagnotte a déjà la forme du partage)."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        valeurs, unite = [int(v) for v in conf["valeurs"]], conf.get("unite", "")
        n = len(valeurs)
        total = sum(valeurs)
        moy = total // n
        bloc = math.gcd(*valeurs, moy)
        g, haut, dr, bas = zone
        par = {p["nature"]: p for p in plan}
        av = lambda nom, defaut=0.0: (self._avancee(par[nom], t) if nom in par else defaut)
        a_mo, a_ca, a_pa = av("montants", 1.0), av("cagnotte"), av("partage")
        pile_max = max(max(valeurs), moy) // bloc
        y_base = bas - 120
        h_pot = moy // bloc
        dispo = y_base - haut - 120
        hb = min(46.0, dispo / (pile_max + h_pot + 2.2))
        pas_x = (dr - g) / n
        wb = min(130.0, pas_x * 0.5)
        xs = [g + pas_x * (i + 0.5) for i in range(n)]
        y_pot = haut + 90 + h_pot * hb               # base de la cagnotte
        fond = self._fond_a(g, y_base)
        # Briques : propriétaire, position de départ, dans la cagnotte, à l'arrivée.
        briques = []
        j = 0
        for i, v in enumerate(valeurs):
            for niveau in range(v // bloc):
                briques.append((i, niveau, j))
                j += 1
        n_b = len(briques)
        w_pot = n * (wb + 6)
        x_pot0 = (g + dr) / 2 - w_pot / 2
        if a_ca > 0:
            ka = _ease(min(1.0, a_ca * 1.6))
            d.rounded_rectangle((x_pot0 - 18, y_pot - h_pot * hb - 14, x_pot0 + w_pot + 12, y_pot + 10), radius=16,
                                outline=_melange(fond, self.c["or"], 0.8 * ka), width=3)
        for i, niveau, j in briques:
            k_ap = _ease((a_mo * (pile_max + 1) - niveau) / 1.0) if t is not None and "montants" in par else 1.0
            if k_ap <= 0:
                continue
            xa, ya = xs[i] - wb / 2, y_base - (niveau + 1) * hb
            xp, yp = x_pot0 + (j % n) * (wb + 6), y_pot - (j // n + 1) * hb
            xf, yf = xs[j % n] - wb / 2, y_base - (j // n + 1) * hb
            d_ca = _ease((a_ca * 1.5 - 0.5 * j / max(1, n_b - 1)))
            d_pa = _ease((a_pa * 1.5 - 0.5 * (j % n) / max(1, n - 1)))
            x, y = xa + (xp - xa) * d_ca, ya + (yp - ya) * d_ca
            x, y = x + (xf - x) * d_pa, y + (yf - y) * d_pa
            y += (1 - k_ap) * 40
            teinte = _melange(self.c["barre"], self.c["or"], i / max(1, n - 1))
            d.rounded_rectangle((x, y + 2, x + wb, y + hb - 2), radius=6, fill=_melange(fond, teinte, k_ap))
        # Personnes et montants.
        pm, pg = self.police("gras", 40), self.police("affichage", 54)
        for i, v in enumerate(valeurs):
            self._personne(d, xs[i], y_base + 58, 34, _melange(fond, self.c["secondaire"], 0.8))
            for txt, k, couleur in ((self._montant(v, unite), (1 - _ease(a_ca * 2)) if a_mo > 0 else 0, self.c["texte"]),
                                    (self._montant(moy, unite), _ease((a_pa - 0.6) / 0.4), self.c["accent"])):
                if k > 0.02:
                    h_pile = (v if couleur == self.c["texte"] else moy) // bloc * hb
                    self._texte_centre(d, txt, pm, xs[i], y_base - h_pile - 56, _melange(fond, couleur, k))
        if a_ca > 0:
            k = _ease((a_ca - 0.5) / 0.5) * (1 - 0.5 * _ease(a_pa))
            lib = LIBELLES_DONNEES[self.langue]["cagnotte"]
            self._texte_centre(d, f"{lib} {self._montant(total, unite)}", pg, (g + dr) / 2, haut + 4,
                               _melange(fond, self.c["accent"], k))

    def _anim_ponderee(self, d, scene, plan, zone, t, ctx):
        """Moyenne pondérée : une pastille par note, puis autant de pastilles que le coefficient ; le repère
        de la moyenne glisse de la moyenne simple à la moyenne pondérée."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        notes = conf["notes"]
        g, haut, dr, bas = zone
        vals = [n_["valeur"] for n_ in notes]
        simple = sum(vals) / len(vals)
        pond = sum(n_["valeur"] * n_["coef"] for n_ in notes) / sum(n_["coef"] for n_ in notes)
        mini, maxi = math.floor(min(vals) - 2), math.ceil(max(vals) + 2)
        pas = _pas_rond((maxi - mini) / 8)
        mini, maxi = math.floor(mini / pas) * pas, math.ceil(maxi / pas) * pas
        grads = [mini + k * pas for k in range(int(round((maxi - mini) / pas)) + 1)]
        y_axe = haut + (bas - haut) * 0.74
        fond = self._fond_a(g, y_axe)
        par = {p["nature"]: p for p in plan}
        av = lambda nom, defaut=0.0: (_ease(self._avancee(par[nom], t)) if nom in par else defaut)
        k_no, k_po, k_mo = av("notes", 1.0), av("poids"), av("ponderee")
        x_de = self._axe(d, g, dr, y_axe, mini, maxi, grads, "", fond, eviter=[simple, pond] if k_no >= 1 else [])
        r = max(14.0, min(40.0, (y_axe - haut - 130) / (2.1 * max(n_["coef"] for n_ in notes))))
        pv, pl = self.police("gras", int(r * 0.95)), self.police("gras", 34)
        for n_ in notes:
            x = x_de(n_["valeur"])
            hauteur = 1
            for c in range(n_["coef"]):
                k = k_no if c == 0 else _ease((k_po * n_["coef"] - (c - 1)) / 1.0) if n_["coef"] > 1 else 0
                if k <= 0:
                    continue
                hauteur = c + 1
                y = y_axe - 12 - r - c * 2.1 * r + (1 - k) * 40
                d.ellipse((x - r, y - r, x + r, y + r), fill=_melange(fond, self.c["or"] if c else self.c["barre"], k))
                txt = formater_nombre(n_["valeur"], self.langue)
                self._texte_centre(d, txt, pv, x, y - r * 0.62, _melange(fond, (255, 255, 255), k))
            y_lib = y_axe - 12 - (2.1 * hauteur - 0.1) * r - 48
            lib = n_.get("libelle", "")
            coef = f"× {n_['coef']}"
            txt = f"{lib} {coef}" if (lib and k_po > 0.5) else (lib or "")
            if k_po > 0.5 and not lib:
                txt = coef
            if txt:
                self._texte_centre(d, txt, pl, x, y_lib, _melange(fond, self.c["texte"], k_no), g, dr)
        lib = LIBELLES_DONNEES[self.langue]
        k_s = _ease((self._avancee(par["notes"], t) - 0.7) / 0.3) if (t is not None and "notes" in par) else 1.0
        if k_s > 0:
            xs_ = x_de(simple)
            d.line((xs_, y_axe + 4, xs_, y_axe + 58), fill=_melange(fond, self.c["secondaire"], k_s), width=3)
            self._texte_centre(d, f"{lib['moyenne_simple']} {self._montant(simple, '', 1)}", pl, xs_, y_axe + 60,
                               _melange(fond, self.c["secondaire"], k_s * (1 - 0.4 * k_mo)), g, dr)
        if k_mo > 0:
            xm = x_de(simple + (pond - simple) * k_mo)
            d.line((xm, y_axe - 8, xm, y_axe + 100), fill=_melange(fond, self.c["or"], 1.0), width=5)
            self._texte_centre(d, f"{lib['moyenne_ponderee']} {self._montant(pond, '', 1)}", pl, xm, y_axe + 102,
                               _melange(fond, self.c["accent"], k_mo), g, dr)
            termes = " + ".join(formater_nombre(n_["valeur"], self.langue) for n_ in notes for _ in range(n_["coef"]))
            calc = f"({termes}) ÷ {sum(n_['coef'] for n_ in notes)} = {self._montant(pond, '', 1)}"
            self._texte_centre(d, calc, self.police("gras", 44), (g + dr) / 2, haut,
                               _melange(fond, self.c["texte"], _ease((k_mo - 0.5) / 0.5)), g, dr)

    def _anim_decoupages(self, d, scene, plan, zone, t, ctx):
        """Les mêmes valeurs, deux largeurs de classes côte à côte : la silhouette change."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        valeurs, largeurs, unite = conf["valeurs"], conf["largeurs"], conf.get("unite", "")
        maxi = max(math.ceil((max(valeurs) + 1e-9) / w) * w for w in largeurs)
        comptes = [[sum(1 for v in valeurs if k * w <= v < (k + 1) * w) for k in range(int(round(maxi / w)))]
                   for w in largeurs]
        c_max = max(max(c) for c in comptes) or 1
        lib = LIBELLES_DONNEES[self.langue]
        courante = self._phase_courante(plan, t)
        for i, (w, cs, panneau) in enumerate(zip(largeurs, comptes, self._panneaux(zone, len(largeurs), gap=90))):
            p = plan[i] if i < len(plan) else None
            k = _ease(self._avancee(p, t)) if p else 1.0
            if k <= 0 and t is not None and (not p or t < p["debut"]):
                continue
            g, haut, dr, bas = panneau
            y_axe = bas - 110
            fond = self._fond_a(g, y_axe)
            vive = t is not None and i == courante
            titre = lib["classes_de"].format(formater_nombre(w, self.langue), unite)
            self._texte_centre(d, titre, self.police("gras", 42), (g + dr) / 2, haut,
                               _melange(fond, self.c["accent"] if vive else self.c["texte"], max(k, 0.3)))
            x_de = self._axe(d, g, dr, y_axe, 0, maxi, [j * w for j in range(len(cs) + 1)],
                             unite if i == 0 else "", fond, k=max(k, 0.3))
            h_max = y_axe - haut - 140
            pn = self.police("gras", 38)
            for j, c in enumerate(cs):
                h = c / c_max * h_max * k
                x0, x1 = x_de(j * w) + 3, x_de((j + 1) * w) - 3
                if c and h > 4:
                    d.rectangle((x0, y_axe - h, x1, y_axe - 2),
                                fill=_melange(fond, self.c["or"] if vive else self.c["barre"], 0.75))
                if c and k > 0.6:
                    self._texte_centre(d, str(c), pn, (x0 + x1) / 2, y_axe - h - 50,
                                       _melange(fond, self.c["texte"], (k - 0.6) / 0.4))

    @staticmethod
    def _courbe_forme(forme, u):
        """Densités de démonstration sur [0, 1] : traîne à droite (log-normale), symétrique, traîne à gauche."""
        if forme == "symetrique":
            return math.exp(-((u - 0.5) / 0.15) ** 2 / 2)
        if forme == "queue_gauche":
            u = 1 - u
        x = max(u * 4.0, 1e-6)
        return math.exp(-(math.log(x / 0.95)) ** 2 / (2 * 0.85 ** 2)) / x

    def _anim_asymetrie(self, d, scene, plan, zone, t, ctx):
        """Moyenne et médiane selon la forme : trois distributions ; la médiane se place, la moyenne part du même
        point et glisse vers la traîne. Calculées sur les courbes elles-mêmes. Une tendance fréquente, pas une loi."""
        from .rendu import _melange
        g0, haut0, dr0, bas0 = zone
        lib = LIBELLES_DONNEES[self.langue]
        fond0 = self._fond_a(g0, haut0)
        self._texte_centre(d, lib["tendance"], self.police("regulier", 34), (g0 + dr0) / 2, haut0,
                           _melange(fond0, self.c["secondaire"], 1.0))
        courante = self._phase_courante(plan, t)
        formes = ("queue_droite", "symetrique", "queue_gauche")
        for i, (forme, panneau) in enumerate(zip(formes, self._panneaux((g0, haut0 + 60, dr0, bas0), 3))):
            p = plan[i] if i < len(plan) else None
            k = self._avancee(p, t) if p else 1.0
            if t is not None and p and t < p["debut"]:
                continue
            g, haut, dr, bas = panneau
            y_axe = bas - 120
            fond = self._fond_a(g, y_axe)
            vive = t is None or i == courante
            n = 160
            ys = [self._courbe_forme(forme, (j + 0.5) / n) for j in range(n)]
            tot = sum(ys)
            moy = sum(y * (j + 0.5) / n for j, y in enumerate(ys)) / tot
            acc, med = 0.0, 0.5
            for j, y in enumerate(ys):
                acc += y
                if acc >= tot / 2:
                    med = (j + 0.5) / n
                    break
            y_top = max(ys)
            h = y_axe - haut - 80
            x_de = lambda u: g + u * (dr - g)
            k_c = _ease(min(1.0, k / 0.45))
            pts = [(x_de(j / n), y_axe - ys[j] / y_top * h) for j in range(int(n * k_c))]
            d.line((g, y_axe, dr, y_axe), fill=_melange(fond, self.c["secondaire"], 0.8), width=3)
            if len(pts) > 1:
                d.polygon(pts + [(pts[-1][0], y_axe), (pts[0][0], y_axe)],
                          fill=_melange(fond, self.c["barre"], 0.22 if vive else 0.12))
                d.line(pts, fill=_melange(fond, self.c["barre"], 1.0 if vive else 0.6), width=4)
            titre = lib[forme]
            self._texte_centre(d, titre, self.police("gras", 38), (g + dr) / 2, haut,
                               _melange(fond, self.c["accent"] if vive and t is not None else self.c["texte"], 1.0))
            k_m = _ease((k - 0.45) / 0.55) if t is not None else 1.0
            if k_m <= 0:
                continue
            pl = self.police("gras", 32)
            xm, xa = x_de(med), x_de(med + (moy - med) * k_m)
            d.line((xm, haut + 70, xm, y_axe + 8), fill=_melange(fond, self.c["texte"], min(1.0, k_m * 2)), width=3)
            d.line((xa, haut + 70, xa, y_axe + 8), fill=_melange(fond, self.c["or"], 1.0), width=5)
            if abs(moy - med) < 0.01:
                self._texte_centre(d, lib["egales"], pl, xm, y_axe + 18, _melange(fond, self.c["accent"], k_m), g, dr)
                continue
            gauche = moy < med
            for txt, x, y, couleur in ((lib["mediane"], xm, y_axe + 18, self.c["texte"]),
                                       (lib["moyenne"], xa, y_axe + 58, self.c["accent"])):
                w = pl.getlength(txt)
                # La moyenne s'écrit du côté de la traîne, la médiane de l'autre.
                cote = (couleur == self.c["accent"]) != gauche
                xt = x + 6 if cote else x - w - 6
                d.text((max(g, min(xt, dr - w)), y), txt, font=pl, fill=_melange(fond, couleur, k_m))

    def _anim_melange(self, d, scene, plan, zone, t, ctx):
        """Deux bosses : l'histogramme global, puis, à titre d'hypothèse, deux sous-distributions colorées qui
        pourraient l'expliquer ; l'histogramme seul ne le prouve pas."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        o, w, groupes = conf["origine"], conf["largeur_classe"], conf["groupes"]
        noms = conf.get("noms") or ["?", "?"]
        unite = conf.get("unite", "")
        totaux = [a + b for a, b in zip(*groupes)]
        g, haut, dr, bas = zone
        y_axe = bas - 110
        fond = self._fond_a(g, y_axe)
        n = len(totaux)
        x_de = self._axe(d, g, dr, y_axe, o, o + n * w, [o + j * w for j in range(n + 1)], unite, fond)
        par = {p["nature"]: p for p in plan}
        av = lambda nom, defaut=0.0: (_ease(self._avancee(par[nom], t)) if nom in par else defaut)
        k_gl, k_hy, k_pr = av("global", 1.0), av("hypothese"), av("prudence")
        h_max = y_axe - haut - 120
        e_max = max(totaux) or 1
        pn = self.police("gras", 36)
        for j, c in enumerate(totaux):
            h = c / e_max * h_max * k_gl
            x0, x1 = x_de(o + j * w) + 3, x_de(o + (j + 1) * w) - 3
            if h > 4:
                d.rectangle((x0, y_axe - h, x1, y_axe - 2), fill=_melange(fond, self.c["barre"], 0.55 * (1 - 0.7 * k_hy)),
                            outline=_melange(fond, self.c["barre"], 0.9), width=2)
            if k_gl > 0.6 and c and k_hy < 0.5:
                self._texte_centre(d, str(c), pn, (x0 + x1) / 2, y_axe - h - 46,
                                   _melange(fond, self.c["texte"], ((k_gl - 0.6) / 0.4) * (1 - 2 * k_hy)))
        if k_hy <= 0:
            return
        alpha = k_hy * (1 - 0.45 * k_pr)
        couleurs = (self.c["barre"], self.c["or"])
        pl = self.police("gras", 38)
        for gi, (eff, couleur) in enumerate(zip(groupes, couleurs)):
            pts = []
            for j, c in enumerate(eff):
                x0, x1 = x_de(o + j * w), x_de(o + (j + 1) * w)
                y = y_axe - c / e_max * h_max * k_hy
                pts += [(x0, y), (x1, y)]
            pts = [(pts[0][0], y_axe)] + pts + [(pts[-1][0], y_axe)]
            d.polygon(pts, fill=_melange(fond, couleur, 0.35 * alpha))
            d.line(pts, fill=_melange(fond, couleur, alpha), width=5)
            pic = max(range(n), key=lambda j: eff[j])
            xp = (x_de(o + pic * w) + x_de(o + (pic + 1) * w)) / 2
            yp = y_axe - eff[pic] / e_max * h_max - 60
            self._texte_centre(d, noms[gi], pl, xp, yp, _melange(fond, self.c["accent"] if gi else self.c["texte"], alpha),
                               g, dr)
        if k_pr > 0:
            self._texte_centre(d, "?", self.police("affichage", 120), dr - 50, haut - 10,
                               _melange(fond, self.c["accent"], k_pr))

    def _anim_questions(self, d, scene, plan, zone, t, ctx):
        """Choisir l'indicateur : deux questions côte à côte, chacune mène à son indicateur ; puis les deux."""
        from .rendu import _melange
        qs = scene.extra["animation"]["questions"]
        par = [p for p in plan if p["nature"] == "question"]
        p_deux = next((p for p in plan if p["nature"] == "deux"), None)
        k_d = _ease(self._avancee(p_deux, t)) if p_deux else 0.0
        panneaux = self._panneaux(zone, len(qs), gap=110)
        courante = self._phase_courante(plan, t)
        for i, (q, (g, haut, dr, bas)) in enumerate(zip(qs, panneaux)):
            p = par[i] if i < len(par) else None
            k = _ease(self._avancee(p, t)) if p else 1.0
            if k <= 0:
                continue
            fond = self._fond_a(g, haut)
            carte = _melange(fond, (255, 255, 255), 0.75) if sum(fond) > 380 else _melange(fond, self.c["barre"], 0.12)
            vive = t is None or plan.index(p) == courante if p else True
            orr = vive or k_d > 0
            y = haut + (1 - k) * 30
            d.rounded_rectangle((g, y, dr, bas), radius=24, fill=_melange(fond, carte, k),
                                outline=_melange(fond, self.c["or"] if orr and t is not None else self.c["barre"],
                                                 (0.9 if orr else 0.45) * k), width=3)
            hq = (bas - haut) * 0.30
            p_t, lignes, pas_, hh = self.ajuster_riche(q["question"], "gras", dr - g - 60, hq, 50, 30, 1.15, ctx,
                                                       equilibre=True)
            yt = y + 30 + (hq - hh) / 2
            for ligne in lignes:
                lw = self._largeur_ligne(ligne, p_t)
                self.ecrire_riche(d, [ligne], p_t, pas_, yt, self.c["texte"], None if k >= 1 else t,
                                  p["debut"] if p else 0.0, centre=False, x_gauche=(g + dr) / 2 - lw / 2)
                yt += pas_
            y_ic = y + 40 + hq
            h_ic = (bas - haut) * 0.30
            self._vignette(d, q["icone"], ((g + dr) / 2 - h_ic * 0.9, y_ic, (g + dr) / 2 + h_ic * 0.9, y_ic + h_ic), k,
                           fond)
            k_r = _ease((self._avancee(p, t) - 0.5) / 0.5) if (p and t is not None) else 1.0
            if k_r > 0:
                cx, y_f = (g + dr) / 2, y_ic + h_ic + 16
                d.line((cx, y_f, cx, y_f + 40), fill=_melange(fond, self.c["or"], k_r), width=4)
                d.polygon(((cx, y_f + 54), (cx - 12, y_f + 36), (cx + 12, y_f + 36)), fill=_melange(fond, self.c["or"], k_r))
                p_r, lr, pas_r, _ = self.ajuster_riche(q["reponse"], "gras", dr - g - 60, bas - y_f - 80, 52, 30, 1.1,
                                                       ctx, equilibre=True)
                yr = y_f + 68
                for ligne in lr:
                    lw = self._largeur_ligne(ligne, p_r)
                    self.ecrire_riche(d, [ligne], p_r, pas_r, yr, self.c["accent"], None, 0.0, centre=False,
                                      x_gauche=cx - lw / 2)
                    yr += pas_r
        if k_d > 0 and len(panneaux) == 2:
            (g1, h1, d1, b1), (g2, h2, d2, b2) = panneaux
            fond = self._fond_a(d1, h1)
            if g2 > d1:      # côte à côte
                cx, cy = (d1 + g2) / 2, (h1 + b1) / 2
            else:
                cx, cy = (g1 + d1) / 2, (b1 + h2) / 2
            r = 40 * k_d
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=self.c["or"])
            pp = self.police("affichage", int(64 * k_d) + 1)
            self._texte_centre(d, "+", pp, cx, cy - 64 * k_d * 0.66, _melange(self.c["or"], (255, 255, 255), 1.0))

    # ------------------------------------------------------------------ finance (parcours actuariel, 23/11/2026)
    def _somme_txt(self, v, unite, dec=2):
        txt = formater_nombre(round(v, dec), self.langue, dec)
        if unite == "€":
            return txt + " €" if self.langue == "fr" else "€" + txt
        if unite == "$":
            return "$" + txt
        return txt + (" " + unite if unite else "")

    def _taux_txt(self, v, dec=2):
        txt = formater_nombre(round(100 * v, dec), self.langue, dec)
        return txt + (" %" if self.langue == "fr" else "%")

    def _anim_capitalisation(self, d, scene, plan, zone, t, ctx):
        """Intérêt simple puis composé : une barre par année. Le capital est posé sur un axe coupé (signalé
        par un zigzag) pour que les intérêts restent visibles ; au-dessus, les intérêts du capital (une marche
        égale par an), puis les intérêts des intérêts, qui grossissent d'année en année."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        c0, i, n, unite = conf["capital"], conf["taux"], conf["annees"], conf.get("unite", "")
        lib = LIBELLES_FINANCE[self.langue]
        g, haut, dr, bas = zone
        par = {p["nature"]: p for p in plan}
        av = lambda nom: _ease(self._avancee(par[nom], t)) if nom in par else 0.0
        fond = self._fond_a(g, bas - 10)
        pl, pv, pa = self.police("regulier", 32), self.police("gras", 40), self.police("regulier", 30)
        y_axe = bas - 70
        h_cap = (y_axe - haut) * 0.22                    # hauteur du capital (axe coupé)
        haut_i = haut + 150                              # place pour les étiquettes du haut
        compose_fin = c0 * ((1 + i) ** n - 1)
        echelle = (y_axe - h_cap - haut_i) / max(compose_fin, n * c0 * i)
        x0 = g + 20
        pas = (dr - 40 - x0) / n
        wb = pas * 0.72
        # Légende (trois couches) en haut à gauche.
        couches = (("capital", self.c["barre"], 0.55, av("capital") if "capital" in par else 1.0),
                   ("simple", self.c["secondaire"], 0.75, av("simple")),
                   ("compose", self.c["or"], 0.95, av("compose")))
        yl = haut
        ecart = c0 * ((1 + i) ** n - 1 - i * n)
        for cle, couleur, force, k in couches:
            if k <= 0:
                continue
            d.rounded_rectangle((g, yl + 8, g + 34, yl + 38), radius=6, fill=_melange(fond, couleur, force * k))
            txt = lib["couche_" + cle]
            d.text((g + 48, yl), txt, font=pl, fill=_melange(fond, self.c["texte"], k))
            if cle == "compose":
                d.text((g + 48 + pl.getlength(txt + " "), yl), lib["ecart"].format(self._somme_txt(ecart, unite)),
                       font=self.police("gras", 32), fill=_melange(fond, self.c["accent"], k))
            yl += 44
        for a in range(1, n + 1):
            x = x0 + (a - 1) * pas + (pas - wb) / 2
            k_c = _ease((av("capital") * (n + 3) - a) / 3) if "capital" in par else 1.0
            if t is None:
                k_c = 1.0
            if k_c <= 0:
                continue
            ybas = y_axe
            d.rectangle((x, ybas - h_cap, x + wb, ybas), fill=_melange(fond, self.c["barre"], 0.55 * k_c))
            # Zigzag de l'axe coupé, au milieu du capital.
            ym = ybas - h_cap * 0.5
            pts = [(x + wb * j / 6, ym + (6 if j % 2 else -6)) for j in range(7)]
            d.line(pts, fill=_melange(fond, fond, k_c), width=5)
            y = ybas - h_cap
            k_s = _ease((av("simple") * (n + 3) - a) / 3)
            if k_s > 0:
                h = c0 * i * a * echelle * k_s
                d.rectangle((x, y - h, x + wb, y), fill=_melange(fond, self.c["secondaire"], 0.75))
                # Marches : une par année d'intérêts du capital.
                for j in (range(1, a) if n <= 12 else ()):
                    yj = y - c0 * i * j * echelle * k_s
                    d.line((x + 2, yj, x + wb - 2, yj), fill=_melange(fond, self.c["secondaire"], 0.35), width=2)
                y -= h
            k_k = _ease((av("compose") * (n + 3) - a) / 3)
            if k_k > 0:
                h = c0 * ((1 + i) ** a - 1 - i * a) * echelle * k_k
                if h > 0.5:
                    d.rectangle((x, y - h, x + wb, y), fill=_melange(fond, self.c["or"], 0.95))
        # Axe et années.
        d.line((g, y_axe, dr, y_axe), fill=_melange(fond, self.c["texte"], 0.6), width=3)
        etiquettes = sorted({1, n} | set(range(5, n + 1, 5 if n <= 30 else 10)))
        for a in etiquettes:
            xc = x0 + (a - 0.5) * pas
            self._texte_centre(d, str(a), pa, xc, y_axe + 12, _melange(fond, self.c["texte"], 0.8), g, dr)
        # Valeur de la dernière barre.
        xc = x0 + (n - 0.5) * pas
        k_s, k_k = av("simple"), av("compose")
        y_top_s = y_axe - h_cap - c0 * i * n * echelle
        a_s = k_s * (1 - min(1.0, k_k * 4))
        if a_s > 0.02:      # texte fondu dans la couleur du fond : on ne le dessine plus une fois effacé
            self._texte_centre(d, self._somme_txt(c0 * (1 + i * n), unite), pv, xc, y_top_s - 54,
                               _melange(fond, self.c["texte"], a_s), g, dr)
        if k_k > 0:
            y_top = y_top_s - c0 * ((1 + i) ** n - 1 - i * n) * echelle
            self._texte_centre(d, self._somme_txt(c0 * (1 + i) ** n, unite), pv, xc, y_top - 54,
                               _melange(fond, self.c["accent"], k_k), g, dr)
        # Capital, écrit dans la première barre.
        k_c = 1.0 if t is None or "capital" not in par else av("capital")
        txt = self._somme_txt(c0, unite, 0)
        d.text((g + 6, y_axe + 54), lib["capital_de"].format(txt), font=pl, fill=_melange(fond, self.c["texte"], k_c))

    def _anim_echeancier(self, d, scene, plan, zone, t, ctx):
        """Des versements sur une frise du temps ; chacun glisse vers aujourd'hui en rétrécissant (× vᵗ), puis
        les valeurs actuelles s'empilent à la date 0 : leur hauteur totale est la valeur actuelle."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        montants, dates, i = conf["montants"], conf["dates"], conf["taux"]
        unite, dec = conf.get("unite", ""), conf.get("decimales", 2)
        lib = LIBELLES_FINANCE[self.langue]
        v = 1 / (1 + i)
        va = [m * v ** a for m, a in zip(montants, dates)]
        n = len(montants)
        g, haut, dr, bas = zone
        par = {p["nature"]: p for p in plan}
        av = lambda nom: (1.0 if t is None else _ease(self._avancee(par[nom], t))) if nom in par else 0.0
        fond = self._fond_a(g, bas - 10)
        pa, pv, pt = self.police("regulier", 32), self.police("gras", 36), self.police("gras", 46)
        y_axe = bas - 80
        t_max = max(dates + [1])
        x_col = g + 250                                # colonne de la date 0 (valeurs actuelles à sa gauche)
        x_de = lambda a: x_col + (dr - 70 - x_col) * a / t_max
        dispo = y_axe - haut - 110
        echelle = min(dispo * 0.62 / max(montants), dispo / max(sum(va), 1e-9))
        wb = min(90.0, (dr - 70 - x_col) / max(t_max, 1) * 0.55, 140.0)
        d.line((g, y_axe, dr, y_axe), fill=_melange(fond, self.c["texte"], 0.6), width=3)
        d.polygon(((dr, y_axe), (dr - 20, y_axe - 11), (dr - 20, y_axe + 11)), fill=_melange(fond, self.c["texte"], 0.6))
        graduations = sorted(set(dates) | {0}) if t_max <= 12 else sorted(set(range(0, t_max + 1, 5)) | set(dates[-1:]))
        for a in graduations:
            x = x_de(a)
            d.line((x, y_axe - 8, x, y_axe + 8), fill=_melange(fond, self.c["texte"], 0.6), width=3)
            self._texte_centre(d, str(a), pa, x, y_axe + 14, _melange(fond, self.c["texte"], 0.8), g, dr)
        self._texte_centre(d, lib["aujourdhui"], pa, x_de(0), y_axe + 50, _melange(fond, self.c["accent"], 0.9), g, dr)
        k_f, k_a, k_s = av("flux"), av("actualisation"), av("somme")
        if "flux" not in par:
            k_f = 1.0
        pile = 0.0
        etiquettes = n <= 4
        for j, (m, a, p) in enumerate(zip(montants, dates, va)):
            kf = _ease((k_f * (n + 2) - j) / 2) if t is not None else 1.0
            if kf <= 0:
                continue
            ka = _ease((k_a * (n + 2) - j) / 2) if t is not None else (1.0 if "actualisation" in par else 0.0)
            ka = ka if "actualisation" in par else 0.0
            h0, h1 = m * echelle, p * echelle
            xa = x_de(a) - wb / 2
            xb = x_col - wb / 2
            ya, yb = y_axe, y_axe - pile
            x = xa + (xb - xa) * ka
            y_bas = ya + (yb - ya) * ka
            h = h0 + (h1 - h0) * ka
            couleur = _melange(self.c["barre"], self.c["or"], ka)
            if ka > 0 and a > 0:      # fantôme du versement à sa date : on voit ce qu'il est devenu
                d.rounded_rectangle((xa, ya - h0, xa + wb, ya - 2), radius=8,
                                    outline=_melange(fond, self.c["barre"], 0.6 * ka), width=3)
                if etiquettes:
                    self._texte_centre(d, self._somme_txt(m, unite, 0 if float(m).is_integer() else dec), pv,
                                       xa + wb / 2, ya - h0 - 48, _melange(fond, self.c["texte"], 0.55 * ka), g, dr)
                    self._texte_centre(d, f"× v{_exposant(a)}", pv, xa + wb / 2, ya - h0 - 96,
                                       _melange(fond, self.c["or"], ka), g, dr)
            if h * kf > 6:
                d.rounded_rectangle((x, y_bas - h * kf, x + wb, y_bas - 2), radius=min(8, int(h * kf / 3)),
                                    fill=_melange(fond, couleur, 0.85 * kf + 0.1))
            if ka < 0.95 and (etiquettes or j in (0, n - 1)):
                self._texte_centre(d, self._somme_txt(m, unite, 0 if float(m).is_integer() else dec), pv,
                                   x + wb / 2, y_bas - h - 48, _melange(fond, self.c["texte"], kf * (1 - ka)), g, dr)
            if ka > 0.95 and etiquettes:
                txt = self._somme_txt(p, unite, 0 if abs(p - round(p)) < 1e-9 else dec)
                d.text((x - 16 - pv.getlength(txt), y_bas - h / 2 - 22), txt, font=pv,
                       fill=_melange(fond, self.c["accent"], 1.0))
            if ka > 0:
                pile += h1 * ka
        if k_s > 0:
            total = sum(va)
            y = y_axe - total * echelle - 70
            txt = lib["valeur_actuelle"].format(self._somme_txt(total, unite, dec))
            d.text((max(g, x_col - pt.getlength(txt) / 2), max(haut, y - 50 * (1 - k_s))), txt, font=pt,
                   fill=_melange(fond, self.c["accent"], k_s))

    def _anim_escompte(self, d, scene, plan, zone, t, ctx):
        """Une facture payable dans un an. La banque la paie aujourd'hui en retenant l'escompte : la même somme
        vaut d du nominal (taux d'escompte, payé au début) et i du montant versé (taux d'intérêt, payé à la fin)."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        nominal, i, unite = conf["nominal"], conf["taux"], conf.get("unite", "")
        lib = LIBELLES_FINANCE[self.langue]
        dd = i / (1 + i)
        verse, retenue = nominal * (1 - dd), nominal * dd
        g, haut, dr, bas = zone
        par = {p["nature"]: p for p in plan}
        av = lambda nom: (1.0 if t is None else _ease(self._avancee(par[nom], t))) if nom in par else 0.0
        k_f, k_r, k_i = (av("facture") if "facture" in par else 1.0), av("retenue"), av("interet")
        fond = self._fond_a(g, bas - 10)
        pa, pv, pg = self.police("regulier", 32), self.police("gras", 38), self.police("gras", 44)
        y_axe = bas - 80
        x0, x1 = g + (dr - g) * 0.15, g + (dr - g) * 0.86
        d.line((g, y_axe, dr, y_axe), fill=_melange(fond, self.c["texte"], 0.6), width=3)
        for x, txt in ((x0, lib["aujourdhui"]), (x1, lib["dans_un_an"])):
            d.line((x, y_axe - 8, x, y_axe + 8), fill=_melange(fond, self.c["texte"], 0.6), width=3)
            self._texte_centre(d, txt, pa, x, y_axe + 16, _melange(fond, self.c["texte"], 0.85), g, dr)
        # Hauteur : la facture occupe 55 % de la zone ; la retenue est grossie pour rester visible.
        h_tot = max(120.0, y_axe - haut - 240)
        h_ret = max(h_tot * dd, 40.0)
        w = min(220.0, (dr - g) * 0.2)
        # La facture à un an.
        if k_f > 0:
            alpha = k_f * (1 - 0.65 * k_r)
            d.rounded_rectangle((x1 - w / 2, y_axe - h_tot, x1 + w / 2, y_axe - 2), radius=12,
                                outline=_melange(fond, self.c["barre"], alpha), width=4,
                                fill=_melange(fond, self.c["barre"], 0.25 * alpha))
            self._texte_centre(d, lib["facture"], pa, x1, y_axe - h_tot - 92, _melange(fond, self.c["texte"], alpha), g, dr)
            self._texte_centre(d, self._somme_txt(nominal, unite, 0), pg, x1, y_axe - h_tot - 52,
                               _melange(fond, self.c["texte"], alpha), g, dr)
        if k_r > 0:
            # Copie ramenée à aujourd'hui, coupée de la retenue.
            x = x1 + (x0 - x1) * min(1.0, k_r * 1.6)
            coupe = _ease((k_r - 0.55) / 0.45)
            h_v = h_tot - h_ret
            d.rounded_rectangle((x - w / 2, y_axe - h_v, x + w / 2, y_axe - 2), radius=12,
                                fill=_melange(fond, self.c["barre"], 0.85))
            yr = y_axe - h_v - 6 * (1 - coupe)
            xr = x + (w * 1.05) * coupe
            d.rounded_rectangle((xr - w / 2, yr - h_ret, xr + w / 2, yr), radius=10,
                                fill=_melange(fond, self.c["or"], 0.95))
            if coupe > 0:
                self._texte_centre(d, self._somme_txt(verse, unite), pv, x, y_axe - h_v / 2 - 20,
                                   _melange(self.c["barre"], (255, 255, 255), coupe), g, dr)
                d.text((xr + w / 2 + 14, yr - h_ret / 2 - 40), lib["escompte"], font=pa,
                       fill=_melange(fond, self.c["texte"], coupe))
                d.text((xr + w / 2 + 14, yr - h_ret / 2 - 2), self._somme_txt(retenue, unite), font=pv,
                       fill=_melange(fond, self.c["accent"], coupe))
        if k_i > 0:
            lignes = (lib["d_egal"].format(self._somme_txt(retenue, unite), self._somme_txt(nominal, unite, 0),
                                           self._taux_txt(dd)),
                      lib["i_egal"].format(self._somme_txt(retenue, unite), self._somme_txt(verse, unite),
                                           self._taux_txt(i)))
            for j, txt in enumerate(lignes):
                k = _ease((k_i * 2 - j))
                d.text((g, haut + j * 52), txt, font=pv,
                       fill=_melange(fond, self.c["accent"] if j == 0 else self.c["texte"], k))

    def _anim_frequences(self, d, scene, plan, zone, t, ctx):
        """Un an au même taux effectif : un seul saut en fin d'année, ou m petits sauts au taux équivalent ;
        les deux arrivent au même point. Le taux proportionnel (i / m) arriverait plus haut."""
        from .rendu import _melange
        conf = scene.extra["animation"]
        i, m, c0, unite = conf["taux"], conf.get("m", 12), conf.get("capital", 1000), conf.get("unite", "")
        lib = LIBELLES_FINANCE[self.langue]
        j = (1 + i) ** (1 / m) - 1
        g, haut, dr, bas = zone
        par = {p["nature"]: p for p in plan}
        av = lambda nom: (1.0 if t is None else _ease(self._avancee(par[nom], t))) if nom in par else 0.0
        k_a, k_m, k_e = (av("annuel") if "annuel" in par else 1.0), av("mensuel"), av("egalite")
        fond = self._fond_a(g, bas - 10)
        pa, pv, pl = self.police("regulier", 30), self.police("gras", 38), self.police("regulier", 32)
        y_axe, y_top = bas - 60, haut + 110
        gx, dx = g + 170, dr - 30
        v_max = c0 * (1 + i)
        y_de = lambda val: y_axe - 24 - (y_axe - 24 - y_top) * (val - c0) / (v_max - c0)
        x_de = lambda mois: gx + (dx - gx) * mois / m
        d.line((gx, y_axe, dx, y_axe), fill=_melange(fond, self.c["texte"], 0.6), width=3)
        for mois in range(m + 1):
            x = x_de(mois)
            d.line((x, y_axe - 6, x, y_axe + 6), fill=_melange(fond, self.c["texte"], 0.5), width=2)
        for mois, txt in ((0, "0"), (m, lib["un_an"])):
            self._texte_centre(d, txt, pa, x_de(mois), y_axe + 12, _melange(fond, self.c["texte"], 0.8), g, dr)
        for val in (c0, v_max):
            txt = self._somme_txt(val, unite, 0 if float(val).is_integer() else 2)
            fort = k_e if val == v_max else 0.0
            police = self.police("gras", 34) if fort > 0.5 else pa
            d.text((g, y_de(val) - 20), txt, font=police,
                   fill=_melange(fond, _melange(self.c["texte"], self.c["accent"], fort), 0.8 + 0.2 * fort))
            d.line((gx, y_de(val), dx, y_de(val)), fill=_melange(fond, self.c["texte"], 0.15), width=2)
        # Annuel : plat, puis un saut à la fin de l'année.
        if k_a > 0:
            xe = gx + (dx - gx) * min(1.0, k_a * 1.25)
            coul = _melange(fond, self.c["secondaire"], 0.9)
            d.line((gx, y_de(c0), xe, y_de(c0)), fill=coul, width=7)
            if k_a > 0.8:
                ks = (k_a - 0.8) / 0.2
                d.line((dx, y_de(c0), dx, y_de(c0) + (y_de(v_max) - y_de(c0)) * ks), fill=coul, width=7)
            if k_e < 0.98:
                d.text((g, haut + 44), lib["une_fois"].format(self._taux_txt(i, 1)), font=pl,
                       fill=_melange(fond, self.c["secondaire"], 0.9 * (1 - k_e)))
        # Mensuel : m marches au taux j.
        if k_m > 0:
            coul = _melange(fond, self.c["or"], 0.95)
            pts = [(x_de(0), y_de(c0))]
            val = c0
            for mois in range(1, m + 1):
                if k_m * m < mois - 1:
                    break
                x = x_de(min(mois, k_m * m + 0.0001)) if k_m * m < mois else x_de(mois)
                pts.append((x, y_de(val)))
                if k_m * m >= mois:
                    val *= 1 + j
                    pts.append((x, y_de(val)))
            d.line(pts, fill=coul, width=6, joint="curve")
            if k_e < 0.98:
                d.text((g, haut), lib["chaque_mois"].format(m, self._taux_txt(j, 4)), font=pl,
                       fill=_melange(fond, self.c["or"], 0.95 * (1 - k_e)))
        if k_e > 0:
            txt = lib["meme_arrivee"].format(self._somme_txt(v_max, unite, 0 if float(v_max).is_integer() else 2))
            d.text((g, haut), txt, font=pv, fill=_melange(fond, self.c["accent"], k_e))
            txt = lib["proportionnel"].format(m, self._taux_txt(j, 4), self._taux_txt(m * j, 4), self._taux_txt(i, 1))
            d.text((g, haut + 48), txt, font=pl, fill=_melange(fond, self.c["texte"], k_e))


FRACTIONS = {(1, 2): "½", (1, 3): "⅓", (2, 3): "⅔", (1, 4): "¼", (3, 4): "¾", (1, 5): "⅕", (1, 6): "⅙",
             (1, 8): "⅛"}


def _ordinal_en(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


LIBELLES_DONNEES = {"fr": {"mediane": "médiane", "moyenne": "moyenne", "hauteur_effectif": "Hauteur = effectif",
                           "hauteur_densite": "Hauteur = densité (effectif ÷ largeur)", "cagnotte": "Cagnotte :",
                           "moyenne_simple": "moyenne simple", "moyenne_ponderee": "moyenne pondérée",
                           "classes_de": "Classes de {} {}", "tendance": "Tendance fréquente, pas une loi",
                           "queue_droite": "Traîne à droite", "symetrique": "Symétrique",
                           "queue_gauche": "Traîne à gauche", "egales": "moyenne = médiane"},
                    "en": {"mediane": "median", "moyenne": "mean", "hauteur_effectif": "Height = count",
                           "hauteur_densite": "Height = density (count ÷ width)", "cagnotte": "Kitty:",
                           "moyenne_simple": "simple mean", "moyenne_ponderee": "weighted mean",
                           "classes_de": "{}-{} bins", "tendance": "A common tendency, not a law",
                           "queue_droite": "Right tail", "symetrique": "Symmetric",
                           "queue_gauche": "Left tail", "egales": "mean = median"}}


def _pas_rond(brut: float) -> float:
    """Pas de graduation « rond » (1, 2 ou 5 × 10^k) proche de `brut`."""
    if brut <= 0:
        return 1.0
    e = 10 ** math.floor(math.log10(brut))
    return next(m * e for m in (1, 2, 5, 10) if m * e >= brut)


LIBELLES_FINANCE = {
    "fr": {"couche_capital": "capital placé", "couche_simple": "intérêts du capital",
           "couche_compose": "intérêts des intérêts", "ecart": ": + {}",
           "annees": "années", "capital_de": "Capital : {} (axe coupé)", "aujourdhui": "aujourd'hui",
           "valeur_actuelle": "Valeur actuelle : {}", "dans_un_an": "dans un an", "facture": "Facture",
           "escompte": "escompte retenu", "d_egal": "d = {} ÷ {} = {}  (payé au début)",
           "i_egal": "i = {} ÷ {} = {}  (payé à la fin)", "un_an": "1 an",
           "une_fois": "une fois par an : {}", "chaque_mois": "{} fois par an : {} chaque mois",
           "meme_arrivee": "Même arrivée : {}",
           "proportionnel": "Mais {} × {} = {} : moins que {}"},
    "en": {"couche_capital": "amount invested", "couche_simple": "interest on the capital",
           "couche_compose": "interest on interest", "ecart": ": + {}",
           "annees": "years", "capital_de": "Capital: {} (broken axis)", "aujourdhui": "today",
           "valeur_actuelle": "Present value: {}", "dans_un_an": "in one year", "facture": "Invoice",
           "escompte": "discount kept", "d_egal": "d = {} ÷ {} = {}  (paid up front)",
           "i_egal": "i = {} ÷ {} = {}  (paid at the end)", "un_an": "1 year",
           "une_fois": "once a year: {}", "chaque_mois": "{} times a year: {} each month",
           "meme_arrivee": "Same end point: {}",
           "proportionnel": "But {} × {} = {}: less than {}"},
}

_EXPOSANTS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _exposant(n: int) -> str:
    return str(n).translate(_EXPOSANTS)
