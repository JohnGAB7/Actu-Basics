# Contrôles qualité avant publication

Trois niveaux, toujours séparés dans `rapport-qc.md` :

- **❌ Bloquant** : le mode final refuse de produire ; en aperçu, les fichiers portent le filigrane.
- **⚠️ Avertissement** : à regarder, n'empêche pas la production.
- **Contrôles humains** : ce que la machine ne sait pas vérifier.

> **Validation structurelle ≠ vérification factuelle.** La machine vérifie que la fiche est complète, bien formée et cohérente avec elle-même. Elle ne vérifie **jamais** qu'un chiffre est vrai, qu'une source dit bien ce qu'on lui fait dire, ou qu'il n'existe pas de donnée plus récente. Cette vérification est humaine (section 1 du rapport).

## 1. Fiche : structure (bloque avant tout rendu)

Champs obligatoires présents **et réellement renseignés**. Une valeur laissée du modèle comme `https://`, `AAAA-MM-JJ` ou une chaîne vide compte comme absente. Le chiffre clé et les points du graphique doivent être des nombres, les types de scènes doivent être connus, aucun texte de scène ne peut être vide, le statut doit être `brouillon` ou `valide`, et les éditions FR et EN doivent toutes deux exister.

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
| Point mis en avant du graphique ≠ chiffre clé ; chiffre clé absent du graphique | ⚠️ |
| Année d'un libellé du graphique hors de la période annoncée | ⚠️ |
| Nombres différents entre les textes FR et EN | ⚠️ |
| « 8.2 » dans le texte FR ; « 8,2 » dans le texte EN | ⚠️ |
| Nombre de scènes différent entre FR et EN | ⚠️ |
| Identifiant ≠ nom du fichier | ⚠️ |
| Vidéo sans voix par choix éditorial (`narration: false`) | ⚠️ |

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

Les limites par plateforme se règlent dans `production/plateformes.yaml`, sans toucher au code. Elles ont été relevées en novembre 2026 et sont à revérifier régulièrement.

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
