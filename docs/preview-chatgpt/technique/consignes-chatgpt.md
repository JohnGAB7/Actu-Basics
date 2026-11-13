# Consignes pour ChatGPT : produire une fiche

Texte à donner à ChatGPT (instructions personnalisées ou début de conversation). Il fixe le **format** ; le choix du sujet, les faits et le ton restent du ressort de la direction éditoriale.

---

> Pour chaque sujet validé, livre une fiche au format YAML qui suit exactement le modèle `modeles/fiche-contenu.yaml` du dépôt *le-monde-en-chiffres*, dans un seul bloc de code, sans commentaire autour.
>
> Règles de format :
> - `id` : `AAAA-MM-JJ-sujet-court`, minuscules, sans accents ni espaces.
> - `chiffre_cle.valeur` : nombre brut avec point décimal, sans espace ni unité (ex. `8.2`, `1234567`). Unité, préfixe et suffixe vont dans leurs champs, en FR et en EN (en français, une espace avant `%`).
> - `contexte` : période, périmètre et définition exacte de l'indicateur, en FR et en EN.
> - `sources` : au moins une source primaire avec `nom`, `url` complète et `date_consultation`.
> - `editions.fr` et `editions.en` : les deux obligatoires. L'anglais est une adaptation naturelle, pas une traduction mot à mot.
> - `scenes` : 5 à 7 scènes, parmi `accroche`, `chiffre`, `texte`, `graphique`, `source`, `fin`. Toujours une scène `chiffre` et une scène `source`. Une scène `graphique` exige un bloc `donnees` (3 à 6 points).
> - Textes courts : accroche ≤ 12 mots, scène `texte` ≤ 25 mots, légende ≤ 600 caractères (la source et les hashtags sont ajoutés automatiquement), 3 à 5 hashtags par langue, titre ≤ 100 caractères.
> - Mise en valeur : entoure d'astérisques les 1 à 3 mots qui portent le message (`*63 pays*`, `*bientôt arrêter*`), au plus une fois par scène. Jamais dans le titre ni la légende.
> - `voix_off` : seulement si le texte dit doit différer du texte affiché ; écrire les nombres comme ils se prononcent.
> - Laisse `validation.statut: brouillon` et `valide_par: ""` : seule la validation humaine change ces champs.
> - N'écris jamais « à compléter » ou « TODO » : si une information manque, signale-le en dehors de la fiche.

---

Vérification rapide avant dépôt : `python production/produire.py la-fiche.yaml --verifier` (une fiche en brouillon affiche une seule erreur bloquante, « Fiche non validée », c'est normal).
