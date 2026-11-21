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
| 1 · Statistiques, modules S1 à S3, S6 à S19 | `apprendre_les_statistiques` | `pedagogique` |
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

## 2.4 Un format principal : l'épisode long

| Format (clé moteur) | Image | Durée | Rôle dans le programme (version 1.13) |
|---|---|---|---|
| **YOUTUBE_LESSON** (`youtube_lesson`) | horizontal 1920 × 1080 | 10–50 min | **Le format principal** : un épisode qui traite plusieurs notions cohérentes, avec chapitres YouTube horodatés, exercices et synthèse. C'est là que l'on se forme de façon complète. |
| **SHORT** (`short`) | vertical 1080 × 1920 | 30–60 s | **Bande-annonce** d'un épisode : son meilleur moment (paradoxe, résultat surprenant), qui renvoie toujours vers l'épisode complet. Jamais une définition isolée. |
| **EDUCATIONAL** (`educational`) | vertical 1080 × 1920 | 1 min 30–10 min | Réservé aux extraits d'un épisode (un chapitre publié à part sur une plateforme verticale) ; plus produit comme vidéo autonome. |

Les {{NB_VIDEOS}} entrées du catalogue gardent leur format d'origine dans les sections 3 à 5 : il indique la place que prend la notion à l'écran, et non plus une vidéo séparée. Leur durée s'additionne dans l'épisode. Les trois anciens SHORT autonomes (Q1.03, Q2.04, Q3.02) deviennent des chapitres courts de leurs épisodes et restent de bons candidats de bande-annonce.

La durée d'un épisode découle de ce qu'il faut pour atteindre ses objectifs, jamais d'un plafond arbitraire (constitution éditoriale, section 10). Au-delà de 50 min, il est coupé en deux épisodes. Les durées sont des **estimations de conception**, corrigées après l'écriture du script.

**Règles de regroupement.** (1) Un épisode regroupe des notions qui répondent à une même question. (2) Il reste dans un seul module, sauf exception justifiée dans le pilier Quotidien. (3) Dans le cursus, aucun chapitre ne demande une notion traitée plus loin. (4) Chaque chapitre garde son exercice, et l'épisode se termine par un exercice de synthèse. Les règles 1 et 2 relèvent de la relecture, les règles 3 et 4 sont contrôlées.

**Plateformes.** Les contrôles hérités du diagnostic TikTok du 21/11/2026 s'appliquent à tous les formats : première image pleine, aucun plan figé de plus de 2 s, logo discret, étiquette « contenu généré par IA » pour la voix de synthèse, aucun lien dans les légendes, vocabulaire sensible cadré (jeux d'argent, argent, santé, poids, élections, mortalité).

## 2.5 La structure d'un épisode

1. **Ouverture** (environ 1 min) : la question concrète de l'épisode, montrée et non seulement dite, avec du mouvement dès la première image.
2. **Plan à l'écran** : les chapitres, qui deviennent les chapitres YouTube.
3. **Chaque chapitre** suit l'arc déjà mis en œuvre dans le moteur et dans la vidéo de lancement :
    1. **Question** concrète, paradoxe ou situation familière ;
    2. **Intuition** : ce que l'on croit spontanément, avec une estimation demandée au spectateur ;
    3. **Données ou exemple minuscule**, que l'on peut suivre de tête ;
    4. **Raisonnement pas à pas**, montré à l'écran (« la voix raconte, l'image démontre ») ;
    5. **Formalisation** : la formule arrive après l'idée, et chaque symbole est expliqué ;
    6. **Exercice** avec un temps de réflexion, puis **correction** détaillée ;
    7. **Application** réelle et **limites** de la méthode.
4. **Synthèse** : comment les notions de l'épisode s'articulent, avec un schéma récapitulatif.
5. **Exercice de synthèse**, qui mobilise plusieurs chapitres, puis sa correction.
6. **Rappel mémorable**, renvoi vers l'unité Programme-B et vers l'épisode suivant, fin de marque (logo, signature).

## 2.6 Principes non négociables, traduits en règles de production

| Principe (ticket n° 10) | Règle appliquée dans le programme |
|---|---|
| La compréhension prime sur la durée | Durée estimée par épisode selon le contenu ; un épisode de plus de 50 min est découpé en deux, pas comprimé. |
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

Chaque vidéo existe en deux éditions, française et anglaise, produites à partir de la **même fiche de conception**. Les scripts sont écrits séparément. Les exemples peuvent être adaptés à chaque public (Insee et Eurostat d'un côté, BLS, ONS ou Banque mondiale de l'autre), à condition que **le raisonnement et les nombres calculés restent identiques**. Le moteur signale déjà un écart de nombres entre les deux éditions. Les titres anglais suivent l'orthographe américaine (-ize, -er : *optimization*, *kilometer*), majoritaire dans le catalogue. Une première relecture des 320 titres anglais a été faite en version 1.12 (cohérence orthographique, titres ambigus corrigés). Ce sont encore des titres de travail : une relecture par un locuteur natif reste prévue avant les fiches bilingues, avec celle des scripts.

## 2.9 Les {{NB_EPISODES}} épisodes

Liste produite par `programme/episodes.py` à partir de `catalogue/episodes.txt`. Durée : somme des fourchettes des chapitres. La colonne Programme-B renvoie au bloc ou à l'unité de la plateforme qui approfondit l'épisode. Les titres sont des titres de travail, relus par l'éditorial avant production.

{{CATALOGUE_EPISODES}}
