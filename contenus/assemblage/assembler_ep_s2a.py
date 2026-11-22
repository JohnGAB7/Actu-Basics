"""Assemble la fiche de production de l'épisode long EP-S2A à partir des cinq fiches de chapitre
validées et de la fiche de conception contenus/conception/EP-S2A.yaml (validée par JG le 22/11/2026)."""
import copy
import sys
from pathlib import Path

import yaml

R = Path(sys.argv[1])
F = R / "contenus/fiches"
CHAP = [F / "2026-11-n1-s2-01-frequences-et-tableaux.yaml",
        F / "2026-11-n1-s2-02-diagrammes-en-barres-et-histogrammes.yaml",
        F / "2026-11-n1-s2-03-la-forme-d-une-distribution.yaml",
        F / "2026-11-n1-s2-04-ce-que-dit-vraiment-la-moyenne.yaml",
        F / "2026-11-pilote-s2-05-moyenne-ou-mediane.yaml"]
conc = yaml.safe_load(open(R / "contenus/conception/EP-S2A.yaml"))
blocs = {b.get("id", b["bloc"]): b for b in conc["deroule_episode"]}
chap = [yaml.safe_load(open(f)) for f in CHAP]
T = [0, 4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44]
T = T[1:]


def S(type_, texte, voix, **extra):
    # univers « immersif » (fond sombre) : laboratoires et transformations de données, 3 à 6 séquences.
    s = {"type": type_, "texte": texte}
    s.update(extra)
    s["voix_off"] = voix
    return s


TRAJETS = [4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44]
CAFE = [1600, 1800, 1900, 2000, 2200, 2300, 2500, 2700, 2800]


def pastilles(texte, voix, largeur, l, etapes=None, verifier=None):
    """Les 20 salariés en pastilles : posées sur l'axe, rangées par classe, puis l'histogramme."""
    s = {"type": "animation", "texte": texte, "univers": "immersif",
         "animation": {"modele": "pastilles", "valeurs": TRAJETS, "largeur_classe": largeur, "unite": "minutes"}}
    if etapes:
        s["etapes"] = etapes
    s["voix_off"] = voix
    if verifier:
        s["verifier"] = verifier
    return s


def curseur(texte, voix, valeurs, indice, vers, axe_max, unite, etapes, verifier, decimales=0):
    return {"type": "animation", "texte": texte, "univers": "immersif",
            "animation": {"modele": "curseur", "valeurs": valeurs, "indice": indice, "vers": vers,
                          "axe_max": axe_max, "unite": unite, "decimales": decimales},
            "etapes": etapes, "voix_off": voix, "verifier": verifier}


def histo(texte, points, largeur, voix, axe_x, axe_y, y_max, note=None, verifier=None, decimales=None):
    c = {"style": "histogramme", "points": points, "largeur_classe": largeur, "valeurs": decimales is None,
         "y_min": 0, "y_max": y_max, "axe_x": axe_x, "axe_y": axe_y}
    if decimales is not None:
        c["decimales_y"] = decimales
    s = {"type": "courbe", "texte": texte, "courbe": c}
    if note:
        s["note"] = note
    s["voix_off"] = voix
    if verifier:
        s["verifier"] = verifier
    return s


def chapitre(k, d, l):
    """Scènes du chapitre k (1 à 5) dans la langue l, avec les changements validés."""
    sc = copy.deepcopy(d["editions"][l]["scenes"])
    titre_chap = blocs[["S2.01", "S2.02", "S2.03", "S2.04", "S2.05"][k - 1]]["titre"][l]
    out = []
    j = 0
    for i, s in enumerate(sc):
        t = s["type"]
        if t == "fin" or (t == "etapes" and i == len(sc) - 2):
            continue                                  # « À retenir » et fin : remplacés par la synthèse
        if t == "accroche":                           # l'accroche du chapitre devient son titre numéroté
            out.append({"type": "titre", "numero": str(k), "texte": titre_chap.split(". ", 1)[1],
                        "voix_off": s["voix_off"]})
            continue
        if t == "titre":
            j += 1
            s["numero"] = f"{k}.{j}"
        out.append(s)
    return out


