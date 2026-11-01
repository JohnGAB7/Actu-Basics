# Production

Transforme une fiche de contenu (`contenus/fiches/*.yaml`) en fichiers prêts à publier, en français et en anglais.

```bash
pip install -r production/requirements.txt   # + ffmpeg et la police Inter installés sur la machine
python production/produire.py contenus/exemples/exemple-fictif.yaml --brouillon-autorise
```

Résultat dans `sortie/<id>/` :

```
rapport-qc.md                 contrôles automatiques + checklist humaine
fr/ et en/
  video.mp4                   1080×1920, H.264/AAC, 30 i/s
  miniature.jpg
  carrousel/01-….png …        1080×1350
  apercu-carrousel.png        toutes les diapositives sur une image
  sous-titres.srt
  legende.txt                 légende + source + hashtags, prête à coller
  script-voix-off.txt
  metadonnees.json            pour une future automatisation
```

| Module | Rôle |
|---|---|
| `lmec/fiche.py` | Chargement et validation structurelle de la fiche |
| `lmec/formatage.py` | Nombres et typographie FR/EN |
| `lmec/rendu.py` | Dessin des scènes (accroche, chiffre, texte, graphique, source, fin) |
| `lmec/carrousel.py` | Images du carrousel et planche d'aperçu |
| `lmec/video.py` | Durées, animation, encodage ffmpeg |
| `lmec/textes.py` | Sous-titres, script de voix off, légendes, métadonnées |
| `lmec/qc.py` | Contrôles qualité et rapport |
| `charte.yaml` | Couleurs, polices, formats, zones de sécurité (modifiable sans code) |

Documentation : [`docs/technique/`](../docs/technique/architecture.md).
