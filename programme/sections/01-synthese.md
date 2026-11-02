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

## Ce que JG a décidé

Le 2/11/2026, JG a retenu **toutes les recommandations** de la section 10.2 (arbitrages A1 à A11). Il a aussi tranché deux questions ouvertes : les sujets non statistiques sont intégrés quand ils sont pertinents (nouveau module S19, passerelles vers l'IA et l'informatique), et feu vert pour préparer les fiches des sujets sensibles, qui gardent la double relecture prévue par la constitution éditoriale. En pratique :

1. les trois piliers deviennent la structure de référence, au-dessus des quatre familles du moteur, sans le modifier ;
2. le seuil de lancement est fixé : vague 1 terminée et au moins 12 semaines de publication en stock, en épisodes entièrement validés en FR et en EN, à recalculer après le pilote ;
3. les vidéos d'actualité sont produites dans les semaines qui précèdent le lancement ;
4. les leçons de plus de 10 minutes passent en 16:9, après un essai.

**Ce qui reste** : la validation finale de ce PDF par JG, puis la mise à jour de la section 5 d'`ARCHITECTURE_EDITORIALE.md` (arbitrage A2), dans une PR distincte.

## Historique des versions

| Version | Changements |
|---|---|
| 1.0 | Première proposition structurée de Claude |
| 1.1 | Corrections après la première revue de ChatGPT : randomisation (S1.06), théorème central limite (S5.13), hypothèses de la marge d'erreur (S6.03, S6.05), premier contact avec le hasard au niveau 1 (S1.11), niveaux mathématiques séparés (comprendre, appliquer, démontrer), maîtrise visée par vidéo, sources des exemples historiques, liens de la bibliographie vérifiés, pilote, unité de stock et charge de travail précisés, minima de la grille d'actualité, décisions déjà prises distinguées des recommandations |
| 1.2 | Revue croisée avec ChatGPT : rapport GAISE 2025 et correspondance avec ses dix recommandations ; spirale explicite autour de la droite de régression (S3.07 → S9.01) ; trois vidéos d'économétrie (graphes causaux E1.05, analyse de sensibilité E4.05, appariement et score de propension E7.07) ; registre des hypothèses ; cycle d'enquête, données ou simulation, reproductibilité et preuve d'apprentissage dans la fiche de conception ; tests de transfert et de diagnostic d'erreur dans le pilote |
| 1.3 | Proposition ARCH/GARCH : nouveau module E9 « Volatilité conditionnelle » (3 vidéos et 2 optionnelles, 11 calculs vérifiés) ; anciens E9 et E10 renumérotés E10 et E11 ; profil « Finance et risque » ; prérequis de E8.04 corrigé (ARMA au lieu des chaînes de Markov) ; bibliographie des articles fondateurs |
| 1.4 | Décision de JG : toutes les vidéos possibles sont intégrées, aucune n'est marquée optionnelle (le spectateur choisit ; le script refuse désormais le champ « option »). Quatre vidéos ajoutées en E9 : changements de régime, volatilité stochastique, corrélations dynamiques (DCC), volatilité réalisée ; 5 calculs vérifiés de plus ; arbitrage A11 retiré, car tranché |
| 1.5 | Règle d'exhaustivité (ChatGPT, conforme à la décision de JG) : inventaire des vidéos manquantes et 35 entrées ajoutées dans les trois piliers ; rôle (socle, approfondissement, spécialisation, sujet autonome, rappel) et état (conçue ou cataloguée) affichés sur chaque vidéo ; corrections de E9 (quasi-vraisemblance, séquence du test ARCH-LM, mesures de volatilité, conditions du GARCH(1,1), annualisation, VaR et Expected Shortfall, test d'indépendance des dépassements) ; corrections détaillées des exercices chiffrés de E9 et des nouvelles vidéos ; 69 calculs vérifiés ; LISEZMOI synchronisé |
| 1.6 | Audit des familles proposées par ChatGPT (15 en statistiques, 14 en économétrie, 14 thèmes du quotidien) : table de correspondance en section 10.8 ; 41 vidéos ajoutées, dont neuf nouveaux modules du quotidien (démographie et santé publique, énergie et climat, logement, finances publiques et commerce, éducation, information et médias, conflits, agriculture, transport) ; objectifs complétés pour 21 vidéos existantes dont la couverture était partielle |
| 1.7 | Audit de la version 1.5 par ChatGPT (section 10.9) : tests d'équivalence (S8.12), inflation de zéros (S10.08), analyse multivers (S11.11), sécurité énergétique (Q8.04), chaînes d'approvisionnement (Q10.04) ; hétérogénéité en méta-analyse et niveau de groupement complétés ; taxonomie renommée « rôle dans le graphe » ; arbitrage A11 sur un statut éditorial ; description de la PR synchronisée |
| 1.8 | Audit de la version 1.7 par ChatGPT (section 10.10) : douze corrections de rigueur (TOST à 90 %, multivers, méta-analyse, zéros, BCa, instruments faibles, LATE, discontinuité, contrôle synthétique, panels dynamiques, émissions cumulées, attribution) ; corrections détaillées ajoutées et 112 calculs vérifiés ; liste fermée des références non vérifiées ; fiche de provenance des chiffres ; registre des affirmations qualitatives ; charge totale du catalogue ; règle des SHORT autonomes |
| 1.9 | Relecture de la version 1.8 par ChatGPT (section 10.11) : exercice et correction de E5.03 rattachés à un cadre précis ; prérequis de E5.04 ramené à E5.02, hypothèses du LATE distinguées des diagnostics ; provenance étendue aux chiffres prononcés, tracés et calculés ; inclusions et exclusions de la charge de travail ; règle de maturité des fiches ; recommandation commune sur A11 |
| 1.10 | Arbitrages rendus par JG : toutes les recommandations A1 à A11 retenues ; sujets non statistiques pertinents intégrés (nouveau module S19, 8 vidéos : réseaux profonds et convolutifs, modèles de langue, optimisation, modèles génératifs, mise en production, complexité, droit et éthique ; 8 calculs vérifiés de plus) ; feu vert pour les fiches des sujets sensibles |
| 1.11 | Dernière revue de ChatGPT (section 10.12) : provenance alignée en section 6.1 ; Anderson-Rubin robuste à l'hétéroscédasticité en E5.03 ; tokens, embeddings et attention précisés en S19.03 ; conditions de l'incompatibilité des critères d'équité en S19.08 |

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
10. Arbitrages rendus par JG
11. Annexe : rapport des contrôles automatiques