def modifier(k, scenes, l):
    fr = l == "fr"
    if k == 2:     # borne gauche incluse, dite à la première classe ; renvoi au chapitre 1
        for s in scenes:
            if "note" in s and ("épisode précédent" in s["note"] or "last episode" in s["note"]):
                s["note"] = "Entreprise fictive de 20 salariés (exercice du chapitre 1)." if fr else "Fictional company of 20 employees (chapter 1 exercise)."
                s["voix_off"] = (s["voix_off"].replace("de l'épisode précédent", "de l'exercice du chapitre 1")
                                 .replace("from the last episode", "from the chapter 1 exercise"))
        for s in scenes:
            if s["type"] == "courbe" and s["courbe"].get("largeur_classe") == 10:
                s["voix_off"] += (" Chaque classe contient sa borne gauche, pas sa borne droite : un trajet de vingt minutes compte dans la classe de vingt à trente."
                                  if fr else " Each bin includes its left edge but not its right one: a 20-minute trip counts in the 20-to-30 bin.")
                break
    if k == 3:
        garde = []
        for s in scenes:
            if s["type"] == "chiffre" and s.get("valeur") == 170:
                deplacee[l] = s                         # passe à la fin du chapitre 4
                continue
            if s["type"] == "etapes" and ("moyenne" in s["voix_off"] or "mean" in s["voix_off"]) and len(s.get("etapes", [])) == 2:
                s["voix_off"] = s["voix_off"].rsplit(". ", 1)[0] + (". Ce qu'une queue fait à la moyenne, on le verra au chapitre 5."
                                                                    if fr else ". What a tail does to the mean, we'll see in chapter 5.")
            garde.append(s)
        scenes[:] = garde
        # ouverture du chapitre sur les trajets de l'entreprise
        scenes.insert(1, pastilles(
            "Nos *20 salariés* : une bosse, une petite queue à droite" if fr else "Our *20 employees*: one hump, a small right tail",
            ("Revenons à nos vingt salariés. Leur histogramme a une bosse, entre dix et trente minutes, et une petite queue à droite : le salarié qui met quarante-quatre minutes. C'est une propriété de ces données fictives, pas une loi des trajets réels."
             if fr else "Back to our twenty employees. Their histogram has one hump, between ten and thirty minutes, and a small right tail: the employee who takes forty-four minutes. That's a property of these made-up data, not a law of real commutes."),
            10, l,
            etapes=(["Un point par salarié", "Une *bosse* entre 10 et 30 minutes", "Une petite *queue* à droite : 44 minutes"] if fr
                    else ["One dot per employee", "A *hump* between 10 and 30 minutes", "A small right *tail*: 44 minutes"]),
            verifier=[{"expression": "3 + 7 + 6 + 3 + 1", "attendu": 20, "libelle": "Total des salariés"}]))
        # pas de moyenne avant le chapitre 4 dans la scène des tailles
        for s in scenes:
            if s["type"] == "texte" and ("plusieurs groupes" in s["texte"] or "several groups" in s["texte"] or "groups" in s["texte"]):
                s["voix_off"] = ("Un seul nombre « central » ne décrirait ni les femmes, ni les hommes de ce groupe. Retenez ce réflexe : deux bosses signalent souvent plusieurs groupes mélangés. Avant de résumer, séparez-les."
                                 if fr else "A single 'central' number would describe neither the women nor the men in this group. Remember this reflex: two peaks often signal several groups mixed together. Before summarizing, separate them.")
    if k == 4:
        s = deplacee[l]
        s["voix_off"] = ("Souvenez-vous des tailles à deux bosses. On ne connaît que les classes : on prend le milieu de chaque classe, par exemple cent cinquante-deux et demi pour la classe de cent cinquante à cent cinquante-cinq, comme valeur de ses adultes. On obtient une moyenne approchée d'environ cent soixante-dix centimètres. Elle tombe dans le creux, là où il y a peu de monde : une moyenne peut ne décrire personne."
                         if fr else "Remember the two-peaked heights. We only know the bins, so we take the middle of each bin, for example a hundred and fifty-two and a half for the bin from a hundred and fifty to a hundred and fifty-five, as the value of its adults. That gives an approximate mean of about a hundred and seventy centimetres. It falls in the dip, where there are few people: a mean can describe no one.")
        s["note"] = ("Moyenne approchée par les centres de classes : environ 169,8 cm." if fr
                     else "Approximate mean from bin midpoints: about 169.8 cm.")
        scenes.append(s)
        scenes.append(S("chiffre", "le trajet moyen de nos *20 salariés*" if fr else "the mean trip of our *20 employees*",
                        ("Et nos vingt salariés ? Leurs trajets font quatre cent vingt-cinq minutes au total. Divisé par vingt, cela donne vingt et une minutes et quart. C'est ce qu'aurait chacun si l'on partageait également le total des durées individuelles. Ce total additionne des trajets séparés : ce n'est pas un temps passé ensemble."
                         if fr else "And our twenty employees? Their trips add up to 425 minutes. Divided by twenty, that's twenty-one and a quarter minutes. It's what each would have if the total of individual durations were shared equally. That total adds up separate trips: it isn't time spent together."),
                        valeur=21.25, decimales=2, suffixe={"fr": " min", "en": " min"},
                        note=("Total des 20 trajets : 425 minutes ; 425 ÷ 20 = 21,25." if fr else "Total of the 20 trips: 425 minutes; 425 ÷ 20 = 21.25."),
                        verifier=[{"expression": " + ".join(map(str, T)), "attendu": 425, "libelle": "Somme des 20 trajets"},
                                  {"expression": "425 / 20", "attendu": 21.25, "libelle": "Trajet moyen"}]))
    return scenes


