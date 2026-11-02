# 2. Architecture éditoriale globale {#architecture}

## 2.1 Une promesse, trois piliers

La promesse reste celle de la marque : **« Éveiller par les chiffres. » / “Enlightening through numbers.”** Partir d'un chiffre ou d'une question, et repartir avec une compréhension que l'on peut réutiliser.

Les trois piliers ne sont pas trois chaînes séparées. Ils se répondent :

- le **pilier 3** (quotidien et actualité) attire et donne envie : « d'où vient ce chiffre ? » ;
- le **pilier 1** (statistiques) donne les outils pour répondre ;
- le **pilier 2** (économétrie) pousse ces outils jusqu'à la question la plus difficile : mesurer un effet causal avec des données qui ne viennent pas d'une expérience.

Chaque vidéo du pilier 3 renvoie vers la leçon qui explique sa notion (« pour aller plus loin »). Chaque leçon des piliers 1 et 2 peut s'appuyer sur un fait réel sourcé. Les fiches gardent ces liens : la fiche d'une leçon liste les vidéos du quotidien qui l'illustrent.

## 2.2 Correspondance avec l'architecture existante

Le moteur de production et `00_STRATEGY/ARCHITECTURE_EDITORIALE.md` utilisent quatre **familles** (champ `famille` des fiches). Ce programme ne les remplace pas. Il les range sous les trois piliers, sans modifier le moteur :

| Pilier du programme | Famille dans la fiche (moteur) | Type de fiche |
|---|---|---|
| 1 · Statistiques, modules S1 à S3, S6 à S18 | `apprendre_les_statistiques` | `pedagogique` |
| 1 · Statistiques, modules S4 et S5 (probabilités) | `comprendre_les_probabilites` | `pedagogique` |
| 1 · Branches appliquées (S10.06, S17) | `statistiques_en_pratique` | `pedagogique` |
| 2 · Économétrie | `statistiques_en_pratique` *(arbitrage A1 : piliers au-dessus des familles, moteur inchangé)* | `pedagogique` |
| 3 · Quotidien (intemporel) | `statistiques_en_pratique` ou `comprendre_le_monde` selon l'angle | `pedagogique` |
| 3 · Actualité | `comprendre_le_monde` | `actualite` |
| Boîte à outils maths | `apprendre_les_statistiques` | `pedagogique` |

**Deux points touchaient des décisions déjà écrites.** JG les a tranchés (arbitrages A2 et A3, section 10) :

- la section 5 d'`ARCHITECTURE_EDITORIALE.md` proposait un rythme de publication dès le lancement (3 SHORT par semaine, etc.). Le ticket n° 10 décide au contraire de **ne rien publier avant d'avoir un stock suffisant**. Ce programme suit le ticket, plus récent et validé par JG. Le document existant sera mis à jour dans une PR distincte, après la validation de ce programme ;
- la répartition par thèmes de la constitution éditoriale (démographie 20 %, économie 20 %, etc.) est appliquée ici **aux seules vidéos d'actualité**, et non au cursus.

## 2.3 Quatre niveaux, avec des branches

{{TABLEAU_NIVEAUX}}

Les niveaux 1 à 3 forment un **tronc commun** linéaire : un spectateur peut les suivre dans l'ordre sans jamais rencontrer une notion qui n'a pas été expliquée. Le niveau 4 est un ensemble de **branches**, chacune avec ses propres prérequis. Il n'existe pas de parcours unique qui serait le prérequis de toutes les spécialités. Par exemple, on peut suivre les séries temporelles (S14) sans l'analyse multivariée (S13).

Pour chaque module, on vise trois seuils de maîtrise, comme le propose la revue de ChatGPT :

- **comprendre** : réexpliquer l'idée avec ses mots ;
- **appliquer** : refaire le calcul sur un nouvel exemple ;
- **critiquer** : dire quand la méthode ne s'applique pas et ce qui pourrait fausser la conclusion.

Les objectifs de chaque vidéo sont écrits avec des verbes observables (calculer, distinguer, interpréter, repérer, expliquer pourquoi) pour que l'exercice final puisse les vérifier.

## 2.4 Trois formats, choisis selon le besoin pédagogique

| Format (clé moteur) | Image | Durée | Rôle dans le programme |
|---|---|---|---|
| **SHORT** (`short`) | vertical 1080 × 1920 | 15–90 s | Accroche, paradoxe ou rappel d'une seule idée. Chaque leçon peut en produire un ou deux, qui renvoient vers elle. |
| **EDUCATIONAL** (`educational`) | vertical 1080 × 1920 | 1 min 30–10 min | **Le format principal** du cursus : une notion expliquée pas à pas, avec exercice. |
| **YOUTUBE_LESSON** (`youtube_lesson`) | horizontal 1920 × 1080 | 5–60 min | Démonstrations longues, études de cas, sujets qui demandent de la place à l'écran (régression multiple, ACP, MCMC). |

