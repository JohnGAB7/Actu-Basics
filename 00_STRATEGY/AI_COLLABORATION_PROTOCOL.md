# Protocole de collaboration — ChatGPT, Claude et propriétaire

## Gouvernance
Le propriétaire du projet conserve la décision finale et valide les publications.

### ChatGPT — direction éditoriale
- stratégie de marque et priorités éditoriales ;
- sélection des sujets et angles ;
- recherche et vérification des faits ;
- scripts FR/EN et contrôle qualité ;
- analyse des performances et recommandations de croissance.

### Claude — direction technique et production
- architecture du dépôt et des systèmes ;
- développement, scripts et automatisations ;
- modèles de production et outils créatifs ;
- tests, documentation technique et maintenance.

### Propriétaire — arbitrage
- fixe les objectifs et priorités ;
- donne accès aux outils et comptes nécessaires ;
- valide les choix structurants et chaque publication ;
- surveille le budget et les risques.

## Source de vérité
Le dépôt GitHub JohnGAB7/le-monde-en-chiffres est l'espace de référence pour les documents, décisions, tâches et livrables. La branche principale est main.

## Workflow de travail
1. Créer une tâche avec un identifiant LMEC-AAAA-NNN.
2. Décrire le résultat attendu, le périmètre, les contraintes et les critères d'acceptation.
3. Attribuer un responsable principal.
4. Pour les changements techniques, travailler sur une branche dédiée et ouvrir une Pull Request vers main.
5. Faire relire les changements par l'autre assistant lorsque cela est pertinent.
6. Le propriétaire arbitre les désaccords et approuve l'intégration.
7. Documenter les décisions importantes dans DECISION_LOG.md.

## Règles de sécurité
- Aucun secret, jeton, mot de passe ou clé API dans Git.
- Utiliser des variables d'environnement et un fichier .env.example sans valeur secrète.
- Appliquer le moindre privilège aux accès.
- Vérifier les coûts, limites, permissions et conditions des API avant intégration.
- Prévoir journalisation, gestion des erreurs et solution manuelle.
- Ne pas prétendre qu'un assistant a effectué une action sans preuve dans le dépôt ou l'outil concerné.

## Limites opérationnelles
Les assistants ne travaillent pas automatiquement en arrière-plan l'un avec l'autre. Le propriétaire lance les tâches et partage les résultats ou autorise les accès nécessaires. Le dépôt et les Pull Requests assurent la coordination asynchrone.

## Définition de terminé
Une tâche est terminée lorsque les livrables existent, les critères d'acceptation sont vérifiés, les tests pertinents passent, la documentation est à jour et le propriétaire a accepté le résultat.
