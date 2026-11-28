"""Assemble la fiche de production de l'épisode long EP-S1A à partir des quatre fiches de chapitre validées
(S1.01 à S1.04, JG, 08/11/2026) et de la fiche de conception contenus/conception/EP-S1A.yaml (PR #60, fusionnée
sur l'accord de JG le 28/11/2026). Même méthode qu'EP-S2A (assembler_ep_s2a.py)."""
import copy
import sys
from pathlib import Path

import yaml

R = Path(sys.argv[1])
F = R / "contenus/fiches"
CHAP = [F / "2026-11-n1-s1-01-qu-est-ce-qu-une-donnee.yaml",
        F / "2026-11-n1-s1-02-population-individu-variable.yaml",
        F / "2026-11-n1-s1-03-types-de-variables.yaml",
        F / "2026-11-n1-s1-04-d-ou-viennent-les-donnees.yaml"]
IDS = ["S1.01", "S1.02", "S1.03", "S1.04"]
conc = yaml.safe_load(open(R / "contenus/conception/EP-S1A.yaml"))
blocs = {b.get("id", b["bloc"]): b for b in conc["deroule_episode"]}
chap = [yaml.safe_load(open(f)) for f in CHAP]
TRAJETS = conc["donnees_ou_simulation"]["donnees"]["temps_trajet_min"]
TIRAGES = conc["donnees_ou_simulation"]["donnees"]["echantillons_lab2"]


def S(type_, texte, voix, **extra):
    s = {"type": type_, "texte": texte}
    s.update(extra)
    s["voix_off"] = voix
    return s


def anim(texte, voix, conf, etapes=None, verifier=None, note=None, univers=None):
    s = {"type": "animation", "texte": texte, "animation": conf}
    if etapes:
        s["etapes"] = etapes
    if univers:
        s["univers"] = univers
    if note:
        s["note"] = note
    s["voix_off"] = voix
    if verifier:
        s["verifier"] = verifier
    return s


def chapitre(k, d, l):
    """Scènes du chapitre k (1 à 4) : l'accroche devient le titre numéroté ; « À retenir » et fin passent
    dans la synthèse de l'épisode."""
    sc = copy.deepcopy(d["editions"][l]["scenes"])
    titre_chap = blocs[IDS[k - 1]]["titre"][l]
    out, j = [], 0
    for i, s in enumerate(sc):
        t = s["type"]
        if t == "fin" or (t == "etapes" and i == len(sc) - 2):
            continue
        if t == "accroche":
            out.append({"type": "titre", "numero": str(k), "texte": titre_chap.split(". ", 1)[1],
                        "voix_off": s["voix_off"]})
            continue
        if t == "titre":
            j += 1
            s["numero"] = f"{k}.{j}"
        out.append(s)
    return out


def _index(scenes, pred):
    return next(i for i, s in enumerate(scenes) if pred(s))


