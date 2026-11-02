# 3. Pilier 1 · Statistiques : syllabus complet {#statistiques}

## 3.1 Pourquoi cet ordre

L'ordre suit la démarche d'une enquête statistique, comme le recommande le rapport GAISE de l'American Statistical Association (révision de 2025, publiée par étapes ; recommandation 1) : poser une question, produire ou trouver des données, les explorer, choisir une méthode, calculer, interpréter, puis dire les limites.

- **Les données avant les calculs (S1).** Un débutant doit savoir d'où vient un chiffre avant d'apprendre à le résumer. Le biais de sélection et la différence entre observer et expérimenter arrivent dès le début, parce qu'ils conditionnent tout le reste.
- **Un premier contact avec le hasard dès le niveau 1 (S1.11).** La révision de ChatGPT a relevé que le débutant attendait 29 vidéos avant de croiser le hasard. S1.11 donne une première lecture intuitive (chance, fréquence, risque) et montre pourquoi deux échantillons diffèrent. Le formalisme reste au niveau 2.
- **Décrire avant de modéliser (S2, S3).** Chaque indicateur est introduit par le problème qu'il résout. On passe par exemple de la moyenne à la médiane à cause des valeurs extrêmes, puis aux quantiles pour décrire « le haut et le bas ».
- **Probabilités après la description (S4, S5).** Le spectateur sait alors ce qu'est une distribution observée. Une loi de probabilité devient « la distribution que l'on attendrait ». Chaque loi est présentée par l'histoire qui la produit avant sa formule.
- **Simulation avant théorie.** La loi des grands nombres, le théorème central limite, la distribution d'échantillonnage et l'intervalle de confiance sont d'abord **montrés par simulation**, puis justifiés. Cela rend le niveau 3 accessible sans calcul intégral avancé.
- **L'inférence en trois temps (S6, S7, S8).** On voit d'abord que le résultat change d'un échantillon à l'autre, puis on estime, puis on décide. La p-value arrive après l'intervalle de confiance, pour qu'elle ne soit pas le seul outil retenu.
- **Une spirale courte autour de la droite de régression.** La relation entre deux variables est montrée tôt, de façon descriptive (S3.04 à S3.07, avant les probabilités), comme dans la séquence alternative proposée par OpenStax. S3.06 (corrélation et causalité) est placée **avant** la droite, pour que la pente ne soit jamais lue comme un effet. S3.07 se termine par trois questions laissées ouvertes : hasard de l'échantillon, causalité, validité hors des données. Le niveau 3 (S9.01, S9.03) et l'économétrie (E1.04) y répondent explicitement.
- **Les modèles en dernier (S9, S10, S11).** La régression du niveau 3 reprend l'intuition donnée en S3.07 (droite des moindres carrés), puis la complète par l'inférence et les diagnostics.

## 3.2 Carte des dépendances entre modules

Chaque flèche signifie « s'appuie sur ». Le contrôle automatique travaille au niveau de chaque vidéo. Cette carte en donne la vue d'ensemble.

{{CARTE_STATS}}

## 3.3 Parcours conseillés

Le tronc commun (niveaux 1 à 3) est le parcours de référence. Il peut être suivi en plusieurs fois selon l'objectif du spectateur :

| Profil | Parcours | Vidéos environ |
|---|---|---|
| **Citoyen curieux** : lire l'actualité sans se faire avoir | S1, S2, S3, puis S4.01 à S4.10 et S6.05 (marge d'erreur) | 40 |
| **Étudiant** : réussir un premier cours de statistique | Niveaux 1 à 3 complets, avec la boîte à outils M1 et M2 | 100 |
| **Professionnel des données** | Niveau 3, puis S11, S17 et au choix S13 ou S14 | 60 |
| **Futur économiste** | S1 à S9, puis pilier 2 (E1 à E7), puis E8 ou E11 | 110 |
| **Finance et risque** | S1 à S9, S14, E2 et E3, puis E9 (volatilité, VaR) | 110 |
| **Actuariat et assurance** | S5, S7, S10 (avec S10.06), S15, S12 | 50 |

Ces parcours sont des **itinéraires recommandés** à travers le catalogue, pas des frontières : aucune vidéo n'en est exclue, et un spectateur peut en sortir à tout moment.

**Règle d'exhaustivité.** Toutes les vidéos pédagogiquement pertinentes figurent au catalogue, y compris les approfondissements et les spécialisations. Aucune n'est marquée « optionnelle » : c'est au spectateur de choisir ce qu'il suit (décision de JG). Pour l'orienter, chaque vidéo porte un **rôle dans le graphe**, calculé par le script à partir de son niveau et des prérequis. C'est une règle mécanique : elle dit où se trouve la vidéo dans les dépendances, **pas son importance pédagogique**. Une vidéo terminale (« approfondissement ») peut être essentielle à un objectif, comme la méta-analyse pour lire l'actualité scientifique. Un statut pédagogique éditorial distinct, s'il est souhaité, relève de la revue éditoriale (arbitrage A11) :

{{TABLEAU_ROLES}}

Chaque vidéo porte aussi son **état** : « Conçue » quand sa fiche de conception est complète ({{NB_CONCUES}} à ce jour, la vidéo de lancement), « Cataloguée » sinon. Aucune n'est encore produite et validée pour publication, en dehors de la vidéo de lancement, en attente de sa validation finale (section 7.2). Le catalogue est exhaustif ; l'ordre de production, lui, se priorise (section 7).

## 3.4 Ce que la statistique partage avec d'autres disciplines

Le ticket demande de préciser ce qui relève des statistiques et ce qui relève d'autres disciplines. La branche S17 est conçue comme une **passerelle**, et non comme un cours de machine learning :

| Relève de la statistique (traité ici) | Relève surtout d'autres disciplines (évoqué, non enseigné) |
|---|---|
| Biais, variance, surajustement, validation | Architecture des réseaux de neurones (informatique) |
| Incertitude d'une prédiction, calibration | Algorithmes d'optimisation à grande échelle (optimisation numérique) |
| Évaluation d'un classifieur, faux positifs | Ingénierie et stockage des données, mise en production (génie logiciel) |
| Biais d'échantillonnage des données d'entraînement | Théorie de la calculabilité, complexité algorithmique |
| Distinction prédire et expliquer, limites causales | Éthique et droit des algorithmes (évoqués à partir des questions statistiques) |
| Réseaux de neurones vus comme une régression non linéaire (S17.08), boosting (S17.07), prédiction conforme (S17.09) | |

## 3.5 Syllabus détaillé

Chaque module présente son objectif, ses prérequis et le sommaire de ses vidéos. Chaque vidéo a ensuite son entrée de syllabus. Ce n'est pas encore la fiche de conception, écrite avant la production (section 6).

Deux repères sont donnés pour chaque vidéo. **Maths** indique le niveau nécessaire pour comprendre l'idée, pour appliquer la méthode et pour la démontrer, quand ces niveaux diffèrent. **Maîtrise** indique ce que l'exercice et les objectifs vérifient : comprendre, appliquer, critiquer. Ce second repère est déduit des verbes des objectifs. Les liens « Prérequis » et « Prépare » permettent de suivre les dépendances dans le PDF. Un exemple marqué « à vérifier » ou « à sourcer » signale un fait extérieur : il sera vérifié et daté lors de la préparation de la vidéo, selon la constitution éditoriale. Ces marqueurs ne concernent que des données courantes : les exemples historiques sont sourcés (section 9.5).

{{SYLLABUS_STATS}}
