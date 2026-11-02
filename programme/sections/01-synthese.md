# Synthèse pour décision {#synthese}

<div class="encadre statut" markdown="1">
**Statut du document.** Version {{VERSION}}, construite le {{DATE}}. Proposition structurée par Claude (direction technique et production) en réponse au ticket n° 10. Elle intègre le cadrage de ChatGPT dans le ticket et les corrections de sa première revue de la version 1 (voir l'historique en fin de synthèse). La revue de ChatGPT se poursuit, puis JG valide. Rien n'est publié, rien n'est fusionné dans `main`. Les décisions à prendre sont rassemblées en section 10.
</div>

## Ce que la chaîne enseignera

ACTU-BASICS apprend à **raisonner avec des chiffres**. Le but n'est pas d'empiler des notions. Chaque vidéo part d'une question concrète, construit l'intuition, fait le raisonnement à l'écran, puis formalise. Elle se termine par une vérification que le spectateur peut faire seul. Le programme repose sur trois piliers et une série de soutien :

| Pilier | Ce qu'il apporte | Vidéos | Durée cumulée |
|---|---|---|---|
| **1. Statistiques** | Un cursus complet, du débutant absolu aux méthodes avancées : 4 niveaux, 18 modules | {{NB_STATS}} | ≈ {{H_S}} h |
| **2. Économétrie** | Une progression autonome, centrée sur la question « quand une régression mesure-t-elle un effet causal ? » | {{NB_ECO}} | ≈ {{H_E}} h |
| **3. Quotidien et actualité** | Une sous-série intemporelle (déjà {{NB_QUOTIDIEN}} sujets) et une sous-série d'actualité, avec une méthode de sélection et de vérification, sans chiffres figés | {{NB_QUOTIDIEN}} + flux | ≈ {{H_Q}} h |
| *Boîte à outils maths* | Des rappels courts (fractions, logarithmes, dérivées, matrices), à voir juste avant la vidéo qui en a besoin | {{NB_MATHS}} | ≈ {{H_M}} h |

Au total, **{{NB_VIDEOS}} vidéos réparties en {{NB_MODULES}} modules, soit environ {{HEURES_TOTAL}} heures de contenu**. Chaque vidéo a une **entrée de syllabus** : question centrale, prérequis, objectifs observables, maîtrise visée, intuition, exemple, niveaux mathématiques, idées fausses à prévenir, exercice, durée et format.

<div class="encadre" markdown="1">
**Entrée de syllabus ou fiche de conception.** Une entrée de syllabus dit *quoi* enseigner et *dans quel ordre*. Elle ne remplace pas la **fiche de conception** (section 6), qui détaille le déroulé, les formules expliquées, les calculs vérifiés, les sources précises, la correction et l'adaptation anglaise. Aujourd'hui, **une seule vidéo a une fiche complète** : le paradoxe des anniversaires (S4.06, vidéo de lancement). Les fiches de conception seront écrites vague par vague, juste avant la production.
</div>

## Dans quel ordre

1. **Niveau 1 · Découverte** (aucun prérequis) : d'où viennent les données, un premier contact avec le hasard (S1.11, sans formule), décrire une variable, décrire une relation. Corrélation et causalité sont distinguées dès ce niveau.
2. **Niveau 2 · Fondamentaux** : le hasard et les probabilités, puis les variables aléatoires, jusqu'à la loi des grands nombres et au théorème central limite.
3. **Niveau 3 · Inférence et modèles** : échantillonnage, estimation, tests, régression, ANOVA, modèles linéaires généralisés, méthodes de simulation.
4. **Niveau 4 · Branches avancées**, à suivre au choix et non en ligne droite : statistique bayésienne, analyse multivariée, séries temporelles, survie, processus stochastiques, apprentissage statistique et passerelles vers le machine learning.

L'économétrie démarre au niveau 2, avec les données économiques et la notion de contrefactuel. Elle s'appuie ensuite sur le module de régression des statistiques sans le refaire. Un script vérifie à chaque construction que, dans le tronc commun, **aucune vidéo ne demande une notion enseignée plus tard**.

## Comment les vidéos seront sélectionnées et produites

- **Tronc commun** : on produit dans l'ordre des prérequis, par vagues thématiques. Une vague ne commence que lorsque ses prérequis sont produits.
- **Quotidien** : chaque sujet est relié à une notion du cursus. Il est rédigé pour être compris sans l'avoir suivi.
- **Actualité** : une grille de sélection notée sur 18 points et un protocole de vérification. Les chiffres sont revérifiés le jour de la préparation et datés à l'écran. Ces vidéos seront produites au plus près du lancement.
- **Chaîne de production** : la fiche de conception (section 6) est remplie par l'éditorial et relue. Elle devient ensuite une fiche YAML que le moteur actuel (`production/produire.py`) transforme en vidéo FR et EN. Le moteur recalcule chaque nombre annoncé.

## Le premier catalogue proposé

Deux vagues, sans publication avant que le stock soit suffisant :

- **Vague 1 · « Lire un chiffre sans se faire avoir »** : {{NB_V1}} vidéos, environ {{H_V1}} h. Niveau 1 complet, premières notions de probabilités, premiers sujets du quotidien et d'économie.
- **Vague 2 · « Le hasard apprivoisé »** : {{NB_V2}} vidéos, environ {{H_V2}} h. Niveau 2 complet, avec les rappels mathématiques nécessaires.

Elles commencent par une **phase pilote interne de 5 vidéos**. Elle sert à mesurer le temps réel de travail humain et à tester la compréhension auprès de spectateurs débutants. Ce n'est pas une mini-série à publier dans cet ordre.

## Ce que JG doit décider

Les dix arbitrages de la section 10, dont les plus structurants :

1. adopter les trois piliers et leur correspondance avec les quatre familles actuelles du moteur ;
2. fixer le seuil de lancement (proposition : vague 1 terminée et au moins 12 semaines de publication en stock, comptées en épisodes entièrement validés en FR et en EN) ;
3. reporter les vidéos d'actualité aux semaines qui précèdent le lancement ;
4. choisir le format des leçons longues (vertical ou 16:9).

## Historique des versions

| Version | Changements |
|---|---|
| 1.0 | Première proposition structurée de Claude |
| 1.1 | Corrections après la première revue de ChatGPT : randomisation (S1.06), théorème central limite (S5.13), hypothèses de la marge d'erreur (S6.03, S6.05), premier contact avec le hasard au niveau 1 (S1.11), niveaux mathématiques séparés (comprendre, appliquer, démontrer), maîtrise visée par vidéo, sources des exemples historiques, liens de la bibliographie vérifiés, pilote, unité de stock et charge de travail précisés, minima de la grille d'actualité, décisions déjà prises distinguées des recommandations |

## Sommaire

1. Synthèse pour décision
2. Architecture éditoriale globale
3. Pilier 1 · Statistiques : syllabus complet
4. Pilier 2 · Économétrie : syllabus et dépendances
5. Pilier 3 · Phénomènes du quotidien et actualité
6. Fiche pédagogique type
7. Feuille de route du premier catalogue
8. Prérequis mathématiques et glossaire
9. Bibliographie et ressources
10. Arbitrages demandés
11. Annexe : rapport des contrôles automatiques