def modifier(k, scenes, l):
    fr = l == "fr"
    if k == 1:      # la correction de l'exercice présente le fil rouge
        i = _index(scenes, lambda s: s["type"] == "correction")
        scenes.insert(i + 1, anim(
            "Une entreprise de *20 salariés* : combien de temps pour venir ?" if fr
            else "A company of *20 employees*: how long to get to work?",
            ("Une entreprise fictive de vingt salariés se pose exactement cette question B pour ses salariés. Nous allons la suivre tout l'épisode."
             if fr else "A fictional company of twenty employees is asking exactly question B about its staff. We'll follow it through the whole episode."),
            {"modele": "foule", "n": 20},
            note="Entreprise fictive de 20 salariés." if fr else "Fictional company of 20 employees."))
    if k == 2:
        i = _index(scenes, lambda s: s["type"] == "etapes" and ("7 heures" in s["texte"] or "7 hours" in s["texte"]))
        scenes.insert(i + 1, S(
            "etapes", "Dans notre entreprise" if fr else "In our company",
            ("Dans notre entreprise fictive, c'est plus simple. La population : les vingt salariés de l'entreprise. L'individu : un salarié. La variable : son temps de trajet, en minutes, un jour donné, tel qu'il le déclare."
             if fr else "In our fictional company, it's simpler. The population: the company's twenty employees. The unit: one employee. The variable: their commuting time, in minutes, on a given day, as they report it."),
            etapes=(["Population : les *20 salariés*", "Individu : *un salarié*", "Variable : son *temps de trajet*, en minutes, déclaré"]
                    if fr else ["Population: the *20 employees*", "Unit: *one employee*", "Variable: their *commuting time*, in minutes, as reported"]),
            note="Entreprise fictive." if fr else "Fictional company."))
        for s in scenes:
            if s["type"] == "etapes" and s.get("verifier") and any("9000 / 3" == v["expression"] for v in s["verifier"]):
                s["voix_off"] = s["voix_off"].replace(
                    "Quel est le revenu moyen du village ?",
                    "Quel est le revenu moyen du village ? La moyenne, c'est le total partagé également.").replace(
                    "What is the average income in the village?",
                    "What is the average income in the village? The average is the total shared out equally.")
    if k == 3:
        i = _index(scenes, lambda s: s["type"] == "texte" and ("qualitatives" in s["texte"] or "categorical" in s["texte"]))
        scenes.insert(i + 1, S(
            "etapes", "Le questionnaire de l'entreprise" if fr else "The company's questionnaire",
            ("Notre entreprise envoie un petit questionnaire. Quatre questions, quatre types. Le mode de transport : une étiquette, variable nominale. La satisfaction du trajet, de un à cinq : un rang, variable ordinale. Le nombre de correspondances : on compte, variable discrète. Le temps de trajet en minutes : on mesure, variable continue."
             if fr else "Our company sends out a short questionnaire. Four questions, four types. The mode of transport: a label, a nominal variable. Satisfaction with the trip, from one to five: a rank, an ordinal variable. The number of changes: we count, a discrete variable. The travel time in minutes: we measure, a continuous variable."),
            etapes=(["Mode de transport : *nominale*", "Satisfaction de 1 à 5 : *ordinale*",
                     "Nombre de correspondances : *discrète*", "Temps de trajet en minutes : *continue*"]
                    if fr else ["Mode of transport: *nominal*", "Satisfaction from 1 to 5: *ordinal*",
                                "Number of changes: *discrete*", "Travel time in minutes: *continuous*"]),
            note="Entreprise fictive." if fr else "Fictional company."))
    if k == 4:
        i = _index(scenes, lambda s: s["type"] == "correction")
        scenes.insert(i + 1, S(
            "texte", "20 salariés : on peut *tous* les interroger" if fr else "20 employees: we can ask *all* of them",
            ("Et notre entreprise ? Avec vingt salariés, on peut tous les interroger : c'est un recensement de l'entreprise. Une entreprise de vingt mille salariés n'interrogerait qu'un échantillon."
             if fr else "And our company? With twenty employees, we can ask every one of them: that's a census of the company. A company of twenty thousand would only ask a sample."),
            note="Entreprise fictive." if fr else "Fictional company."))
    return scenes


ECRAN_TRANSITION = {
    1: {"fr": "Un groupe, oui. Mais *lequel* ?", "en": "A group, yes. But *which one*?"},
    2: {"fr": "Changer d'individu : *jusqu'où* ?", "en": "Changing the unit: *how far*?"},
    3: {"fr": "*Qui* a mesuré, et *comment* ?", "en": "*Who* measured it, and *how*?"},
    4: {"fr": "Et si l'on n'interrogeait que *5 salariés* ?", "en": "What if we only asked *5 employees*?"},
}


def transition(k, l):
    return S("texte", ECRAN_TRANSITION[k][l], blocs[IDS[k - 1]]["transition"][l])