La durée de chaque vidéo découle de ce qu'il faut pour atteindre l'objectif, jamais d'un plafond arbitraire (constitution éditoriale, section 10). Les durées indiquées sont des **estimations de conception** : elles seront corrigées après l'écriture du script. Trois entrées du catalogue sont des SHORT autonomes (Q1.03, Q2.04, Q3.02) : ce sont des capsules de paradoxe d'une seule idée, sans exercice, qui renvoient vers la leçon qui les explique. Toutes les autres sont des leçons EDUCATIONAL ou YOUTUBE_LESSON, dont les SHORT dérivés ne figurent pas au catalogue.

## 2.5 La structure d'un épisode

Toutes les vidéos pédagogiques suivent le même arc, déjà mis en œuvre dans le moteur et dans la vidéo de lancement :

1. **Question** concrète, paradoxe ou situation familière ;
2. **Intuition** : ce que l'on croit spontanément, avec une estimation demandée au spectateur ;
3. **Données ou exemple minuscule**, que l'on peut suivre de tête ;
4. **Raisonnement pas à pas**, montré à l'écran (« la voix raconte, l'image démontre ») ;
5. **Formalisation** : la formule arrive après l'idée, et chaque symbole est expliqué ;
6. **Exercice** avec un temps de réflexion, puis **correction** détaillée ;
7. **Application** réelle et **limites** de la méthode ;
8. **Rappel** mémorable, puis fin de marque (logo, signature).

## 2.6 Principes non négociables, traduits en règles de production

| Principe (ticket n° 10) | Règle appliquée dans le programme |
|---|---|
| La compréhension prime sur la durée | Durée estimée par vidéo selon le contenu ; un sujet trop long est découpé en deux vidéos, pas comprimé. |
| Intuition d'abord, formalisation ensuite | Champ « Intuition d'abord » obligatoire dans chaque fiche. |
| Expliquer les formules | Toute formule a une voix off qui la lit et l'explique (contrôle bloquant du moteur). |
| Pouvoir réutiliser la notion | Chaque fiche a un exercice ; un exercice sans correction bloque la production. |
| Pas de prérequis implicites | Prérequis listés par identifiant et contrôlés par script ; niveau mathématique (M0 à M4) indiqué partout. |
| Corrélation ≠ causalité, description ≠ inférence, prédiction ≠ explication | Trois vidéos dédiées (S3.06, S6.01, S17.01), et le champ « Idées fausses à prévenir » les rappelle là où le piège existe. |
| Accessible sans sacrifier la rigueur | Relecture humaine des définitions (ChatGPT) et contrôle automatique des calculs (moteur). |
| FR et EN naturels, pas traduits | Titre de travail anglais propre à chaque vidéo ; scripts écrits dans chaque langue à partir de la même fiche de conception. |

## 2.7 Correspondance avec les recommandations GAISE (révision 2025)

Le rapport GAISE de l'American Statistical Association, révisé en 2025 et publié par étapes, formule dix recommandations pour l'enseignement de la statistique et de la science des données. Le tableau indique comment le programme les applique, et où il s'en écarte à cause du format vidéo.

| Recommandation GAISE (résumé) | Application dans ACTU-BASICS |
|---|---|
| 1. Enseigner la statistique comme un processus qui va des données à la décision | Cycle d'enquête en 9 étapes dans chaque fiche de conception (section 6) ; S3.09 en démonstration complète |
| 2. Communiquer les résultats, avec leur portée et leurs limites | Étape « limites » obligatoire dans l'arc d'un épisode ; champ « hypothèses et limites » |
| 3. Viser la compréhension plutôt que la manipulation de formules | Intuition d'abord, formule ensuite, chaque symbole expliqué |
| 4. Utiliser des données réelles, avec un contexte | Choix explicite dans chaque fiche : données réelles, simulation ou calcul pur, avec la raison |
| 5. Encourager la pensée multivariée | Tableaux croisés et Simpson dès le niveau 1 (S3.02, S3.03), régression multiple, graphes causaux (E1.05) |
| 6. Utiliser des logiciels pour explorer | Simulations à l'écran ; scripts reproductibles fournis en description (arbitrage A9) |
| 7. Collecte et usage éthiques des données | S1.10, S17.06, prudence de la constitution éditoriale |
| 8. Pédagogies actives | Estimation demandée, exercice avec temps de réflexion dans chaque vidéo. **Limite du format** : une vidéo reste moins interactive qu'un cours |
| 9. Évaluations formatives et sommatives variées | Exercice dans chaque vidéo (formatif) ; tests de transfert et de diagnostic d'erreur pendant le pilote (section 7.2). La section « Assessment » de GAISE 2025 est encore en préparation : à intégrer dès sa parution |
| 10. Stratégies inclusives | Éditions FR et EN autonomes, exemples variés, formulation non stigmatisante. À renforcer : sous-titres et accessibilité visuelle sont contrôlés, la diversité des exemples ne l'est pas encore |

## 2.8 Bilinguisme

Chaque vidéo existe en deux éditions, française et anglaise, produites à partir de la **même fiche de conception**. Les scripts sont écrits séparément. Les exemples peuvent être adaptés à chaque public (Insee et Eurostat d'un côté, BLS, ONS ou Banque mondiale de l'autre), à condition que **le raisonnement et les nombres calculés restent identiques**. Le moteur signale déjà un écart de nombres entre les deux éditions. Les titres anglais de ce document sont des titres de travail, à revoir par l'éditorial.
