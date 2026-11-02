# 4. Pilier 2 · Économétrie : syllabus et dépendances {#econometrie}

## 4.1 L'idée directrice

L'économétrie d'ACTU-BASICS est organisée autour d'une seule question : **ajuster une relation statistique, est-ce mesurer un effet ?** La réponse est presque toujours « pas automatiquement ». Toute la progression sert à dire à quelles conditions elle devient « oui ».

Pour chaque méthode causale (modules E5 et E7), la vidéo suit la grille proposée par ChatGPT :

| Rubrique | Question posée à l'écran |
|---|---|
| **Estimand** | Quel effet, sur qui, exactement ? |
| **Contrefactuel** | À quoi compare-t-on ce qui s'est passé ? |
| **Hypothèses** | Que faut-il croire pour que la comparaison soit juste ? |
| **Menaces** | Qu'est-ce qui pourrait fausser la conclusion ? |
| **Diagnostics** | Comment vérifier ce qui peut l'être ? |
| **Portée externe** | Le résultat vaut-il ailleurs, pour d'autres personnes, à une autre époque ? |

## 4.2 Prérequis statistiques et mathématiques

| Module d'économétrie | Prérequis statistiques | Mathématiques |
|---|---|---|
| E1 · Données économiques et questions causales | S1, S3 (corrélation et causalité) | M1 |
| E2 · Le modèle linéaire (MCO) | **S9 complet** (régression) | M2, M3 en option |
| E3 · Inférence et diagnostics | S8 (tests), S9.06 (diagnostics) | M2 |
| E4 · Endogénéité | E2, E3 | M2 |
| E5 · Variables instrumentales | E4 | M2 |
| E6 · Données de panel | E3, E4.01 | M2 |
| E7 · Méthodes d'évaluation | E4, E5.01, E6.02 pour E7.04 | M2 |
| E8 · Séries temporelles économiques | S14.02, S16.01 (marche aléatoire), E3 | M2 à M3 |
| E9 · Réponses limitées | S10 (GLM) | M2 |
| E10 · Études de cas | E6, E7 | M2 |

## 4.3 Fondamental ou avancé

| Fondamental, pour tout spectateur du pilier | Extension avancée |
|---|---|
| E1 complet, E2 complet, E3.01 à E3.04 | E6.04 panels dynamiques *(optionnel)* |
| E4 complet : variable omise, simultanéité, erreur de mesure, sélection | E7.04 différences de différences échelonnées |
| E5.01 à E5.03 : idée, 2SLS, instruments faibles | E5.04 effet local (LATE) |
| E7.01 à E7.03, E7.05 : expérience, expérience naturelle, différences de différences, discontinuité | E7.06 contrôle synthétique |
| E6.01 et E6.02 : différences premières et effets fixes | E8 complet : racines unitaires, cointégration, VAR |
| | E9 complet : probit et logit, Tobit et Heckman, comptages |

## 4.4 Ce qui n'est pas refait, pour éviter les doublons

- **La régression** est enseignée une seule fois, en S9. Le module E2 la reprend sous l'angle de l'économiste (formes fonctionnelles, élasticités, contrôle) sans refaire les moindres carrés.
- **Les séries temporelles** sont partagées. La description, ARIMA et la prévision sont en S14. Les régressions fallacieuses, la cointégration, les VAR et la causalité de Granger sont en E8.
- **Les GLM** sont en S10. Le module E9 n'ajoute que les effets marginaux, la censure et la sélection.
- **Les expériences randomisées** sont introduites en S1.06 (intuition) et reprises en E7.01 sous l'angle des résultats potentiels.

## 4.5 Carte des dépendances

En bleu les modules de statistiques utilisés, en orange les modules d'économétrie. Les flèches en pointillé relient des modules d'un même niveau. Le syllabus détaillé suit, niveau par niveau.

{{CARTE_ECO}}

{{SYLLABUS_ECO}}
