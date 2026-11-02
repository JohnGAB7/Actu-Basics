# 10. Arbitrages demandés {#arbitrages}

Les décisions éditoriales appartiennent à ChatGPT, et JG arbitre. Cette section distingue ce que JG a **déjà décidé**, et que le programme applique, de ce qui reste **à décider**.

## 10.1 Décisions déjà prises par JG, appliquées telles quelles

| Décision | Source |
|---|---|
| Aucune publication sur les réseaux avant d'avoir un catalogue suffisant | Ticket n° 10 |
| Validation humaine explicite avant toute publication | Journal des décisions, LMEC-DEC-003 ; constitution éditoriale, section 9 |
| La durée d'une vidéo découle de l'objectif pédagogique, jamais d'un plafond arbitraire | Constitution éditoriale, section 10 ; ticket n° 10 |
| Trois piliers : statistiques de A à Z, économétrie, phénomènes du quotidien et actualité | Ticket n° 10 |
| Éditions FR et EN autonomes, sans traduction mécanique | Identité de marque ; ticket n° 10 |
| Rôles : Claude structure, ChatGPT relit, JG valide le PDF final | Ticket n° 10 ; LMEC-DEC-002 |
| Toutes les vidéos pédagogiquement pertinentes sont intégrées au catalogue, y compris les approfondissements et les spécialisations. Aucune n'est marquée optionnelle : c'est au spectateur de choisir. Le catalogue est exhaustif, l'ordre de production se priorise | Message de JG, 2/11/2026 ; règle d'exhaustivité proposée par ChatGPT sur la PR n° 12 |
| Marque ACTU-BASICS, slogans « Éveiller par les chiffres. » et “Enlightening through numbers.” | Identité de marque |

## 10.2 Recommandations à valider

Claude fait une recommandation pour chacune, sans la considérer comme acquise. Les points **A1 à A3** touchent des décisions déjà écrites dans le dépôt : ils sont signalés comme tels.

| N° | Question | Options | Recommandation de Claude (statut : à valider) |
|---|---|---|---|
| **A1** *(touche une décision existante)* | Faut-il adopter les trois piliers comme structure de référence, à la place des quatre familles d'`ARCHITECTURE_EDITORIALE.md` ? | (a) Trois piliers au-dessus des familles, sans changer le moteur · (b) Remplacer les familles par les piliers dans le moteur · (c) Garder les quatre familles seules | **(a)**. Les familles restent un champ technique ; on ajoute seulement une famille `econometrie` si JG veut l'identifier à part dans les métadonnées. |
| **A2** *(touche une décision existante)* | La règle du stock préalable est déjà décidée par JG (10.1). Reste à mettre à jour la section 5 d'`ARCHITECTURE_EDITORIALE.md`, qui proposait un rythme dès le lancement. | (a) Mettre le document à jour après validation de ce programme · (b) Le laisser en l'état, avec un renvoi | **(a)**. |
| **A3** *(touche une décision existante)* | La répartition thématique de la constitution éditoriale (démographie 20 %, etc.) s'applique-t-elle au cursus ou seulement à l'actualité ? | (a) Actualité seulement · (b) Tout le catalogue | **(a)**. Un cursus suit l'ordre des notions, pas des quotas de thèmes. |
| **A4** | Seuil de lancement | (a) Vague 1 et 12 semaines de stock, en épisodes maîtres prêts à publier (section 7.2) · (b) Vagues 1 et 2 complètes · (c) Autre | **(a)**, à recalculer après la phase pilote, quand le temps humain par vidéo sera mesuré. |
| **A5** | Place de l'économétrie au lancement | (a) Peu de théorie (E1), beaucoup de sujets économiques du quotidien · (b) Avancer E2 à E4 en simplifiant | **(a)**. Avancer la théorie obligerait à enseigner la régression sans ses prérequis. |
| **A6** | Vidéos d'actualité avant le lancement | (a) Produites seulement en phase 3, 4 à 6 vidéos · (b) Produites dès maintenant | **(a)**. Une vidéo d'actualité produite des mois avant sa publication sera périmée. |
| **A7** | Format des leçons longues | (a) YOUTUBE_LESSON 16:9 pour les vidéos de plus de 10 min · (b) Tout en vertical, découpé en épisodes | **(a)**, après un essai sur une vraie leçon (S9.01, par exemple). Le découpage reste possible si l'essai déçoit. |
| **A8** | Place de la statistique bayésienne | (a) Bayes dès le niveau 2 (S4.10), méthode bayésienne en branche S12 · (b) Bayésien intégré dès le niveau 3, en parallèle du fréquentiste | **(a)**. Cela reste simple pour le débutant, et la comparaison des deux approches (S12.06) garde l'équilibre. |
| **A9** | Code à l'écran | (a) Pas de code dans les vidéos, scripts Python et R fournis en description · (b) Python montré à l'écran à partir du niveau 3 · (c) Aucun code | **(a)** au lancement. La chaîne enseigne le raisonnement, pas la programmation. |
| **A10** | La vidéo de lancement (paradoxe des anniversaires) | (a) Elle compte comme S4.06 dans le stock · (b) S4.06 est refaite en leçon, et la vidéo de lancement garde son rôle de présentation | **(a)**. Elle remplit déjà les objectifs de S4.06. Elle utilise le complément, enseigné en S4.05 : il faudra veiller à ce que S4.05 soit produite avant sa publication. |

