# 10. Arbitrages demandés {#arbitrages}

Les décisions éditoriales appartiennent à ChatGPT, et JG arbitre. Claude fait une recommandation pour chacune, sans la considérer comme acquise. Les points **A1 à A3** touchent des décisions déjà écrites dans le dépôt : ils sont signalés comme tels.

| N° | Question | Options | Recommandation de Claude |
|---|---|---|---|
| **A1** *(touche une décision existante)* | Faut-il adopter les trois piliers comme structure de référence, à la place des quatre familles d'`ARCHITECTURE_EDITORIALE.md` ? | (a) Trois piliers au-dessus des familles, sans changer le moteur · (b) Remplacer les familles par les piliers dans le moteur · (c) Garder les quatre familles seules | **(a)**. Les familles restent un champ technique ; on ajoute seulement une famille `econometrie` si JG veut l'identifier à part dans les métadonnées. |
| **A2** *(touche une décision existante)* | Le rythme de publication de lancement (section 5 d'`ARCHITECTURE_EDITORIALE.md`) est-il remplacé par la règle du stock préalable ? | (a) Oui, le document est mis à jour après validation · (b) Les deux coexistent | **(a)**, conformément au ticket n° 10. |
| **A3** *(touche une décision existante)* | La répartition thématique de la constitution éditoriale (démographie 20 %, etc.) s'applique-t-elle au cursus ou seulement à l'actualité ? | (a) Actualité seulement · (b) Tout le catalogue | **(a)**. Un cursus suit l'ordre des notions, pas des quotas de thèmes. |
| **A4** | Seuil de lancement | (a) Vague 1 et 12 semaines de stock · (b) Vagues 1 et 2 complètes · (c) Autre | **(a)**, à confirmer après la phase pilote, quand le temps réel par vidéo sera connu. |
| **A5** | Place de l'économétrie au lancement | (a) Peu de théorie (E1), beaucoup de sujets économiques du quotidien · (b) Avancer E2 à E4 en simplifiant | **(a)**. Avancer la théorie obligerait à enseigner la régression sans ses prérequis. |
| **A6** | Vidéos d'actualité avant le lancement | (a) Produites seulement en phase 3, 4 à 6 vidéos · (b) Produites dès maintenant | **(a)**. Une vidéo d'actualité produite des mois avant sa publication sera périmée. |
| **A7** | Format des leçons longues | (a) YOUTUBE_LESSON 16:9 pour les vidéos de plus de 10 min · (b) Tout en vertical, découpé en épisodes | **(a)**, après un essai sur une vraie leçon (S9.01, par exemple). Le découpage reste possible si l'essai déçoit. |
| **A8** | Place de la statistique bayésienne | (a) Bayes dès le niveau 2 (S4.10), méthode bayésienne en branche S12 · (b) Bayésien intégré dès le niveau 3, en parallèle du fréquentiste | **(a)**. Cela reste simple pour le débutant, et la comparaison des deux approches (S12.06) garde l'équilibre. |
| **A9** | Code à l'écran | (a) Pas de code dans les vidéos, scripts Python et R fournis en description · (b) Python montré à l'écran à partir du niveau 3 · (c) Aucun code | **(a)** au lancement. La chaîne enseigne le raisonnement, pas la programmation. |
| **A10** | La vidéo de lancement (paradoxe des anniversaires) | (a) Elle compte comme S4.06 dans le stock · (b) S4.06 est refaite en leçon, et la vidéo de lancement garde son rôle de présentation | **(a)**. Elle remplit déjà les objectifs de S4.06. Elle utilise le complément, enseigné en S4.05 : il faudra veiller à ce que S4.05 soit produite avant sa publication. |

## Points de vigilance pour la revue de ChatGPT

La revue indépendante annoncée dans le ticket est la prochaine étape. Pour la faciliter, voici les points où Claude est le moins sûr de ses choix :

1. **Granularité du niveau 1** : 29 vidéos avant les probabilités. Est-ce trop long pour un public débutant, ou faut-il intercaler des probabilités plus tôt ?
2. **Ordre S6 et S7** : la marge d'erreur (S6.05) arrive avant l'intervalle de confiance formel (S7.06), pour répondre tôt à une question d'actualité. C'est un choix pédagogique discutable.
3. **Méthodes non paramétriques (S11.04)** : placées avec les méthodes computationnelles plutôt qu'avec les tests.
4. **Exemples historiques** (Literary Digest, Monte-Carlo 1913, Wald, Bortkiewicz) : tous signalés « à vérifier », car ils circulent souvent sous une forme simplifiée.
5. **Titres anglais** : titres de travail, à revoir par un regard éditorial anglophone.
6. **Références bibliographiques** : éditions à vérifier (section 9).
