# Conducteur 2026-12-ep-s2a-resumer-des-donnees (FR) : « Moyenne, médiane, histogramme : résumer des données sans se faire avoir »

Généré depuis `contenus/fiches/2026-12-ep-s2a-resumer-des-donnees.yaml` (103 scènes, données fictives). Pour chaque scène : type, univers visuel, texte à l'écran, animation, légendes successives, puis la voix off. Les calculs écrits à l'écran apparaissent terme à terme pendant que la voix les dit.

### 1. accroche
- Écran : Vingt salariés. *Qui dit vrai* : la moyenne ou la médiane ?
- Voix : Vingt salariés. Une seule question : combien de temps mettent-ils pour venir travailler ? La moyenne dit un peu plus de 21 minutes. Pourtant, la moitié d'entre eux met 20 minutes ou moins. Et si un seul salarié déménage loin, la moyenne bondit… alors que presque rien n'a changé pour les autres. Qui dit vrai ?

### 2. accueil
- Écran : Bonjour, et *bienvenue* !
- Voix : Bonjour, et bienvenue ! Merci d'être là. Salaires, notes, temps de trajet : on résume tout avec une moyenne. Dans cet épisode, on voit quand elle dit vrai, quand elle trompe, et par quoi la remplacer.

### 3. animation
- Écran : Ce que vous allez *apprendre*
- Animation « apercu » : cartes=[{'icone': 'tableau', 'texte': 'Construire un *tableau* de fréquences'}, {'icone': 'histogramme', 'texte': 'Choisir et lire un *histogramme*'}, {'icone': 'forme', 'texte': "Reconnaître la *forme* d'une distribution"}, {'icone': 'equilibre', 'texte': 'Calculer une *moyenne*'}, {'icone': 'mediane', 'texte': 'Trouver la *médiane*'}, {'icone': 'laboratoire', 'texte': "Tester en *laboratoire*, puis s'exercer"}]
- Voix : À la fin, vous saurez résumer un jeu de données, lire sa distribution et choisir entre moyenne et médiane. Concrètement : construire un tableau de fréquences ; choisir et lire un histogramme ; reconnaître la forme d'une distribution ; calculer une moyenne, et voir pourquoi c'est un point d'équilibre ; trouver une médiane ; et tout vérifier vous-même, avec deux laboratoires et un exercice corrigé.

### 4. titre 1
- Écran : Compter : effectifs, fréquences, cumul
- Voix : Mille réponses à un questionnaire : personne ne va les lire une par une. Comment les résumer ?

### 5. animation
- Écran : *20 salariés* : notre fil rouge
- Animation « foule » : n=20
- Note à l'écran : Entreprise fictive de 20 salariés.
- Voix : Notre fil rouge, ce sont vingt salariés et leurs temps de trajet : nous les suivrons jusqu'à la fin de l'épisode. Pour bien voir la méthode, échauffons-nous d'abord sur une petite classe de vingt-cinq élèves.

### 6. titre 1.1
- Écran : Compter : les effectifs
- Voix : Première étape, toute simple : compter.

### 7. courbe
- Écran : Combien de *frères et sœurs* ? Classe de 25 élèves
- Graphique barres : points [[0, 5], [1, 10], [2, 6], [3, 4]]
- Note à l'écran : Autre exemple, pour la méthode : une classe fictive de 25 élèves.
- Voix : On demande à vingt-cinq élèves combien ils ont de frères et sœurs. Cinq n'en ont aucun, dix en ont un, six en ont deux et quatre en ont trois. Ces nombres s'appellent des effectifs.

### 8. texte
- Écran : Toujours vérifier le *total* : 5 + 10 + 6 + 4 = 25
- Voix : Premier réflexe : vérifier le total. Cinq plus dix plus six plus quatre, cela fait bien vingt-cinq. Sans total, un effectif ne veut pas dire grand-chose.

### 9. titre 1.2
- Écran : Rapporter au total : les fréquences
- Voix : Deuxième étape : rapporter chaque effectif au total.

### 10. formule
- Écran : Fréquence = effectif ÷ total
- Formule : ['\\text{fréquence}=\\dfrac{\\text{effectif}}{\\text{effectif total}}', '\\dfrac{10}{25}=0{,}40=40\\ \\%']
- Voix : La fréquence, c'est l'effectif divisé par le total. Pour les élèves qui ont un frère ou une sœur : dix divisé par vingt-cinq, cela fait zéro virgule quarante, soit quarante pour cent.

### 11. etapes
- Écran : Le tableau complet
  - 0 : 5 élèves, soit *20 %*
  - 1 : 10 élèves, soit *40 %*
  - 2 : 6 élèves, soit *24 %*
  - 3 : 4 élèves, soit *16 %*
- Voix : Voici le tableau complet. Aucun frère ou sœur : cinq élèves, soit vingt pour cent. Un : dix élèves, soit quarante pour cent. Deux : six élèves, soit vingt-quatre pour cent. Trois : quatre élèves, soit seize pour cent.

### 12. texte
- Écran : Les fréquences font toujours *100 %*
- Voix : Les fréquences s'additionnent toujours pour faire cent pour cent. Si ce n'est pas le cas, il manque quelqu'un, ou un arrondi est passé par là.

### 13. titre 1.3
- Écran : Additionner : les fréquences cumulées
- Voix : Troisième étape : les fréquences cumulées.

### 14. animation
- Écran : *Au plus* tant de frères et sœurs
- Animation « cumul » : categories=['0', '1', '2', '3'], frequences=[20, 40, 24, 16]
  - Au plus 0 : *20 %*
  - Au plus 1 : 20 + 40 = *60 %*
  - Au plus 2 : 60 + 24 = *84 %*
  - Au plus 3 : 84 + 16 = *100 %*