deplacee = {}


ECRAN_TRANSITION = {
    1: {"fr": "Gardez ces *20 salariés* en tête", "en": "Keep these *20 employees* in mind"},
    2: {"fr": "Et si l'on changeait *nous-mêmes* les classes ?", "en": "What if we changed the bins *ourselves*?"},
    3: {"fr": "Un seul nombre pour résumer : *la moyenne* ?", "en": "One number to sum it up: *the mean*?"},
    4: {"fr": "21,25 min : le trajet d'un salarié *typique* ?", "en": "21.25 min: a *typical* employee's trip?"},
}


def transition(k, l):
    b = blocs[["S2.01", "S2.02", "S2.03", "S2.04", "S2.05"][k - 1]]
    return S("texte", ECRAN_TRANSITION[k][l], b["transition"][l])


def _court(phrase):
    p = phrase.split(". ")[0].rstrip(".")
    return p if len(p) <= 90 else p[:87].rsplit(" ", 1)[0] + "…"


def lab1(l):
    fr = l == "fr"
    ax = "Temps de trajet (minutes)" if fr else "Commuting time (minutes)"
    ay = "Effectif (salariés)" if fr else "Count (employees)"
    b = blocs["LAB-1"]
    return [
        S("titre", "Laboratoire : la largeur des classes" if fr else "Lab: bin width",
          "Laboratoire. Prenons les vingt temps de trajet et changeons nous-mêmes la largeur des classes." if fr
          else "Lab time. Let's take the twenty travel times and change the bin width ourselves.", numero="2.4",
          univers="immersif"),
        pastilles("Classes de *20 minutes*" if fr else "*20-minute* bins",
                  "Classes de vingt minutes : dix, neuf, un. Le sommet a disparu." if fr else "Twenty-minute bins: ten, nine, one. The peak has gone.",
                  20, l, verifier=[{"expression": "3 + 7", "attendu": 10, "libelle": "0 à 20 minutes"}]),
        pastilles("Classes de *10 minutes*" if fr else "*10-minute* bins",
                  "Classes de dix minutes : trois, sept, six, trois, un. Une bosse nette." if fr else "Ten-minute bins: three, seven, six, three, one. A clear hump.",
                  10, l),
        pastilles("Classes de *5 minutes* : deux « sommets » ?" if fr else "*5-minute* bins: two 'peaks'?",
                  ("Classes de cinq minutes. Le trajet de quinze minutes est compté dans la classe de quinze à vingt : la borne gauche est incluse. Deux sommets apparaissent, à quinze et à vingt-cinq minutes. Ils ne tiennent qu'à un ou deux salariés. Trop larges, les classes cachent ; trop étroites, elles inventent."
                   if fr else "Five-minute bins. The fifteen-minute trip counts in the fifteen-to-twenty bin: the left edge is included. Two peaks appear, at fifteen and at twenty-five minutes. They rest on one or two employees. Too wide, bins hide; too narrow, they invent."),
                  5, l, verifier=[{"expression": "1 + 2 + 3 + 4 + 2 + 4 + 1 + 2 + 1", "attendu": 20, "libelle": "Classes de 5 minutes"}]),
        histo("Âges de 40 visiteurs : *hauteur = effectif*" if fr else "Ages of 40 visitors: *height = count*",
              [[0, 8], [20, 12], [30, 20]], 30,
              ("Second réglage : les âges de quarante visiteurs, en classes inégales. Avec l'effectif comme hauteur, les trente à soixante ans dominent."
               if fr else "Second setting: the ages of forty visitors, in unequal bins. With the count as the height, the thirty-to-sixty group dominates."),
              "Âge (années)" if fr else "Age (years)", "Effectif (visiteurs)" if fr else "Count (visitors)", 24),
        histo("Hauteur = *densité d'effectif*" if fr else "Height = *count density*",
              [[0, 0.4], [20, 1.2], [30, 0.6667]], 30,
              ("On bascule sur la densité d'effectif : l'effectif divisé par la largeur, en visiteurs par année d'âge. Zéro virgule quatre, un virgule deux, environ zéro virgule soixante-sept. La classe la plus dense est vingt à trente ans. Et l'aire de chaque rectangle redonne son effectif : un virgule deux fois dix ans, douze visiteurs. L'aire totale vaut quarante, le nombre de visiteurs."
               if fr else "We switch to count density: the count divided by the width, in visitors per year of age. Zero point four, one point two, about zero point six seven. The densest bin is twenty to thirty. And each rectangle's area gives back its count: one point two times ten years, twelve visitors. The total area is forty, the number of visitors."),
              "Âge (années)" if fr else "Age (years)", "Densité (visiteurs par an)" if fr else "Density (visitors per year)", 1.6,
              note=("Aires : 0,4 × 20 = 8 ; 1,2 × 10 = 12 ; ⅔ × 30 = 20 ; total 40 (hauteur 0,67 arrondie)." if fr
                    else "Areas: 0.4 × 20 = 8; 1.2 × 10 = 12; ⅔ × 30 = 20; total 40 (height 0.67 rounded)."),
              decimales=1,
              verifier=[{"expression": "1.2 * 10", "attendu": 12, "libelle": "Aire 20–30 ans"},
                        {"expression": "0.4 * 20 + 1.2 * 10 + 20 / 30 * 30", "attendu": 40, "libelle": "Aire totale"}]),
    ]


