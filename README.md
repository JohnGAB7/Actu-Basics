# ACTU-BASICS

**Éveiller par les chiffres.** · **Enlightening through numbers.**

Média pédagogique bilingue (français et anglais) consacré aux statistiques, aux probabilités, à l'économétrie, à l'actuariat et à la lecture des chiffres de l'actualité. « Le Monde en chiffres / The World in Numbers » était le nom de travail du projet jusqu'au 1/11/2026.

## Ce que contient le dépôt

| Dossier | Rôle |
|---|---|
| `00_STRATEGY/` | Identité de marque, constitution éditoriale, architecture des cours, protocole de collaboration Claude / ChatGPT, monétisation |
| `programme/` | Programme éditorial et pédagogique (version 1.13 : 93 épisodes longs, 333 chapitres) ; `catalogue/` est la source de vérité, `construire.py` et `episodes.py` la contrôlent |
| `contenus/conception/` | Fiches de conception (avant script) : objectifs, notions utilisées, provenance de chaque chiffre, déroulé, exercices corrigés |
| `contenus/fiches/` | Fiches de production lues par le moteur (scènes, voix off FR et EN, calculs à vérifier) |
| `production/` | Moteur de rendu (Python, Pillow, ffmpeg) : vidéos verticales et 16:9, carrousels, contrôle qualité, voix de synthèse locale, laboratoires (`lmec/laboratoires.py`) |
| `docs/` | Site (GitHub Pages) et documentation technique (`docs/technique/`) |
| `docs/actuariat/` | Sources de référence du parcours Actuariat |
| `assets/brand/actu-basics/` | Logos officiels et règles d'usage : ne jamais les redessiner ni changer leurs couleurs |
| `modeles/` | Modèles de fiches (conception, production) |

## Principes

- Toute affirmation importante est vérifiable et sourcée ; période, périmètre et définition toujours précisés.
- Un apprenant ne doit jamais manquer d'une notion indispensable : chaque fiche liste les notions qu'elle utilise et dit où elles sont enseignées (règle de complétude).
- Les éditions française et anglaise sortent en même temps et sont adaptées, pas traduites mot à mot.
- Aucune publication automatique : JG valide chaque contenu avant publication.

## Installer et tester

```bash
pip install -r production/requirements.txt -r production/requirements-voix.txt pytest -c production/contraintes.txt
sudo apt-get install ffmpeg fonts-inter        # outils système
python -m pytest production/tests -q           # tests du moteur
python programme/episodes.py                   # contrôle des épisodes et des compteurs
python programme/construire.py                 # programme en HTML (ajouter --pdf pour le PDF)
```

Versions de référence : Python 3.12, ffmpeg d'Ubuntu (runner GitHub `ubuntu-latest`), police Inter, versions Python figées dans `production/contraintes.txt`.

## Produire une vidéo

1. Fiche de conception relue (Claude, ChatGPT) puis validée par JG.
2. Fiche de production : l'**aperçu** (workflow « Aperçu des contenus ») se lance à chaque pull request et accepte les brouillons.
3. **Validation finale** (workflow lancé à la main, depuis `main`) : elle attend l'approbation de l'environnement GitHub `production`, refuse toute fiche non validée ou toute erreur bloquante, puis écrit `sortie/manifeste.json` (commit, empreintes SHA-256 de la fiche, du moteur, des voix et des rapports QC, acteur du run).
4. Publication manuelle par JG. Les vidéos finales ne sont pas versionnées dans Git.

Détails : [`docs/technique/architecture.md`](docs/technique/architecture.md), [`docs/technique/guide-quotidien.md`](docs/technique/guide-quotidien.md), [`docs/technique/controles-qualite.md`](docs/technique/controles-qualite.md).

## Limites connues

- Le contrôle automatique ne remplace ni l'inspection complète des vidéos ni l'écoute humaine, ni un test auprès de débutants.
- Les licences des voix de synthèse (`docs/voice-licenses.md`) restent à confirmer fichier par fichier avant toute monétisation.
- Les laboratoires interactifs du site sont conçus, pas encore livrés.

Les décisions du projet sont consignées dans [`DECISION_LOG.md`](DECISION_LOG.md).
