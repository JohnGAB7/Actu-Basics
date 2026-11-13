# Architecture cible du site ACTU-BASICS

**Statut :** document de conception initial — à confronter à l'implémentation et à enrichir au fil des lots.  
**Branche de référence :** `chatgpt/actu-basics-site-v1`  
**Branche de travail :** `chatgpt/actu-basics-site-completion-architecture`

## 1. Objectif

Achever l'architecture fonctionnelle du site avant d'alimenter régulièrement le catalogue en vidéos, leçons, parcours et ressources.

Une fois cette architecture en place, l'ajout d'un nouveau contenu doit principalement consister à :
1. ajouter ou mettre à jour sa fiche structurée ;
2. déposer ou référencer ses médias et ressources ;
3. valider les relations et les contrôles ;
4. reconstruire le site.

Il ne doit plus être nécessaire de créer manuellement une page HTML, modifier les cartes de bibliothèque ou réécrire une page de parcours pour chaque nouvel épisode.

## 2. Principes non négociables

- **Une source de vérité structurée :** les fiches, le programme et les métadonnées des médias sont des données versionnées ; le HTML publié est un résultat généré.
- **Identifiants stables :** chaque unité du programme, leçon, vidéo et ressource possède un identifiant durable.
- **Séparation des objets :** une unité du programme n'est pas nécessairement une leçon déjà produite ; une leçon peut exister sans vidéo publiée ; une vidéo peut avoir plusieurs formats et éditions linguistiques.
- **Bilinguisme natif :** FR et EN sont des éditions reliées du même objet, avec des URL canoniques et des liens de langue réciproques.
- **Disponibilité explicite :** prévu, en préparation, validé, disponible et publié ne sont pas des synonymes. La validation pédagogique d'une fiche ne prouve pas qu'une vidéo est en ligne.
- **Pas de liens inventés :** une vidéo, un téléchargement ou une source externe n'est affiché que si sa référence a été fournie et vérifiée.
- **Progression cohérente :** les prérequis et l'ordre du programme restent la référence ; les recommandations « pour aller plus loin » ne deviennent pas artificiellement des prérequis.
- **Accessibilité et mobile dès la conception :** navigation clavier, contrastes, structure des titres, libellés, sous-titres et affichage mobile font partie des critères de livraison.
- **Publication contrôlée :** aucune fusion dans `main` ni modification de la configuration GitHub Pages sans accord explicite.

## 3. Périmètre fonctionnel du site

### Navigation principale

1. **Accueil** — promesse, portes d'entrée, nouveautés réellement disponibles et orientation vers les deux missions du média.
2. **Apprendre** — entrée vers les parcours, le programme et la bibliothèque des leçons.
3. **Comprendre le monde** — contenus d'actualité et dossiers fondés sur des chiffres, lorsque ces contenus sont publiés sur le site.
4. **À propos** — mission, méthode, principes éditoriaux, contact et informations légales.

Les intitulés définitifs pourront être ajustés au moment de l'intégration visuelle, sans modifier le modèle de données.

### Pages et vues à prévoir

- Accueil FR et EN.
- Vue d'ensemble des parcours et page individuelle de chaque parcours.
- Vue d'ensemble du programme : piliers, niveaux, modules et unités.
- Bibliothèque de leçons avec recherche, filtres et états de disponibilité.
- Page individuelle d'une leçon.
- Bibliothèque vidéo et page individuelle d'un épisode lorsque cela apporte une vraie valeur de navigation.
- Dossiers et contenus d'actualité, reliés aux notions pédagogiques correspondantes.
- Pages À propos, méthode éditoriale et mentions légales.
- Pages de recherche et états vides explicites.

## 4. Modèle de données cible

Les objets suivants doivent être distingués, même si leur stockage initial reste dans des fichiers YAML ou JSON.

### 4.1 Unité de programme

Représente une entrée du syllabus, qu'elle soit déjà produite ou non.