def lab2(l):
    fr = l == "fr"
    e = lambda x: f"{x:,}".replace(",", " ") if fr else f"{x:,}"
    return [
        S("titre", "Laboratoire : une seule valeur extrême" if fr else "Lab: a single extreme value",
          "Deuxième laboratoire. Faisons bouger une seule valeur, et regardons qui suit." if fr
          else "Second lab. Let's move a single value and watch who follows.", numero="5.4", univers="immersif"),
        curseur("Le dixième client : *curseur* de 2 300 à 200 000 €" if fr else "The tenth customer: *slider* from €2,300 to €200,000",
                ("Les neuf salaires du café, et un dixième client dont on fait monter le salaire. À chaque position, on range à nouveau les dix salaires et on recalcule. À deux mille trois cents euros : moyenne deux mille deux cent dix, médiane deux mille deux cent cinquante. À cinquante mille : moyenne six mille neuf cent quatre-vingts, médiane toujours deux mille deux cent cinquante. À deux cent mille : moyenne vingt et un mille neuf cent quatre-vingts. La médiane ne bouge pas : dès deux mille trois cents euros, le dixième client se range après le sixième salaire, et les deux valeurs du milieu restent deux mille deux cents et deux mille trois cents."
           if fr else "The café's nine salaries, and a tenth customer whose salary we raise. At each position, we sort the ten salaries again and recompute. At two thousand three hundred euros: mean two thousand two hundred and ten, median two thousand two hundred and fifty. At fifty thousand: mean six thousand nine hundred and eighty, median still two thousand two hundred and fifty. At two hundred thousand: mean twenty-one thousand nine hundred and eighty. The median doesn't move: from two thousand three hundred up, the tenth customer sorts after the sixth salary, so the two middle values stay two thousand two hundred and two thousand three hundred."),
                CAFE + [2300], 9, 200000, 3600, "€",
                (["Neuf salaires, et un *dixième client* à 2 300 €", f"Médiane : *{e(2250)} €*", f"Moyenne : *{e(2210)} €*",
                  "Le dixième monte à 200 000 € : la moyenne *s'envole*, la médiane *reste*"] if fr else
                 ["Nine salaries, and a *tenth customer* at €2,300", f"Median: *€{e(2250)}*", f"Mean: *€{e(2210)}*",
                  "The tenth climbs to €200,000: the mean *flies off*, the median *stays*"]),
                [{"expression": "(19800 + 2300) / 10", "attendu": 2210, "libelle": "Moyenne à 2 300 €"},
                 {"expression": "(19800 + 50000) / 10", "attendu": 6980, "libelle": "Moyenne à 50 000 €"},
                 {"expression": "(19800 + 200000) / 10", "attendu": 21980, "libelle": "Moyenne à 200 000 €"},
                 {"expression": "(2200 + 2300) / 2", "attendu": 2250, "libelle": "Médiane dès 2 300 €"}]),
        curseur("Un salarié *déménage* : 44 → 120 minutes" if fr else "One employee *moves*: 44 → 120 minutes",
                ("Retour à l'entreprise. On n'ajoute personne : le salarié qui mettait quarante-quatre minutes déménage et en met cent vingt. Ce sont toujours les mêmes vingt salariés. La moyenne passe de vingt et une minutes et quart à vingt-cinq minutes et cinq centièmes. La médiane reste à vingt minutes. Un seul individu a bougé, et seule la moyenne l'a suivi."
           if fr else "Back to the company. No one is added: the employee who took forty-four minutes moves and now takes one hundred and twenty. Still the same twenty employees. The mean goes from twenty-one and a quarter to twenty-five point zero five minutes. The median stays at twenty minutes. One individual moved, and only the mean followed."),
                TRAJETS, 19, 120, 55, "minutes",
                (["Les mêmes *20 salariés*", "Médiane : *20 min*", "Moyenne : *21,25 min*",
                  "44 → 120 minutes : moyenne *25,05 min*, médiane *20 min*"] if fr else
                 ["The same *20 employees*", "Median: *20 min*", "Mean: *21.25 min*",
                  "44 → 120 minutes: mean *25.05 min*, median *20 min*"]),
                [{"expression": "(425 - 44 + 120) / 20", "attendu": 25.05, "libelle": "Moyenne après le déménagement"},
                 {"expression": "(19 + 21) / 2", "attendu": 20, "libelle": "Médiane des trajets"}], decimales=2),
    ]


