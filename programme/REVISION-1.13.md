# Révision 1.13 du programme : des vidéos longues qui regroupent les notions

**Statut : proposition de Claude, à valider par JG. Relecture éditoriale des titres : ChatGPT.**
Demande de JG du 21/11/2026 : des vidéos longues, dont chacune aborde plusieurs concepts quand c'est cohérent, et plus de vidéos courtes qui définissent un seul concept. YouTube devient l'endroit où l'on se forme de façon complète. Les Shorts servent seulement à rediriger vers les vidéos complètes.

## Ce qui change

| | V1.12 | V1.13 |
|---|---|---|
| Unité publiée | 320 vidéos de 3 à 16 min, une notion chacune | **89 épisodes**, médiane 28 min (de 11 à 44 min), qui regroupent 2 à 7 notions |
| Rôle des 320 entrées | Une entrée = une vidéo | Une entrée = un **chapitre** d'un épisode (objectifs, intuition, exemple, exercice inchangés) |
| Format principal | `educational` vertical | `youtube_lesson` 16:9, avec des chapitres YouTube horodatés |
| Formats courts | SHORT dérivés, hors catalogue | Shorts et TikTok = **bandes-annonces** d'un épisode, qui renvoient vers lui. Plus de vidéo courte qui définit seule une notion |
| Lien avec la plateforme | Aucun | Correspondance interne avec un bloc Programme-B (champ `programme_b`) pour vérifier les sources ; aucun lien public, le site ACTU-BASICS se suffit à lui-même |

Le volume total ne change pas : environ 42 h. C'est une estimation haute, car un épisode n'a qu'une ouverture et qu'une fin, au lieu d'une par notion. Les durées seront recalculées après l'écriture des premiers scripts.

## Ce qui ne change pas

Les 320 entrées, leurs prérequis et leurs contrôles. Les 4 niveaux, les 3 piliers et la boîte à outils. La rigueur de la V1.12 : intuition d'abord, formule expliquée, exercice corrigé, chiffres recalculés par le moteur, double relecture. Et le bilinguisme FR et EN, publiés en même temps.

## Règles de regroupement

1. Un épisode regroupe des notions qui répondent à **une même question** (« pourquoi un échantillon peut mentir », « comment tester une hypothèse »).
2. Il reste dans un seul module de la V1.12, sauf exception justifiée (pilier Quotidien : Q9 rejoint l'argent, Q15 rejoint les risques et les pièges de l'intuition).
3. **Ordre pédagogique contrôlé** : dans le cursus, aucun chapitre ne demande une notion traitée plus loin (script `episodes.py`).
4. Durée cible de 20 à 45 min, bornes contrôlées entre 10 et 50 min. Au-delà, l'épisode est coupé en deux.
5. Chaque chapitre garde son exercice. L'épisode se termine par un exercice de synthèse qui mobilise plusieurs chapitres.
6. **Complétude** : chaque fiche de conception liste toutes les notions utilisées, et pour chacune l'épisode antérieur qui l'enseigne ou le rappel intégré. Sans l'un ni l'autre, pas de script (champ `notions_utilisees`).

## Structure d'un épisode

