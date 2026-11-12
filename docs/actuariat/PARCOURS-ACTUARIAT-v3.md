# ACTU-BASICS · Parcours Actuariat de A à Z (proposition v3.1)

Statut : **proposition v3.1 : v3 de Claude, débattue avec Perplexity le 2026-11-12, retour intégré. À valider par JG.** La v2 (`PARCOURS-ACTUARIAT.md`) reste la référence tant que la v3.1 n'est pas validée. Rien n'est produit sur cette base avant validation.

Demande de JG (2026-11-12) : « Adaptons le programme et débat d'une nouvelle version avec Claude et Perplexity ».

Ce document part du bilan du pilote (trois leçons et six extraits, FR et EN, validés et rendus le 2026-11-11). Chaque changement indique la position retenue après le débat. Les faits extérieurs sont donnés avec leur source et leur date de consultation (2026-11-12). Ce qui n'a pas pu être vérifié à la source est marqué **à vérifier**.

## 1. Bilan du pilote : ce qu'il nous apprend

| Constat | Conséquence pour le programme |
| --- | --- |
| Les trois leçons durent 6 min 29 à 7 min 04 et couvrent leur question sans remplissage. | La cible de 8 à 20 minutes de la v2 ne correspond pas à la matière d'une leçon d'introduction. |
| Les six extraits durent 58 à 88 s. Cinq sur six dépassent 60 s. | La fourchette 45 à 90 s tient, mais il faut une idée par extrait, pas deux. |
| Un écran d'extrait trop chargé est devenu illisible sur mobile (A2.01-x2). | Règle : au plus trois lignes courtes par écran d'étapes dans un extrait. |
| Trois relectures ChatGPT ont été nécessaires sur les versions FR, surtout pour la typographie, la notation et les nuances (« de même loi », « dans 98 % des cas »). | Une liste de contrôle FR (typographie, notation, vocabulaire actuariel) en amont évite des allers-retours. |
| Les fiches PDF à télécharger et les fichiers de tableur prévus par la v2 n'ont pas été produits pour le pilote. | Soit on les produit, soit on les retire de la promesse. |
| Le public visé, « étudiants débutants en actuariat », prépare souvent un examen précis. | Le programme gagne à dire à quel examen chaque module prépare, en partie. |

## 2. Changements retenus

### 2.1 Relier chaque module aux examens