def anim(texte, voix, conf, etapes, verifier=None, note=None, univers=None):
    s = {"type": "animation", "texte": texte, "animation": conf, "etapes": etapes}
    if univers:
        s["univers"] = univers
    if note:
        s["note"] = note
    s["voix_off"] = voix
    if verifier:
        s["verifier"] = verifier
    return s


def _exprs(s):
    return [v["expression"] for v in s.get("verifier", [])]


def visuels(sc, l):
    """Trois scènes trop textuelles deviennent des animations (revue ChatGPT du 22/11/2026, retenue par JG) :
    densité des classes inégales, point d'équilibre de la moyenne, médiane par élimination."""
    fr = l == "fr"
    out = []
    for i, s in enumerate(sc):
        if s["type"] == "courbe" and s["courbe"].get("points") == [[0, 0.3], [10, 0.7], [20, 0.3333]]:
            out.append(anim(
                s["texte"],
                ("Reprenons la construction trompeuse : avec l'effectif comme hauteur, la grande classe de vingt à cinquante minutes écrase tout. "
                 "Passons à la densité : les barres montent ou descendent, et les pastilles, une par salarié, prennent le même espacement partout ; la classe de dix à vingt minutes redevient la plus dense. "
                 "La surface de chaque barre redonne son effectif : zéro virgule trois fois dix, trois ; zéro virgule sept fois dix, sept ; un tiers fois trente, dix."
                 if fr else
                 "Back to the misleading build: with the count as the height, the big twenty-to-fifty-minute bin crushes everything. "
                 "Let's switch to density: the bars rise or fall, and the dots, one per employee, take the same spacing everywhere; the ten-to-twenty-minute bin is the densest again. "
                 "Each bar's area gives back its count: zero point three times ten, three; zero point seven times ten, seven; a third times thirty, ten."),
                {"modele": "densite", "bornes": [0, 10, 20, 50], "effectifs": [3, 7, 10], "unite": "minutes"},
                (["Hauteur = effectif : la grande classe *écrase tout*", "Hauteur = *densité* : le même espacement partout",
                  "Surface = densité × largeur = *effectif*"] if fr else
                 ["Height = count: the wide bin *crushes everything*", "Height = *density*: the same spacing everywhere",
                  "Area = density × width = *count*"]),
                verifier=s.get("verifier")))   # note inutile : les surfaces sont écrites sur les barres
            continue
        if s["type"] == "texte" and i and "(5 - 15) + (10 - 15) + (15 - 15) + (30 - 15)" in _exprs(sc[i - 1]):
            out.append(anim(
                "La moyenne, *point d'équilibre*" if fr else "The mean, a *balance point*",
                ("Posons les quatre montants de la cagnotte sur une planche : cinq, dix, quinze et trente euros. "
                 "Pour que la planche tienne à l'horizontale, l'appui doit se placer exactement à la moyenne, quinze euros. "
                 "Là, les écarts se compensent : moins dix et moins cinq d'un côté, plus quinze de l'autre, zéro au total ; c'est toujours vrai pour la moyenne, et une seule valeur très loin suffit à déplacer l'équilibre."
                 if fr else
                 "Let's put the four amounts from the kitty on a plank: five, ten, fifteen and thirty euros. "
                 "For the plank to stay level, the pivot must sit exactly at the mean, fifteen euros. "
                 "There, the deviations cancel out: minus ten and minus five on one side, plus fifteen on the other, zero in total; that's always true for the mean, and a single value far away is enough to shift the balance."),
                {"modele": "equilibre", "valeurs": [5, 10, 15, 30], "unite": "€"},
                (["Quatre amis : *5, 10, 15 et 30 €*", "L'appui à *15 €* : la planche s'équilibre",
                  "Les écarts se *compensent* : leur somme vaut 0"] if fr else
                 ["Four friends: *€5, €10, €15 and €30*", "Pivot at *€15*: the plank balances",
                  "The deviations *cancel out*: they sum to 0"]),
                verifier=[{"expression": "(5 + 10 + 15 + 30) / 4", "attendu": 15, "libelle": "Moyenne de la cagnotte"},
                          {"expression": "(5 - 15) + (10 - 15) + (15 - 15) + (30 - 15)", "attendu": 0,
                           "libelle": "Somme des écarts à la moyenne"}]))
            continue
        if s["type"] == "formule" and "(9 + 1) / 2" in _exprs(s):
            out.append(anim(
                "La médiane *par élimination*" if fr else "The median *by elimination*",
                ("Revenons au café et rangeons ses neuf premiers salaires, du plus bas au plus haut. "
                 "Barrons le plus bas et le plus haut, puis recommençons, deux par deux. "
                 "Il reste la cinquième valeur, deux mille deux cents euros : c'est la médiane, à la position n plus un sur deux. "
                 "Le client riche entre, avec deux cent mille euros : il y a maintenant dix salaires. "
                 "On barre à nouveau deux par deux, et il en reste deux, la cinquième et la sixième : la médiane est leur moyenne, deux mille deux cent cinquante euros."
                 if fr else
                 "Back to the café: let's sort its first nine salaries, from lowest to highest. "
                 "Cross out the lowest and the highest, then again, two by two. "
                 "The fifth value is left, two thousand two hundred euros: that's the median, at position n plus one over two. "
                 "The rich customer walks in, with two hundred thousand euros: there are now ten salaries. "
                 "Cross out two by two again, and two are left, the fifth and the sixth: the median is their mean, two thousand two hundred and fifty euros."),
                {"modele": "elimination", "valeurs": CAFE, "ajout": 200000, "unite": "€"},
                (["Neuf salaires, *rangés*", "On barre le plus *bas* et le plus *haut*", "Il reste le *milieu* : la 5e valeur",
                  "Le client à *200 000 €* entre", "Dix valeurs : la moyenne des *deux du milieu*"] if fr else
                 ["Nine salaries, *sorted*", "Cross out the *lowest* and the *highest*", "The *middle* is left: the 5th value",
                  "The *€200,000* customer walks in", "Ten values: the mean of the *two middle ones*"]),
                verifier=[{"expression": "(9 + 1) / 2", "attendu": 5, "libelle": "Position du milieu, 9 valeurs"},
                          {"expression": "(10 + 1) / 2", "attendu": 5.5, "libelle": "Position du milieu, 10 valeurs"},
                          {"expression": "(2200 + 2300) / 2", "attendu": 2250, "libelle": "Médiane des 10 salaires"}]))
            continue
        if (s["type"] == "etapes" and "(5 - 15) + (10 - 15) + (15 - 15) + (30 - 15)" in _exprs(s)
                and i + 1 < len(sc) and sc[i + 1]["type"] == "texte"):
            continue        # « Les écarts à la moyenne » : tracés par l'animation d'équilibre qui suit
        if s["type"] == "etapes" and "(2200 + 2300) / 2" in _exprs(s) and out and out[-1]["type"] == "animation":
            continue        # « La médiane du café » : montrée par l'élimination
        out.append(s)
    return out


