# Fiches pédagogiques et formats SHORT, EDUCATIONAL, YOUTUBE_LESSON

Vision éditoriale : [`00_STRATEGY/ARCHITECTURE_EDITORIALE.md`](../../00_STRATEGY/ARCHITECTURE_EDITORIALE.md). Modèle : [`modeles/fiche-pedagogique.yaml`](../../modeles/fiche-pedagogique.yaml). Exemple complet : la vidéo de lancement, [`contenus/fiches/2026-11-lancement-actu-basics.yaml`](../../contenus/fiches/2026-11-lancement-actu-basics.yaml).

L'architecture est inchangée : même commande (`python production/produire.py <fiche>`), même charte, mêmes voix, même rapport qualité. Une fiche sans `type_fiche` reste une fiche d'actualité et produit exactement les mêmes fichiers qu'avant.

## En-tête

| Champ | Valeurs | Effet |
|---|---|---|
| `type_fiche` | `actualite` (défaut), `pedagogique` | Structure et contrôles qualité |
| `famille` | `comprendre_le_monde`, `apprendre_les_statistiques`, `comprendre_les_probabilites`, `statistiques_en_pratique`, `presentation` | Classement, métadonnées |
| `format` | `short` (défaut), `educational`, `youtube_lesson` | `short` et `educational` : vertical 1080 × 1920 ; `youtube_lesson` : 16:9 1920 × 1080. Carrousel seulement en `short` |
| `habillage_sonore` | `true`, `false` (défaut) | Signature sonore et nappe sous la voix (`lmec/son.py`, réglages `charte.yaml` → `son`) |
| `pedagogie` | `niveau`, `objectifs` (FR, EN), `prerequis`, `hypotheses` | Obligatoire pour une fiche pédagogique |

Une fiche pédagogique n'a pas besoin de `chiffre_cle`, de `contexte` ni de `sources`, sauf si elle cite un fait extérieur.

## Scènes

Les scènes d'actualité restent disponibles (`accroche`, `chiffre`, `texte`, `graphique`, `source`, `fin`). Une scène `chiffre` peut porter sa propre `valeur`. Scènes propres aux fiches pédagogiques :

| Type | Champs | À l'écran |
|---|---|---|
| `titre` | `texte`, `numero` | Carte de chapitre |
| `formule` | `formule` (texte ou liste de lignes, notation LaTeX), `voix_off` obligatoire | Lignes de formule à la même taille, qui apparaissent une à une |
| `etapes` | `texte` (titre), `etapes` (liste), `disposition: liste` (défaut) ou `cartes` | Lignes numérotées qui apparaissent quand la voix les annonce ; `cartes` : cartes arrondies sur deux colonnes, utiles pour des notions distinctes (les quatre piliers de la conclusion) |
| `courbe` | `courbe` : `expression` + `variable` + `de` + `a` (calculée) ou `points`, `format_y: pourcent`, `axe_x`, `reperes`, `seuil` (ex. 0.9) | Courbe tracée progressivement ; chaque repère apparaît sur sa phrase de voix ; `seuil` trace une ligne pointillée ; au-delà de deux repères, les étiquettes passent dans une légende en haut à gauche |
| `exercice` | `texte`, `pause` (s), `etiquette` | Badge « À VOUS », question, compte à rebours après la voix |
| `correction` | `reponse` et/ou `etapes` | Badge « CORRECTION », démarche, réponse dans un encadré mesuré sur son texte |
| `animation` | `texte` (titre), `animation: {modele, n, phases, …}`, `etapes` (une légende par phase) | Animation découpée en **phases**, chacune calée sur une phrase de la voix, avec une seule légende à la fois en bas. Durée minimale 5 s |

Modèles d'animation et leurs phases :

| Modèle | Paramètres | Phases possibles | Ce qu'on voit |
|---|---|---|---|
| `foule` | `n` (≤ 60) | `apparition` | n silhouettes qui apparaissent |
| `paires` | `n` (≤ 60), `depuis` (facultatif) | `apparition`, `personne` (répétable), `vous`, `reste`, `total` | Personnes sur un cercle ; avec n ≤ 6, lettres A, B, C… et liste des paires à droite ; `personne` relie la personne suivante à toutes les autres (3 + 2 + 1) ; `vous` montre seulement vos 22 paires ; `total` colore toutes les paires |
| `doublon` | — | `aller`, `retour`, `fusion`, `legende` | A → B puis B → A, les deux flèches fusionnent : « A–B = B–A », d'où la division par 2 |
| `calendrier` | `n` (≤ 365), `jours` | `personne` (répétable), `reste` | Grille de 365 jours ; chaque personne prend un jour libre ; ligne « Tous différents : xx,x % » |
| `complement` | `valeur` (entre 0 et 1) | `gauche`, `droite`, `total` | Barre coupée en deux : P₀ et 1 − P₀, avec leurs pourcentages, puis une accolade sur l'ensemble |

Le contrôle refuse une animation dont le nombre de légendes (`etapes`) diffère du nombre de phases.

**Champ commun `note`** (toutes les scènes pédagogiques sauf `fin`) : une mention courte et discrète en bas de l'image, non lue par la voix, 140 caractères au plus. Usage : hypothèse de calcul (« 365 jours équiprobables »), détail d'un calcul (« 23 × 22 ÷ 2 = 253 »), ordre de grandeur. Elle allège l'écran principal sans perdre la rigueur.