Champs conceptuels :
- identifiant et code du programme ;
- pilier, niveau, module, ordre ;
- titre FR et EN ;
- question de départ, objectifs et durée indicative ;
- prérequis ;
- renvois complémentaires ;
- format éditorial prévu ;
- état de production.

Le programme éditorial existant — trois piliers, quatre niveaux et ses unités reliées par prérequis — reste la référence de progression. Le site doit le rendre consultable sans confondre unités prévues et leçons disponibles.

### 4.2 Contenu pédagogique ou éditorial

Représente la matière d'une leçon, d'une capsule ou d'un dossier.

Champs conceptuels :
- identifiant stable et type de contenu ;
- code de programme associé, s'il existe ;
- famille éditoriale ;
- éditions FR et EN ;
- objectifs, niveau, prérequis et hypothèses ;
- scènes structurées : texte, formule, graphique, étapes, animation, exercice, correction ;
- sources et vérifications ;
- état de validation éditoriale et pédagogique.

Les fiches YAML existantes restent la base de départ. Leur schéma sera étendu de manière rétrocompatible.

### 4.3 Média

Un contenu peut être associé à plusieurs médias, et chaque média peut exister dans plusieurs langues ou formats.

Champs conceptuels :
- identifiant du média et identifiant du contenu parent ;
- type : vidéo, audio, miniature, sous-titre, transcription, image ou animation ;
- langue ;
- format et ratio : vertical 9:16, horizontal 16:9, carrousel 4:5, etc. ;
- fournisseur et URL ou chemin de fichier ;
- durée, chapitres, date de publication ;
- état : absent, en production, contrôlé, publié ;
- droits et informations d'attribution lorsque nécessaires.

Une page de leçon peut donc être disponible avant sa vidéo ; le bloc vidéo apparaît automatiquement dès qu'un média publié et vérifié lui est associé.

### 4.4 Ressource pédagogique

Permet de rattacher à un contenu :
- PDF, fiche récapitulative ou support de cours ;
- jeu de données ;
- notebook, script ou exemple de code ;
- exercice complémentaire ;
- bibliographie et liens de référence.

Chaque ressource possède un titre, une description, une langue, un type, une URL ou un chemin vérifié et un état de disponibilité.

### 4.5 Parcours

Un parcours est une sélection ordonnée ou conditionnelle d'unités du programme et de contenus.

Champs conceptuels :
- identifiant, titre et description FR/EN ;
- public et niveau visés ;
- objectifs du parcours ;
- unités et contenus associés ;
- ordre recommandé ;
- prérequis ou embranchements ;
- état global et progression de disponibilité.

Le parcours est généré à partir de ses données ; il ne doit pas être une liste de liens HTML écrite à la main.

## 5. Expérience d'une page de leçon

Une page de leçon doit pouvoir accueillir, sans changement de structure :

1. titre, code, résumé et fil d'Ariane ;
2. objectifs, niveau, prérequis et hypothèses ;
3. vidéo principale si elle existe et est publiée ;
4. chapitres, transcription et sous-titres si disponibles ;
5. explication structurée et scènes pédagogiques ;
6. formules rendues lisiblement ;
7. graphiques et visualisations construits depuis les données de la fiche ;
8. exercices, pause de réflexion et correction ;
9. ressources téléchargeables ;
10. notions liées, prérequis, suite du parcours et retour au programme ;
11. bascule FR/EN vers l'équivalent exact.

Les blocs sans contenu vérifié sont masqués ou signalés comme non disponibles selon leur nature ; ils ne doivent jamais afficher de faux lecteur, de lien factice ou de placeholder technique destiné aux visiteurs.

## 6. Génération et chaîne de construction

La construction du site doit devenir un processus déterministe et contrôlé :

1. lire les fichiers du programme ;
2. lire les fiches de contenu validées et leurs éditions linguistiques ;
3. lire les métadonnées des médias et ressources ;
4. vérifier les identifiants, les langues, les prérequis et les références ;
5. relier unités du programme, contenus, médias, ressources et parcours ;
6. générer les pages individuelles et les vues catalogue ;
7. générer l'index de recherche, le sitemap et les métadonnées SEO ;
8. exécuter les tests de liens, de structure et de cohérence ;
9. publier uniquement le résultat validé sur la branche GitHub Pages configurée.

