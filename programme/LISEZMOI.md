# Programme éditorial et pédagogique ACTU-BASICS

Réponse au ticket n° 10. Le livrable est le PDF
[`PROGRAMME_EDITORIAL_ACTU-BASICS_v1-12.pdf`](PROGRAMME_EDITORIAL_ACTU-BASICS_v1-12.pdf),
construit à partir des fichiers de ce dossier. **Statut : validé par JG le 2/11/2026 (PR #12). Les versions suivantes traitent les points laissés en suspens.**

## Contenu

| Chemin | Rôle |
|---|---|
| `REVISION-1.13.md` | Révision 1.13 (proposition) : les 320 entrées regroupées en 89 épisodes longs |
| `catalogue/episodes.txt` | Les épisodes longs : chaque entrée du catalogue y figure une fois, comme chapitre |
| `episodes.py` | Contrôle les épisodes (couverture, ordre des prérequis, durées) et produit leur tableau |
| `catalogue/*.txt` | Les entrées de syllabus (leur nombre est calculé à chaque construction) du programme, rangées en modules : une entrée par vidéo (pas encore la fiche de conception) |
| `sections/*.md` | Les sections rédigées du document (synthèse, architecture, méthode d'actualité, feuille de route, glossaire, bibliographie, arbitrages) |
| `construire.py` | Contrôle le programme et construit le HTML, puis le PDF |
| `gabarit.html` | Mise en page (couleurs et logo officiels de `assets/brand/actu-basics/`) |
| `imprimer_pdf.js` | Impression PDF par le Chromium de Playwright |
| `../modeles/fiche-conception-episode.yaml` | Modèle vierge de fiche de conception d'un épisode |

## Format du catalogue

Une ligne `clé: valeur` par champ. `# MODULE X` ouvre un module, `## X.nn` ouvre une vidéo.
Les listes sont séparées par ` | `. `pre` liste les prérequis (identifiants de vidéos),
`renvoi` (pilier 3) liste les leçons « pour aller plus loin », qui ne sont pas des prérequis.
Aucune vidéo n'est marquée optionnelle (décision de JG : tout est proposé, le spectateur choisit) ; le champ `option` est refusé par le script. `correction` (facultatif) donne la correction détaillée d'un exercice chiffré. `duree` est en minutes (`5-7`).
`format` vaut `short`, `educational` ou `youtube_lesson`, comme dans le moteur.

## Contrôles (bloquants)

Identifiants uniques, champs obligatoires, prérequis existants, absence de cycle, aucun prérequis
placé plus loin dans le tronc commun ni à un niveau plus élevé, durée compatible avec le format,
et recalcul des réponses chiffrées (liste `VERIFICATIONS` de `construire.py`) avec l'évaluateur du moteur.

## Reconstruire

```
pip install -r programme/requirements.txt
python programme/construire.py          # contrôles + HTML (programme/sortie/)
python programme/construire.py --pdf    # + PDF (Node et Playwright requis)
cp programme/sortie/PROGRAMME_EDITORIAL_ACTU-BASICS_v1-12.pdf programme/
```
