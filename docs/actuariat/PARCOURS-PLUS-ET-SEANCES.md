# Parcours Actuariat : extension « + » et vidéos des séances du parcours actuariel

Statut : **proposition de Claude (2026-11-23), à valider par JG.** Elle complète la v3.3 (`PARCOURS-ACTUARIAT-v3.md`) sans la modifier. Rien n'est produit sur cette base avant validation.

Demande de JG (2026-11-23) : le parcours de remise à niveau en actuariat (dépôt public [`JohnGAB7/parcours-actuariel`](https://github.com/JohnGAB7/parcours-actuariel)) utilise les vidéos d'Actu-Basics à l'étape 1 « Vidéo » de chaque séance. Ce parcours prévoit plus de modules que le programme d'Actu-Basics ; le programme d'Actu-Basics grandit donc pour les couvrir.

## 1. Le principe

- **Un module du parcours = un épisode long Actu-Basics** (règle LMEC-DEC-009 : un épisode couvre plusieurs notions liées), dont les chapitres sont les leçons du module (A1.01 à A1.05…). Chaque séance pointe le chapitre qui la concerne. FR et EN en même temps, comme toute la chaîne.
- **Mise à jour du 2026-11-23 (dépôt du parcours, PR #2 à #4)** : l'entrée d'Actu-Basics n'est plus la séance seule mais le fichier `a-produire/<module>.md`, déposé dans le parcours quand JG maîtrise le module (notions, exercices corrigés, pièges, vocabulaire anglais, notes pour la vidéo). Les chiffres des vidéos viennent des séances : **taux fictif de 2,5 %** et table MK.
- **Niveau** : la vidéo vise un débutant (intuition, exemple chiffré, exercice simple). La séance garde le niveau examen (formes continues, code, IAS 19). Règle reprise de `docs/ACTU-BASICS.md` du parcours : la vidéo prend le premier tiers de la séance.
- **Ordre de production** : l'ordre du parcours, **en commençant par A1** (demande de JG, 2026-11-23). Les brouillons de fiches sont préparés à partir des séances déjà écrites (a1/s01, puis a3/s01 et a3/s02) ; ils sont finalisés et rendus quand `a-produire/<module>.md` arrive. A1.01 et A2.01 existent déjà (pilote) et servent tout de suite aux séances A1 et A2.
- **Aucun échange direct entre projets** : le lien passe par les dépôts (section 4).
- **Règles inchangées** : JG's Holding toujours annoncée comme fictive ; chaque nombre passe par `verifier` ; aucun chiffre réel sans source datée ; supports de cours et CV de JG jamais sur un dépôt ; rien de fusionné ni publié sans l'accord de JG.

## 2. Correspondance des modules

| Parcours actuariel | Programme Actu-Basics | Leçons | État |
| --- | --- | --- | --- |
| A1 · Mathématiques financières | A1 (v3.3) | 5 | A1.01 rendue (pilote) |
| A2 · Probabilités pour l'assurance | A2 (v3.3) | 6 | A2.01 rendue (pilote) |
| A2b · Statistique pour l'assurance | A2b (v3.3) | 4 | à écrire |
| A3 · Vie et mortalité | A3 (v3.3) | 6 | **A3.01 en premier** (séance a3/s01) |
| A3+ · Temps continu, plusieurs têtes, tables prospectives | **A3+ (nouveau)** | 4 | proposé ici |
| A4 · Provisions vie | A4 (v3.3) | 5 | à écrire |
| A4+ · Variable de perte, Zillmer, profit testing | **A4+ (nouveau)** | 3 | proposé ici |
| A4+ · Décréments multiples, plans DB et IAS 19 | **A4R (nouveau, « Retraite »)** | 4 | proposé ici |
| A5 · Sinistres non-vie | A5 (v3.3) | 5 | à écrire |
| A6 · Tarification | A6 (v3.3) | 5 | à écrire |
| A6+ · GAM, GBM, élasticité, tarification sous contrainte | **A6+ (nouveau)** | 4 | proposé ici |
| A7 · Provisionnement non-vie | A7 (v3.3) | 4 | à écrire |
| A7+ · Bornhuetter-Ferguson, Cape Cod, bootstrap | **A7+ (nouveau)** | 3 | proposé ici |
| A8 · Risque et solvabilité | A8 (v3.3) | 5 | à écrire |
| A8+ · IFRS 17, capital canadien (LICAT, MCT), normes de l'ICA | **A8+ (nouveau, Canada)** | 4 | proposé ici |
| O1 · Python : NumPy, pandas, tests | **O1 (nouveau)** | 3 | proposé ici |
| O2 · SQL sur un portefeuille fictif | **O2 (nouveau)** | 2 | proposé ici |
| O3 · Excel et VBA de l'actuaire | **O3 (nouveau)** | 2 | proposé ici |
| — | A0 (orientation) et A9 (projet) | 5 + 3 | hors parcours, inchangés |

Le parcours a deux modules nommés « A4+ ». Côté Actu-Basics, le second devient **A4R** (retraite) pour garder des identifiants uniques. Dans les noms de fichiers, « + » s'écrit `p` : `A3p.01`, `act-a3p-01-…`.

**Effet sur le volume** : 29 leçons de plus, soit **82 leçons longues** au lieu de 53 (hors vidéos d'exercices). À ce rythme (un ensemble bilingue toutes les une à deux semaines, v3.3 § 2.6), le programme complet dépasse deux ans : la priorité reste l'ordre des séances, pas l'exhaustivité.

## 3. Contenu proposé des modules « + »

Les titres sont des propositions de travail. Chaque leçon garde le niveau débutant à l'écran ; le niveau examen reste dans la séance. Les faits réglementaires (dates, organismes, tables) seront vérifiés par Perplexity au moment de l'écriture, comme pour toute leçon.

**A3+ · Temps continu, plusieurs têtes, tables prospectives**
1. La force de mortalité : mourir « à un instant » (lien entre μₓ et lₓ, loi de Gompertz et de Makeham).
2. Les âges fractionnaires : que se passe-t-il entre deux anniversaires (UDD, force constante) ?
3. Deux vies : vie jointe et dernier survivant.
4. Les tables prospectives : pourquoi une table vieillit (amélioration de la mortalité ; exemple canadien CPM2014, **à vérifier**).

**A4+ · Variable de perte, Zillmer, profit testing**
1. La variable de perte et le principe d'équivalence.
2. Les frais d'acquisition et la provision zillmérisée.
3. Le profit testing : la signature de profit d'un contrat de JG's Holding.

**A4R · Décréments multiples, plans DB et IAS 19**
1. Plusieurs causes de sortie : décès, démission, retraite (tables à décréments multiples).
2. Un régime à prestations définies : ce que l'employeur promet.
3. La méthode des unités de crédit projetées et la DBO.
4. IAS 19 : coût des services, intérêt, écarts actuariels, et la sensibilité au taux et à la table.

**A6+ · GAM, GBM, élasticité, tarification sous contrainte**
1. Au-delà du GLM : les effets non linéaires (GAM).
2. Les arbres boostés (GBM) : gain de précision, perte de lisibilité.
3. L'élasticité-prix : le client qui part quand le prix monte.
4. Tarifer sous contrainte : réglementation, équité, stabilité des primes.

**A7+ · Bornhuetter-Ferguson, Cape Cod, bootstrap**
1. Bornhuetter-Ferguson : mêler l'historique et un a priori.
2. Cape Cod : l'a priori estimé à partir des données.
3. Le bootstrap : une distribution des provisions, pas un seul chiffre.

**A8+ · IFRS 17, capital canadien, normes de l'ICA**
1. IFRS 17 : meilleure estimation, ajustement pour risque, marge sur services contractuels.
2. Le capital des assureurs vie au Canada : le TSAV / LICAT (BSIF / OSFI).
3. Le capital des assureurs IARD : le TCM / MCT.
4. Les normes de pratique de l'ICA et le rôle de l'actuaire désigné.

**O1 à O3 · Outils du métier** (décision de JG du 22/11/2026 : la programmation entre dans les cours avancés, dont l'actuariat avancé)
- O1 : un tableau de mortalité en NumPy ; un portefeuille en pandas ; tester un calcul actuariel.
- O2 : interroger un portefeuille fictif en SQL ; agréger des sinistres par année de survenance.
- O3 : une table de mortalité dans Excel ; automatiser un calcul en VBA.

Pour O1 à O3, la vidéo montre l'idée et le résultat ; l'écriture du code reste dans la séance (règle du parcours : JG écrit lui-même ses exercices).

## 4. Le lien entre les deux dépôts

Circuit défini par le parcours (`a-produire/README.md` et `docs/ACTU-BASICS.md` de son dépôt, état du 2026-11-23) :

1. Les séances du module sont écrites dans `parcours-actuariel` (`contenus/<module>/sNN.yaml`), et JG les travaille jusqu'à maîtriser le module.
2. Un fichier `a-produire/<module>.md` y est alors déposé, par PR, après accord de JG : c'est **l'entrée** d'Actu-Basics.
3. Côté Actu-Basics : Claude écrit ou finalise les fiches de conception du module à partir de ce fichier (champ `source_seance` : séances et commit), ChatGPT relit, Perplexity vérifie les faits extérieurs, JG valide, puis le moteur rend l'épisode (9:16 et 16:9, chapitres YouTube).
4. Le registre [`videos-seances.yaml`](videos-seances.yaml) de ce dépôt donne, pour chaque séance, le chapitre, l'état et, une fois publiées, les URL FR et EN avec le début et la fin du chapitre. C'est le seul fichier que le parcours a besoin de lire pour remplir son étape « Vidéo ».

**Préparer sans attendre.** Rien n'empêche de préparer les brouillons dès qu'une séance existe : ils reprennent ses chiffres et sont recalés sur `a-produire/<module>.md` à son arrivée. Aucun rendu final avant ce fichier et l'accord de JG.

**Durée dans la séance.** L'étape « Vidéo » d'une séance prévoit environ 3 minutes ; un épisode de module dure bien plus. La séance pointe le **chapitre** utile (lien horodaté, champs `debut` et `fin` du registre), avec l'épisode complet en lien « pour aller plus loin ». Les chapitres YouTube existent déjà dans le moteur (`chapitres.txt` en 16:9).

**Côté parcours** (à faire dans l'autre dépôt, pas ici) : son étape `video` affiche aujourd'hui « Vidéo en préparation ». Il lui suffira de lire `video_fr`, `debut` et `fin` dans le registre.

**Correspondance des séances écrites (2026-11-23)**

| Séance du parcours | Contenu | Chapitres Actu-Basics |
| --- | --- | --- |
| a1/s01 · Intérêt composé et annuités certaines (2,5 %) | i, v, d, δ, aₙ, äₙ, valeur actuelle d'une suite de flux | A1.01 (rendue) et A1.04 ; A1.03 pour la somme de flux. d et δ restent dans la séance (niveau examen) |
| a3/s01 · Force de mortalité et espérance de vie (MK) | lₓ, ₜpₓ, μₓ, eₓ | A3.01 ; μₓ dans A3+.01 |
| a3/s02 · Valeur actuelle d'une assurance (MK, 2,5 %) | A¹ₓ:ₙ, ₙEₓ, mixte Aₓ:ₙ | A3.02 et A3.03 ; la mixte comme application de A3.03 |

## 5. Décisions à prendre par JG

1. Valider l'extension (29 leçons, modules A3+, A4+, A4R, A6+, A7+, A8+, O1 à O3) ou indiquer ce qui doit changer.
2. Valider le lien par chapitre horodaté (section 4) ou préférer une vidéo courte dédiée à chaque séance.
3. ~~A3.01 : choisir la table de l'exemple~~ : option C choisie par JG le 2026-11-23 (`A3-01-PROPOSITION.md`, section 14).