**Réponse d'un test par un chiffre** : un exercice peut être résolu par une scène `chiffre` qui le suit, à condition qu'elle ait un bloc `verifier`. C'est le cas du test d'ouverture de la vidéo de lancement (réponse : 50,7 %).

**Synchronisation avec la voix** (étapes, phases d'animation, repères de courbe) : si la voix off a une phrase de plus que d'étapes, la première phrase introduit et chaque phrase suivante fait apparaître une étape. Avec autant de phrases que d'étapes, chacune en fait apparaître une. Sinon, les étapes se répartissent sur les phrases. Pour une correction avec `etapes` et `reponse`, la dernière phrase fait apparaître la réponse. **Règle d'écriture : une phrase d'introduction, puis une phrase par étape ou par phase.** Seuls « . ! ? … » comptent : un deux-points ou un point-virgule marque une courte pause sans faire apparaître d’étape.

**Formules** : notation LaTeX rendue par `mathtext` (matplotlib), sans installation de LaTeX : fractions, exposants, indices, `\sum`, `\binom`, `\approx`, lettres grecques, `\mathrm{…}`. En vertical, une formule longue doit être coupée en plusieurs lignes : le rapport signale une formule trop petite.

## Calculs vérifiés : `verifier`

Toute scène peut déclarer les nombres qu'elle annonce :

```yaml
verifier:
  - {expression: "100 * (1 - prod((365 - k) / 365 for k in range(23)))", attendu: 50.7, libelle: "P(23 personnes), en %"}
```

La machine recalcule l'expression. Si l'écart dépasse la tolérance, c'est **bloquant**. Par défaut, la tolérance vaut la moitié de la dernière décimale écrite : 0,05 pour 50,7. On peut aussi la fixer avec `tolerance`. Une courbe donnée par `expression` est elle aussi calculée, jamais recopiée à la main.

Expressions acceptées : nombres, `+ - * / // % **`, comparaisons, `sum`, `prod`, `range`, `comb`, `perm`, `factorial`, `sqrt`, `exp`, `log`, `log10`, `erf`, `min`, `max`, `abs`, `round`, `floor`, `ceil`, `int`, `pi`, `e`, et les générateurs (`… for k in range(n)`). Tout le reste est refusé : texte, attributs, modules, fichiers. Les calculs démesurés le sont aussi (`10**10**10`, `range` de plus d'un million de valeurs).

## Contrôles qualité propres aux fiches pédagogiques

| Contrôle | Gravité |
|---|---|
| Bloc `pedagogie` incomplet (niveau, objectifs FR et EN) | ❌ fiche refusée |
| Formule sans voix off | ❌ fiche refusée |
| Scène pédagogique dans une fiche d'actualité | ❌ fiche refusée |
| Nombre annoncé ≠ nombre recalculé | ❌ |
| Exercice sans correction (ni chiffre vérifié qui y répond) | ❌ |
| Formule illisible par le moteur | ❌ |
| Durée hors de la plage du format (SHORT 15–90 s, EDUCATIONAL 90–600 s, YOUTUBE_LESSON 300–3 600 s) | ⚠️ |
| Aucun nombre recalculé dans la fiche | ⚠️ |
| Formule trop petite sur mobile | ⚠️ |
| Nombres différents entre FR et EN | ⚠️ |
| Exactitude des définitions et des raisonnements | Humain |
| Fait extérieur cité sans source | Humain |

Les plafonds des plateformes (TikTok, Reels, Shorts) ne sont contrôlés que pour le format `short`.

## Format YOUTUBE_LESSON (16:9) : état actuel

Première mise en page dédiée (novembre 2026), **à ne pas considérer comme terminée** : elle passe les tests techniques mais n'a pas encore été jugée sur un vrai cours.
- **Deux colonnes** pour les scènes pédagogiques : titre à gauche (36 % de la largeur, centré verticalement, filet d'accent), visuel à droite (formule, courbe, animation, étapes, compte à rebours).
- **Cartes de chapitre** : grand numéro à gauche, titre à droite.
- **Corrections** sur une seule colonne centrée, car les étapes ont besoin de largeur.
- Marges de confort `zones_securite_lecon`, logo de fin `logo.lecon`.

Reste à faire avant le premier vrai cours : sommaire et chapitres YouTube (horodatage dans la description), écrans plus denses autorisés en 16:9 (un cours se regarde sur grand écran), relecture visuelle sur une leçon de 10 minutes au moins.

## Habillage sonore (prototype)

`lmec/son.py` synthétise tout, sans fichier ni service extérieur ni droits à payer :
- une **signature** de quatre notes de cloche ascendantes (la, do#, mi, la) : un souffle monte avant la dernière note, qui s'ouvre sur un accord tenu, avec une réverbération légère. Début de la signature à l'ouverture, signature complète sur le logo de fin ;
- une **nappe** : un accord tenu très bas, qui baisse encore quand la voix parle ;
- des **repères** : un tic discret à chaque seconde d'un compte à rebours, un carillon de deux notes quand un chiffre s'arrête ou qu'une réponse apparaît.

Les niveaux se règlent dans `charte.yaml`, section `son` (`signature_db`, `nappe_db`, `tic_db`, `revele_db`, `reperes: false` pour couper les repères). C'est un prototype : une identité sonore composée devra le remplacer avant publication.

Voix de la vidéo de lancement : voir [voix-video-lancement.md](voix-video-lancement.md).