def lab1(l):
    fr = l == "fr"
    e = lambda x: f"{x:,}".replace(",", " ") if fr else f"{x:,}"
    return [
        S("titre", "Laboratoire : par ménage ou par personne" if fr else "Lab: per household or per person",
          ("Laboratoire. Reprenons le village et faisons-le changer sous nos yeux." if fr
           else "Lab time. Let's take the village and change it before our eyes."), numero="2.3", univers="immersif"),
        anim("Par *ménage* : 9 000 € partagés entre 3" if fr else "Per *household*: €9,000 shared among 3",
             ("Trois ménages, neuf mille euros par mois. Versons tout dans une cagnotte et partageons également entre les trois ménages : trois mille euros chacun."
              if fr else "Three households, nine thousand euros a month. Pour it all into a pot and share it equally among the three households: three thousand euros each."),
             {"modele": "partage", "valeurs": [2000, 4000, 3000], "unite": "€"},
             verifier=[{"expression": "9000 / 3", "attendu": 3000, "libelle": "Par ménage"}],
             note="Village fictif." if fr else "Fictional village."),
        S("chiffre", "par *personne* : 9 000 € ÷ 7 habitants" if fr else "per *person*: €9,000 ÷ 7 people",
          ("Partageons maintenant entre les sept habitants : environ mille deux cent quatre-vingt-six euros chacun."
           if fr else "Now let's share among the seven people: about one thousand two hundred and eighty-six euros each."),
          valeur=1286, suffixe={"fr": " €", "en": " €"}, univers="immersif",
          verifier=[{"expression": "9000 / 7", "attendu": 1286, "libelle": "Par personne au départ"}]),
        S("etapes", "Le ménage B passe de *4 à 6* personnes" if fr else "Household B grows from *4 to 6* people",
          ("Deux enfants naissent dans le ménage B, qui passe de quatre à six personnes. Les revenus ne bougent pas. Par ménage : toujours neuf mille divisé par trois, trois mille euros. Par personne : neuf mille divisé par neuf, mille euros. Même village, même argent : un chiffre ne bouge pas, l'autre baisse d'un quart. Avant de dire « le revenu moyen a baissé », demandez par qui on divise."
           if fr else "Two babies are born in household B, which grows from four to six people. Income doesn't change. Per household: still nine thousand divided by three, three thousand euros. Per person: nine thousand divided by nine, one thousand euros. Same village, same money: one number stays put, the other falls by a quarter. Before saying 'average income fell', ask what you're dividing by."),
          etapes=([f"Par ménage : 9 000 ÷ 3 = *{e(3000)} €*, inchangé", f"Par personne : 9 000 ÷ 9 = *{e(1000)} €*",
                   "Même argent : *précisez l'individu*"] if fr else
                  [f"Per household: 9,000 ÷ 3 = *€{e(3000)}*, unchanged", f"Per person: 9,000 ÷ 9 = *€{e(1000)}*",
                   "Same money: *name the unit*"]),
          univers="immersif",
          verifier=[{"expression": "9000 / 3", "attendu": 3000, "libelle": "Par ménage, à l'arrivée"},
                    {"expression": "9000 / (1 + 6 + 2)", "attendu": 1000, "libelle": "Par personne, à l'arrivée"}]),
    ]


def pastilles(texte, voix, valeurs, l, etapes=None, verifier=None):
    s = {"type": "animation", "texte": texte, "univers": "immersif",
         "animation": {"modele": "pastilles", "valeurs": valeurs, "largeur_classe": 20, "unite": "minutes"}}
    if etapes:
        s["etapes"] = etapes
    s["voix_off"] = voix
    if verifier:
        s["verifier"] = verifier
    return s


