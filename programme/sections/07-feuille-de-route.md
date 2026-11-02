# 7. Feuille de route du premier catalogue {#feuille-de-route}

Le ticket n° 10 fixe la règle : **constituer un catalogue conséquent avant de lancer les plateformes**. Cette section propose un volume, un ordre et un équilibre entre piliers. Elle ne planifie aucune publication.

## 7.1 Volume total du programme

{{TABLEAU_VOLUMES}}

Ces {{NB_VIDEOS}} vidéos représentent plusieurs années de production. Le premier catalogue n'en vise qu'une partie : de quoi lancer la chaîne avec une offre cohérente, puis continuer en flux.

## 7.2 Phases proposées

| Phase | Contenu | But | Condition pour passer à la suite |
|---|---|---|---|
| **0 · Pilote** | 5 vidéos de la vague 1, choisies pour couvrir les formes (leçon, paradoxe, SHORT) plutôt que dans l'ordre : S1.08, S2.05, S3.06, Q3.01, Q2.04 | Mesurer le temps réel de conception, de relecture et de rendu. Régler le gabarit pédagogique et la boucle de revue. | Les 5 vidéos sont validées par JG. Le temps moyen par vidéo est connu. |
| **1 · Vague 1** | {{NB_V1}} vidéos, environ {{H_V1}} h : niveau 1 complet, boîte à outils M0, premières probabilités, 10 sujets du quotidien, 2 vidéos d'économie | Un parcours « Lire un chiffre sans se faire avoir » complet, utile seul | Vague complète et validée |
| **2 · Vague 2** | {{NB_V2}} vidéos, environ {{H_V2}} h : niveau 2 complet, rappels M1 et M2, 8 sujets du quotidien, contrefactuels | Un second parcours « Le hasard apprivoisé » | Au moins la moitié produite avant le lancement |
| **3 · Pré-lancement** | 4 à 6 vidéos d'actualité, choisies avec la grille de la section 5.2 | Une actualité fraîche au moment du lancement | Revalidation des chiffres moins de 7 jours avant la mise en ligne |
| **4 · Lancement puis flux** | Publication du stock selon le rythme choisi par JG. En parallèle : niveau 3, pilier 2 (E2 à E5) et actualité. | Garder au moins 8 semaines d'avance | Décision de JG |

**Seuil de lancement proposé** : vague 1 terminée **et** au moins **12 semaines de publication en stock** au rythme qui sera choisi. Par exemple, avec 3 vidéos EDUCATIONAL par semaine, il faut 36 vidéos, soit la vague 1 seule. Avec 5 par semaine, il faut 60 vidéos, soit la vague 1 et une partie de la vague 2. Chaque EDUCATIONAL peut produire un ou deux SHORT d'accroche, qui s'ajoutent au stock sans travail pédagogique supplémentaire.

## 7.3 Équilibre entre piliers

| | Vague 1 | Vague 2 | Programme complet |
|---|---|---|---|
| Statistiques | {{V1_S}} | {{V2_S}} | {{NB_STATS}} |
| Économétrie | {{V1_E}} | {{V2_E}} | {{NB_ECO}} |
| Quotidien | {{V1_Q}} | {{V2_Q}} | {{NB_QUOTIDIEN}} |
| Boîte à outils | {{V1_M}} | {{V2_M}} | {{NB_MATHS}} |

Le pilier 1 domine les deux premières vagues parce qu'il porte les prérequis de tout le reste. Le pilier 3 y occupe environ un cinquième des vidéos. C'est lui qui attire de nouveaux spectateurs, et ses vidéos se comprennent sans le cursus. L'économétrie est volontairement réduite au départ : ses modules centraux (E2 à E7) demandent la régression (S9), qui n'arrive qu'au niveau 3. Si JG veut plus d'économie dès le lancement, la solution est d'ajouter des sujets du quotidien à forte composante économique (Q1, Q4), et non d'avancer la théorie (arbitrage A5).

## 7.4 Ordre de production

L'ordre ci-dessous est calculé par le script. Il respecte tous les prérequis et suit, à prérequis égaux, l'ordre de lecture du programme. Les sujets du quotidien sont intercalés dès que la notion qu'ils illustrent est produite, pour varier le stock.

{{PREMIER_CATALOGUE}}

## 7.5 Ce qui est opérationnel et ce qui reste à faire

| Opérationnel aujourd'hui | Reste à faire avant la phase pilote |
|---|---|
| Moteur de rendu FR et EN, fiches pédagogiques, scènes de formule, de courbe, d'exercice, de correction et d'animation | Valider ce programme (JG), après la revue de ChatGPT |
| Recalcul automatique des nombres annoncés, contrôle qualité bloquant | Écrire les 5 fiches de conception de la phase pilote (éditorial) |
| Voix de synthèse locale (Kokoro), sous-titres, miniatures, métadonnées | Mise en page YOUTUBE_LESSON 16:9 à éprouver sur une vraie leçon de plus de 10 minutes |
| Contrôle des prérequis et des calculs de ce programme (`programme/construire.py`) | Nouveaux modèles d'animation pour le niveau 1 (histogramme, boîte à moustaches, nuage de points) |
| Modèle de fiche de conception (`modeles/fiche-conception-episode.yaml`) | Identité sonore définitive (prototype synthétique à ce jour) |

**Risques principaux.** (1) La capacité de relecture humaine est le vrai goulot d'étranglement : la phase pilote sert à la mesurer. (2) Le format long 16:9 n'a pas encore été jugé sur un vrai cours. (3) Les vidéos d'actualité vieillissent : elles sont donc produites en dernier. (4) Les exemples réels « à sourcer » demandent un travail de recherche qui n'est pas encore fait. Ils sont signalés dans chaque fiche.