Une commande d'orchestration unique devra appeler les générateurs spécialisés existants plutôt que dupliquer leur logique.

## 7. Fonctionnalités transversales

- Recherche unifiée dans les titres, résumés, notions, codes et mots-clés.
- Filtres par pilier, niveau, module, langue, format et disponibilité.
- Liens croisés entre actualités, leçons, parcours et ressources.
- Navigation clavier, menu mobile robuste et repères de focus visibles.
- Rendu des formules et graphiques sans exposer de LaTeX brut ni de placeholders.
- Métadonnées SEO, canonical, hreflang, Open Graph et sitemap.
- Pages rapides, responsive et utilisables sans compte.
- Aucun compte utilisateur ni suivi individuel de progression dans le périmètre initial ; cette possibilité pourra être étudiée séparément si un besoin réel apparaît.

## 8. État actuel et écarts connus

À la date de ce document, la branche de publication contient :
- 38 fiches pédagogiques Niveau 1 valides ;
- 76 pages de leçons générées en FR et EN ;
- A0.01 conservée comme page manuelle ;
- 39 entrées dans chaque bibliothèque.

La PR #24 a intégré le lot 4 via le générateur. Le déploiement GitHub Pages associé a réussi.

Écarts à traiter :
- la page Parcours est encore statique et affiche un état antérieur au catalogue actuel ;
- la documentation `docs/SITE-README.md` décrit encore l'ajout manuel des pages ;
- le générateur de leçons ne construit pas encore le programme, les parcours, la bibliothèque vidéo ni les relations de ressources ;
- le rendu web des formules et des courbes doit être achevé ;
- les URL vidéo individuelles ne sont pas encore rattachées aux leçons dans le modèle du site ;
- les contrôles visuels, mobiles et clavier doivent être effectués sur le site rendu.

## 9. Ordre de réalisation recommandé

### Lot A — fondations et modèle
- formaliser les schémas de programme, contenu, média, ressource et parcours ;
- établir les identifiants et règles de liaison ;
- définir les états de disponibilité ;
- ajouter les validateurs et tests de données.

### Lot B — programme et parcours
- exploiter le syllabus existant comme source de progression ;
- générer les pages programme, modules et parcours ;
- relier automatiquement les leçons disponibles ;
- distinguer clairement les unités à venir des leçons consultables.

### Lot C — pages de contenu complètes
- unifier les gabarits FR/EN ;
- intégrer les médias et chapitres ;
- finaliser le rendu des formules, graphiques et animations ;
- intégrer exercices, corrections et ressources.

### Lot D — découverte et navigation
- recherche unifiée et filtres ;
- liens croisés et recommandations de suite ;
- mise à jour de l'accueil selon les contenus réellement disponibles ;
- bibliothèque vidéo et pages d'actualité si les données sont présentes.

### Lot E — qualité et livraison
- tests automatiques de génération et de liens ;
- contrôle des 2 langues et des métadonnées ;
- audit visuel desktop/mobile ;
- tests clavier et accessibilité ;
- mise à jour de la documentation ;
- revue finale avant toute fusion ou publication.

## 10. Critère de fin

L'architecture du site sera considérée comme achevée lorsque l'ajout d'une nouvelle unité, d'une nouvelle leçon, d'une vidéo ou d'un parcours pourra être réalisé par les données et les médias associés, sans modification manuelle des pages d'accueil, des bibliothèques, des pages de parcours ou des gabarits — sauf lorsqu'une nouvelle fonctionnalité réellement inédite est introduite.

La complétude de l'architecture ne signifie pas que les 320 unités, toutes les vidéos ou tous les parcours doivent déjà être produits. Le site doit pouvoir les accueillir proprement, afficher leur disponibilité réelle et se mettre à jour automatiquement au fur et à mesure.