def lab2(l):
    fr = l == "fr"
    sous = lambda v: sum(1 for t in v if t < 20)
    out = [
        S("titre", "Laboratoire : tout le monde ou un échantillon" if fr else "Lab: everyone or a sample",
          ("Deuxième laboratoire. Comparons la réponse des vingt salariés à celle de cinq salariés tirés au hasard."
           if fr else "Second lab. Let's compare the answer from all twenty employees with the answer from five drawn at random."),
          numero="4.3", univers="immersif"),
        pastilles("Les *20 salariés* : 10 sous 20 minutes, *50 %*" if fr else "All *20 employees*: 10 under 20 minutes, *50%*",
                  ("Les vingt salariés, chacun avec son temps de trajet. Dans la première barre, ceux qui mettent moins de vingt minutes : dix sur vingt, soit cinquante pour cent. C'est la vraie réponse, puisqu'on a interrogé tout le monde."
                   if fr else "The twenty employees, each with their travel time. In the first bar, those who take under twenty minutes: ten out of twenty, so fifty percent. That's the true answer, since everyone was asked."),
                  TRAJETS, l,
                  verifier=[{"expression": f"sum(1 for t in {TRAJETS} if t < 20)", "attendu": 10, "libelle": "Sous 20 minutes, les 20"},
                            {"expression": "10 / 20 * 100", "attendu": 50, "libelle": "Part, les 20"}]),
    ]
    noms = (["Premier", "Deuxième", "Troisième"] if fr else ["First", "Second", "Third"])
    for k, (cle, v) in enumerate(TIRAGES.items()):
        n = sous(v)
        p = n * 20
        liste = ", ".join(map(str, v[:-1])) + (" et " if fr else " and ") + str(v[-1])
        out.append(pastilles(
            (f"Tirage {k + 1} : {n} sur 5, *{p} %*" if fr else f"Draw {k + 1}: {n} out of 5, *{p}%*"),
            (f"{noms[k]} tirage de cinq salariés : {liste} minutes. {n} sur cinq sous vingt minutes, soit {p} pour cent."
             if fr else f"{noms[k]} draw of five employees: {liste} minutes. {n} out of five under twenty minutes, so {p} percent."),
            v, l, verifier=[{"expression": f"{n} / 5 * 100", "attendu": p, "libelle": f"Tirage {k + 1}"}]))
    out.append(S("etapes", "Trois échantillons, *trois réponses*" if fr else "Three samples, *three answers*",
                 ("Trois échantillons, trois réponses, et aucune ne vaut cinquante pour cent. Personne n'a menti : c'est le hasard du tirage. C'est la marge d'erreur d'un sondage, et c'est tout l'objet du prochain épisode."
                  if fr else "Three samples, three answers, and none of them is fifty percent. Nobody lied: it's the luck of the draw. That's a survey's margin of error, and it's what the next episode is all about."),
                 etapes=(["Les 20 : *50 %*", "Échantillons de 5 : *40 %*, *60 %*, *80 %*", "Personne n'a menti : c'est le *hasard du tirage*"]
                         if fr else ["All 20: *50%*", "Samples of 5: *40%*, *60%*, *80%*", "Nobody lied: it's the *luck of the draw*"]),
                 univers="immersif"))
    return out