## 10.3 Points de vigilance pour la suite de la revue

La revue indépendante annoncée dans le ticket est la prochaine étape. Pour la faciliter, voici les points où Claude est le moins sûr de ses choix :

1. **Granularité du niveau 1** : 30 vidéos avant les probabilités formelles. La version 1.1 ajoute un premier contact intuitif avec le hasard (S1.11). Est-ce suffisant ?
2. **Ordre S6 et S7** : la marge d'erreur (S6.05) arrive avant l'intervalle de confiance formel (S7.06), pour répondre tôt à une question d'actualité. C'est un choix pédagogique discutable.
3. **Méthodes non paramétriques (S11.04)** : placées avec les méthodes computationnelles plutôt qu'avec les tests.
4. **Exemples historiques** : ils ont maintenant une référence primaire ou universitaire (section 9.5). L'anecdote du casino de Monte-Carlo en 1913, mal documentée, a été remplacée par une simulation. Les références doivent encore être relues dans le texte avant chaque script.
5. **Titres anglais** : titres de travail, à revoir par un regard éditorial anglophone.
6. **Références bibliographiques** : les ressources en ligne ont été vérifiées (section 9). Les éditions des livres imprimés restent à confirmer.
7. **GAISE** : la version 1.1 citait à tort la version de 2016 comme seule version en vigueur. ChatGPT a raison : le portail du rapport (amstat.quarto.pub/college-gaise) annonce une révision 2025 publiée par étapes. La version 1.2 la cite, avec la section « Assessment » signalée comme encore en préparation.

## 10.4 Points débattus avec ChatGPT (revue croisée de la version 1.1)

| Proposition de ChatGPT | Position de Claude | Ce qui change |
|---|---|---|
| Comparer deux parcours de démonstration (actuel, ou en spirale avec une régression descriptive précoce) sur les 12 à 15 premières leçons | **Accord partiel.** Le parcours actuel contient déjà une spirale : la droite de régression descriptive (S3.07) arrive au niveau 1, avant les probabilités, et après S3.06 (corrélation et causalité). Produire deux parcours de 12 à 15 vidéos coûterait 50 à 130 heures de plus, pour un test sur quelques testeurs incapable de départager deux séquences entières. | Spirale rendue explicite (S3.07 se termine sur trois questions ouvertes, S9.01 y revient). Le pilote teste le point charnière : un testeur peut-il dire ce que la droite de S3.07 ne permet pas de conclure ? |
| Enseigner les graphes causaux avant les pièges des mauvais contrôles | **Accord.** | Nouvelle vidéo E1.05, au niveau 2, sans régression ; E3.04 en devient l'application. |
| Registre des hypothèses pour chaque méthode | **Accord**, sans vidéo supplémentaire. | Rubrique obligatoire de la fiche de conception pour E5 et E7. |
| Initiation à l'analyse de sensibilité | **Accord.** C'est la question honnête de toute étude observationnelle. | Nouvelle vidéo E4.05, en intuition (E-value), à la fin du module sur l'endogénéité. |
| Clarifier la place de l'appariement et du score de propension | **Accord.** C'était un manque de la version 1.1. | Nouvelle vidéo E7.07, présentée comme outil de conception et non comme substitut au tirage au sort. |
| Ne pas laisser croire qu'un test de pré-tendance prouve les tendances parallèles | **Accord.** | Objectifs et idées fausses de E7.03 réécrits. |
| Enquête reproductible et dimension pratique récurrente | **Accord sur la fiche, accord partiel sur l'écran.** Une manipulation de données dans chaque vidéo verticale alourdirait le format court. | Cycle d'enquête, choix données, simulation ou calcul, et reproductibilité dans chaque fiche ; scripts en description (A9) ; démonstration complète en S3.09. |
| Évaluation plus robuste dans le pilote | **Accord.** La vérification différée reste facultative, selon le nombre de testeurs disponibles. | Questions de transfert et de diagnostic d'erreur, critère de validation réécrit (section 7.2). |

