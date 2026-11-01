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
| `etapes` | `texte` (titre), `etapes` (liste) | Lignes numérotées qui apparaissent quand la voix les annonce |
| `courbe` | `courbe` : `expression` + `variable` + `de` + `a` (calculée) ou `points`, `format_y: pourcent`, `axe_x`, `reperes` | Courbe tracée progressivement, repères annotés |
| `exercice` | `texte`, `pause` (s), `etiquette` | Badge « À VOUS », question, compte à rebours après la voix |
| `correction` | `reponse` et/ou `etapes` | Badge « CORRECTION », démarche, réponse surlignée |

**Synchronisation avec la voix** : si la voix off a une phrase de plus que d'étapes, la première phrase introduit et chaque phrase suivante fait apparaître une étape. Avec autant de phrases que d'étapes, chacune en fait apparaître une. Sinon, les étapes se répartissent sur les phrases.

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
| Exercice sans correction | ❌ |
| Formule illisible par le moteur | ❌ |
| Durée hors de la plage du format (SHORT 15–90 s, EDUCATIONAL 90–600 s, YOUTUBE_LESSON 300–3 600 s) | ⚠️ |
| Aucun nombre recalculé dans la fiche | ⚠️ |
| Formule trop petite sur mobile | ⚠️ |
| Nombres différents entre FR et EN | ⚠️ |
| Exactitude des définitions et des raisonnements | Humain |
| Fait extérieur cité sans source | Humain |

Les plafonds des plateformes (TikTok, Reels, Shorts) ne sont contrôlés que pour le format `short`.

## Format YOUTUBE_LESSON (16:9) : état actuel

Le moteur produit déjà le 16:9. Il reprend les mises en page verticales, adaptées à la largeur, avec des marges de confort (`zones_securite_lecon`) et le logo de fin (`logo.lecon`). Ce rendu est utilisable pour des essais. Avant le premier vrai cours, il manque une mise en page dédiée : deux colonnes texte et visuel, sommaire et chapitres YouTube, formules plus grandes, tableau de bord d'exercice.

## Habillage sonore (prototype)

`lmec/son.py` synthétise tout, sans fichier ni service extérieur :
- une **signature** de quatre notes de cloche ascendantes (la, do#, mi, la), deux notes au début et la signature complète sur le logo de fin ;
- une **nappe** : un accord tenu très bas, qui baisse encore quand la voix parle.

Les niveaux se règlent dans `charte.yaml`, section `son`. C'est un prototype : une identité sonore composée devra le remplacer avant publication.
