# 5. Pilier 3 · Phénomènes du quotidien et actualité {#quotidien}

Ce pilier explique des phénomènes familiers et des événements importants avec les chiffres, la statistique, l'économie et le raisonnement scientifique. Il a deux sous-séries, aux rythmes très différents.

| | Quotidien (intemporel) | Actualité (daté) |
|---|---|---|
| Point de départ | Une expérience que tout le monde connaît | Un événement mondial important et récent |
| Durée de vie | Plusieurs années | Quelques semaines à quelques mois |
| Production | **Dès maintenant**, dans le stock du premier catalogue | **Au plus près du lancement**, puis en flux |
| Chiffres | Calculs purs, ou statistiques stables revérifiées | Revérifiés le jour de la préparation, datés à l'écran |
| Type de fiche moteur | `pedagogique` | `actualite` |

## 5.1 Taxonomie des phénomènes du quotidien

Six familles de sujets, chacune reliée aux notions du cursus. La liste détaillée (section 5.5) en donne {{NB_QUOTIDIEN}} sujets prêts à scénariser. Elle reste ouverte.

| Famille | Exemples de questions | Notions mobilisées |
|---|---|---|
| **Q1 · Argent, prix et consommation** | Pourquoi « mon » inflation n'est pas celle de l'institut ? Pourquoi −30 % puis −20 % ne font pas −50 % ? | Pourcentages, moyennes pondérées, croissance composée, espérance |
| **Q2 · Risque, santé et sécurité** | Faut-il croire un test positif ? Avion ou voiture ? | Risque relatif et absolu, Bayes, dénominateurs, biais du survivant |
| **Q3 · Pièges de l'intuition** | Pourquoi mon bus semble toujours en retard ? Pourquoi un champion déçoit-il la saison suivante ? | Paradoxe de l'inspection, régression vers la moyenne, coïncidences |
| **Q4 · Mesurer la société** | Qui est chômeur ? Que mesure le PIB ? Comment lire un sondage ? | Définitions, sources, inégalités, projections |
| **Q5 · Technologie et algorithmes** | Comment un site décide-t-il quel bouton montrer ? L'IA se trompe-t-elle « en moyenne » ? | Tests A/B, recommandation, évaluation d'un classifieur |
| **Q6 · Sport, jeux et loisirs** | Le classement dit-il qui est le meilleur ? Combien de paquets pour finir l'album ? | Simulation, hasard, espérance, loi géométrique |

**Règle d'écriture.** Une vidéo du quotidien doit être **comprise sans avoir suivi le cursus**. Le lien vers la leçon (« pour aller plus loin ») est une invitation, pas un prérequis. Le contrôle automatique traite donc ces liens comme des renvois, et non comme des prérequis.

## 5.2 Actualité : méthode de sélection

Un sujet d'actualité n'est pas retenu parce qu'il est « tendance ». On part d'un événement important, puis on cherche **la notion mesurable qui l'éclaire vraiment**. Chaque sujet candidat est noté de 0 à 3 sur six critères :

| Critère | 0 | 3 |
|---|---|---|
| **Importance** | Fait divers local | Événement qui touche des millions de personnes ou plusieurs pays |
| **Intérêt pédagogique** | Aucun concept à transmettre | Notion claire, réutilisable, reliée au cursus |
| **Fiabilité des sources** | Chiffre de seconde main, sans méthode | Source primaire accessible, méthode publiée |
| **Stabilité des données** | Chiffre provisoire qui change chaque jour | Données publiées, révisions connues |
| **Valeur ajoutée d'ACTU-BASICS** | Déjà bien expliqué partout | Angle chiffré absent ou mal traité ailleurs |
| **Risque éditorial** (noté à l'envers) | Sujet sensible sans données solides | Sujet sans risque de stigmatisation ou de récupération |

**Seuils proposés** : 12 sur 18 au moins, et aucun critère à 0. Les sujets sensibles listés dans la constitution éditoriale (santé, criminalité, conflits, politique, migration, religion, identité, pauvreté) demandent en plus une double relecture et au moins 2 sur 3 en fiabilité des sources.

Répartition thématique visée pour l'actualité, reprise de la constitution éditoriale (section 2) : démographie 20 %, économie et argent 20 %, IA et technologie 20 %, sciences 15 %, société 15 %, comparaisons internationales 10 %.

## 5.3 Actualité : protocole de vérification

Chaque épisode d'actualité a un **dossier de sources**, dans la fiche d'actualité existante (`modeles/fiche-contenu.yaml`) :

1. **Source primaire** du chiffre central, avec URL et date de consultation, et au moins une **source de contexte** indépendante.
2. **Date de publication** de la source et **période couverte** par les données. Ce sont deux dates différentes, et les deux sont enregistrées.
3. **Définition exacte** de l'indicateur, périmètre géographique, population couverte.
4. **Statut du chiffre** : observé, estimé, provisoire ou projeté. Révisions déjà connues.
5. **Faits et interprétations séparés** dans le script : ce que disent les données, ce qu'en concluent les experts, ce qui reste débattu. Une interprétation est toujours attribuée.
6. **Limites et incertitudes** dites à voix haute : marge d'erreur, données manquantes, comparabilité.
7. **Revalidation le jour J** : les chiffres sont revérifiés juste avant l'écriture du script, puis juste avant le rendu si plus de 7 jours ont passé.
8. **Date de référence à l'écran** (« données 2025, publiées en mars 2026 ») et dans la description.
9. **Date de péremption** inscrite dans les métadonnées. À cette date, la vidéo est relue : elle est mise à jour, annotée ou retirée, et la correction est consignée.

**Ce que le programme ne fait pas.** Aucun chiffre d'actualité n'est inscrit dans ce syllabus. Seuls les gabarits et la méthode sont fixés, pour éviter de figer des données qui deviendront vite fausses.

## 5.4 Actualité : gabarits d'épisodes

| Gabarit | Question type | Format | Notion la plus souvent reliée |
|---|---|---|---|
| **Le chiffre derrière l'info** | « Que veut dire exactement ce chiffre ? » | SHORT | Définitions, pourcentages (S1.08) |
| **Décryptage** | « Que montrent vraiment les données ? » | EDUCATIONAL | Selon le sujet |
| **Le sondage de la semaine** | « Ce sondage dit-il ce qu'on lui fait dire ? » | SHORT ou EDUCATIONAL | Marge d'erreur (S6.05), Q4.05 |
| **Corrélation ou causalité ?** | « Cette étude prouve-t-elle ce que dit le titre ? » | EDUCATIONAL | S3.06, E1.04 |
| **Comparaison internationale** | « Peut-on comparer ces pays ? » | EDUCATIONAL | Définitions, parité de pouvoir d'achat (Q4.01) |
| **Mise à jour** | « Un an après, que disent les nouvelles données ? » | SHORT | Révision des données, S1.07 |

## 5.5 Sujets du quotidien : fiches détaillées

{{SYLLABUS_QUOTIDIEN}}