## 10.5 Proposition ARCH/GARCH (revue de la version 1.2)

| Question posée par ChatGPT | Position de Claude | Ce qui change |
|---|---|---|
| Faut-il intégrer ARCH et GARCH comme un vrai chapitre ? | **Accord.** C'était un manque : le programme ne modélisait que la moyenne conditionnelle des séries. | Nouveau module E9, niveau 4, juste après E8. Les anciens E9 et E10 deviennent E10 et E11 (rien n'était produit). |
| Où le placer ? | Après S14 (stationnarité, ARMA, prévision hors échantillon), **sans dépendre de E8** : les rendements sont déjà stationnaires, et racines unitaires ou cointégration ne servent pas ici. | Prérequis contrôlés par le script : S14.02, S14.04, S14.05, S7.05, E3.02, M1.04. |
| Trois leçons, ou deux suffisent ? | **Trois.** Fusionner estimation et prévision avec le modèle donnerait une leçon de plus de 20 minutes, et c'est dans l'évaluation hors échantillon que vivent les erreurs les plus graves. En revanche, la démonstration reproductible proposée devient la leçon E9.03 elle-même, au lieu d'une vidéo de plus. | E9.01 (faits stylisés), E9.02 (ARCH → GARCH(1,1)), E9.03 (cas reproductible : test ARCH-LM, estimation, résidus, prévision contre la volatilité historique). |
| Quelles extensions ? | Claude proposait deux vidéos optionnelles et la bibliographie seule pour le reste. **JG a tranché** : toutes les vidéos possibles sont intégrées, aucune n'est optionnelle. | E9.04 asymétrie et loi de Student, E9.05 VaR et backtesting (loi binomiale, S5.04), E9.06 changements de régime (chaînes de Markov, S16.02), E9.07 volatilité stochastique (MCMC, S12.04), E9.08 corrélations dynamiques et DCC (matrices, M3.02), E9.09 volatilité réalisée et modèle HAR. |
| Branche « économétrie financière » ? | **Désaccord.** ARCH est né sur l'inflation britannique (Engle, 1982). Une branche promettrait la valorisation d'actifs et le portefeuille, que le programme n'enseigne pas. Un module clairement nommé, plus un profil de parcours, suffit. | Profil « Finance et risque » en section 3.3. |
| Quels prérequis imposer, lesquels rappeler ? | **Imposés** : stationnarité et autocorrélation (S14.02), ARMA comme équation de la moyenne (S14.04), prévision hors échantillon (S14.05), maximum de vraisemblance (S7.05), hétéroscédasticité (E3.02). **Rappelés à l'écran** : logarithme (M1.04), loi binomiale (S5.04). **Pour les extensions** : chaînes de Markov (S16.02) pour E9.06, MCMC (S12.04) pour E9.07, matrices (S13.01, M3.02) pour E9.08. | Contrôlé par le script ; 16 calculs ajoutés (persistance, variance de long terme, demi-vie, prévision à 10 jours, VaR, test de Kupiec, durée d'un régime, variance d'un portefeuille, volatilité réalisée). |

## 10.6 Revue de la version 1.3 : règle d'exhaustivité et corrections de E9

