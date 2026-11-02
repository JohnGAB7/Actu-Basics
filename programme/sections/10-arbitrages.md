# 10. Arbitrages demandés {#arbitrages}

Les décisions éditoriales appartiennent à ChatGPT, et JG arbitre. Cette section distingue ce que JG a **déjà décidé**, et que le programme applique, de ce qui reste **à décider**.

## 10.1 Décisions déjà prises par JG, appliquées telles quelles

| Décision | Source |
|---|---|
| Aucune publication sur les réseaux avant d'avoir un catalogue suffisant | Ticket n° 10 |
| Validation humaine explicite avant toute publication | Journal des décisions, LMEC-DEC-003 ; constitution éditoriale, section 9 |
| La durée d'une vidéo découle de l'objectif pédagogique, jamais d'un plafond arbitraire | Constitution éditoriale, section 10 ; ticket n° 10 |
| Trois piliers : statistiques de A à Z, économétrie, phénomènes du quotidien et actualité | Ticket n° 10 |
| Éditions FR et EN autonomes, sans traduction mécanique | Identité de marque ; ticket n° 10 |
| Rôles : Claude structure, ChatGPT relit, JG valide le PDF final | Ticket n° 10 ; LMEC-DEC-002 |
| Marque ACTU-BASICS, slogans « Éveiller par les chiffres. » et “Enlightening through numbers.” | Identité de marque |

## 10.2 Recommandations à valider

Claude fait une recommandation pour chacune, sans la considérer comme acquise. Les points **A1 à A3** touchent des décisions déjà écrites dans le dépôt : ils sont signalés comme tels.

| N° | Question | Options | Recommandation de Claude (statut : à valider) |
|---|---|---|---|
| **A1** *(touche une décision existante)* | Faut-il adopter les trois piliers comme structure de référence, à la place des quatre familles d'`ARCHITECTURE_EDITORIALE.md` ? | (a) Trois piliers au-dessus des familles, sans changer le moteur · (b) Remplacer les familles par les piliers dans le moteur · (c) Garder les quatre familles seules | **(a)**. Les familles restent un champ technique ; on ajoute seulement une famille `econometrie` si JG veut l'identifier à part dans les métadonnées. |
| **A2** *(touche une décision existante)* | La règle du stock préalable est déjà décidée par JG (10.1). Reste à mettre à jour la section 5 d'`ARCHITECTURE_EDITORIALE.md`, qui proposait un rythme dès le lancement. | (a) Mettre le document à jour après validation de ce programme · (b) Le laisser en l'état, avec un renvoi | **(a)**. |
| **A3** *(touche une décision existante)* | La répartition thématique de la constitution éditoriale (démographie 20 %, etc.) s'applique-t-elle au cursus ou seulement à l'actualité ? | (a) Actualité seulement · (b) Tout le catalogue | **(a)**. Un cursus suit l'ordre des notions, pas des quotas de thèmes. |
| **A4** | Seuil de lancement | (a) Vague 1 et 12 semaines de stock, en épisodes maîtres prêts à publier (section 7.2) · (b) Vagues 1 et 2 complètes · (c) Autre | **(a)**, à recalculer après la phase pilote, quand le temps humain par vidéo sera mesuré. |
| **A5** | Place de l'économétrie au lancement | (a) Peu de théorie (E1), beaucoup de sujets économiques du quotidien · (b) Avancer E2 à E4 en simplifiant | **(a)**. Avancer la théorie obligerait à enseigner la régression sans ses prérequis. |
| **A6** | Vidéos d'actualité avant le lancement | (a) Produites seulement en phase 3, 4 à 6 vidéos · (b) Produites dès maintenant | **(a)**. Une vidéo d'actualité produite des mois avant sa publication sera périmée. |
| **A7** | Format des leçons longues | (a) YOUTUBE_LESSON 16:9 pour les vidéos de plus de 10 min · (b) Tout en vertical, découpé en épisodes | **(a)**, après un essai sur une vraie leçon (S9.01, par exemple). Le découpage reste possible si l'essai déçoit. |
| **A8** | Place de la statistique bayésienne | (a) Bayes dès le niveau 2 (S4.10), méthode bayésienne en branche S12 · (b) Bayésien intégré dès le niveau 3, en parallèle du fréquentiste | **(a)**. Cela reste simple pour le débutant, et la comparaison des deux approches (S12.06) garde l'équilibre. |
| **A9** | Code à l'écran | (a) Pas de code dans les vidéos, scripts Python et R fournis en description · (b) Python montré à l'écran à partir du niveau 3 · (c) Aucun code | **(a)** au lancement. La chaîne enseigne le raisonnement, pas la programmation. |
| **A10** | La vidéo de lancement (paradoxe des anniversaires) | (a) Elle compte comme S4.06 dans le stock · (b) S4.06 est refaite en leçon, et la vidéo de lancement garde son rôle de présentation | **(a)**. Elle remplit déjà les objectifs de S4.06. Elle utilise le complément, enseigné en S4.05 : il faudra veiller à ce que S4.05 soit produite avant sa publication. |

## 10.3 Points de vigilance pour la suite de la revue

La revue indépendante annoncée dans le ticket est la prochaine étape. Pour la faciliter, voici les points où Claude est le moins sûr de ses choix :

1. **Granularité du niveau 1** : 30 vidéos avant les probabilités formelles. La version 1.1 ajoute un premier contact intuitif avec le hasard (S1.11). Est-ce suffisant ?
2. **Ordre S6 et S7** : la marge d'erreur (S6.05) arrive avant l'intervalle de confiance formel (S7.06), pour répondre tôt à une question d'actualité. C'est un choix pédagogique discutable.
3. **Méthodes non paramétriques (S11.04)** : placées avec les méthodes computationnelles plutôt qu'avec les tests.
4. **Exemples historiques** : ils ont maintenant une référence primaire ou universitaire (section 9.5). L'anecdote du casino de Monte-Carlo en 1913, mal documentée, a été remplacée par une simulation. Les références doivent encore être relues dans le texte avant chaque script.
5. **Titres anglais** : titres de travail, à revoir par un regard éditorial anglophone.
6. **Références bibliographiques** : les ressources en ligne ont été vérifiées (section 9). Les éditions des livres imprimés restent à confirmer.
7. **GAISE** : le cadrage de ChatGPT parle d'une révision 2025/2026. Le site de l'ASA, consulté le 2 novembre 2026, présente toujours la version révisée de **2016** comme la version en vigueur et n'annonce pas de nouvelle révision. Le programme cite donc la version de 2016. Merci de confirmer ou de fournir la source de la révision évoquée.
