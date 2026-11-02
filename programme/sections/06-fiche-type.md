# 6. Fiche pédagogique type {#fiche-type}

Chaque vidéo est conçue à partir d'une **fiche de conception**, avant tout script. Elle reprend la liste demandée par le ticket et la grille de ChatGPT. Elle sert ensuite à remplir la fiche de production YAML que le moteur lit (`modeles/fiche-pedagogique.yaml`). Le modèle vierge est dans le dépôt : `modeles/fiche-conception-episode.yaml`.

## 6.1 Les rubriques

| Rubrique | Contenu attendu | Qui la remplit |
|---|---|---|
| **Identifiant stable** | Le numéro du programme (ex. S2.05), qui ne change jamais | Programme |
| **Titre de travail FR et EN** | Deux titres naturels, pas une traduction | Éditorial |
| **Question centrale** | La question à laquelle le spectateur saura répondre à la fin | Éditorial |
| **Pilier, niveau, module, position** | Où la vidéo se situe dans le parcours | Programme |
| **Public visé et prérequis** | Vidéos à avoir vues, niveau mathématique M0 à M4, rappel conseillé | Programme |
| **Objectifs observables** | 2 ou 3 verbes d'action : calculer, distinguer, interpréter, repérer, expliquer pourquoi | Éditorial |
| **Intuition à transmettre** | L'image ou l'idée qui doit rester, avant toute formule | Éditorial |
| **Exemple fil rouge** | Un exemple minuscule, puis un exemple réel sourcé si besoin | Éditorial |
| **Déroulé des scènes** | Question → intuition → données → raisonnement → formalisation → exercice → application → limites → rappel | Éditorial puis production |
| **Formules** | Chaque formule, chaque symbole expliqué, unités et conditions d'usage | Éditorial |
| **Données, simulation ou calcul** | Le choix est explicite : données réelles (source, licence, population, variables, période, limites), données synthétiques ou simulation (paramètres), ou calcul pur, avec la raison du choix | Éditorial |
| **Hypothèses et limites** | Hypothèses de la méthode, conséquence si chacune échoue. Pour une méthode causale : registre des hypothèses (testable, non testable, diagnostic) | Éditorial |
| **Calculs vérifiés** | Chaque nombre annoncé, avec l'expression qui le recalcule (bloc `verifier`) | Production |
| **Reproductibilité** | Calcul, code ou paramètres qui permettent de refaire le résultat ; script fourni en description quand il y en a un | Production |
| **Idées fausses à prévenir** | Les contresens les plus fréquents, et le moment de la vidéo où on les désamorce | Éditorial |
| **Exercice et correction** | Une question que le spectateur peut résoudre seul, avec la démarche complète. Le cadre de l'exercice est précisé (hypothèses, données fournies), et la correction ne conclut que dans ce cadre. Une fiche ne passe pas au statut « validée par JG » tant qu'un exercice chiffré n'a pas sa correction détaillée | Éditorial |
| **Preuve d'apprentissage** | La tâche observable que le spectateur doit réussir sans aide, une question de **transfert** (exemple différent de la vidéo) et une question de **diagnostic d'erreur** (pourquoi une interprétation séduisante est fausse). Utilisées pour les tests du pilote | Éditorial |
| **Provenance des chiffres** | Pour chaque chiffre affiché, prononcé, représenté dans un graphique, comparé ou calculé, avec sa nature (source, calcul dérivé, paramètre de simulation) : définition, unité, population, période, couverture, révisions, source primaire, incertitude, comparabilité (section 5.3) | Éditorial |
| **Affirmations qualitatives** | Toute affirmation non chiffrée (« les débutants confondent… », « cette histoire est souvent déformée ») est inscrite avec son statut : hypothèse, sourcée, ou testée pendant le pilote. Une hypothèse n'est jamais présentée comme un fait ; la relecture croisée Claude et ChatGPT porte sur ce registre | Éditorial, relu par Claude |
| **Durée indicative** | Celle du catalogue n'est qu'un ordre de grandeur : elle est réestimée d'après le script dans la fiche, puis mesurée après la synthèse vocale | Production |
| **Format** | SHORT, EDUCATIONAL ou YOUTUBE_LESSON, avec la raison du choix | Programme |
| **Sources et licences** | Sources de tout fait extérieur, licences des données et des visuels | Éditorial |
| **Adaptation EN** | Ce qui change d'exemple ou de formulation, ce qui ne change pas (raisonnement, nombres) | Éditorial |
| **Critères de contrôle** | Test du débutant (peut-il réexpliquer ?), relecture des définitions, contrôle visuel mobile | Les deux |

## 6.2 Le cycle d'enquête, colonne vertébrale de chaque fiche

Toute fiche de conception répond, même brièvement, aux neuf questions de l'enquête statistique. Une vidéo courte n'en traite pas toutes les étapes à l'écran, mais la fiche dit lesquelles sont montrées et lesquelles sont seulement supposées.