def episode(l):
    fr = l == "fr"
    b = blocs
    sc = [S("accroche", "Vingt salariés. *Qui dit vrai* : la moyenne ou la médiane ?" if fr else "Twenty employees. *Which tells the truth*: the mean or the median?",
            b["ouverture"][l]),
          S("accueil", "Bonjour, et *bienvenue* !" if fr else "Hi, and *welcome*!", b["accueil"][l]),
          S("etapes", "Au programme" if fr else "In this episode", b["plan"][l],
            etapes=[c["titre"][l] for c in conc["deroule_episode"] if c["bloc"] == "chapitre"])]
    for k, d in enumerate(chap, 1):
        sc += modifier(k, chapitre(k, d, l), l)
        if k < 5:
            sc.append(transition(k, l))
        if k == 2:
            sc += lab1(l)
        if k == 5:
            sc += lab2(l)
    sc = visuels(sc, l)
    sy = b["synthese"][l]
    sc.append(S("etapes", "À retenir" if fr else "Key takeaways", sy,
                etapes=(["Comparer des *fréquences*, pas des effectifs", "Classes inégales : la *surface* compte",
                         "Regarder la *forme* avant tout calcul", "Moyenne : *partage égal* du total", "Médiane : coupe en *deux* ; queue à droite, moyenne au-dessus"]
                        if fr else ["Compare *frequencies*, not counts", "Unequal bins: *area* counts",
                                    "Look at the *shape* before any calculation", "Mean: an *equal share* of the total", "Median: splits in *two*; right tail, mean above"])))
    ex = b["exercice_de_synthese"]
    sc.append(S("exercice", "10 trajets : 5, 8, 12, 15, 15, 18, 22, 25, 30, *90* min. Part sous 20 min, forme, moyenne, médiane ?" if fr
                else "10 trips: 5, 8, 12, 15, 15, 18, 22, 25, 30, *90* min. Share under 20 min, shape, mean, median?", ex[l], pause=ex["pause_secondes"]))
    sc.append(S("correction", "", ex["correction_" + l],
                etapes=(["Moins de 20 min : 6 sur 10, *60 %*", "Forme : *queue à droite* (le trajet de 90 min)",
                         "Moyenne : 240 ÷ 10 = *24 min*", "Médiane : (15 + 18) ÷ 2 = *16,5 min*", "7 sur 10 sous la moyenne : trajet typique *16,5 min*"]
                        if fr else ["Under 20 min: 6 out of 10, *60%*", "Shape: *right tail* (the 90-minute trip)",
                                    "Mean: 240 ÷ 10 = *24 min*", "Median: (15 + 18) ÷ 2 = *16.5 min*", "7 out of 10 below the mean: typical trip *16.5 min*"]),
                verifier=[{"expression": "5+8+12+15+15+18+22+25+30+90", "attendu": 240, "libelle": "Somme"},
                          {"expression": "240 / 10", "attendu": 24, "libelle": "Moyenne"},
                          {"expression": "(15 + 18) / 2", "attendu": 16.5, "libelle": "Médiane"},
                          {"expression": "6 / 10 * 100", "attendu": 60, "libelle": "Part sous 20 min"},
                          {"expression": "(240 - 90 + 35) / 10", "attendu": 18.5, "libelle": "Moyenne si 90 était 35"}]))
    sc[-1].pop("texte")
    c = sc[-1]
    vo = c["voix_off"]
    coupe = vo.index("Quatre" if fr else "Four")
    c["voix_off"], suite = vo[:coupe].strip(), vo[coupe:].strip()
    et, c["etapes"] = c["etapes"][4:], c["etapes"][:4]
    v = c.pop("verifier")
    c["verifier"] = v[:4]
    sc.append(S("etapes", "Correction (suite)" if fr else "Answer (continued)", suite, etapes=et + [
        "Si 90 était une erreur pour 35 : moyenne *18,5 min*, médiane inchangée" if fr
        else "If 90 were a typo for 35: mean *18.5 min*, median unchanged"], verifier=v[4:]))
    sc.append(S("cloture", ("Prochain épisode : *les écarts*. Une question ? *En commentaire*" if fr
                            else "Next episode: *spread*. A question? *Ask in the comments*"), b["cloture"][l]))
    sc.append(S("fin", "Éveiller par les chiffres." if fr else "Enlightening through numbers.",
                "ACTU-BASICS. Éveiller par les chiffres." if fr else "ACTU-BASICS. Enlightening through numbers."))
    return sc


