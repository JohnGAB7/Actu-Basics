# ACTU-BASICS · Parcours Actuariat de A à Z (proposition v3, à débattre)

Statut : **proposition v3 de Claude, à débattre avec Perplexity, puis à valider par JG.** La v2 (`PARCOURS-ACTUARIAT.md`) reste la référence tant que la v3 n'est pas validée. Rien n'est produit sur la base de la v3 avant validation.

Demande de JG (2026-11-12) : « Adaptons le programme et débat d'une nouvelle version avec Claude et Perplexity ».

Ce document part du bilan du pilote (trois leçons et six extraits, FR et EN, validés et rendus le 2026-11-11). Chaque changement proposé est suivi de la raison et d'une question ouverte pour le débat. Les faits extérieurs sont donnés avec leur source et leur date de consultation (2026-11-12) ; Perplexity est invité à les vérifier.

## 1. Bilan du pilote : ce qu'il nous apprend

| Constat | Conséquence pour le programme |
| --- | --- |
| Les trois leçons durent 6 min 29 à 7 min 04 et couvrent leur question sans remplissage. | La cible de 8 à 20 minutes de la v2 ne correspond pas à la matière d'une leçon d'introduction. |
| Les six extraits durent 58 à 88 s. Cinq sur six dépassent 60 s. | La fourchette 45 à 90 s tient, mais il faut une idée par extrait, pas deux. |
| Un écran d'extrait trop chargé est devenu illisible sur mobile (A2.01-x2). | Règle : au plus trois lignes courtes par écran d'étapes dans un extrait. |
| Trois relectures ChatGPT ont été nécessaires sur les versions FR, surtout pour la typographie, la notation et les nuances (« de même loi », « dans 98 % des cas »). | Une liste de contrôle FR (typographie, notation, vocabulaire actuariel) en amont évite des allers-retours. |
| Les fiches PDF à télécharger et les fichiers de tableur prévus par la v2 n'ont pas été produits pour le pilote. | Soit on les produit, soit on les retire de la promesse. |
| Le public visé, « étudiants débutants en actuariat », prépare souvent un examen précis. | Le programme gagne à dire clairement à quel examen chaque module prépare. |

## 2. Changements proposés

### 2.1 Relier chaque module aux examens

**Proposition.** Chaque module affiche les examens auxquels il prépare, sans prétendre remplacer le programme officiel :

| Module | SOA (États-Unis, Canada) | IFoA (Royaume-Uni) | France |
| --- | --- | --- | --- |
| A1 Mathématiques financières | Exam FM | CM1 (partie financière) | Master accrédité par l'Institut des actuaires |
| A2 Probabilités pour l'assurance | Exam P | CS1 | idem |
| A3, A4 Vie et provisions vie | FAM (partie vie), ALTAM | CM1 (partie vie) | idem |
| A5, A7 Sinistres et provisionnement non-vie | FAM (partie courte durée), ASTAM | CS2, CM2 | idem |
| A6 Tarification | SRM, PA ; ASTAM | CS2 | idem |
| A8 Risque et solvabilité | ALTAM, ASTAM (en partie) | CM2, CP1 | Solvabilité II, ACPR |

Sources consultées le 2026-11-12 :
- SOA, « ASA Pathway Changes and Transition Information » : le parcours ASA comprend Exam P, Exam FM, Exam FAM, Exam ALTAM ou ASTAM, Exam SRM et Exam PA ; FAM depuis octobre 2022.
- SOA, compte rendu du conseil d'administration de juin 2026 : un groupe de travail propose de faire évoluer le parcours ASA (application pratique, IA, simplification) ; le conseil a approuvé une phase d'étude de marché. **Le parcours peut donc changer** : la correspondance doit être datée et revue.
- IFoA : la correspondance CS1, CS2, CM1, CM2, CP1 est donnée de mémoire et **doit être vérifiée** sur le site de l'IFoA.

**Raison.** Un étudiant cherche « Exam P probability » ou « CS1 » ; afficher l'examen rend la série trouvable et utile.

**Question pour le débat.** Faut-il afficher les codes d'examen dans les titres (meilleure recherche) ou seulement dans les descriptions (moins de risque si le parcours change) ?

### 2.2 Durées réalistes

**Proposition.**
- Leçon longue : **6 à 12 minutes**, la matière décide. Au-delà de 12 minutes, on coupe en deux leçons.
- Extrait vertical : **45 à 75 s** visés, 90 s au plus. Une seule idée.
- YouTube accepte désormais des Shorts jusqu'à 3 minutes (aide YouTube, « Understand three-minute YouTube Shorts », consultée le 2026-11-12). On ne s'en sert pas comme cible : un extrait plus long n'est pas plus utile.

