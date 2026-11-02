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
| **A11** | Faut-il un statut pédagogique éditorial, en plus du rôle dans le graphe ? | (a) Non : rôle dans le graphe et parcours suffisent · (b) Oui : un champ éditorial (par exemple « essentiel pour le parcours X »), attribué par l'éditorial, sans jamais dire « optionnel » | **(a)** pour l'instant, (b) si la revue éditoriale le juge utile. Ce choix appartient à ChatGPT, puis à JG. |

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


## 10.8 Audit des familles proposées par ChatGPT (contribution sur la version 1.4)

Pour chaque famille : ce qui existait, et ce que la version 1.6 ajoute (« + » : nouvelle vidéo ; « obj. » : objectifs complétés dans une vidéo existante). Une famille déjà couverte n'est pas doublée : une leçon enseigne une compétence identifiable.

**A. Statistiques**

| Famille | Couverture | Version 1.6 |
|---|---|---|
| A1 Données manquantes | S1.07 (intuition), S18.03 (MCAR, MAR, MNAR, imputation multiple) | obj. S18.03 : indicateurs de manquants, limites de l'imputation simple |
| A2 Erreurs de mesure, qualité | S1.07 en partie, E4.03 (atténuation) | + S1.12 fiabilité, validité, biais de mesure |
| A3 Plan d'expérience, essais | S1.06, S9.10, S9.13, E7.01 | + S9.14 aveugle, conformité, attrition, intention de traiter |
| A4 Puissance | S7.09, S8.03 | obj. S8.03 : effet minimal détectable ; + S8.12 tests d'équivalence (preuve d'absence, version 1.7) |
| A5 Tests multiples | S8.09 | obj. S8.09 : Holm, Benjamini-Hochberg, HARKing, exploration et confirmation |
| A6 Rééchantillonnage | S11.02 (bootstrap), S11.03 (permutation) | + S11.09 jackknife, BCa, bootstrap par blocs |
| A7 Statistique robuste | S2.09 (valeurs atypiques), S9.06 (points influents) | + S11.10 moyenne tronquée, MAD, M-estimateurs, régression robuste ; + S11.11 robustesse et analyse multivers (version 1.7) |
| A8 Survie | S15.01 à S15.04 | obj. S15.01 à S15.03 : censure à gauche, log-rank, vérification des risques proportionnels |
| A9 Valeurs extrêmes | S18.06 | obj. S18.06 : GEV, GPD, niveau de retour |
| A10 Données spatiales | S14.08 | obj. S14.08 : MAUP |
| A11 Longitudinal, modèles mixtes | S10.07, S12.05, E3.02, S9.14 (randomisation par grappes) | obj. S10.07 et E3.02 : pente aléatoire, ICC, niveau de groupement, modèle mixte ou erreurs groupées |
| A12 Non paramétrique | S11.04, S11.03 | obj. S11.04 : ce que teste vraiment Mann-Whitney, Kruskal-Wallis |
| A13 Fonctionnel, haute dimension | S17.03 (ridge, lasso) | + S13.09 données fonctionnelles, + S17.10 haute dimension et inférence après sélection ; obj. S17.03 : elastic net |
| A14 Enquêtes avancées | S6.04, S6.07, S6.08 | + S6.09 effet de plan, poids de réplication |
| A15 Données de composition | absente | + S13.10 |

**B. Économétrie**

| Famille | Couverture | Version 1.6 |
|---|---|---|
| B1 Expériences naturelles, encouragement | E7.02, E5.04 | obj. E5.04 et E7.02 : ITT et TOT, non-conformité |
| B2 Régression sur discontinuité | E7.05 | obj. E7.05 : bande passante, placebos, validité locale |
| B3 Contrôle synthétique | E7.06 | obj. E7.06 : pré-ajustement, placebos, contrôle synthétique généralisé |
| B4 Panel dynamique | E6.04 | obj. E6.04 : GMM système, prolifération des instruments, diagnostics |
| B5 Séries structurelles | S14.04, S14.05, S14.07 | obj. S14.04 : SARIMA ; ruptures en B14 |
| B6 Cointégration | E8.03 | obj. E8.03 : Engle-Granger, Johansen, VECM |
| B7 Prévision et évaluation | S14.05, E9.03 | + S14.09 fenêtres, fuite temporelle, métriques, calibration |
| B8 Économétrie spatiale | E6.05 | obj. E6.05 : SAR, SEM, SDM, effets directs et indirects |
| B9 Régression quantile | S9.12 | + E10.06 quantiles conditionnels et inconditionnels |
| B10 Choix discret, durée | E10.01, E10.04, S15 | + E10.07 logit emboîté et mixte, + E10.08 modèles de durée en économie |
| B11 Instruments avancés | E5.03 | obj. E5.03 : Anderson-Rubin, plusieurs instruments |
| B12 Inférence causale moderne | E7.08 | obj. E7.08 : échantillonnage croisé |
| B13 Équations simultanées | E4.02 (intuition) | + E5.06 identification, 2SLS et 3SLS |
| B14 Ruptures et régimes | E9.06 (régimes de volatilité) | + E8.08 Chow, Bai-Perron |