def enonces(sc, l):
    """Exercices lisibles à l'arrêt sur image (LMEC-DEC-017) : l'énoncé garde les données, chaque question est
    écrite à l'écran, numérotée ; la voix finit par les questions, dans l'ordre, une phrase par question."""
    fr = l == "fr"
    for s in sc:
        if s["type"] != "exercice":
            continue
        t = s["texte"]
        if "tour Eiffel" in t or "Eiffel Tower" in t:
            s["texte"] = ("Deux questions. *A* : la hauteur de la tour Eiffel. *B* : le temps que mettent les Parisiens pour aller travailler."
                          if fr else "Two questions. *A*: the height of the Eiffel Tower. *B*: how long Parisians take to get to work.")
            s["questions"] = ["Laquelle est une question statistique ?"] if fr else ["Which one is a statistical question?"]
            s["voix_off"] = ("À vous. A : quelle est la hauteur de la tour Eiffel ? B : combien de temps les Parisiens mettent-ils pour aller travailler ? Laquelle de ces deux questions est une question statistique ?"
                             if fr else "Your turn. A: how tall is the Eiffel Tower? B: how long do Parisians take to get to work? Which of these two questions is a statistical question?")
        elif "30 %" in t or "30%" in t:
            s["texte"] = ("Titre fictif : « *30 %* des collégiens ont un téléphone avant 11 ans. »" if fr
                          else "Made-up headline: \"*30%* of middle-school pupils have a phone before age 11.\"")
            s["questions"] = (["Quelle est la population ?", "Quel est l'individu ?", "Quelle est la variable ?"] if fr
                              else ["What is the population?", "What is the unit?", "What is the variable?"])
            s.pop("note", None)
            s["voix_off"] = ("À vous. Voici un autre titre fictif : trente pour cent des collégiens ont un téléphone avant onze ans. Quelle est la population ? Quel est l'individu ? Quelle est la variable ?"
                             if fr else "Your turn. Here's another made-up headline: thirty percent of middle-school pupils have a phone before age eleven. What is the population? What is the unit? What is the variable?")
        elif "étoiles" in t or "stars" in t:
            s["texte"] = "Les étoiles d'un hôtel, de *1 à 5*." if fr else "A hotel's stars, from *1 to 5*."
            s["questions"] = (["Quel est le type de cette variable ?", "Un 4 étoiles est-il *deux fois* meilleur qu'un 2 étoiles ?"] if fr
                              else ["What type of variable is this?", "Is a 4-star hotel *twice* as good as a 2-star one?"])
        elif "naissances" in t or "births" in t.lower():
            s["texte"] = ("Trois chiffres : les *naissances* de l'année ; la *confiance* dans les scientifiques ; le *trafic* du périphérique à 8 h."
                          if fr else "Three numbers: the year's *births*; *trust* in scientists; *traffic* on the ring road at 8 a.m.")
            s["questions"] = ["D'où vient chacun de ces trois chiffres ?"] if fr else ["Where does each of these three numbers come from?"]
            s["voix_off"] = ("À vous. Trois chiffres : le nombre de naissances de l'année, la part des gens qui font confiance aux scientifiques, et le nombre de voitures sur le périphérique à huit heures du matin. D'où vient chacun de ces trois chiffres ?"
                             if fr else "Your turn. Three numbers: the number of births in the year, the share of people who trust scientists, and the number of cars on the ring road at eight in the morning. Where does each of these three numbers come from?")
    return sc