**Question pour le débat.** Des Shorts de 2 à 3 minutes, de type « exercice corrigé », peuvent-ils servir les étudiants mieux que des extraits de 60 s ?

### 2.3 Ajouter un module de statistique pour actuaires

**Proposition.** Un module **A2b · Statistique pour l'assurance** (4 vidéos) entre A2 et A3 : estimation, maximum de vraisemblance, intervalles de confiance, adéquation d'une loi aux données.

**Raison.** A5, A6 et A7 supposent ces outils. La v2 renvoie à la série courte S, mais un étudiant qui suit le parcours long n'a pas à chercher ailleurs.

**Question pour le débat.** A2b est-il nécessaire, ou un rappel intégré au début de A5 suffit-il ?

### 2.4 Des exercices de type examen

**Proposition.** Chaque module se termine par une vidéo **« Exercices de type examen »** : trois problèmes originaux, du niveau des examens, résolus pas à pas. Jamais de reprise des questions officielles, qui sont protégées.

**Raison.** C'est le format le plus utile à un étudiant débutant, et le pilote montre que l'exercice en pause fonctionne bien dans le moteur.

**Question pour le débat.** Trois problèmes par vidéo, ou un seul problème plus long ?

### 2.5 Tenir ou retirer les promesses de la v2

**Proposition.**
- **Fiche PDF** : une page par leçon (formules, exemple, exercice corrigé), générée à partir de la fiche, comme les documents de relecture. On la produit à partir de A0.01.
- **Fichiers de tableur, R et Python** : seulement là où ils apportent quelque chose (A1, A3, A5, A6, A7, A9), et non « à chaque module ».

**Question pour le débat.** Où héberger ces fichiers pour le public (description YouTube, dépôt public, autre) ?

### 2.6 Rythme de production

**Proposition.** Un module à la fois, par lots de 2 ou 3 leçons. Pour chaque lot : fiches FR et EN, relecture, validation par JG, rendu. Cible : **une leçon longue toutes les une à deux semaines**, en FR et en EN, avec leurs extraits.

**Raison.** Le pilote a demandé plusieurs tours de relecture pour trois leçons. Promettre une leçon par semaine sans stock d'avance expose à des trous de publication.

### 2.7 Deux relecteurs, deux rôles

**Proposition.**
- **ChatGPT** : langue, pédagogie, typographie FR et anglais naturel, cohérence FR/EN.
- **Perplexity** : vérification des faits datés et sourcés (examens, réglementation, tables de mortalité, chiffres réels), avec liens vers les sources primaires.
- **JG** : validation finale.

**Question pour le débat.** Perplexity doit-il relire chaque leçon, ou seulement celles qui citent des faits réels (A0, A3, A8) ?

## 3. Parcours révisé (vue d'ensemble)

| Bloc | Modules | Vidéos longues (v2 → v3) |
| --- | --- | --- |
| 1 · Fondamentaux | A0 Métier et contrat ; A1 Mathématiques financières ; A2 Probabilités pour l'assurance ; **A2b Statistique pour l'assurance** | 14 → 18 + 3 vidéos d'exercices |
| 2 · Techniques actuarielles | A3 Vie et mortalité ; A4 Provisions vie ; A5 Sinistres non-vie ; A6 Tarification ; A7 Provisionnement non-vie | 25 → 25 + 5 vidéos d'exercices |
| 3 · Risque et pratique | A8 Risque et solvabilité ; A9 Projet de synthèse | 8 → 8 + 1 vidéo d'exercices |
| **Total** | 11 modules | **47 → 51 leçons + 9 vidéos d'exercices = 60** |

Le contenu des modules A0 à A9 reste celui de la v2. Seuls s'ajoutent A2b, les vidéos d'exercices et la correspondance avec les examens.

## 4. Ce qui ne change pas

- JG's Holding, assureur fictif, toujours annoncé comme tel.
- FR et EN en même temps, mêmes nombres, version FR adaptée et non traduite mot pour mot.
- Chaque calcul passe par le vérificateur ; aucun chiffre réel sans source datée ; aucun conseil personnalisé.
- Aucune publication, fusion ni modification de `main` sans l'accord explicite de JG.

## 5. Décisions à prendre par JG après le débat

1. Valider ou modifier la correspondance avec les examens, et où l'afficher.
2. Ajouter ou non le module A2b.
3. Valider les durées (6 à 12 min ; 45 à 75 s).
4. Valider le rythme (une leçon toutes les une à deux semaines).
5. Valider le rôle de Perplexity dans la relecture.
6. Choisir la suite : A0.02 et A0.03 pour finir A0, ou A3.01 comme prévu dans la v2.
