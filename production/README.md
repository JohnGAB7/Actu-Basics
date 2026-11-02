# Production

Transforme une fiche de contenu (`contenus/fiches/*.yaml`) en fichiers prêts à publier, en français et en anglais.

```bash
pip install -r production/requirements.txt -r production/requirements-voix.txt   # + ffmpeg et la police Inter
python production/telecharger_voix.py
python production/produire.py contenus/exemples/exemple-fictif.yaml               # aperçu
python production/produire.py contenus/fiches/<fiche>.yaml --mode final           # fichiers à publier
```

Guide sans code : [`docs/technique/guide-quotidien.md`](../docs/technique/guide-quotidien.md).

Résultat dans `sortie/<id>/` :

```
rapport-qc.md                 contrôles automatiques + checklist humaine
fr/ et en/
  video.mp4                   1080×1920, H.264/AAC, 30 i/s, avec voix
  narration.wav               voix seule
  inspection/                 planche vidéo, aperçu mobile, zones des plateformes
  miniature.jpg               couverture, avec le logo
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
| `lmec/qc.py` | Contrôles qualité (bloquants, avertissements, contrôles humains) et rapport |
| `lmec/tts.py` | Fournisseurs de voix interchangeables, cache |
| `lmec/narration.py` | Phrases → voix → durées de scènes → piste audio et repères de sous-titres |
| `lmec/inspection.py` | Images d'inspection extraites de la vidéo encodée (dont `logo-mobile.png`) |
| `lmec/logo.py` | Logo officiel ACTU-BASICS : variante selon le fond, placement, contrôle de recouvrement ([guide](../docs/technique/logo-et-marque.md)) |
| `tts.yaml` / `plateformes.yaml` | Voix ; limites des plateformes avec leurs références officielles et dates de vérification (modifiables sans code) |
| `charte.yaml` | Couleurs, polices, formats, zones de sécurité (modifiable sans code) |

Documentation : [`docs/technique/`](../docs/technique/architecture.md).
