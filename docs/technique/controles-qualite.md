# Contrôles qualité avant publication

Trois niveaux, toujours séparés dans `rapport-qc.md` :

- **❌ Bloquant** : le mode final refuse de produire ; en aperçu, les fichiers portent le filigrane.
- **⚠️ Avertissement** : à regarder, n'empêche pas la production.
- **Contrôles humains** : ce que la machine ne sait pas vérifier.

> **Validation structurelle ≠ vérification factuelle.** La machine vérifie que la fiche est complète, bien formée et cohérente avec elle-même. Elle ne vérifie **jamais** qu'un chiffre est vrai, qu'une source dit bien ce qu'on lui fait dire, ou qu'il n'existe pas de donnée plus récente. Cette vérification est humaine (section 1 du rapport).

## 1. Fiche : structure (bloque avant tout rendu)

Champs obligatoires présents **et réellement renseignés**. Une valeur laissée du modèle comme `https://`, `AAAA-MM-JJ` ou une chaîne vide compte comme absente. Le chiffre clé et les points du graphique doivent être des nombres, les types de scènes doivent être connus, aucun texte de scène ne peut être vide, le statut doit être `brouillon` ou `valide`, et les éditions FR et EN doivent toutes deux exister.

**Types et structure.** Chaque bloc est contrôlé : un bloc attendu (`validation`, `chiffre_cle`, `editions.fr`…) écrit comme un simple texte, une liste à la place d'un texte, un texte à la place d'une liste (`hashtags`, `sources`, `scenes`, `points`), une langue inconnue dans `{fr: …, en: …}`, un `oui` à la place de `true`, une durée écrite « 3 s »… Tout cela produit une **liste d'erreurs en français** qui nomme le champ, jamais une trace d'erreur Python. Un YAML illisible indique la ligne et la colonne. En dernier recours, un cas imprévu est rapporté comme « Structure inattendue » ; une erreur du programme lui-même est rapportée comme « erreur inattendue du programme », sans arrêter les autres fiches. Un test automatique remplace chaque champ de la fiche réelle par 13 valeurs de types différents (environ 1 600 variantes) et vérifie qu'aucune ne fait planter le programme.

## 2. Fiche : contrôles automatiques

| Contrôle | Gravité |
|---|---|
| Statut `valide` sans `valide_par` | ❌ |
| Statut `valide` sans date, date illisible ou dans le futur | ❌ |
| Statut `brouillon` (aucun rendu final possible) | ❌ |
| Statut `brouillon` mais `valide_par` ou `date` rempli | ⚠️ |
| Source consultée après la date de validation | ⚠️ |
| URL de source mal formée | ❌ |
| Date de consultation illisible ou dans le futur | ❌ |
| Date de consultation absente, ou de plus d'un an | ⚠️ |
| Scène `accroche`, `chiffre`, `source` ou `fin` absente (par langue) | ❌ |
| Vidéo qui ne commence pas par l'accroche / ne finit pas par la fin | ⚠️ |
| Marqueur « TODO », « à compléter », « XXX »… | ❌ |
| Astérisques dans le titre ou la légende ; astérisque non fermé | ❌ |
| Hashtag avec espace | ❌ |
| Légende < 40 caractères ; aucun hashtag | ⚠️ |
| Unité, préfixe, suffixe ou contexte renseigné dans une seule langue | ❌ |
| Unité du chiffre clé de nature ou d'échelle différente entre FR et EN (« milliards » / « million », « % » d'un seul côté) | ❌ |
| Unité du graphique de nature ou d'échelle différente entre FR et EN | ❌ |
| Chiffre clé ≠ point mis en avant du graphique, **après conversion d'échelle** (1 234 567 = 1,2 million) | ⚠️ |
| Chiffre clé absent du graphique ; plusieurs points mis en avant | ⚠️ |
| Chiffre clé et graphique de natures différentes (pourcentage contre valeur) | ⚠️ |
| Pourcentage hors de 0–100 (chiffre clé ou graphique) | ⚠️ |
| Valeur plus précise que les décimales affichées (arrondi visible) | ⚠️ |
| Période : années différentes entre FR et EN | ❌ |
| Période sans aucune année (contrôle des années impossible) | ⚠️ |
| Année citée avec le chiffre clé (unité, scène « chiffre ») hors de la période | ⚠️ |
| Libellé du graphique : années différentes entre FR et EN | ❌ |
| Libellé du graphique : année hors de la période annoncée | ⚠️ |
| Nombres différents entre les textes FR et EN | ⚠️ |
| « 8.2 » dans le texte FR ; « 8,2 » dans le texte EN | ⚠️ |
| Nombre de scènes différent entre FR et EN | ⚠️ |
| Identifiant ≠ nom du fichier | ⚠️ |
| Vidéo sans voix par choix éditorial (`narration: false`) | ⚠️ |