- Voix : On additionne les fréquences au fur et à mesure. Au plus zéro frère ou sœur : vingt pour cent. Au plus un : vingt plus quarante, soit soixante pour cent. Au plus deux : soixante plus vingt-quatre, soit quatre-vingt-quatre pour cent. Au plus trois : cent pour cent, toute la classe.

### 15. chiffre
- Écran : des élèves ont *au plus deux* frères et sœurs
- Chiffre clé : 84
- Note à l'écran : Le cumul suit l'ordre des valeurs : il a un sens ici parce que 0, 1, 2, 3 sont rangés.
- Voix : Une seule phrase résume alors la classe : quatre-vingt-quatre pour cent des élèves ont au plus deux frères et sœurs. Le cumul a un sens ici parce que les valeurs sont rangées dans l'ordre.

### 16. titre 1.4
- Écran : Le piège : comparer des effectifs
- Voix : Dernier point, et c'est le piège le plus courant.

### 17. etapes
- Écran : Deux classes, *deux tailles*
  - Classe A, 25 élèves : 10 ont un frère ou une sœur, *40 %*
  - Classe B, 40 élèves : 12 en ont un, *30 %*
- Voix : Comparons deux classes. Dans la classe A, de vingt-cinq élèves, dix ont exactement un frère ou une sœur, soit quarante pour cent. Dans la classe B, de quarante élèves, ils sont douze, soit trente pour cent seulement.

### 18. texte
- Écran : 12 est plus grand que 10, mais *30 % est plus petit que 40 %*
- Voix : Douze est plus grand que dix. Mais rapporté à la taille de la classe, c'est moins. Pour comparer deux groupes de tailles différentes, on compare des fréquences, pas des effectifs.

### 19. exercice
- Écran : 20 salariés et leur mode de transport : *8 voiture*, *6 transports en commun*, *4 vélo*, *2 marche*.
  1. Calculez la fréquence de chaque mode de transport.
  2. Un cumul aurait-il un sens ici ?
- Voix : À vous. Vingt salariés indiquent leur mode de transport : huit en voiture, six en transports en commun, quatre à vélo et deux à pied. Calculez les fréquences. Puis demandez-vous : un cumul aurait-il un sens ici ?

### 20. correction
  - Voiture 8 ÷ 20 = *40 %*, transports 6 ÷ 20 = *30 %*
  - Vélo 4 ÷ 20 = *20 %*, marche 2 ÷ 20 = *10 %*
  - Cumul : *pas de sens*, ces catégories n'ont pas d'ordre
- Réponse : Total 100 % ; pas de cumul sans ordre
- Voix : Correction. Voiture : huit divisé par vingt, quarante pour cent ; transports en commun : trente pour cent. Vélo : vingt pour cent ; marche : dix pour cent. Et le cumul ? Il n'a pas de sens ici : les modes de transport n'ont pas d'ordre naturel. Le total fait bien cent pour cent, et l'on ne cumule que des valeurs rangées, comme un nombre de frères et sœurs ou des durées.

### 21. texte
- Écran : Gardez ces *20 salariés* en tête
- Voix : Retrouvons nos vingt salariés, notre fil rouge : gardez-les en tête. D'abord, dessinons leurs réponses.

### 22. titre 2
- Écran : Dessiner : barres ou histogramme
- Voix : Deux graphiques faits de barres. Sur l'un, elles se touchent ; sur l'autre, non. Ce détail change toute la façon de les lire.

### 23. titre 2.1
- Écran : Le diagramme en barres : des catégories
- Voix : Commençons par le diagramme en barres.

### 24. courbe
- Écran : Mode de transport de *20 salariés*
- Graphique barres : points [[0, 8], [1, 6], [2, 4], [3, 2]]
- Note à l'écran : Entreprise fictive de 20 salariés (exercice du chapitre 1).
- Voix : Voici les vingt salariés de l'exercice du chapitre 1. Une barre par mode de transport : voiture, transports en commun, vélo, marche. Les barres sont séparées, parce que ce sont des catégories distinctes. On pourrait les ranger dans un autre ordre sans rien changer au sens.

### 25. titre 2.2
- Écran : L'histogramme : des nombres en classes
- Voix : Passons maintenant à une variable numérique : le temps de trajet, en minutes. Un histogramme regroupe ces valeurs en intervalles. Pour une variable numérique discrète, comme un nombre de frères et sœurs, des barres séparées restent possibles, une par valeur.

### 26. courbe
- Écran : Temps de trajet, *classes de 10 minutes*
- Graphique histogramme : points [[0, 3], [10, 7], [20, 6], [30, 3], [40, 1]]
- Note à l'écran : Temps de trajet fictifs des 20 mêmes salariés.
- Voix : On range les temps de trajet en classes de dix minutes. Trois salariés mettent moins de dix minutes, sept entre dix et vingt, six entre vingt et trente, trois entre trente et quarante, un seul entre quarante et cinquante. Cette fois, les barres se touchent : les minutes forment une suite continue, sans trou entre les classes. Chaque classe contient sa borne gauche, pas sa borne droite : un trajet de vingt minutes compte dans la classe de vingt à trente.

### 27. courbe
- Écran : Les mêmes temps, *classes de 20 minutes*
- Graphique histogramme : points [[0, 10], [20, 9], [40, 1]]
- Voix : Ce sont exactement les mêmes données, regroupées en classes de vingt minutes. Dix salariés mettent moins de vingt minutes, neuf entre vingt et quarante, un seul plus de quarante. Le sommet, entre dix et vingt minutes, a disparu.

### 28. animation · univers immersif (fond sombre)
- Écran : Le choix des classes *change la silhouette*
- Animation « decoupages » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeurs=[10, 20], unite=min
  - *Une bosse* nette entre 10 et 20 minutes
  - Le même sommet *disparaît*