def episode(l):
    fr = l == "fr"
    b = blocs
    sc = [S("accroche", ("Paris : *2,1*, *11* ou *13,3 millions* d'habitants ? Chômeurs : *2,7* ou *3,3 millions* ? *Tous justes.*"
                         if fr else "Paris: *2.1*, *11* or *13.3 million* people? Unemployed: *2.7* or *3.3 million*? *All correct.*"),
            b["ouverture"][l],
            note=("Insee : recensement 2023 ; enquête Emploi et France Travail, 2e trimestre 2026." if fr
                  else "Insee: 2023 census; Labour Force Survey and France Travail, Q2 2026.")),
          S("accueil", "Bonjour, et *bienvenue* !" if fr else "Hi, and *welcome*!", b["accueil"][l]),
          S("etapes", "Au programme" if fr else "Coming up", b["plan"][l], disposition="cartes",
            etapes=(["Qu'est-ce qu'une *donnée* ?", "De *qui* parle ce chiffre ?", "Quel *type* de variable ?",
                     "D'où viennent les *données* ?"] if fr else
                    ["What counts as *data*?", "*Who* is this number about?", "What *type* of variable?",
                     "Where do *data* come from?"]))]
    for k, d in enumerate(chap, 1):
        sc += modifier(k, chapitre(k, d, l), l)
        if k == 2:
            sc += lab1(l)
        if k == 4:
            sc += lab2(l)
        else:
            sc.append(transition(k, l))
    sc.append(S("etapes", "À retenir" if fr else "Key takeaways", b["synthese"][l],
                etapes=(["Une donnée est une *mesure*, selon une définition", "De qui parle le chiffre : *population, individu, variable*",
                         "Étiquette, rang ou quantité : l'*échelle* dit ce qu'on peut calculer", "Chaque source a une *force* et une *limite*",
                         "Quelle *question* ? Quelle *définition* ? *Qui* a mesuré, quand et comment ?"]
                        if fr else ["Data are *measurements*, under a definition", "Who it's about: *population, unit, variable*",
                                    "Label, rank or quantity: the *scale* says what you can compute", "Every source has a *strength* and a *limit*",
                                    "Which *question*? Which *definition*? *Who* measured it, when and how?"])))
    ex = b["exercice_de_synthese"]
    vo = ex[l]
    pause = "Mettez la vidéo en pause." if fr else "Pause the video."
    vo = vo.replace(" " + pause, "").replace("À vous. ", "À vous, et mettez la vidéo en pause pour répondre. ").replace(
        "Your turn. ", "Your turn, and pause the video to answer. ")
    sc.append(S("exercice", ("Une commune fictive : le *temps quotidien* de ses habitants dans les transports, leur *mode de transport* principal, une note de *satisfaction de 1 à 5*."
                             if fr else "A fictional town: its residents' *daily time* in transport, their main *mode of transport*, a *satisfaction score from 1 to 5*."),
                vo, pause=ex["pause_secondes"],
                questions=(["Est-ce une question statistique ?", "Quelle est la population, l'individu, la variable ?",
                            "Quel est le type de chacune des trois variables ?",
                            "Tous les habitants, 500 tirés au sort, ou les validations de cartes de bus : une force et une limite de chaque source ?"]
                           if fr else ["Is this a statistical question?", "What are the population, the unit and the variable?",
                                       "What type is each of the three variables?",
                                       "Every resident, 500 drawn at random, or bus card taps: one strength and one limit of each source?"])))
    corr = ex["correction_" + l]
    coupe = corr.index("Quatre" if fr else "Four")
    sc.append({"type": "correction", "voix_off": corr[:coupe].strip(),
               "etapes": (["Oui : les durées *varient* d'un habitant à l'autre", "Habitants (âge ? semaine ?) ; *un habitant* ; *minutes par jour*",
                           "Temps : *continue* ; mode : *nominale* ; satisfaction : *ordinale*"] if fr else
                          ["Yes: times *vary* from one resident to another", "Residents (age? week?); *one resident*; *minutes a day*",
                           "Time: *continuous*; mode: *nominal*; satisfaction: *ordinal*"])})
    sc.append(S("etapes", "Correction (suite)" if fr else "Answer (continued)", corr[coupe:].strip(),
                etapes=(["Tous : *recensement*, complet mais lourd", "500 au hasard : *sondage*, rapide mais marge d'erreur",
                         "Validations : *fichier*, énorme, mais seulement le bus, et des *passages*, pas des personnes"] if fr else
                        ["Everyone: a *census*, complete but heavy", "500 at random: a *survey*, quick but with a margin of error",
                         "Card taps: *records*, huge, but bus only, and *taps*, not people"])))
    sc = enonces(sc, l)
    sc.append(S("cloture", ("Prochain épisode : *pourquoi un échantillon peut mentir*. Une question ? *En commentaire*" if fr
                            else "Next episode: *why a sample can lie*. A question? *Ask in the comments*"), b["cloture"][l]))
    sc.append(S("fin", "Éveiller par les chiffres." if fr else "Enlightening through numbers.",
                "ACTU-BASICS. Éveiller par les chiffres." if fr else "ACTU-BASICS. Enlightening through numbers."))
    return sc