**C. Quotidien et actualité**

| Thème | Couverture | Version 1.6 |
|---|---|---|
| Démographie | Q4.04, Q4.06 | + module Q7 : Q7.03 fécondité, Q7.04 migrations |
| Travail et inégalités | Q4.02, Q4.03, Q4.07 | + Q4.08 écart de salaire brut ou ajusté, + Q4.09 mobilité sociale |
| Logement | absent | + module Q9 (2 vidéos) |
| Énergie et climat | Q2.05 | + module Q8 (3 vidéos) |
| Santé publique | Q2.01, Q2.03 | + Q7.01 incidence et prévalence, + Q7.02 taux standardisés |
| Éducation | absent | + module Q11 (2 vidéos) |
| Conflits | absent | + module Q13 (2 vidéos, protocole renforcé) |
| Commerce et mondialisation | absent | + Q10.03 |
| Dette et finances publiques | absent | + Q10.01, Q10.02 |
| Chaînes d'approvisionnement | absent | + Q10.04 (version 1.7) |
| Sécurité énergétique | absent | + Q8.04 (version 1.7) |
| Technologie et IA | Q5.01 à Q5.04 | + Q5.05 ce que mesure un score d'IA |
| Information et médias | Q4.05, S1.09 | + module Q12 : agrégation de sondages, causalité inversée |
| Agriculture et alimentation | absent | + module Q14 (2 vidéos) |
| Transport et ville | Q2.02 | + module Q15 (2 vidéos) |
| Sport | Q6.01 à Q6.03 | + Q6.04 expected goals, + Q6.05 force du calendrier |

Pour l'actualité, ces thèmes sont aussi des familles de questions à activer quand un événement et des sources primaires le justifient (section 5.2) ; ils ne figent aucun chiffre.

## 10.9 Audit de la version 1.5 par ChatGPT

L'audit de ChatGPT portait sur la version 1.5. La version 1.6 y répondait déjà en grande partie (table de la section 10.8). La version 1.7 complète ce qui restait.

| Demande | Position de Claude | Ce qui change |
|---|---|---|
| Table de correspondance avec l'inventaire précédent | **Fait** en version 1.6 (section 10.8). Toutes les correspondances renvoient à des vidéos réellement enseignées, avec leurs objectifs ; aucune ne repose sur une simple mention en bibliographie. L'entrée « S13.13 » citée n'existe pas : il s'agit de S9.13 (plans factoriels) et de S9.14 (essai randomisé). | Section 10.8 complétée. |
| Puissance, absence de preuve | **Accord** : la « preuve d'absence » est une compétence distincte. | + S8.12 tests d'équivalence (TOST). |
| Comparaisons multiples et FDR | **Déjà couvert** : S8.09 enseigne Bonferroni, Holm et Benjamini-Hochberg depuis la version 1.6. | Aucun. |
| Sensibilité et robustesse, multivers | **Accord**, c'était un manque. | + S11.11 analyse multivers. |
| Statistique robuste, données de composition | **Déjà ajoutées** en version 1.6 (S11.10, S13.10). | Aucun. |
| Méta-analyse approfondie | **Accord** : l'hétérogénéité manquait. | obj. S8.11 : Q de Cochran, I², limites du funnel plot. |
| Comptages avancés | **Accord** : S10.04 s'arrêtait à la surdispersion. | + S10.08 inflation de zéros et modèles à seuil. |
| Données groupées | **Déjà couvert** (E3.02, S10.07, S9.14). | obj. E3.02 : niveau de groupement, peu de groupes. |
| Thèmes du quotidien | **Déjà ajoutés** en version 1.6 (modules Q7 à Q15), sauf deux. | + Q8.04 sécurité énergétique, + Q10.04 chaînes d'approvisionnement ; le caractère ouvert du catalogue est écrit en section 5.1. |
| Description de la PR | **Accord**, elle décrivait encore la version 1. | Description mise à jour sur GitHub. |
| Nom de la taxonomie | **Accord** : la règle est mécanique et ne mesure pas l'importance. | Renommée « rôle dans le graphe » ; statut éditorial éventuel soumis à l'arbitrage A11. |

## 10.10 Audit de la version 1.7 par ChatGPT

Réponse contradictoire, point par point. « Accord » signifie que la remarque est justifiée et corrigée en version 1.8 ; « nuance » qu'elle est retenue sous une autre forme ; « à vérifier » qu'elle demande un test ou une source avant de trancher.