**Position retenue (Claude et Perplexity d'accord).**
- Les codes d'examen vont dans la **description, la fiche PDF et les chapitres**, pas dans le titre. Le titre reste pédagogique et stable, ce qui protège la chaîne si un parcours change.
- Formule unique : **« prépare partiellement à »**, jamais « équivaut à ».
- Exemple de description : « Utile pour SOA Exam P, CAS Exam 1 et IFoA CS1 (recouvrement partiel). »

**Correspondance (recouvrement partiel, pas d'équivalence)**

| Module | SOA | CAS | IFoA | France |
| --- | --- | --- | --- | --- |
| A1 Mathématiques financières | Exam FM | Exam 2 | CM1 (partie financière) | Bases communes |
| A2 Probabilités pour l'assurance | Exam P | Exam 1 | CS1 (partie probabilités) | Bases communes |
| A2b Statistique pour l'assurance | SRM (en partie) | MAS-I, MAS-II | CS1 (partie statistique) | Bases communes |
| A3, A4 Vie et provisions vie | FAM (partie vie), ALTAM | — | CM1 (partie vie) ; CS2 (analyse de survie) | Bases communes |
| A5 Sinistres non-vie | FAM (partie courte durée), ASTAM | MAS-I, Exam 5 | CS2 | Bases communes |
| A6 Tarification | SRM, PA, ASTAM | Exam 5 | CS1, CS2 (**à vérifier**) | Bases communes |
| A7 Provisionnement non-vie | ASTAM | Exam 5 | **à vérifier** (CM2 dans l'ancien programme) | Bases communes |
| A8 Risque et solvabilité | ALTAM, ASTAM (en partie) | Exam 6 (variante selon le pays) | CM2, CP1 (mise en perspective, **à vérifier**) | Repères réglementaires : Solvabilité II, ACPR |

« Bases communes » signifie : utile pour les bases communes aux formations reconnues par l'Institut des actuaires, sans remplacer un diplôme ni donner d'équivalence. La reconnaissance porte sur un cursus complet, pas sur un module. Solvabilité II et l'ACPR sont un cadre réglementaire et une autorité de contrôle, pas des examens.

**Sources (consultées le 2026-11-12)**
- SOA, « ASA Pathway Changes and Transition Information » et « Associate of the Society of Actuaries (ASA) » : Exam P, FM, FAM, SRM, PA, puis ALTAM ou ASTAM, plus VEE, modules e-learning, FAP et APC.
- SOA, « June 2026 SOA Board of Directors Meeting Recap » : **la SOA a lancé une phase d'étude d'une évolution de l'ASA ; le contenu et le calendrier restent à confirmer.** Aucun examen n'est annoncé comme ajouté ou supprimé.
- CAS, « Credential Requirements » : l'ACAS comprend notamment MAS-I, MAS-II, Exam 5, Exam 6, le Course on Professionalism, et le PCPA (examen et projet). Exams 1 et 2 : relevé par Perplexity sur la page CAS « Validation by Educational Experience ». La date d'entrée du PCPA (1er janvier 2026, selon Perplexity) est **à vérifier**.
- IFoA, syllabi 2026 : CS1 « Actuarial Statistics », CS2 « Risk Modelling and Survival Analysis », CM1 « Actuarial Mathematics for Modelling », CM2 « Economic Modelling ». Les sujets détaillés de CS2, CM1 et CM2 n'ont pas pu être lus dans cette passe : les rattachements marqués **à vérifier** le seront dans les syllabi avant publication.
- France : page de l'Institut des actuaires sur les formations reconnues, **à consulter** avant publication.

### 2.2 Durées réalistes

**Position retenue (accord).**
- Leçon longue : **6 à 12 minutes**, la matière décide. Au-delà de 12 minutes, on coupe en deux leçons.
- Extrait vertical : **45 à 75 s** visés, 90 s au plus, une seule idée.
- **Short de 2 à 3 minutes** : seulement pour un **exercice complet** (énoncé, méthode, calcul, réponse), jamais un extrait ordinaire allongé. YouTube accepte les Shorts jusqu'à 3 minutes depuis le 15 octobre 2024 (aide YouTube, « Understand three-minute YouTube Shorts »).
- TikTok : pas de durée maximale annoncée, elle varie selon le format et l'application.

### 2.3 Ajouter un module de statistique pour l'assurance (A2b)

**Position retenue (accord, avec la réserve de Perplexity).** Quatre vidéos entre A2 et A3 : estimation, maximum de vraisemblance, intervalles de confiance, adéquation d'une loi. **Chaque vidéo part d'un problème d'assurance** (fréquence de sinistres, montant d'un sinistre, ajustement d'une loi, incertitude d'une estimation) : ce n'est pas un cours de statistique générale.

### 2.4 Des exercices de type examen

**Position retenue (accord, avec l'ajustement de Perplexity).** Une vidéo d'exercices à la fin de chaque module, avec des problèmes originaux, jamais des questions officielles.
- A1, A2, A2b : **trois problèmes courts**.
- A3 à A8 : **un problème long et contextualisé** sur JG's Holding.
- Chaque problème annonce la compétence visée.

### 2.5 Tenir ou retirer les promesses de la v2

**Position retenue (accord).**
- **Fiche PDF** d'une page par leçon (formules, exemple, exercice corrigé), **publiée en même temps que la leçon**, à partir de A0.01.
- **Fichiers tableur, R ou Python** seulement quand ils permettent une vraie manipulation : A1 (actualisation), A3 (table de mortalité), A5 (simulation de sinistres), A6 (tarification), A7 (provisionnement), A9.
- Question restant ouverte pour JG : où héberger ces fichiers (description YouTube, dépôt public, autre).

### 2.6 Rythme de production

**Position retenue (accord).** Une leçon longue **toutes les une à deux semaines**, FR et EN, avec ses extraits. **Constituer un stock de deux leçons avant d'annoncer un rythme** au public. Production par lots de 2 ou 3 leçons d'un même module.

### 2.7 Trois rôles de relecture

**Position retenue (accord, avec la précision de Perplexity).**
- **ChatGPT** : langue, pédagogie, typographie FR et anglais naturel, cohérence FR/EN. Toutes les leçons.
- **Perplexity** : faits sourcés. **Toute leçon qui contient un fait externe vérifiable** (examens, réglementation, définitions institutionnelles, chiffres réels, tables de mortalité, dates, plateformes). Pour une leçon purement mathématique, seulement les définitions, notations et sources citées.
- **JG** : validation finale.

## 3. Ajouts issus du débat

- **A0 · nouvelle vidéo « SOA, CAS, IFoA, France : quelles différences ? »** La correspondance est expliquée une fois, au lieu d'être répétée dans chaque module.
- **A0 · nouvelle vidéo « Comment lire un syllabus d'examen »** : sujets, pondérations, formules autorisées, style des questions.
- **A5 et A7 restent séparés** : sinistres et provisionnement non-vie sont deux sujets distincts.
- **A9 précise ses livrables dès le départ** : données fictives, hypothèses, modèle, limites, communication des résultats.

## 4. Parcours révisé (vue d'ensemble)

| Bloc | Modules | Leçons longues (v2 → v3.1) | Vidéos d'exercices |
| --- | --- | --- | --- |
| 1 · Fondamentaux | A0 Métier, contrat et examens ; A1 Mathématiques financières ; A2 Probabilités pour l'assurance ; **A2b Statistique pour l'assurance** | 14 → 20 (A0 : 3 → 5 ; A2b : 4) | 3 (A1, A2, A2b) |
| 2 · Techniques actuarielles | A3 Vie et mortalité ; A4 Provisions vie ; A5 Sinistres non-vie ; A6 Tarification ; A7 Provisionnement non-vie | 25 → 25 | 5 |
| 3 · Risque et pratique | A8 Risque et solvabilité ; A9 Projet de synthèse | 8 → 8 | 1 (A8) |
| **Total** | 11 modules | **47 → 53** | **9**, soit **62 vidéos** |

Le contenu des modules A1 à A9 reste celui de la v2, à l'exception des ajouts ci-dessus.

## 5. Ce qui ne change pas

- JG's Holding, assureur fictif, toujours annoncé comme tel.
- FR et EN en même temps, mêmes nombres, version FR adaptée et non traduite mot pour mot.
- Chaque calcul passe par le vérificateur ; aucun chiffre réel sans source datée ; aucun conseil personnalisé.
- Aucune publication, fusion ni modification de `main` sans l'accord explicite de JG.

## 6. Décisions à prendre par JG

1. Valider la v3.1 telle quelle, ou indiquer ce qui doit changer.
2. Choisir où héberger les fichiers tableur, R et Python.
3. Choisir la suite de la production : finir A0 (A0.02 à A0.05) ou ouvrir A3.01 comme prévu dans la v2.