sources = []
for d in chap:
    for s in d.get("sources", []):
        if s not in sources:
            sources.append(s)
fiche = {
    "id": "2026-12-ep-s1a-d-ou-vient-un-chiffre",
    "type_fiche": "pedagogique",
    "famille": "apprendre_les_statistiques",
    "format": "youtube_lesson",
    "habillage_sonore": True,
    "theme": "EP-S1A · D'où vient un chiffre ?",
    "pedagogie": {
        "niveau": "decouverte",
        "objectifs": conc["objectifs"],
        "prerequis": {"fr": ["Aucun : premier épisode du parcours", "Pourcentages (épisode EP-M01), conseillé"],
                      "en": ["None: first episode of the course", "Percentages (episode EP-M01), recommended"]},
        "hypotheses": {"fr": "Chiffres de l'Insee des chapitres validés (Paris, recensement 2023 ; chômage, 2e trimestre 2026). Entreprise, village et commune fictifs, annoncés comme tels.",
                       "en": "Insee figures from the validated chapters (Paris, 2023 census; unemployment, Q2 2026). The company, village and town are made up, and labelled as such."},
    },
    "validation": {"statut": "brouillon", "valide_par": "", "date": ""},   # aperçu FR et EN à valider par JG
    "sources": sources,
    "editions": {},
}
for l in ("fr", "en"):
    fiche["editions"][l] = {
        "titre": conc["titres"]["youtube_" + l],
        "legende": ("Combien d'habitants à Paris : 2,1, 11 ou 13,3 millions ? Combien de chômeurs : 2,7 ou 3,3 millions ? Tous ces chiffres sont justes. Avant de calculer quoi que ce soit, il faut savoir d'où vient un chiffre : quelle question, quelle définition, qui a mesuré et comment. Quatre chapitres, deux laboratoires en direct, un exercice de synthèse corrigé. Sources : Insee, recensement de la population 2023 ; Insee, Informations Rapides n° 192 et « L'essentiel sur... le chômage » (2e trimestre 2026). Entreprise, village et commune fictifs. Un exercice vous bloque ? Posez votre question en commentaire.\n"
                    if l == "fr" else
                    "How many people live in Paris: 2.1, 11 or 13.3 million? How many are unemployed in France: 2.7 or 3.3 million? All these figures are correct. Before calculating anything, you need to know where a number comes from: which question, which definition, who measured it and how. Four chapters, two live labs, a worked summary exercise. Sources: Insee (the French statistics office), 2023 population census; Insee, Informations Rapides no. 192 and \"Key facts on unemployment\" (Q2 2026). The company, village and town are made up. Stuck on an exercise? Ask in the comments.\n"),
        "hashtags": ["statistiques", "donnees", "chiffres"] if l == "fr" else ["statistics", "data", "numbers"],
        "scenes": episode(l),
    }

entete = ("# Épisode long EP-S1A « D'où vient un chiffre ? Données, populations et variables » (YOUTUBE_LESSON).\n"
          "# Assemblé le 28/11/2026 à partir des quatre fiches de chapitre validées par JG le 08/11/2026 (S1.01 à S1.04)\n"
          "# et de la fiche de conception contenus/conception/EP-S1A.yaml (PR #60, fusionnée le 28/11/2026), changements compris.\n"
          "# Généré par contenus/assemblage/assembler_ep_s1a.py : modifier ce script, pas ce fichier.\n"
          "# Statut : aperçu FR et EN à valider par JG.\n")
out = R / "contenus/fiches/2026-12-ep-s1a-d-ou-vient-un-chiffre.yaml"
out.write_text(entete + yaml.safe_dump(fiche, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
print(out, sum(1 for _ in fiche["editions"]["fr"]["scenes"]), "scènes FR")