1. **Ouverture (15 à 30 s)** : la question concrète de l'épisode, montrée et non seulement dite, avec du mouvement dès la première image.
2. **Accueil (10 à 20 s)** : saluer, remercier le spectateur d'être là, dire ce qu'il saura faire à la fin.
3. **Plan à l'écran** : les chapitres, qui deviennent les chapitres YouTube.
4. **Chaque chapitre** suit l'arc de la V1.12 : intuition, exemple minuscule, raisonnement à l'écran, formule expliquée, exercice avec pause, correction.
5. **Synthèse** : comment les notions s'articulent, avec un schéma récapitulatif.
6. **Exercice de synthèse**, puis sa correction.
7. **Clôture (30 à 45 s)** : rappel en une phrase, puis orientation (épisode suivant, autres épisodes utiles, page de l'épisode sur le site) et invitations à s'abonner, liker et partager, et offre d'aide gratuite aux exercices de l'épisode (en commentaire sous la vidéo), une seule fois, sans formule qui culpabilise.
8. **Fin de marque (3 à 5 s)** : logo officiel et slogan de la langue de l'édition, sous l'écran de fin YouTube.

Le moteur bloque un épisode long sans accueil après l'ouverture ou sans clôture complète (`production/charte.yaml`, `parcours_spectateur`).

**Logo mobile.** Plus de nom de marque ni de logo fixe pendant la vidéo : le logo officiel glisse lentement dans le bandeau du haut, sans déformation ni recoloration, et peut être coupé au profit du filigrane YouTube Studio (`logo.mobile` dans la charte).

## Formats courts : bandes-annonces seulement

- Chaque épisode produit 1 à 3 Shorts de 30 à 60 s, extraits de son meilleur moment (un paradoxe, un résultat surprenant).
- Un Short ne commence jamais par un accueil et se termine toujours par l'épisode complet, cité par son titre : vidéo associée sur YouTube Shorts, « lien en bio » sur TikTok.
- Contrôles anti-blocage conservés pour toutes les plateformes : première image pleine, aucun plan figé plus de 2 s, aucune marque fixe à l'écran (logo mobile), étiquette « contenu généré par IA », pas de lien en légende, vocabulaire sensible cadré (voir le document de diagnostic TikTok du 21/11).

## Sources : ce qui est couvert et ce qui manque

Chaque épisode s'appuie sur le registre des sources de Programme-B (`docs/SOURCE-REGISTER.md`, version 1.0 du 21/11/2026), par l'intermédiaire de son champ `programme_b`. Une page de catalogue universitaire situe le niveau mais ne permet pas de vérifier un contenu : seuls les cours détaillés (notes, polycopiés, manuels ouverts) comptent comme sources de vérification.

| Bloc Programme-B | Épisodes concernés | Cours détaillés déjà au registre | État |
|---|---|---|---|
| B01, B03, B04, B05 | EP-M01 à EP-M05 | OpenStax (S18 à S21, S31, S32), MIT 18.06, 18.065, 18.01SC, 18.02SC, 18.03SC, 18.100B, Strang, Axler | Couvert |
| B08 Probabilités | EP-S4A à EP-S5D, une partie du Quotidien | Harvard Stat 110 (S03, S46), MIT 18.05 (S04, S48), MIT 6.041SC (S47) | Couvert |
| B09 Processus | EP-S16 | MIT 18.445, 6.262, 15.070J (S50 à S53) | Couvert |
| B10 Descriptif et sondage | EP-S1A à EP-S3C, EP-S6B | MIT 15.075J (S54), NIST e-Handbook (S55), Lohr (S56) | Couvert |
| B11 Inférence | EP-S6A, EP-S7A à EP-S8C, EP-S11A, EP-S12A, EP-S12B | MIT 18.05 seulement (niveau introductif) | Partiel : manque un cours de statistique mathématique et un cours bayésien |
| B12 Régression et modèles | EP-S9A à EP-S10B, EP-S11C | MIT 18.05 seulement | Partiel : manquent la régression multiple, les GLM et les modèles mixtes |
| B13 Multivarié | EP-S13A à EP-S13D | MIT 18.065 et 18.657 | Partiel : manquent l'analyse des correspondances, les copules et les données fonctionnelles |
| B14 Causalité et expériences | EP-S9D, EP-E7A, EP-E7B | Aucun | Lacune |
| B15 Apprentissage | EP-S17A à EP-S17D, EP-S19A à EP-S19C, EP-Q5 | MIT 18.657 (théorie seulement) | Partiel : manquent les arbres, le boosting et les réseaux de neurones |
| B16 Séries temporelles | EP-S14A à EP-S14C, EP-E8A, EP-E8B | Aucun | Lacune |
| B17 Reproductibilité | EP-S11B, EP-S19C | Documentation technique seulement | Lacune |
| B18 Actuariat et survie | EP-S15, pilier A | Aucun | Lacune |
| B19 Économétrie | EP-E1 à EP-E11D | Aucun | Lacune |
| B20 Théorie avancée | EP-S18A, EP-S18B | MIT 18.100B et 18.657 | Partiel |
| Quotidien (chiffres réels) | EP-Q1 à EP-Q13 | Sans objet : sources statistiques officielles (Insee, Eurostat, OMS, etc.), vérifiées et datées à la préparation, selon le protocole V1.12 | Par fiche |

Règle : aucun épisode marqué « lacune » ou « partiel » ne passe en fiche de conception avant que le registre contienne au moins un cours détaillé pour ses chapitres. JG fournit ou valide ces cours spécialisés.

## À décider ensuite

- Valider les 89 épisodes et leurs titres (les titres restent des titres de travail, relus par ChatGPT).
- L'ordre de publication. Proposition : alterner un épisode du cursus et un épisode du Quotidien.
- Les 10 fiches du lot 5 déjà produites deviennent des extraits ou des Shorts des épisodes correspondants (EP-S2A, EP-S3B, EP-Q2, EP-Q3). Le pilier A (Actuariat) garde son parcours propre, hors de ces 89 épisodes, et suivra les mêmes règles.
- Le PDF V1.13 est reconstruit (`PROGRAMME_EDITORIAL_ACTU-BASICS_v1-13.pdf`) : synthèse, sections 2.4, 2.5, 2.9, 7 et 10.14 réécrites, épisode affiché sur chaque chapitre.

## Les 89 épisodes

Tableau produit par `python programme/episodes.py`. Durées : somme des fourchettes des chapitres de la V1.12.

### Boîte à outils maths

| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |
|---|---|---|---|---|
| EP-M01 | Calculer de tête : fractions, puissances de 10, graphiques et Σ | M0.01, M0.02, M0.03, M1.01 | 12–20 min | B01 |
| EP-M02 | L'algèbre qui sert vraiment : droites, puissances, exponentielle et logarithme | M1.02, M1.03, M1.04, M1.05 | 18–26 min | B01 |
| EP-M03 | Dérivées et intégrales, sans peur | M2.01, M2.02, M2.03 | 18–24 min | B04, B05 |
| EP-M04 | Les matrices, ou comment ranger des données | M3.01, M3.02, M3.03 | 20–26 min | B03 |
| EP-M05 | Convergence et hasard formalisé | M4.01, M4.02 | 16–20 min | B04, B08 |

### Niveau 1 · Découverte

| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |
|---|---|---|---|---|
| EP-S1A | D'où vient un chiffre ? Données, populations et variables | S1.01, S1.02, S1.03, S1.04 | 17–25 min | B10-T01 |
| EP-S1B | Pourquoi un échantillon peut mentir | S1.05, S1.06, S1.07, S1.12 | 21–31 min | B10-T02, B10-T03 |
| EP-S1C | Pourcentages, graphiques et hasard : lire un chiffre sans se faire avoir | S1.08, S1.09, S1.10, S1.11 | 17–25 min | B10-T07 |
| EP-S2A | Résumer des données : tableaux, histogrammes, moyenne et médiane | S2.01, S2.02, S2.03, S2.04, S2.05 | 20–30 min | B10-T05, B10-T07 |
| EP-S2B | Mesurer les écarts : quartiles, variance, écart-type et score z | S2.06, S2.07, S2.08, S2.09, S2.10 | 23–32 min | B10-T06 |
| EP-S3A | Comparer sans se tromper : groupes, tableaux croisés, Simpson et évolutions | S3.01, S3.02, S3.03, S3.08 | 20–27 min | B10-T08 |
| EP-S3B | Deux variables liées : nuage de points, corrélation, causalité et droite | S3.04, S3.05, S3.06, S3.07 | 20–28 min | B10-T08 |
| EP-S3C | Explorer un jeu de données de A à Z | S3.09 | 12–20 min | B10-T10 |

### Niveau 2 · Fondamentaux

| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |
|---|---|---|---|---|
| EP-S4A | Le hasard se calcule : probabilités, simulation et dénombrement | S4.01, S4.02, S4.03, S4.04 | 20–28 min | B08-P01 |
| EP-S4B | Combiner des événements : du paradoxe des anniversaires au sophisme du joueur | S4.05, S4.06, S4.07, S4.08 | 24–30 min | B08-P01, B08-P02, B08-P03 |
| EP-S4C | Changer d'avis avec les chiffres : arbres, Bayes et Monty Hall | S4.09, S4.10, S4.11 | 18–24 min | B08-P02 |
| EP-S5A | Variables aléatoires : espérance, variance et loi binomiale | S5.01, S5.02, S5.03, S5.04 | 22–29 min | B08-P04 |
| EP-S5B | Attendre et compter : lois géométrique, de Poisson et exponentielle | S5.05, S5.06, S5.07, S5.08 | 23–29 min | B08-P04, B08-P05 |
| EP-S5C | La loi normale et ses cousines | S5.09, S5.10, S5.11, S5.14 | 26–34 min | B08-P05, B08-P06, B08-P07 |
| EP-S5D | Pourquoi les moyennes se stabilisent : grands nombres et théorème central limite | S5.12, S5.13, S5.15 | 21–27 min | B08-P08, B08-P10 |

### Niveau 3 · Inférence et modèles

| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |
|---|---|---|---|---|
| EP-S6A | De l'échantillon à la population : erreur standard et lois d'échantillonnage | S6.01, S6.02, S6.03, S6.06 | 22–29 min | B11 |
| EP-S6B | Faire un bon sondage : plans, marge d'erreur, non-réponse et calage | S6.04, S6.05, S6.07, S6.08, S6.09 | 34–44 min | B10-T03, B10-T04 |
| EP-S7A | Bien estimer : biais, variance et maximum de vraisemblance | S7.01, S7.02, S7.03, S7.04, S7.05 | 34–45 min | B11 |
| EP-S7B | Intervalles de confiance et taille d'échantillon | S7.06, S7.07, S7.08, S7.09 | 23–31 min | B11 |
| EP-S8A | La logique d'un test : p-value, erreurs et puissance | S8.01, S8.02, S8.03, S8.08 | 25–32 min | B11 |
| EP-S8B | Les tests de tous les jours : t, données appariées, khi-deux et taille d'effet | S8.04, S8.05, S8.06, S8.07 | 25–33 min | B11 |
| EP-S8C | Quand les tests trompent : p-hacking, adéquation, méta-analyse et équivalence | S8.09, S8.10, S8.11, S8.12 | 30–38 min | B11 |
| EP-S9A | La régression linéaire simple, de la droite à l'inférence | S9.01, S9.02, S9.03 | 23–31 min | B12 |
| EP-S9B | Régression multiple : toutes choses égales par ailleurs | S9.04, S9.05, S9.08 | 23–31 min | B12 |
| EP-S9C | Un modèle fiable : diagnostics, transformations, choix et régression quantile | S9.06, S9.07, S9.11, S9.12 | 31–39 min | B12 |
| EP-S9D | ANOVA et plans d'expérience, jusqu'à l'essai randomisé | S9.09, S9.10, S9.13, S9.14 | 36–44 min | B12, B14 |
| EP-S10A | Prédire un oui ou un non, et compter : logistique et Poisson | S10.01, S10.02, S10.03, S10.04 | 27–34 min | B12 |
| EP-S10B | Le cadre GLM : Gamma, Tweedie, modèles mixtes et excès de zéros | S10.05, S10.06, S10.07, S10.08 | 36–44 min | B12 |
| EP-S11A | Calculer en simulant : Monte-Carlo, bootstrap et permutations | S11.01, S11.02, S11.03, S11.09 | 29–37 min | B11 |
| EP-S11B | Valider et reproduire : validation croisée et bonnes pratiques | S11.05, S11.06 | 12–16 min | B17 |
| EP-S11C | Sans hypothèses fortes : rangs, robustesse, lissage et multivers | S11.04, S11.10, S11.08, S11.07, S11.11 | 37–47 min | B11, B12 |

### Niveau 4 · Branches avancées

| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |
|---|---|---|---|---|
| EP-S16 | Processus aléatoires : marche aléatoire, Markov, Poisson et brownien | S16.01, S16.02, S16.03, S16.04 | 33–41 min | B09 |
| EP-S12A | Penser en bayésien : a priori, bêta-binomial et crédibilité | S12.01, S12.02, S12.03 | 23–29 min | B11 |
| EP-S12B | Bayésien en pratique : MCMC, modèles hiérarchiques et comparaison honnête | S12.04, S12.05, S12.06 | 28–38 min | B11 |
| EP-S13A | Voir en p dimensions : nuage multivarié, loi normale multivariée et ACP | S13.01, S13.07, S13.02 | 26–34 min | B13 |
| EP-S13B | Variables cachées et proportions : AFC, ACM, analyse factorielle et compositions | S13.03, S13.06, S13.10 | 25–33 min | B13 |
| EP-S13C | Classer : k-moyennes, classification hiérarchique et discriminante | S13.04, S13.05 | 20–24 min | B13 |
| EP-S13D | Dépendances et courbes : copules et données fonctionnelles | S13.08, S13.09 | 18–22 min | B13 |
| EP-S14A | Lire une série temporelle : tendance, saisonnalité, autocorrélation et lissage | S14.01, S14.02, S14.03 | 21–27 min | B16 |
| EP-S14B | Prévoir : ARIMA, incertitude et évaluation honnête | S14.04, S14.05, S14.09 | 27–35 min | B16 |
| EP-S14C | Cycles, états cachés et espace : spectre, Kalman et krigeage | S14.06, S14.07, S14.08 | 26–32 min | B16 |
| EP-S15 | L'analyse de survie : censure, Kaplan-Meier et modèle de Cox | S15.01, S15.02, S15.03, S15.04 | 32–42 min | B18 |
| EP-S17A | Expliquer ou prédire : biais-variance et évaluation d'un classifieur | S17.01, S17.02, S17.05 | 21–27 min | B15 |
| EP-S17B | Beaucoup de variables : ridge, lasso et haute dimension | S17.03, S17.10 | 20–24 min | B15 |
| EP-S17C | Arbres, forêts et boosting | S17.04, S17.07 | 18–22 min | B15 |
| EP-S17D | Réseaux de neurones, prédiction conforme et frontières de la statistique | S17.06, S17.08, S17.09 | 27–35 min | B15 |
| EP-S18A | Les grands outils de la théorie : Fisher, Cramér-Rao, méthode delta et trois tests | S18.01, S18.02, S18.04 | 30–38 min | B20 |
| EP-S18B | Données cachées et événements extrêmes : imputation multiple, EM et valeurs extrêmes | S18.03, S18.05, S18.06 | 28–34 min | B20 |
| EP-S19A | Comment apprend un réseau profond : couches, convolutions et gradient | S19.01, S19.02, S19.04 | 26–34 min | B15 |
| EP-S19B | Modèles de langue et modèles génératifs | S19.03, S19.05 | 18–24 min | B15 |
| EP-S19C | Des modèles dans le monde réel : production, complexité, droit et éthique | S19.06, S19.07, S19.08 | 25–31 min | B15, B17 |

### Pilier 2 · Économétrie

| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |
|---|---|---|---|---|
| EP-E1 | Données économiques et questions causales | E1.01, E1.02, E1.03, E1.04, E1.05 | 31–41 min | B19 |
| EP-E2 | Les moindres carrés en économie : du modèle à Frisch-Waugh-Lovell | E2.01, E2.02, E2.03, E2.04 | 28–36 min | B19 |
| EP-E3 | Tester et diagnostiquer une régression : F, erreurs robustes et mauvais contrôles | E3.01, E3.02, E3.03, E3.04 | 30–38 min | B19 |
| EP-E4A | Quand la régression ment : variable omise, simultanéité et erreur de mesure | E4.01, E4.02, E4.03 | 22–28 min | B19 |
| EP-E4B | Sélection, facteurs cachés et bornes | E4.04, E4.05, E4.06 | 22–28 min | B19 |
| EP-E5A | Les variables instrumentales : idée, doubles moindres carrés et instruments faibles | E5.01, E5.02, E5.03 | 23–29 min | B19 |
| EP-E5B | Au-delà des doubles moindres carrés : effet local, GMM et systèmes | E5.04, E5.05, E5.06 | 28–34 min | B19 |
| EP-E6 | Les données de panel : effets fixes, aléatoires, dynamiques et spatiaux | E6.01, E6.02, E6.03, E6.04, E6.05 | 39–49 min | B19 |
| EP-E7A | Évaluer une politique : expériences, expériences naturelles et différences de différences | E7.01, E7.02, E7.03, E7.04 | 33–43 min | B14, B19 |
| EP-E7B | Discontinuités, contrôle synthétique, appariement et effets hétérogènes | E7.05, E7.06, E7.07, E7.08 | 36–44 min | B14, B19 |
| EP-E8A | Séries économiques : erreurs HAC, racines unitaires, cointégration et ruptures | E8.01, E8.02, E8.03, E8.08 | 33–41 min | B16, B19 |
| EP-E8B | Réponses dans le temps : VAR, Granger, projections locales et effet d'un événement | E8.04, E8.05, E8.06, E8.07 | 33–43 min | B16, B19 |
| EP-E9A | La volatilité qui change : de l'ARCH au GARCH, avec un cas complet | E9.01, E9.02, E9.03 | 29–37 min | B19 |
| EP-E9B | Crises et risque : asymétries, VaR, Expected Shortfall et changements de régime | E9.04, E9.05, E9.06 | 24–30 min | B19 |
| EP-E9C | Volatilité avancée : stochastique, multivariée, réalisée et mémoire longue | E9.07, E9.08, E9.09, E9.10 | 36–44 min | B19 |
| EP-E10A | Choix et comptages : probit, logit, comptage et choix discrets | E10.01, E10.03, E10.04, E10.07 | 30–38 min | B19 |
| EP-E10B | Sélection, demande, distributions et durées | E10.02, E10.05, E10.06, E10.08 | 36–44 min | B19 |
| EP-E11A | Étude de cas : que rapporte une année d'études ? | E11.01 | 12–16 min | B19 |
| EP-E11B | Étude de cas : le salaire minimum et l'emploi | E11.02 | 12–16 min | B19 |
| EP-E11C | Étude de cas : l'élasticité-prix de la demande d'énergie | E11.03 | 10–12 min | B19 |
| EP-E11D | Étude de cas : banques centrales, taux d'intérêt et inflation | E11.04 | 12–16 min | B19 |

### Pilier 3 · Quotidien

| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |
|---|---|---|---|---|
| EP-Q1 | L'argent en chiffres : inflation, intérêts, crédit, soldes, loto et logement | Q1.01, Q1.02, Q1.03, Q1.04, Q1.05, Q9.01, Q9.02 | 32–44 min | B10, B08 |
| EP-Q2 | Comparer des risques : relatif ou absolu, avion ou voiture, tests et vélo | Q2.01, Q2.02, Q2.03, Q2.04, Q2.05, Q2.06, Q15.01 | 29–42 min | B08, B10 |
| EP-Q3 | Les pièges de l'intuition : bus, amis, coïncidences, main chaude et bouchons | Q3.01, Q3.02, Q3.03, Q3.04, Q3.05, Q15.02 | 29–40 min | B08 |
| EP-Q4A | Mesurer l'économie : PIB, chômage, inégalités et pauvreté | Q4.01, Q4.02, Q4.03, Q4.07 | 25–33 min | B10 |
| EP-Q4B | Mesurer la société : espérance de vie, population, écart de salaire et mobilité | Q4.04, Q4.06, Q4.08, Q4.09 | 22–30 min | B10 |
| EP-Q5 | Les algorithmes en chiffres : tests A/B, recommandations et scores des IA | Q5.01, Q5.02, Q5.03, Q5.04, Q5.05 | 29–39 min | B15 |
| EP-Q6 | Le sport en chiffres : penalties, classements, collections et expected goals | Q6.01, Q6.02, Q6.03, Q6.04, Q6.05 | 26–36 min | B08, B10 |
| EP-Q7 | Démographie : incidence, taux standardisés, fécondité et migrations | Q7.01, Q7.02, Q7.03, Q7.04 | 23–31 min | B10 |
| EP-Q8 | Énergie et climat : puissance, émissions, canicules et dépendance | Q8.01, Q8.02, Q8.03, Q8.04 | 23–31 min | B10 |
| EP-Q10 | Dette, déficit et commerce : stocks, flux et effet boule de neige | Q10.01, Q10.02, Q10.03, Q10.04 | 24–32 min | B10 |
| EP-Q11 | Classements, sondages et titres de presse : lire les chiffres des médias | Q4.05, Q11.01, Q11.02, Q12.01, Q12.02 | 29–39 min | B10, B11 |
| EP-Q13 | Compter dans les crises : victimes, réfugiés, faim et prix alimentaires | Q13.01, Q13.02, Q14.01, Q14.02 | 24–32 min | B10 |
