# Guide quotidien (objectif : 10 minutes)

## Routine normale

| Min. | Action |
|---|---|
| 2 | Récupérer la fiche YAML préparée par ChatGPT, la relire, mettre `statut: valide`, `valide_par` et la date. |
| 1 | Sur GitHub : `contenus/fiches/` → *Add file* → *Create new file* → nom `AAAA-MM-JJ-sujet.yaml` → coller → *Commit*. |
| 1 | Attendre le rendu (~1 à 2 min) : onglet *Actions* → dernière exécution → *Artifacts* → télécharger le zip. |
| 3 | Ouvrir `rapport-qc.md`, regarder `apercu-carrousel.png`, visionner `video.mp4` FR et EN, cocher la checklist. |
| 3 | Programmer : vidéo + `legende.txt` (FR puis EN) dans les outils natifs ; carrousel (images `carrousel/`) sur Instagram. Puis déplacer la fiche vers `contenus/publie/`. |

Astuce : le résumé de l'exécution GitHub Actions affiche directement le rapport qualité, sans rien télécharger.

## Modes de secours

**GitHub Actions indisponible** — en local, depuis le dossier du dépôt :

```bash
pip install -r production/requirements.txt     # une seule fois (et installer ffmpeg + police Inter)
python production/produire.py contenus/fiches/AAAA-MM-JJ-sujet.yaml
# résultats dans sortie/AAAA-MM-JJ-sujet/
```

Sans ffmpeg : ajouter `--sans-video` pour obtenir au moins les carrousels et les légendes.

**Script inutilisable** — mode entièrement manuel : la fiche contient tous les textes. Les recopier dans un modèle Canva ou CapCut aux mêmes formats (1080×1920 vidéo, 1080×1350 carrousel), en respectant la charte (`production/charte.yaml`) et en gardant la diapositive « source ». Les contrôles humains restent obligatoires.

**Plateforme ou outil de programmation en panne** — publier directement depuis l'application mobile au créneau prévu, ou décaler ; ne jamais publier une version non relue pour rattraper le retard.

## Commandes utiles

```bash
python production/produire.py FICHE --verifier              # structure seulement, rien n'est produit
python production/produire.py FICHE --brouillon-autorise    # aperçu filigrané d'une fiche non validée
python production/produire.py FICHE --langues fr            # une seule langue
python -m pytest production/tests -q                        # tests
```