### Ce que les contrôles de cohérence ne prouvent pas

La machine compare des **nombres** et reconnaît les **mots d'échelle** (milliers, millions, milliards / thousand, million, billion, trillion, en tenant compte du faux ami « billion »), les pourcentages et les « pour mille ». Elle ne sait pas si deux nombres mesurent **la même grandeur** avec **la même définition**. Le rapport n'écrit donc « Chiffre clé égal au point mis en avant » que lorsque la comparaison a vraiment été faite, précise « après conversion d'échelle » ou « en supposant des unités simples » quand c'est le cas, et liste en tête de la section 1 les points qu'elle n'a pas pu vérifier (cases à cocher par une personne).

## 3. Rendus : contrôles automatiques

| Contrôle | Gravité |
|---|---|
| Voix impossible à produire (clé absente, quota, réseau, enregistrement manquant) | ❌ |
| Voix de test utilisée | ❌ |
| Durée imposée trop courte pour la voix (allongée automatiquement) | ⚠️ |
| Vidéo 1080×1920, H.264, piste audio présente | ❌ |
| Durée, légende, titre, hashtags **par plateforme** ([`plateformes.yaml`](../../production/plateformes.yaml)) | ❌ au-delà du maximum, ⚠️ hors fourchette conseillée |
| Zone de texte qui empiète sur l'interface d'une plateforme | ⚠️ |
| Texte qui ne tient pas dans sa zone malgré la réduction | ⚠️ |
| Texte principal < 34 px (illisible sur téléphone) | ⚠️ |
| Durées FR et EN très différentes (> 35 %), ou scène deux fois plus longue dans une langue | ⚠️ |

Les limites par plateforme se règlent dans `production/plateformes.yaml`, sans toucher au code. Chaque valeur y a une **référence** : lien vers la page officielle, date de lecture (`verifie_le`) et statut :

- `officiel` : écrit tel quel sur une page officielle (ex. YouTube : 3 minutes, titre 100 caractères, description 5 000) ;
- `non_confirme` : valeur courante qu'aucune page officielle lue ne confirme (ex. TikTok 10 minutes, Reels 3 minutes) ;
- `estimation` : choix technique sans source officielle (zones d'interface, durées conseillées).

Une erreur bloquante fondée sur une valeur qui n'est pas `officiel` le dit dans le rapport. Les références ont été lues le 1er novembre 2026 ; à revérifier au moins tous les 3 mois. Un test refuse toute limite sans référence ni date.

## 4. Contrôles humains

**Vérification factuelle** (section 1 du rapport)
- [ ] Chaque chiffre affiché **ou prononcé** retrouvé dans la source (valeur, unité, année).
- [ ] Période, périmètre et définition conformes.
- [ ] Pas d'édition plus récente de la source.
- [ ] La formulation ne déforme pas le chiffre.

**Visuel** : `inspection/planche-video.png`, `apercu-mobile.png`, `zones-*.png`
- [ ] Aucun texte coupé, chevauchant ou illisible ; lisible à taille réelle de téléphone.
- [ ] Rien d'important sous l'interface des applications.

**Audio et sous-titres** : la vidéo, son activé
- [ ] Prononciation des nombres, sigles, noms propres ; rythme ; volume.
- [ ] Sous-titres synchronisés, sans faute.

**Publication**
- [ ] Bon compte, bonne langue, légende complète.
- [ ] Mention « contenu généré par IA » activée si voix de synthèse.
- [ ] Après publication : fiche déplacée vers `contenus/publie/`.

## 5. En cas de problème

- Erreur de fond : ne pas corriger le chiffre soi-même dans la fiche ; renvoyer à la direction éditoriale.
- Texte trop long : raccourcir (décision éditoriale si le sens change).
- Panne : voir le [mode de secours](guide-quotidien.md#5-mode-de-secours).
