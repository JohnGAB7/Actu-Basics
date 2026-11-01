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

Les contenus pédagogiques avancent par séries courtes de 5 à 8 épisodes, chaque épisode s'appuyant sur le précédent. Exemples :
- « Les probabilités qui trompent l'intuition » : anniversaires, Monty Hall, faux positifs, loi des grands nombres, joueur et hasard.
- « Lire un chiffre sans se faire avoir » : moyenne ou médiane, pourcentage ou point de pourcentage, échelle d'un graphique, corrélation, échantillon.
- « Les statistiques en pratique » : l'actuaire et le prix d'une assurance, un test A/B, la régression, ce que fait un modèle de machine learning.

Proposition de rythme au lancement : 3 SHORT par semaine (dont au moins 1 d'actualité), 1 EDUCATIONAL tous les 15 jours, la première YOUTUBE_LESSON après les 4 premiers EDUCATIONAL. À décider par JG selon la capacité de relecture.

## 6. Vidéo de lancement

**Titre de travail** : « Et si les chiffres changeaient votre façon de voir le monde ? »
**Format** : EDUCATIONAL, environ 2 min 30, FR et EN. **Fiche** : `contenus/fiches/2026-11-lancement-actu-basics.yaml`.

**Idée** : prouver la valeur éducative par l'expérience, plutôt que l'annoncer. La vidéo piège d'abord l'intuition du spectateur avec le paradoxe des anniversaires. Elle explique ensuite, le fait participer, puis présente la mission et les quatre familles.

| Temps | Scène | Rôle |
|---|---|---|
| 0:00 | Accroche : le titre | Promesse |
| 0:07 | TEST : 23 personnes, même anniversaire ? (compte à rebours) | Participation immédiate |
| 0:20 | « Spontanément : environ 6 % » | L'intuition |
| 0:28 | « Plus d'une chance sur deux » → 50,7 % | Révélation, effet de surprise |
| 0:40 | Chapitre 1 : pourquoi notre intuition se trompe | Rythme, respiration |
| 0:44 | 253 paires (étapes) | Comprendre sans formule |
| 1:00 | Formule par l'événement contraire, ligne à ligne | Montrer la rigueur |
| 1:25 | Courbe calculée de 1 à 70 personnes | Visualiser |
| 1:40 | À VOUS : combien pour 90 % ? (compte à rebours) | Exercice |
| 1:50 | Correction : 41 personnes | Récompense |
| 2:05 | Applications : fraude, données, risque | Utilité réelle |
| 2:15 | Les quatre familles d'ACTU-BASICS | Mission |
| 2:30 | « Votre intuition vient de se tromper. C'est exactement comme ça qu'on apprend. » | Conclusion mémorable |
| 2:38 | Logo, slogan dit à voix haute, signature sonore | Marque |

Les temps sont indicatifs. Ils dépendent de la voix, et le rendu donne les durées réelles.

**Points à arbitrer** :
- Voix : la voix gratuite (Piper) suffit pour le prototype. Pour la vraie vidéo de lancement, une voix humaine enregistrée (`--voix manuel`) ou une voix de synthèse payante serait nettement plus captivante. C'est une décision de dépense, non engagée.
- Identité sonore : la signature (quatre notes ascendantes, « l'éveil ») et la nappe sont des prototypes synthétisés, sans droits. Une identité composée reste à valider.
- Phrase d'application (« repérer une fraude, sécuriser des données, évaluer un risque ») : formulation générale à relire par l'éditorial. Exemple établi : en cryptographie, l'« attaque des anniversaires » exploite exactement ce raisonnement.

## 7. Ce qui reste à faire avant la production en série

1. Valider cette architecture (JG), puis le script de la vidéo de lancement (ChatGPT pour la langue, JG pour le ton).
2. Choisir la voix de la vidéo de lancement.
3. Mise en page dédiée 16:9 pour YOUTUBE_LESSON (deux colonnes texte et visuel, chapitres) : le moteur sait déjà produire du 16:9, mais avec la mise en page verticale adaptée.
4. Modèle de fiche pédagogique pour l'éditorial : `modeles/fiche-pedagogique.yaml`.
5. Écrire les trois premières fiches de la série « Les probabilités qui trompent l'intuition », sans les produire en masse avant validation.