- Voix : Mettons côte à côte les mêmes vingt temps de trajet. En classes de dix minutes, une bosse nette apparaît, entre dix et vingt minutes. En classes de vingt minutes, ce sommet disparaît : trop larges, les classes cachent les détails ; trop étroites, elles inventent des bosses dues au hasard ; regardez toujours leur largeur.

### 29. titre 2.3
- Écran : Classes inégales : la surface compte
- Voix : Dernier piège : les classes de largeurs différentes.

### 30. courbe
- Écran : *Construction trompeuse* : hauteur = effectif, classes inégales
- Graphique histogramme : points [[0, 3], [10, 7], [20, 10]]
- Voix : Regroupons maintenant tout ce qui dépasse vingt minutes dans une seule classe, de vingt à cinquante. Elle contient dix salariés. Si l'on prend l'effectif comme hauteur, cette grande barre écrase tout : on croirait que les trajets longs dominent.

### 31. formule
- Écran : La bonne hauteur : la *densité*
- Formule : ['\\text{densité}=\\dfrac{\\text{effectif}}{\\text{largeur de la classe}}', '\\dfrac{10}{30}\\approx 0{,}33\\ \\text{salarié par minute}']
- Voix : Dans un histogramme, c'est la surface qui représente l'effectif. La hauteur doit donc être une densité : l'effectif divisé par la largeur de la classe. Pour la classe de vingt à cinquante minutes : dix divisé par trente, environ zéro virgule trente-trois salarié par minute.

### 32. animation
- Écran : Hauteur = *densité* : l'image redevient juste
- Animation « densite » : bornes=[0, 10, 20, 50], effectifs=[3, 7, 10], unite=minutes
  - Hauteur = effectif : la grande classe *écrase tout*
  - Hauteur = *densité* : le même espacement partout
  - Surface = densité × largeur = *effectif*
- Voix : Reprenons la construction trompeuse : avec l'effectif comme hauteur, la grande classe de vingt à cinquante minutes écrase tout. Passons à la densité : les barres montent ou descendent, et les pastilles, une par salarié, prennent le même espacement partout ; la classe de dix à vingt minutes redevient la plus dense. La surface de chaque barre redonne son effectif : zéro virgule trois fois dix, trois ; zéro virgule sept fois dix, sept ; un tiers fois trente, dix.

### 33. exercice
- Écran : 40 visiteurs d'un musée : *0–20 ans : 8* ; *20–30 ans : 12* ; *30–60 ans : 20*.
  1. Un histogramme en effectifs met en avant les 30–60 ans. A-t-il raison ?
  2. Quelle classe est la plus dense ?
- Voix : À vous. Quarante visiteurs d'un musée fictif : huit ont entre zéro et vingt ans, douze entre vingt et trente ans, vingt entre trente et soixante ans. Un histogramme qui prend l'effectif comme hauteur met en avant les trente à soixante ans. A-t-il raison ? Quelle classe est la plus dense ?

### 34. correction
  - 0–20 ans : 8 ÷ 20 = *0,4* visiteur par année d'âge
  - 20–30 ans : 12 ÷ 10 = *1,2* visiteur par année d'âge
  - 30–60 ans : 20 ÷ 30 ≈ *0,67* visiteur par année d'âge
- Réponse : Les 20–30 ans : la classe la plus dense
- Voix : Divisons chaque effectif par la largeur de sa classe. De zéro à vingt ans : huit divisé par vingt, zéro virgule quatre visiteur par année d'âge. De vingt à trente ans : douze divisé par dix, un virgule deux. De trente à soixante ans : vingt divisé par trente, environ zéro virgule soixante-sept. La classe la plus dense est celle des vingt à trente ans : l'histogramme en effectifs était trompeur.

### 35. texte
- Écran : Et si l'on changeait *nous-mêmes* les classes ?
- Voix : Avant de regarder la forme, essayons nous-mêmes de changer les classes.

### 36. titre 2.4 · univers immersif (fond sombre)
- Écran : Laboratoire : la largeur des classes
- Voix : Laboratoire. Prenons les vingt temps de trajet et changeons nous-mêmes la largeur des classes.

### 37. animation · univers immersif (fond sombre)
- Écran : Classes de *20 minutes*
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=20, unite=minutes
- Voix : Classes de vingt minutes : dix, neuf, un. Le sommet a disparu.

### 38. animation · univers immersif (fond sombre)
- Écran : Classes de *10 minutes*
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=10, unite=minutes
- Voix : Classes de dix minutes : trois, sept, six, trois, un. Une bosse nette.

### 39. animation · univers immersif (fond sombre)
- Écran : Classes de *5 minutes* : deux « sommets » ?
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=5, unite=minutes
- Voix : Classes de cinq minutes. Le trajet de quinze minutes est compté dans la classe de quinze à vingt : la borne gauche est incluse. Deux sommets apparaissent, à quinze et à vingt-cinq minutes. Ils ne tiennent qu'à un ou deux salariés. Trop larges, les classes cachent ; trop étroites, elles inventent.

### 40. courbe
- Écran : Âges de 40 visiteurs : *hauteur = effectif*
- Graphique histogramme : points [[0, 8], [20, 12], [30, 20]]
- Voix : Second réglage : les âges de quarante visiteurs, en classes inégales. Avec l'effectif comme hauteur, les trente à soixante ans dominent.

### 41. courbe
- Écran : Hauteur = *densité d'effectif*
- Graphique histogramme : points [[0, 0.4], [20, 1.2], [30, 0.6667]]
- Note à l'écran : Aires : 0,4 × 20 = 8 ; 1,2 × 10 = 12 ; ⅔ × 30 = 20 ; total 40 (hauteur 0,67 arrondie).
- Voix : On bascule sur la densité d'effectif : l'effectif divisé par la largeur, en visiteurs par année d'âge. Zéro virgule quatre, un virgule deux, environ zéro virgule soixante-sept. La classe la plus dense est vingt à trente ans. Et l'aire de chaque rectangle redonne son effectif : un virgule deux fois dix ans, douze visiteurs. L'aire totale vaut quarante, le nombre de visiteurs.