| Point | Position de Claude | Ce qui change en 1.8 |
|---|---|---|
| S8.12 TOST | **Accord.** Deux tests unilatéraux à 5 % équivalent à un intervalle bilatéral à **90 %** inclus dans la marge ; un IC à 95 % donne un test plus conservateur. | Exercice et correction énoncés avec des IC à 90 % ; distinction « non significatif » et « équivalence démontrée ». |
| S11.11 multivers | **Accord.** 9/64 n'est ni une p-value ni une probabilité ; les spécifications sont dépendantes. | Correction : justification de l'ensemble, taille et signe des effets, incertitude. |
| S8.11 méta-analyse | **Accord.** | Effet fixe et effets aléatoires distingués ; le funnel plot ne diagnostique pas seul un biais de publication. |
| S10.08 zéros | **Accord.** | Garde-fou : surdispersion, hétérogénéité, mauvaise spécification ; comparaison de modèles comme étape suivante. |
| S11.09 BCa, blocs | **Accord.** | Biais et accélération nommés ; longueur des blocs et limites du bootstrap par blocs. |
| E5.03 instruments faibles | **Accord**, avec une nuance de source : le seuil chiffré de Lee et coll. (2022) n'a pas été lu dans le texte intégral, il n'est donc pas cité. | Correction ajoutée ; F > 10 présenté comme règle approximative (Staiger et Stock, 1997), seuils de Stock et Yogo, Anderson-Rubin ; références avec DOI (section 9.5). |
| E5.04 LATE | **Accord.** | Pertinence, indépendance, exclusion, monotonie dans les objectifs, avec un exemple de violation (« defiers »). |
| E7.05 discontinuité | **Accord.** | Intuition conditionnée : pas de manipulation précise, continuité au seuil ; les diagnostics ne prouvent rien, ils révèlent certaines violations. |
| E7.06 contrôle synthétique | **Accord.** | Inférence avec un seul traité, choix du pool de donneurs, fragilité des placebos. |
| E6.04 panels dynamiques | **Accord.** | Prolifération des instruments (collapse, restriction des retards, Roodman, 2009) ; un test de Hansen non rejeté ne valide rien. |
| Q8.02 émissions cumulées | **Accord.** | Émissions nettes, puits, concentration distingués. |
| Q8.03 attribution | **Accord.** | Rapport de probabilités, intensité, probabilité absolue ; « dix fois plus probable » ne veut pas dire « causé seul ». |
| Durées et formats | **Nuance.** Le catalogue ne contient que **trois** SHORT autonomes (Q1.03, Q2.04, Q3.02), tous des capsules de paradoxe d'une seule idée. Les entrées de 0,75 à 1,5 min sont ces trois-là ; aucune leçon avec hypothèses et exercice n'est en format court. | Règle écrite en section 2.4 ; la durée du catalogue est un ordre de grandeur, réestimée dans la fiche après le déroulé (section 6.1, modèle YAML). |
| Une seule fiche conçue | **Accord.** | Section 7.3 : charge totale du catalogue calculée par le script, et rappel que le catalogue n'est pas un stock ; capacité bilingue mesurée au pilote. |
| Corrections et contrôles | **Nuance.** Les 112 contrôles (79 en 1.7) recalculent l'arithmétique ; ils ne vérifient pas que l'énoncé contient les données utilisées. Ce défaut existait : S2.10 utilisait des notes absentes de l'énoncé, corrigé. | Le script signale désormais tout exercice chiffré sans correction (8 restants, notés pour la fiche de conception). Les énoncés qualitatifs passent par le registre des affirmations (section 6.1). |
| Bibliographie | **Accord.** | Liste fermée des références non vérifiées en section 9.5 ; la bibliographie n'est plus présentée comme validée. |
| Fiche de provenance | **Accord.** | Neuf champs en section 5.3, bloc `provenance` du modèle YAML. |
| Pilier 3 : objectif, exemple, erreur | **À vérifier.** La présence des trois champs est contrôlée par le script pour les 59 entrées ; qu'une erreur soit propre au sujet ne se contrôle pas mécaniquement. | Vérification à faire dans chaque fiche de conception. |

**Lacunes que Claude voit dans l'audit.**

- L'édition anglaise n'a pas été relue : titres EN et adaptation des exemples restent à auditer.
- La vague 1 est passée de 47 à 49 vidéos depuis l'ajout de S1.12 ; l'impact sur le seuil de lancement n'a pas été discuté.
- Plusieurs nouveaux sujets du pilier 3 (conflits, santé publique, migration) relèvent des sujets sensibles de la constitution éditoriale : ils demandent le veto de JG avant toute fiche, ce que l'audit ne mentionne pas.
- Des liens « pour aller plus loin » du pilier 3 pointent vers des vidéos de niveau 4 ; c'est voulu (renvoi, pas prérequis), mais l'écart de niveau mérite un signal au spectateur.