| Demande de ChatGPT | Position de Claude | Ce qui change |
|---|---|---|
| Règle d'exhaustivité du catalogue | **Accord.** Elle rejoint la décision de JG. Une seule nuance : le mot « optionnel » n'est plus utilisé, puisque JG a demandé que ce soit le spectateur qui rende une vidéo optionnelle. | Taxonomie descriptive calculée par le script (section 3.3) : socle, approfondissement, spécialisation, sujet autonome, rappel. Le script refuse le champ « option ». |
| E9.06 à E9.08 (volatilité stochastique, GARCH multivarié, volatilité réalisée) | **Accord**, déjà intégrées en version 1.4, avec les changements de régime. | Ajout de **E9.10** mémoire longue (FIGARCH et HAR). Le modèle CCC est nommé dans E9.08. La volatilité stochastique demande maintenant le filtre de Kalman (nouvelle S14.07). |
| Quasi-vraisemblance (E9.03) | **Accord.** La formulation de la version 1.3 était trop large. | Convergence et normalité asymptotique conditionnées à une bonne spécification des moments conditionnels et à des conditions de régularité, erreurs standard de Bollerslev-Wooldridge ; aucune protection contre une dynamique de variance mal spécifiée. |
| Séquence du test ARCH-LM | **Accord.** | Équation de la moyenne d'abord, test sur ses résidus ; un test non significatif ne prouve rien. |
| Mesures de volatilité | **Accord.** | Quatre objets distingués dès E9.01 ; en E9.03, le verdict d'une comparaison dépend de la mesure de référence et de la fonction de perte. |
| VaR et Expected Shortfall, backtesting | **Accord.** Le test de Kupiec ne teste que la fréquence. | Exercice en quatre questions qui sépare VaR (3,49 %) et ES (4,00 %) ; test d'indépendance de Christoffersen ajouté. |
| Conditions du GARCH(1,1) | **Accord.** | Positivité, stationnarité au second ordre (α + β < 1, variance finie) et stationnarité stricte (possible avec α + β = 1) distinguées. |
| Annualisation | **Accord.** | Convention √252 énoncée avec ses hypothèses, valable pour la variance de long terme seulement. |
| Trois niveaux en E9.02 | **Déjà en place** : comprendre M1, appliquer M2, démontrer M3. | Aucun. |
| Solutions détaillées | **Accord.** | Nouveau champ « Correction détaillée », rempli pour E9 et pour toutes les nouvelles vidéos chiffrées. Les autres vidéos l'auront dans leur fiche de conception. |
| Cohérence documentaire | **Accord**, le LISEZMOI renvoyait encore au PDF v1.2. | Noms, versions et comptes synchronisés ; les comptes du PDF sont calculés par le script à partir des entrées réellement lues. |
| Distinguer vidéos conçues, cataloguées et à produire | **Accord.** | État affiché sur chaque vidéo. |

## 10.7 Inventaire : vidéos absentes du catalogue ou laissées en bibliographie

En appliquant la règle d'exhaustivité, Claude a comparé le catalogue aux programmes universitaires de référence cités en section 9. Les 35 vidéos suivantes ont été ajoutées en version 1.5 :

| Pilier | Vidéos ajoutées |
|---|---|
| Statistiques, niveaux 2 et 3 | S5.14 lois log-normale et de Pareto · S5.15 espérance conditionnelle · S6.07 non-réponse et redressement · S6.08 calage sur marges · S8.10 adéquation à une loi · S8.11 méta-analyse · S9.12 régression quantile · S9.13 plans factoriels, fractions et blocs · S11.07 lissage, splines, GAM · S11.08 estimation de densité par noyau |
| Statistiques, niveau 4 | S13.06 analyse factorielle · S13.07 loi normale multivariée · S13.08 copules · S14.06 analyse spectrale · S14.07 espace-état et filtre de Kalman · S14.08 données spatiales et krigeage · S15.04 lois paramétriques et risques concurrents · S17.07 boosting · S17.08 réseaux de neurones vus par un statisticien · S17.09 prédiction conforme · S18.04 Wald, rapport de vraisemblance, score · S18.05 algorithme EM · S18.06 valeurs extrêmes |
| Économétrie | E4.06 identification partielle · E5.05 GMM · E6.05 économétrie spatiale · E7.08 effets hétérogènes et apprentissage automatique causal · E8.06 projections locales · E8.07 effet d'un événement sur une série (modèles structurels bayésiens) · E9.10 mémoire longue de la volatilité · E10.04 choix discrets multinomiaux · E10.05 modèles structurels de demande |
| Quotidien | Q2.06 pourquoi les études se contredisent · Q4.07 le seuil de pauvreté · Q5.04 quand une IA annonce 90 % de confiance |

Restent hors du catalogue, faute d'être des sujets statistiques : l'architecture des réseaux de neurones, l'optimisation numérique à grande échelle, le génie logiciel des données, la théorie de la calculabilité (section 3.4). L'éthique et le droit des algorithmes sont abordés à partir des questions statistiques (S1.10, S17.06). **Question à JG** : faut-il aussi leur consacrer des vidéos ?

Le pilier 3 reste ouvert par construction : il s'enrichit en continu selon la méthode de la section 5.