### 42. titre 3
- Écran : Lire la forme d'une distribution
- Voix : Avant de calculer quoi que ce soit, regardez la silhouette d'un histogramme. Elle en dit déjà beaucoup.

### 43. animation · univers immersif (fond sombre)
- Écran : Nos *20 salariés* : une bosse, une petite queue à droite
- Animation « pastilles » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], largeur_classe=10, unite=minutes
  - Un point par salarié
  - Une *bosse* entre 10 et 30 minutes
  - Une petite *queue* à droite : 44 minutes
- Voix : Revenons à nos vingt salariés. Leur histogramme a une bosse, entre dix et trente minutes, et une petite queue à droite : le salarié qui met quarante-quatre minutes. C'est une propriété de ces données fictives, pas une loi des trajets réels.

### 44. titre 3.1
- Écran : Symétrique : deux côtés comparables
- Voix : Première forme, la plus simple.

### 45. courbe
- Écran : Notes de *20 élèves*, sur 20
- Graphique histogramme : points [[0, 1], [4, 4], [8, 10], [12, 4], [16, 1]]
- Note à l'écran : Notes fictives de 20 élèves.
- Voix : Voici les notes fictives de vingt élèves. Une bosse au milieu, entre huit et douze, et deux côtés qui se ressemblent comme dans un miroir. Dans cet exemple, la distribution est à peu près symétrique. Ici, le milieu résume bien le groupe.

### 46. titre 3.2
- Écran : Asymétrique : une longue queue
- Voix : Deuxième forme : la distribution asymétrique.

### 47. courbe
- Écran : Revenus mensuels de *25 personnes*
- Graphique histogramme : points [[0, 2], [1000, 9], [2000, 6], [3000, 3], [4000, 2], [5000, 1], [6000, 1], [7000, 1]]
- Note à l'écran : Revenus fictifs de 25 personnes, classes de 1 000 €.
- Voix : Voici des revenus mensuels fictifs. La plupart des gens sont à gauche, entre mille et trois mille euros. Puis une longue queue s'étire vers la droite : quelques revenus très élevés. On parle d'asymétrie à droite.

### 48. etapes
- Écran : Une queue, *d'un côté ou de l'autre*
  - Queue *à droite* : quelques valeurs très grandes
  - Queue *à gauche* : quelques valeurs très petites
- Voix : Une queue peut aller d'un côté ou de l'autre. À droite, elle signale quelques valeurs très grandes, comme les hauts revenus. À gauche, quelques valeurs très petites. Ce qu'une queue fait à la moyenne, on le verra au chapitre 5.

### 49. titre 3.3
- Écran : Deux bosses : deux groupes ?
- Voix : Troisième forme, la plus surprenante.

### 50. animation
- Écran : Tailles de *44 adultes*
- Animation « melange » : origine=150, largeur_classe=5, unite=cm, groupes=[[2, 6, 8, 4, 2, 0, 0, 0], [0, 0, 1, 1, 4, 9, 5, 2]], noms=['Femmes ?', 'Hommes ?']
  - Deux bosses : une distribution *bimodale*
  - *Une explication possible* : deux groupes mélangés
  - L'histogramme seul *ne le prouve pas*
- Note à l'écran : Tailles fictives ; la décomposition en deux groupes est une hypothèse d'illustration.
- Voix : Voici les tailles fictives de quarante-quatre adultes : deux bosses, l'une autour de cent soixante centimètres, l'autre autour de cent soixante-quinze ; on dit que la distribution est bimodale. Une explication possible : le mélange de deux groupes aux tailles moyennes différentes, par exemple des femmes et des hommes. Mais l'histogramme seul ne le prouve pas : il faut d'autres informations pour l'établir.

### 51. texte
- Écran : Deux bosses ? Cherchez si *plusieurs groupes* se mélangent
- Voix : Si deux groupes se mélangent, un seul nombre « central » ne décrirait ni l'un ni l'autre. Retenez ce réflexe : deux bosses peuvent signaler un mélange de groupes. Vérifiez-le avec d'autres informations, puis séparez-les avant de résumer.

### 52. courbe
- Écran : Forme *A*
- Graphique histogramme : points [[0, 1], [1, 1], [2, 2], [3, 3], [4, 5], [5, 8], [6, 10], [7, 6]]
- Voix : Forme A : une queue vers la gauche.

### 53. courbe
- Écran : Forme *B*
- Graphique histogramme : points [[0, 1], [1, 3], [2, 6], [3, 9], [4, 9], [5, 6], [6, 3], [7, 1]]
- Voix : Forme B : deux côtés comparables.

### 54. courbe
- Écran : Forme *C*
- Graphique histogramme : points [[0, 2], [1, 7], [2, 9], [3, 4], [4, 4], [5, 9], [6, 7], [7, 2]]
- Voix : Forme C : deux bosses.

### 55. courbe
- Écran : Forme *D*
- Graphique histogramme : points [[0, 6], [1, 10], [2, 8], [3, 5], [4, 3], [5, 2], [6, 1], [7, 1]]
- Voix : Forme D : une queue vers la droite.

### 56. exercice
- Écran : Quatre formes, *A*, *B*, *C* et *D*. Quatre variables : âge au décès, revenus, notes à un examen, tailles d'adultes.
  1. Associez chaque variable à sa forme.
- Formes à l'écran : A, B, C, D
- Voix : À vous. Voici quatre formes, A, B, C et D. Et quatre variables : l'âge au décès, les revenus, les notes à un examen, les tailles d'adultes. Associez chaque variable à sa forme.