base = chap[4]
fiche = {
    "id": "2026-12-ep-s2a-resumer-des-donnees",
    "type_fiche": "pedagogique",
    "famille": "apprendre_les_statistiques",
    "format": "youtube_lesson",
    "habillage_sonore": True,
    "theme": "EP-S2A · Résumer des données",
    "pedagogie": {
        "niveau": "decouverte",
        "objectifs": conc["objectifs"],
        "prerequis": {"fr": ["S1.03 : types de variables (épisode EP-S1A)", "Pourcentages (épisode EP-M01)"],
                      "en": ["S1.03: types of variables (episode EP-S1A)", "Percentages (episode EP-M01)"]},
        "hypotheses": {"fr": "Données fictives : 20 salariés d'une entreprise imaginaire, une classe, un café, des visiteurs. Aucun chiffre réel.",
                       "en": "Made-up data: 20 employees of an imaginary company, a class, a café, visitors. No real numbers."},
    },
    "validation": {"statut": "brouillon", "valide_par": "", "date": ""},
    "sources": [],
    "editions": {},
}
for l in ("fr", "en"):
    fiche["editions"][l] = {
        "titre": conc["titres"]["youtube_" + l],
        "legende": ("Comment résumer des données sans les trahir ? Un tableau garde les proportions, un histogramme la silhouette, la moyenne le total, la médiane le milieu. Cinq chapitres, deux laboratoires en direct, un exercice de synthèse corrigé. Données fictives, calculs vérifiés. Sources de méthode : OpenStax, Introductory Statistics 2e, « Measures of the Center of the Data » ; NIST/SEMATECH e-Handbook of Statistical Methods, « Histogram ». Un exercice vous bloque ? Posez votre question en commentaire.\n"
                    if l == "fr" else
                    "How do you summarize data without betraying it? A table keeps the proportions, a histogram the shape, the mean the total, the median the middle. Five chapters, two live labs, a worked summary exercise. Made-up data, checked calculations. Method sources: OpenStax, Introductory Statistics 2e, “Measures of the Center of the Data”; NIST/SEMATECH e-Handbook of Statistical Methods, “Histogram”. Stuck on an exercise? Ask in the comments.\n"),
        "hashtags": ["statistiques", "moyenne", "mediane", "histogramme"] if l == "fr" else ["statistics", "mean", "median", "histogram"],
        "scenes": episode(l),
    }

entete = ("# Épisode long EP-S2A « Résumer des données : tableaux, histogrammes, moyenne et médiane » (YOUTUBE_LESSON).\n"
          "# Assemblé le 22/11/2026 à partir des cinq fiches de chapitre validées (S2.01 à S2.05) et de la fiche de\n"
          "# conception contenus/conception/EP-S2A.yaml (validée par JG le 22/11/2026, PR #50), changements compris.\n"
          "# Données fictives, aucun chiffre réel. Statut : brouillon, en attente de relecture et de validation par JG.\n")
out = R / "contenus/fiches/2026-12-ep-s2a-resumer-des-donnees.yaml"
out.write_text(entete + yaml.safe_dump(fiche, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
print(out, sum(1 for _ in fiche["editions"]["fr"]["scenes"]), "scènes FR")