1. Quelle question veut-on réellement résoudre ?
2. Quelle population et quelle mesure ?
3. D'où viennent les données, et quel mécanisme les a produites ?
4. Quelle exploration graphique et descriptive ?
5. Quelle méthode, et pourquoi celle-là ?
6. Quelles hypothèses cette méthode exige-t-elle ?
7. Quel résultat numérique, avec quelle incertitude ?
8. Quelle interprétation est permise, et laquelle ne l'est pas ?
9. Peut-on reproduire le résultat à partir des données, du code et des sources ?

## 6.3 Exemple rempli : S2.05 « Moyenne ou médiane ? »

<div class="exemple-fiche" markdown="1">

| | |
|---|---|
| **Identifiant** | S2.05 · Pilier 1 · Niveau 1 · Module S2 « Décrire une variable » · 5e vidéo sur 10 |
| **Titres de travail** | FR : « Moyenne ou médiane ? » · EN : “Mean or median?” |
| **Question centrale** | Pourquoi le « salaire moyen » est-il plus élevé que ce que gagne la plupart des gens ? |
| **Public et prérequis** | Grand public. A vu S2.04 (moyenne) et S2.03 (forme d'une distribution). Mathématiques M0. |
| **Objectifs** | À la fin, le spectateur sait (1) calculer une médiane avec un nombre pair ou impair de valeurs, (2) prévoir le sens de l'écart entre moyenne et médiane quand la distribution est asymétrique, (3) choisir l'indicateur qui répond à une question donnée. |
| **Intuition** | Une seule valeur extrême déplace la moyenne, presque jamais la médiane. |
| **Exemple fil rouge** | Neuf personnes dans un café gagnent entre 1 600 et 3 000 € par mois. Un dixième client, très riche, entre. La moyenne bondit, la médiane bouge à peine. Puis un exemple réel : distribution des salaires d'un institut statistique, à sourcer et dater. |
| **Déroulé** | 1. Question et estimation demandée : « quelle part des salariés gagne moins que le salaire moyen ? » · 2. Le café, la moyenne calculée · 3. Le client riche entre, la moyenne recalculée · 4. La médiane : ranger, prendre le milieu, cas pair · 5. Formalisation : définition, position (n + 1)/2 · 6. Exercice · 7. Correction · 8. Application aux salaires réels · 9. Limites : la médiane ignore l'ampleur des écarts, d'où l'intérêt de donner les deux · 10. Rappel. |
| **Calculs vérifiés** | Moyenne et médiane du café avant et après, part des salaires sous la moyenne dans l'exemple. Tous déclarés dans le bloc `verifier`. |
| **Idées fausses** | « La moitié des gens gagne plus que le salaire moyen » (désamorcée à l'étape 3). « La médiane est toujours meilleure » (désamorcée à l'étape 9). |
| **Données ou calcul** | Calcul pur pour le café (nombres fictifs, choisis pour être suivis de tête), puis données réelles pour l'application : distribution des salaires d'un institut statistique, source, période et licence notées dans la fiche. |
| **Exercice** | Calculer moyenne et médiane de 7 salaires donnés, puis après l'arrivée d'un salaire de 20 000 €. Pause de 5 s. |
| **Preuve d'apprentissage** | Transfert : « le prix moyen d'une maison dans un village où se trouve un château » (même raisonnement, autre contexte). Diagnostic d'erreur : « le salaire moyen a augmenté, donc la plupart des salariés gagnent plus » : pourquoi est-ce faux ? |
| **Durée et format** | 5 à 7 min, EDUCATIONAL vertical. Un SHORT d'accroche (le café) en dérivé. |
| **Adaptation EN** | Mêmes nombres. Exemple réel tiré de l'ONS ou du BLS au lieu de l'Insee. Formulation propre, sans calque. |
| **Contrôle** | Un débutant peut-il réexpliquer pourquoi la moyenne dépasse la médiane ? Les nombres sont-ils lisibles sur mobile ? La source est-elle datée ? |

</div>

## 6.4 Du programme à la vidéo : le circuit d'une fiche

1. **Programme** : la vidéo existe dans ce document, avec son identifiant et ses prérequis.
2. **Fiche de conception** : remplie par l'éditorial (ChatGPT). Statut « brouillon ».
3. **Revue croisée** : Claude vérifie la cohérence pédagogique, les prérequis et la faisabilité à l'écran. ChatGPT vérifie l'exactitude et la langue. JG tranche en cas de désaccord.
4. **Fiche de production YAML** : scènes, voix off FR et EN, bloc `verifier`. Le moteur refuse une fiche incomplète.
5. **Rendu et contrôle qualité** : `python production/produire.py <fiche>`, rapport qualité, revue image par image.
6. **Validation** : JG valide, la vidéo entre dans le stock. **Elle n'est pas publiée** tant que le seuil de lancement n'est pas atteint.