### 57. correction
  - Notes : *B*, à peu près symétrique
  - Revenus : *D*, queue à droite
  - Âge au décès : *A*, queue à gauche
  - Tailles d'adultes : *C*, deux bosses
- Réponse : Chaque forme a une explication
- Voix : Voici la correction. Les notes, forme B : souvent à peu près symétriques. Les revenus, forme D : une queue à droite, à cause de quelques revenus très élevés. L'âge au décès, forme A : là où la plupart des décès surviennent à un âge avancé, une queue vers les âges jeunes. Les tailles d'adultes, forme C : deux bosses, sans doute un mélange de femmes et d'hommes. Derrière chaque forme, il y a une explication.

### 58. texte
- Écran : Un seul nombre pour résumer : *la moyenne* ?
- Voix : La forme se voit. Maintenant, mettons-la en un seul nombre. Le premier qui vient à l'esprit : la moyenne.

### 59. titre 4
- Écran : Ce que dit vraiment la moyenne
- Voix : « En moyenne. » On le lit dans tous les articles. Mais que veut dire ce mot, exactement ?

### 60. titre 4.1
- Écran : La moyenne, un partage égal
- Voix : Commençons par une image simple : un partage.

### 61. animation
- Écran : Quatre amis, *une cagnotte*
- Animation « partage » : valeurs=[5, 10, 15, 30], unite=€
  - Ils ont 5, 10, 15 et 30 €
  - Tout dans la cagnotte : *60 €*
  - Partagé en quatre : *15 € chacun*
- Note à l'écran : Autre exemple : quatre amis (fictif).
- Voix : Quatre amis mettent leur argent en commun. Ils ont cinq, dix, quinze et trente euros. Dans la cagnotte, cela fait soixante euros. Partagés à parts égales entre les quatre, cela fait quinze euros chacun : c'est la moyenne.

### 62. formule
- Écran : Moyenne = *somme ÷ nombre*
- Formule : ['\\text{moyenne}=\\dfrac{\\text{somme des valeurs}}{\\text{nombre de valeurs}}', '\\dfrac{5+10+15+30}{4}=\\dfrac{60}{4}=15']
- Voix : D'où la formule : la moyenne, c'est la somme des valeurs divisée par leur nombre. Ici, soixante divisé par quatre : quinze.

### 63. titre 4.2
- Écran : La notation Σ, pas à pas
- Voix : Dans les livres, cette formule s'écrit avec un symbole qui fait peur. Il n'a rien de compliqué.

### 64. formule
- Écran : Σ veut dire *« additionner »*
- Formule : ['\\bar{x}=\\dfrac{x_1+x_2+x_3+x_4}{4}', '\\bar{x}=\\dfrac{1}{n}\\times\\sum_{i=1}^{n}x_i']
- Voix : On appelle les valeurs x un, x deux, x trois, x quatre, et la moyenne x barre. Le symbole sigma indique qu'on additionne toutes les valeurs, de la première à la n-ième. Puis on divise cette somme par n, le nombre de valeurs. C'est exactement le calcul de la cagnotte.

### 65. titre 4.3
- Écran : Le point d'équilibre
- Voix : Deuxième façon de voir la moyenne : un point d'équilibre.

### 66. animation
- Écran : La moyenne, *point d'équilibre*
- Animation « equilibre » : valeurs=[5, 10, 15, 30], unite=€
  - Quatre amis : *5, 10, 15 et 30 €*
  - L'appui à *15 €* : la planche s'équilibre
  - Les écarts se *compensent* : leur somme vaut 0
- Voix : Posons les quatre montants de la cagnotte sur une planche : cinq, dix, quinze et trente euros. Pour que la planche tienne à l'horizontale, l'appui doit se placer exactement à la moyenne, quinze euros. Là, les écarts se compensent : moins dix et moins cinq d'un côté, plus quinze de l'autre, zéro au total ; c'est toujours vrai pour la moyenne, et une seule valeur très loin suffit à déplacer l'équilibre.

### 67. titre 4.4
- Écran : La moyenne pondérée
- Voix : Et quand toutes les valeurs ne comptent pas autant ?

### 68. formule
- Écran : 14 en maths, *coefficient 3* ; 10 en français, *coefficient 1*
- Formule : ['\\dfrac{14\\times 3+10\\times 1}{3+1}', '=\\dfrac{52}{4}=13']
- Voix : Une élève a quatorze en mathématiques, avec un coefficient trois, et dix en français, avec un coefficient un. On multiplie chaque note par son coefficient, on additionne, puis on divise par la somme des coefficients. Quatorze fois trois plus dix, cinquante-deux, divisé par quatre : treize.

### 69. animation
- Écran : Sans coefficients : 12. Avec : *13*
- Animation « ponderee » : notes=[{'valeur': 14, 'coef': 3, 'libelle': 'Maths'}, {'valeur': 10, 'coef': 1, 'libelle': 'Français'}]
  - Sans coefficients : moyenne *12*
  - Coefficient 3 : le 14 compte *trois fois*
  - Avec coefficients : moyenne *13*
- Voix : Représentons les deux notes par des pastilles : quatorze et dix, dont la moyenne simple vaut douze. Le coefficient trois fait compter le quatorze trois fois : trois pastilles de quatorze, une seule de dix. La moyenne glisse alors de douze à treize : la moyenne pondérée donne plus de poids à ce qui compte le plus, ici les mathématiques.

### 70. exercice
- Écran : Classe de *10 élèves* : 12 de moyenne. Classe de *30 élèves* : 8 de moyenne.
  1. Quelle est la moyenne générale des 40 élèves ?
- Voix : À vous. Une classe de dix élèves a douze de moyenne. Une classe de trente élèves a huit de moyenne. Quelle est la moyenne générale des quarante élèves ?

### 71. correction
  - 10 × 12 = 120 points et 30 × 8 = 240 points
  - (120 + 240) ÷ 40 = *9*
