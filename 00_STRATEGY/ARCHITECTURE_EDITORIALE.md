# Architecture éditoriale ACTU-BASICS — proposition

> Proposition de la direction technique (Claude), novembre 2026, à valider par JG et à enrichir par l'éditorial (ChatGPT). Elle ne remplace ni `BRAND_IDENTITY.md` ni `EDITORIAL_CONSTITUTION.md`. Elle organise les contenus pour que le moteur de production et les contrôles qualité suivent.

## 1. Deux missions, un même média

ACTU-BASICS **informe** par les chiffres et **enseigne** les statistiques et les probabilités. Les deux missions se renforcent :
- l'actualité donne envie d'apprendre (« d'où vient ce chiffre ? ») ;
- l'enseignement donne les outils pour lire l'actualité (« que veut dire ce pourcentage ? »).

Promesse commune : *partir d'un chiffre ou d'une question, et repartir avec une compréhension.*

## 2. Quatre familles de contenus

| Famille | Clé dans la fiche | Question de départ | Exemples | Type de fiche |
|---|---|---|---|---|
| 1. Comprendre le monde par les chiffres | `comprendre_le_monde` | « Que dit ce chiffre de l'actualité ? » | Pic de population mondiale, inflation, records climatiques | `actualite` |
| 2. Apprendre les statistiques | `apprendre_les_statistiques` | « Comment résumer et lire des données ? » | Moyenne ou médiane, écart-type, corrélation n'est pas causalité, sondages et marge d'erreur | `pedagogique` |
| 3. Comprendre les probabilités | `comprendre_les_probabilites` | « Pourquoi notre intuition se trompe-t-elle ? » | Paradoxe des anniversaires, loi des grands nombres, faux positifs (Bayes), Monty Hall | `pedagogique` |
| 4. Les statistiques en pratique | `statistiques_en_pratique` | « À quoi ça sert dans un métier ? » | Data science, machine learning, actuariat, économie, assurance, tests A/B | `pedagogique` (ou `actualite` si l'angle est un fait daté) |
| Présentation de la marque | `presentation` | « Qui sommes-nous ? » | Vidéo de lancement, bandes-annonces de séries | `pedagogique` |

Passerelles : chaque contenu d'actualité peut renvoyer vers une notion (« pour comprendre ce chiffre, voir la capsule sur la médiane »). Chaque leçon peut s'appuyer sur un fait réel sourcé.

## 3. Trois formats

| Format | Clé `format` | Image | Durée visée | Usage | Carrousel |
|---|---|---|---|---|---|
| **SHORT** | `short` | vertical 1080 × 1920 | 15–90 s | TikTok, Reels, Shorts : un chiffre ou une idée | oui |
| **EDUCATIONAL** | `educational` | vertical 1080 × 1920 | 1 min 30–10 min | une notion expliquée pas à pas, avec exercice | non |
| **YOUTUBE_LESSON** | `youtube_lesson` | horizontal 1920 × 1080 | 5–60 min | cours approfondi, chapitres, exercices corrigés | non |

Un même sujet peut se décliner dans les trois formats : le SHORT pose la question, l'EDUCATIONAL l'explique, la YOUTUBE_LESSON la généralise.

## 4. Deux types de fiches

### Fiche d'actualité (`type_fiche: actualite`, défaut)
Structure inchangée : accroche → chiffre clé → graphique → contexte → source → fin.
**Vérité = la source.** Contrôles : source datée et en ligne, chiffre clé cohérent avec le graphique, unités et périodes cohérentes, FR et EN identiques sur les nombres. Vérification factuelle humaine obligatoire.

### Fiche pédagogique (`type_fiche: pedagogique`)
Structure recommandée (arc pédagogique) :

1. **Accroche ou question** : un paradoxe, une erreur fréquente, une situation concrète.
2. **Intuition** : ce que l'on croit spontanément.
3. **Révélation** : la bonne réponse, avec le chiffre.
4. **Explication** pas à pas : étapes, formule, graphique ou courbe.
5. **Exercice** : une question, un temps de réflexion.
6. **Correction** : la démarche, puis la réponse.
7. **Application** : à quoi cela sert dans le monde réel.
8. **Conclusion mémorable**, puis fin (abonnement, logo, signature sonore).

**Vérité = le calcul et le raisonnement.** Contrôles :
- objectifs pédagogiques en FR et en EN, niveau, prérequis ;
- chaque nombre annoncé est **recalculé par la machine** (bloc `verifier`) : un écart bloque ;
- chaque exercice a sa correction : un manque bloque ;
- les formules sont rendues sans erreur, et chaque formule a une voix off ;
- la durée respecte le format ;
- relecture humaine de l'exactitude des définitions et des notations ;
- si un fait extérieur est cité (étude, statistique publiée), une source est exigée comme pour l'actualité.

Niveaux : `decouverte` (grand public), `lycee`, `licence`, `master`, `professionnel`.

## 5. Séries et progression

> Section mise à jour après la validation par JG du programme éditorial et pédagogique (ticket n° 10, `programme/PROGRAMME_EDITORIAL_ACTU-BASICS_v1-11.pdf`, arbitrages A1 à A11 du 2/11/2026). Elle remplace la proposition de rythme de la version précédente.

**Le programme fait référence.** La progression pédagogique est celle du programme : trois piliers (statistiques de A à Z, économétrie, phénomènes du quotidien et actualité), quatre niveaux, 320 entrées de syllabus reliées par leurs prérequis. Les piliers s'ajoutent **au-dessus** des quatre familles de la section 2, qui restent un champ technique des fiches ; le moteur n'est pas modifié (arbitrage A1).

**Pas de publication avant un stock suffisant** (ticket n° 10, arbitrage A4). La publication commence quand la vague 1 du programme (49 épisodes, « Lire un chiffre sans se faire avoir ») est terminée **et** qu'au moins 12 semaines de publication sont en stock, en épisodes maîtres entièrement validés en FR et en EN. Ce seuil sera recalculé après la phase pilote, quand le temps humain par épisode sera mesuré. Le rythme de publication sera fixé à ce moment, selon la capacité de relecture de JG.

**Les séries deviennent des vagues.** Les séries de 5 à 8 épisodes de la version précédente sont reprises dans les vagues du programme :
- « Lire un chiffre sans se faire avoir » est la vague 1 ;
- « Les probabilités qui trompent l'intuition » est couverte par les modules S4 et S5 et le pilier 3 (Q1 à Q3) ;
- « Les statistiques en pratique » est couverte par les branches de niveau 4 (S10, S15, S17, S19) et le pilier 2.

**Autres décisions qui s'appliquent ici** :
- la répartition thématique de la constitution éditoriale (démographie 20 %, etc.) vaut pour les vidéos d'actualité, pas pour le cursus (A3) ;
- les vidéos d'actualité sont produites dans les semaines qui précèdent le lancement, pour ne pas être périmées (A6) ;
- les leçons de plus de 10 minutes passent en YOUTUBE_LESSON 16:9, après un essai sur une vraie leçon (A7) ;
- pas de code à l'écran, scripts fournis en description (A9) ;
- la vidéo de lancement compte comme l'épisode S4.06 du programme (A10).

## 6. Vidéo de lancement

**Titre de travail** : « Et si les chiffres changeaient votre façon de voir le monde ? »
**Format** : EDUCATIONAL, version 3 (refonte demandée par JG) : **8 min 01 en FR, 7 min 38 en EN** avec la voix Kokoro. La durée n'est pas une contrainte : elle découle de la profondeur pédagogique (constitution éditoriale, section 10). **Fiche** : `contenus/fiches/2026-11-lancement-actu-basics.yaml`. **Storyboard scène par scène** (durées réelles, narration FR et EN, texte à l'écran, animation, intention) : [STORYBOARD_LANCEMENT.md](STORYBOARD_LANCEMENT.md). **Contrôle qualité** (vérification mathématique et pédagogique) : [QC_LANCEMENT.md](QC_LANCEMENT.md).

**Idée** : la vidéo n'annonce pas la réponse, elle la construit. Le spectateur estime d'abord, puis refait le raisonnement avec nous, s'entraîne deux fois et repart avec une méthode. Principe de réalisation : la voix raconte, l'image démontre.

| Chapitre | Contenu | Objectif pédagogique |
|---|---|---|
| A · Le défi | 23 silhouettes, estimation, hypothèses (365 jours, 29 février ignoré) | Faire estimer avant d'expliquer |
| B · Compter les paires | A, B, C, D, une paire à la fois (3 + 2 + 1 = 6) ; A–B = B–A, d'où la division par 2 | Compter les paires |
| C · De 4 à 23 | 22 + 21 + … + 1 = 253, puis n(n − 1)/2 ; exercice à 10 personnes ; les paires ne sont pas indépendantes | Généraliser, éviter « 253/365 » |
| D · Tous différents | 365/365 × 364/365 × … ≈ 0,493, puis le complément : 50,7 % | Produit conditionnel et complément |
| E · L'intuition | vos 22 paires (≈ 6 %) contre les 253 paires du groupe | Pourquoi l'intuition se trompe |
| F · La courbe | repères 23 / 40 / 41 / 50, exercice : seuil de 90 % atteint à 41 | Comprendre plutôt que mémoriser |
| G · Le monde réel | collisions d'empreintes numériques (exemple prudent), les quatre piliers, conclusion | Utilité, mission de la marque |

Conclusion : « Un chiffre ne raconte pas toujours toute l'histoire. Apprendre à le comprendre change notre façon de voir le monde. ACTU-BASICS — Éveiller par les chiffres. »

**Points à arbitrer par JG** :
- Voix : Kokoro (gratuit, local) est la voix prioritaire, Piper le secours. À valider à l'écoute ; licences et attribution SIWIS dans `docs/voice-licenses.md`.
- Prononciation française de « ACTU-BASICS » par Kokoro (« aktybazik ») : à confirmer ou à corriger dans le lexique de `production/tts.yaml`.
- Identité sonore : signature et nappe synthétisées, prototypes sans droits.

## 7. Ce qui reste à faire avant la production en série

1. Valider cette architecture (JG), puis le script de la vidéo de lancement (ChatGPT pour la langue, JG pour le ton).
2. Choisir la voix de la vidéo de lancement.
3. Mise en page dédiée 16:9 pour YOUTUBE_LESSON (deux colonnes texte et visuel, chapitres) : le moteur sait déjà produire du 16:9, mais avec la mise en page verticale adaptée.
4. Modèle de fiche pédagogique pour l'éditorial : `modeles/fiche-pedagogique.yaml`.
5. Écrire les trois premières fiches de la série « Les probabilités qui trompent l'intuition », sans les produire en masse avant validation.
