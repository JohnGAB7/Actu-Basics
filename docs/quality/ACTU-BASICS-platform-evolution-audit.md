# ACTU-BASICS — Audit initial et plan d'évolution

Date : 2026-11-18
Base de travail : `chatgpt/actu-basics-site-v1`
Branche d'évolution : `chatgpt/actu-basics-platform-evolution`

## Décisions de conception à préserver

- La version Claude publiée constitue la base fonctionnelle et éditoriale.
- Palette : ivoire, turquoise profond et or mat, définie dans `docs/assets/css/tokens.css`.
- Typographies : Source Serif 4 et Inter, déjà chargées par les pages.
- Architecture bilingue FR/EN.
- Les vidéos YouTube servent à découvrir les notions ; le site permet d'approfondir et de pratiquer.
- Ne pas fusionner dans `main` ni publier cette branche sans validation explicite.

## Constats techniques vérifiés lors de l'audit initial

1. Les pages chargent bien les feuilles `tokens.css`, `main.css`, puis `premium.css`. Le fichier premium réapplique Source Serif 4 et Inter et s'appuie largement sur les tokens.
2. `main.css` conserve néanmoins des déclarations historiques et des couleurs littérales. Il faut vérifier les collisions avec `premium.css` avant de refactorer : ne pas supprimer des règles simplement parce qu'elles paraissent anciennes.
3. Le HTML de la page d'accueil contient des URL canoniques et hreflang qui pointent encore vers `johngab7.github.io/le-monde-en-chiffres/`. C'est un risque SEO et de navigation après renommage/transfert du dépôt ; à confirmer par un audit exhaustif des pages et de la configuration Pages.
4. La bibliothèque contient des compteurs de leçons par module ; le programme affiche une trentaine de leçons livrées tandis que d'autres zones annoncent 45. Les compteurs éditoriaux doivent être générés depuis une source de vérité, mais les corriger manuellement partout serait fragile.
5. Le générateur `tools/build_lessons.py` est la source des pages de leçons et bibliothèques. Les améliorations structurelles doivent être apportées au générateur et aux fiches YAML, pas uniquement aux HTML générés.
6. Le test `tools/test_build_site.py` vérifie déjà plusieurs invariants (pages FR/EN, liens de bibliothèque, modules, hreflang, iframes). Le plan doit étendre cette couverture plutôt que créer un second système de tests.

## Plan d'exécution

### Phase 1 — Audit et fiabilisation V1
- Cartographier les pages, scripts, sources YAML, médias et liens internes FR/EN.
- Vérifier le contenu réel et la cohérence scientifique des graphiques, en commençant par la leçon « Le même chiffre, catastrophe ou détail ? Lire un graphique ».
- Vérifier formules, unités, axes, sources, légendes et accessibilité des graphiques.
- Vérifier vidéos, iframes, liens externes, navigation, métadonnées SEO et URL après renommage.
- Étendre les tests de génération et de liens ; produire un rapport de défauts classés par sévérité.

### Phase 2 — Expérience pédagogique
- Définir un modèle de leçon cohérent : question, objectifs, explication, exemple, visualisation, à retenir, exercice corrigé, suite du parcours.
- Introduire des interactions uniquement lorsqu'elles améliorent la compréhension.
- Améliorer les liens entre prérequis, leçons suivantes et parcours.
- Ajouter recherche et filtres robustes à la bibliothèque.

### Phase 3 — Bilinguisme, accessibilité et performance
- Contrôler les paires FR/EN et les liens de changement de langue vers la page équivalente.
- Tester responsive, clavier, contrastes, alternatives textuelles, réduction des animations.
- Mesurer les performances et limiter les dépendances inutiles sans modifier arbitrairement les polices approuvées.
- Automatiser les contrôles dans CI.

### Phase 4 — Préparation à la croissance
- Corriger canonical, hreflang, sitemap, robots et métadonnées de partage.
- Préparer le futur domaine personnalisé sans l'activer.
- Documenter la publication et la procédure de mise à jour.
- Évaluer plus tard un espace de progression, sans introduire prématurément de compte utilisateur ou backend.

## Règles de qualité

- Pas de chiffres, graphiques ou sources inventés.
- Toute correction de fond doit rester traçable à une fiche ou une source.
- Préserver les pages générées et modifier leur source de génération.
- Tester chaque lot avant d'ouvrir une PR.
- Aucun déploiement ni fusion dans `main` sans accord explicite.