- Réponse : 9, et non 10
- Voix : Faisons le calcul. La première classe totalise dix fois douze, cent vingt points ; la seconde, trente fois huit, deux cent quarante points. Trois cent soixante points pour quarante élèves : neuf de moyenne. Pas dix, qui serait la moyenne des deux moyennes : la grande classe pèse trois fois plus.

### 72. chiffre
- Écran : la moyenne tombe *dans le creux*, entre les deux bosses
- Chiffre clé : 170
- Note à l'écran : Moyenne approchée par les centres de classes : environ 169,8 cm.
- Voix : Souvenez-vous des tailles à deux bosses. On ne connaît que les classes : on prend le milieu de chaque classe, par exemple cent cinquante-deux et demi pour la classe de cent cinquante à cent cinquante-cinq, comme valeur de ses adultes. On obtient une moyenne approchée d'environ cent soixante-dix centimètres. Elle tombe dans le creux, là où il y a peu de monde : une moyenne peut ne décrire personne.

### 73. chiffre
- Écran : le trajet moyen de nos *20 salariés*
- Chiffre clé : 21.25
- Note à l'écran : Total des 20 trajets : 425 minutes ; 425 ÷ 20 = 21,25.
- Voix : Et nos vingt salariés ? Leurs trajets font quatre cent vingt-cinq minutes au total. Divisé par vingt, cela donne vingt et une minutes et quart. C'est ce qu'aurait chacun si l'on partageait également le total des durées individuelles. Ce total additionne des trajets séparés : ce n'est pas un temps passé ensemble.

### 74. texte
- Écran : 21,25 min : le trajet d'un salarié *typique* ?
- Voix : 21,25 minutes. Est-ce le trajet d'un salarié typique ? Pas forcément.

### 75. titre 5
- Écran : Moyenne ou médiane ?
- Voix : Pourquoi la plupart des gens gagnent-ils moins que le salaire moyen ? Ça paraît impossible. Et pourtant, c'est très courant.

### 76. exercice
- Écran : Dans un groupe, quelle part des gens gagne *moins que la moyenne* ?
- Voix : Une question pour commencer. Dans un groupe de salariés, quelle part gagne moins que le salaire moyen ? Moins de la moitié, la moitié, ou plus de la moitié ? Gardez votre réponse en tête.

### 77. titre 5.1
- Écran : La moyenne
- Voix : Commençons par la moyenne.

### 78. texte
- Écran : Neuf clients dans un café gagnent de *1 600 €* à *2 800 €* par mois
- Note à l'écran : 1 600 · 1 800 · 1 900 · 2 000 · 2 200 · 2 300 · 2 500 · 2 700 · 2 800 €
- Voix : Neuf clients sont assis dans un café. Ils gagnent entre mille six cents et deux mille huit cents euros par mois.

### 79. formule
- Écran : Leur salaire *moyen*
- Formule : ['\\mathrm{moyenne}=\\dfrac{\\mathrm{somme}}{\\mathrm{nombre}}', '=\\dfrac{19\\,800}{9}=2\\,200']
- Note à l'écran : En euros par mois.
- Voix : La moyenne, c'est la somme divisée par le nombre de personnes. Leurs salaires font au total dix-neuf mille huit cents euros. Divisé par neuf : deux mille deux cents euros.

### 80. texte
- Écran : Un dixième client entre. Il gagne *200 000 €* par mois.
- Voix : La porte s'ouvre. Un dixième client entre : il gagne deux cent mille euros par mois.

### 81. formule
- Écran : La moyenne *s'envole*
- Formule : ['\\dfrac{19\\,800+200\\,000}{10}', '=21\\,980']
- Voix : Recalculons. Dix-neuf mille huit cents plus deux cent mille, divisé par dix. Le salaire moyen du café passe à vingt et un mille neuf cent quatre-vingts euros.

### 82. chiffre
- Écran : des clients gagnent désormais *moins que la moyenne*
- Chiffre clé : 90
- Note à l'écran : 9 clients sur 10.
- Voix : Neuf clients sur dix gagnent maintenant moins que la moyenne. Personne n'a changé de salaire : une seule valeur extrême a tiré la moyenne vers le haut.

### 83. titre 5.2
- Écran : La médiane
- Voix : Il existe un autre indicateur, qui résiste beaucoup mieux : la médiane.

### 84. etapes
- Écran : Calculer une médiane
  - Ranger les valeurs *dans l'ordre*
  - Nombre impair : la valeur *du milieu*
  - Nombre pair : la moyenne des *deux du milieu*
- Voix : La médiane se calcule en trois temps. D'abord, on range les valeurs de la plus petite à la plus grande. Avec un nombre impair de valeurs, la médiane est celle du milieu. Avec un nombre pair, on prend la moyenne des deux valeurs du milieu.

### 85. animation
- Écran : La médiane *par élimination*
- Animation « elimination » : valeurs=[1600, 1800, 1900, 2000, 2200, 2300, 2500, 2700, 2800], ajout=200000, unite=€
  - Neuf salaires, *rangés*
  - On barre le plus *bas* et le plus *haut*
  - Il reste le *milieu* : la 5e valeur
  - Le client à *200 000 €* entre
  - Dix valeurs : la moyenne des *deux du milieu*
- Voix : Revenons au café et rangeons ses neuf premiers salaires, du plus bas au plus haut. Barrons le plus bas et le plus haut, puis recommençons, deux par deux. Il reste la cinquième valeur, deux mille deux cents euros : c'est la médiane, à la position n plus un sur deux. Le client riche entre, avec deux cent mille euros : il y a maintenant dix salaires. On barre à nouveau deux par deux, et il en reste deux, la cinquième et la sixième : la médiane est leur moyenne, deux mille deux cent cinquante euros.

### 86. etapes
- Écran : Une valeur extrême
  - Moyenne : de 2 200 € à *21 980 €*
  - Médiane : de 2 200 € à *2 250 €*
- Voix : Comparons. Une seule valeur extrême fait passer la moyenne de deux mille deux cents à près de vingt-deux mille euros. La médiane, elle, ne gagne que cinquante euros.

### 87. courbe
- Écran : Les dix salaires, *du plus bas au plus haut*
- Graphique points : points [[1, 1600], [2, 1800], [3, 1900], [4, 2000], [5, 2200], [6, 2300], [7, 2500], [8, 2700], [9, 2800], [10, 200000]]
- Note à l'écran : Neuf salaires groupés en bas, un seul tout en haut.
- Voix : Rangeons les dix salaires, du plus bas au plus haut : neuf restent groupés, la médiane avec eux, à deux mille deux cent cinquante euros. Le dixième, deux cent mille euros, tire à lui seul la moyenne jusqu'à vingt et un mille neuf cent quatre-vingts euros, au-dessus de neuf salaires sur dix.

### 88. animation
- Écran : Moyenne et médiane selon la *forme* de la distribution
- Animation « asymetrie » : 
  - Longue traîne vers le haut : moyenne *souvent au-dessus* de la médiane
  - Distribution symétrique : moyenne *proche* de la médiane
  - Longue traîne vers le bas : moyenne *souvent en dessous* de la médiane
- Voix : C'est une tendance fréquente, pas une loi : tout dépend de la forme de la distribution. Quand quelques valeurs très grandes forment une longue traîne vers le haut, comme souvent les salaires ou les patrimoines, la moyenne passe souvent au-dessus de la médiane. Quand la distribution est parfaitement symétrique, elles coïncident ; à peu près symétrique, elles sont proches. Et quand la traîne part vers le bas, la moyenne passe souvent en dessous.

### 89. texte
- Écran : Moyenne au-dessus de la médiane : *au moins la moitié* des valeurs sont inférieures à la moyenne
- Voix : Voilà la réponse au défi. Par définition, au moins la moitié des valeurs sont inférieures ou égales à la médiane. Si la moyenne est au-dessus de la médiane, au moins la moitié des valeurs sont donc inférieures à la moyenne. Pour des salaires, cela fait au moins la moitié des salariés, et souvent bien plus.

### 90. exercice
- Écran : Sept salaires mensuels : 1 500, 1 600, 1 700, 1 800, 1 900, 2 000 et 2 100 €.
  1. Calculez la moyenne et la médiane.
  2. Un salaire de *20 000 €* arrive : recalculez la moyenne et la médiane.
- Voix : À vous. Sept salaires mensuels : mille cinq cents, mille six cents, mille sept cents, mille huit cents, mille neuf cents, deux mille et deux mille cent euros. Calculez la moyenne et la médiane. Puis recommencez après l'arrivée d'un salaire de vingt mille euros.

### 91. correction
  - Avant : 12 600 ÷ 7 = *1 800 €* ; médiane *1 800 €*
  - Après : 32 600 ÷ 8 = *4 075 €*
  - Médiane : (1 800 + 1 900) ÷ 2 = *1 850 €*
- Réponse : La moyenne fait plus que doubler, la médiane gagne 50 €
- Voix : Voici la correction. Avant, la somme vaut douze mille six cents euros : divisée par sept, la moyenne est de mille huit cents euros, comme la médiane, la quatrième valeur. Après, la somme passe à trente-deux mille six cents euros, divisée par huit : quatre mille soixante-quinze euros. Avec huit valeurs, la médiane est la moyenne de la quatrième et de la cinquième : mille huit cent cinquante euros. La moyenne a plus que doublé, la médiane n'a gagné que cinquante euros.

### 92. titre 5.3
- Écran : Laquelle choisir ?
- Voix : La moyenne est sensible aux valeurs extrêmes : une seule valeur très élevée peut la tirer vers le haut. La médiane, elle, dépend de la position centrale des valeurs ordonnées. Cela ne signifie pas qu'elle est toujours meilleure : le bon indicateur dépend de la question que l'on cherche à éclairer.

### 93. animation
- Écran : Chaque indicateur répond à *sa* question
- Animation « questions » : questions=[{'question': 'Que gagne un salarié *typique* ?', 'reponse': 'la *médiane*', 'icone': 'mediane'}, {'question': 'Combien coûtent *tous* les salaires ?', 'reponse': "la *moyenne* × l'effectif", 'icone': 'equilibre'}]
  - « Que gagne un salarié typique ? » → la *médiane*
  - « Combien coûtent tous les salaires ? » → la *moyenne*, × l'effectif
  - Le plus honnête : donner *les deux*
- Voix : Chaque indicateur répond à sa propre question. Pour savoir ce que gagne un salarié typique, la médiane est la bonne réponse. Pour savoir combien coûtent tous les salaires ensemble, il faut la moyenne, multipliée par le nombre de salariés : la médiane ne le permet pas. Le plus honnête est souvent de donner les deux, car l'écart entre elles dit à lui seul si la distribution est asymétrique.

### 94. texte
- Écran : La médiane a sa limite : elle ignore *l'ampleur* des écarts
- Note à l'écran : Avec un client à 2 millions € par mois, la médiane du café resterait 2 250 €.
- Voix : La médiane a aussi sa limite : elle ignore l'ampleur des écarts. Que le client riche gagne deux cent mille euros ou deux millions, la médiane du café reste la même. Elle indique le centre, mais pas à quel point les valeurs sont dispersées : deux groupes peuvent avoir la même médiane et des inégalités très différentes.

### 95. titre 5.4 · univers immersif (fond sombre)
- Écran : Laboratoire : une seule valeur extrême
- Voix : Deuxième laboratoire. Faisons bouger une seule valeur, et regardons qui suit.

### 96. animation · univers immersif (fond sombre)
- Écran : Le dixième client : *curseur* de 2 300 à 200 000 €
- Animation « curseur » : valeurs=[1600, 1800, 1900, 2000, 2200, 2300, 2500, 2700, 2800, 2300], indice=9, vers=200000, axe_max=3600, unite=€, decimales=0
  - Neuf salaires, et un *dixième client* à 2 300 €
  - Médiane : *2 250 €*
  - Moyenne : *2 210 €*
  - Le dixième monte à 200 000 € : la moyenne *s'envole*, la médiane *reste*
- Voix : Les neuf salaires du café, et un dixième client dont on fait monter le salaire. À chaque position, on range à nouveau les dix salaires et on recalcule. À deux mille trois cents euros : moyenne deux mille deux cent dix, médiane deux mille deux cent cinquante. À cinquante mille : moyenne six mille neuf cent quatre-vingts, médiane toujours deux mille deux cent cinquante. À deux cent mille : moyenne vingt et un mille neuf cent quatre-vingts. La médiane ne bouge pas : dès deux mille trois cents euros, le dixième client se range après le sixième salaire, et les deux valeurs du milieu restent deux mille deux cents et deux mille trois cents.

### 97. animation · univers immersif (fond sombre)
- Écran : Un salarié *déménage* : 44 → 120 minutes
- Animation « curseur » : valeurs=[4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44], indice=19, vers=120, axe_max=55, unite=minutes, decimales=2
  - Les mêmes *20 salariés*
  - Médiane : *20 min*
  - Moyenne : *21,25 min*
  - 44 → 120 minutes : moyenne *25,05 min*, médiane *20 min*
- Voix : Retour à l'entreprise. On n'ajoute personne : le salarié qui mettait quarante-quatre minutes déménage et en met cent vingt. Ce sont toujours les mêmes vingt salariés. La moyenne passe de vingt et une minutes et quart à vingt-cinq minutes et cinq centièmes. La médiane reste à vingt minutes. Un seul individu a bougé, et seule la moyenne l'a suivi.

### 98. etapes
- Écran : À retenir
  - Comparer des *fréquences*, pas des effectifs
  - Classes inégales : la *surface* compte
  - Regarder la *forme* avant tout calcul
  - Moyenne : *partage égal* du total
  - Médiane : coupe en *deux* ; queue à droite, moyenne souvent au-dessus
- Voix : Ce qu'il faut retenir. Un : on compte, puis on rapporte au total ; on compare des fréquences, pas des effectifs. Deux : des barres séparées pour des catégories, un histogramme pour des nombres, et quand les classes sont inégales, c'est la surface qui compte. Trois : regardez la forme avant tout calcul ; deux bosses, c'est peut-être deux groupes. Quatre : la moyenne, c'est le total divisé par le nombre, ce qu'aurait chacun si l'on partageait également ; une seule valeur extrême la déplace. Cinq : la médiane coupe en deux ; avec une queue à droite, la moyenne est souvent au-dessus de la médiane. Choisissez celle qui répond à votre question.

### 99. exercice
- Écran : Dix salariés, temps de trajet en minutes : 5, 8, 12, 15, 15, 18, 22, 25, 30 et *90*.
  1. Quelle part met moins de 20 minutes ?
  2. Quelle forme a cette distribution ?
  3. Calculez la moyenne et la médiane.
  4. Combien de salariés sont sous la moyenne ? Quel « trajet typique » annonceriez-vous ?
- Voix : À vous, et mettez la vidéo en pause pour répondre. Dix salariés d'une agence fictive mettent, en minutes : 5, 8, 12, 15, 15, 18, 22, 25, 30 et 90. Un : quelle part met moins de 20 minutes ? Deux : quelle forme a cette distribution ? Trois : calculez la moyenne et la médiane. Quatre : combien de salariés sont sous la moyenne, et quel nombre annonceriez-vous comme « trajet typique » ?

### 100. correction
  - Moins de 20 min : 6 sur 10, *60 %*
  - Forme : *queue à droite* (le trajet de 90 min)
  - Moyenne : 240 ÷ 10 = *24 min*
  - Médiane : (15 + 18) ÷ 2 = *16,5 min*
- Voix : Un : 6 sur 10, soit 60 % (5, 8, 12, 15, 15 et 18). Deux : une queue à droite, due au trajet de 90 minutes. Trois : somme 240, moyenne 240 ÷ 10 = 24 minutes ; dix valeurs, donc la médiane est la moyenne des 5e et 6e : (15 + 18) ÷ 2 = 16,5 minutes.

### 101. etapes
- Écran : Correction (suite)
  - 7 sur 10 sous la moyenne : trajet typique *16,5 min*
  - Si 90 était une erreur pour 35 : moyenne *18,5 min*, médiane inchangée
- Voix : Quatre : 7 salariés sur 10 sont sous la moyenne ; le trajet typique, c'est la médiane, 16,5 minutes. Pour aller plus loin : si les 90 minutes étaient une erreur de saisie pour 35, la moyenne tomberait à 18,5 minutes et la médiane ne bougerait pas.

### 102. cloture
- Écran : Prochain épisode : *les écarts*. Une question ? *En commentaire*
- Voix : Voilà : la prochaine fois qu'on vous annonce un salaire moyen ou un temps d'attente moyen, vous saurez quelle question poser. Mais deux équipes peuvent avoir la même médiane et des trajets très différents : c'est tout l'enjeu du prochain épisode, sur les écarts. Si cette vidéo vous a été utile, abonnez-vous, laissez un like et partagez-la avec quelqu'un à qui elle servira. Et si un exercice vous résiste, écrivez-nous en commentaire : on vous aide, gratuitement. Merci d'avoir regardé, et à très vite !

### 103. fin
- Écran : Éveiller par les chiffres.
- Voix : ACTU-BASICS. Éveiller par les chiffres.
