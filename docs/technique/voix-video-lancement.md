# Voix de la vidéo de lancement : étude (novembre 2026)

> Étude technique demandée par JG. Piper reste la voix des aperçus et **n'est pas la voix définitive** de la vidéo officielle. Aucune dépense n'est engagée ici. Le choix se fait à l'oreille et reste une décision de JG.

## Ce que la vidéo demande à la voix

La vidéo de lancement est un récit court, pas un journal. Elle pose une question, laisse un silence, surprend, puis explique. La voix doit donc :
- **changer de ton** : intrigue sur le test, surprise sur « plus d'une chance sur deux », calme sur la formule, complicité sur la conclusion ;
- **marquer les silences** : après une question, avant une révélation ;
- **dire les nombres clairement** (« cinquante virgule sept pour cent », « deux puissance cent vingt-huit »).

Piper lit correctement mais sur un ton égal. C'est sa limite principale pour cette vidéo, pas un défaut de réglage.

## Volume du texte

| | FR | EN |
|---|---|---|
| Caractères lus (voix off des 17 scènes) | ≈ 2 850 | ≈ 2 460 |
| Durée parlée (prototype Piper) | voir le rapport de rendu | voir le rapport de rendu |

## Ce qui a été amélioré dès maintenant, sans dépense

- **Silences selon la ponctuation** (`narration.py`) : 0,6 s après une question, 0,5 s après des points de suspension, 0,4 s après une exclamation, 0,32 s après un point, 0,12 s après un deux-points. Le spectateur a le temps de réfléchir à la question avant la suite.
- **Script réécrit pour l'oral** : phrases plus courtes, questions directes (« Gardez votre réponse en tête »), une idée par phrase.
- **Repères sonores** : un tic discret à chaque seconde des comptes à rebours, un carillon à chaque révélation. Ils portent une partie de l'émotion que la voix de synthèse ne porte pas.

## Les quatre options

| Option | Expressivité | Coût | Effort | Remarques |
|---|---|---|---|---|
| **1. Voix humaine enregistrée** (`--voix manuel`) | La meilleure : intention, sourire, silences | **0 €** | 17 prises par langue au téléphone, environ 30 min par langue avec les reprises | Déjà prise en charge. Les étapes apparaissent à intervalles réguliers (pas de temps par phrase connus), à vérifier à l'image. Il faut une voix anglaise native ou très à l'aise pour l'EN. |
| **2. Piper réglé** | Faible à moyenne | 0 € | Quelques minutes | `lenteur: 0.95`, `variation: 0.8` dans `tts.yaml` ; la comparaison des voix gratuites est dans [voix-off.md](voix-off.md). Utile pour les aperçus, pas pour le lancement. |
| **3. Synthèse locale récente et libre** | Moyenne à bonne (à écouter) | 0 € | Intégration d'un nouveau fournisseur, une demi-journée | À n'envisager qu'avec une licence qui autorise l'usage commercial. Plusieurs modèles connus l'interdisent : vérifier la licence du modèle **et** des voix avant tout essai. Non testé ici. |
| **4. Synthèse payante** (OpenAI, ElevenLabs, déjà intégrés) | Bonne à très bonne (réputation, non écoutée ici) | Quelques centimes à 1 $ pour cette vidéo avec OpenAI (≈ 5 300 caractères au total) ; abonnement mensuel pour ElevenLabs | Une clé dans les secrets GitHub, jamais dans le dépôt | OpenAI accepte des consignes de ton (`consignes` dans `tts.yaml`). **Dépense à décider par JG** ; tarifs à revérifier sur les pages officielles. |

## Recommandation

1. **Vidéo officielle de lancement : voix humaine enregistrée (option 1).** C'est gratuit, c'est la seule option qui porte vraiment la surprise et la complicité du script, et une voix humaine renforce la crédibilité d'un média qui se présente. Le moteur sait déjà l'assembler.
2. **Si aucun enregistrement n'est possible : essai OpenAI en aperçu (option 4)**, avec des consignes de ton par scène, après accord de JG sur la dépense. Coût estimé de l'essai : quelques centimes.
3. **Piper reste la voix des aperçus** et des tests automatiques.

## Comment enregistrer la vidéo de lancement (option 1)

1. Ouvrir `script-voix-off.txt` du rendu : une ligne par scène, `[01]` à `[17]`.
2. Enregistrer une prise par scène, dans une pièce calme, téléphone à 20 cm : `01.m4a`, `02.m4a`… Laisser une seconde de silence avant et après.
3. Indications de jeu :
   - scènes 2 et 9 (exercices) : poser la question, puis **se taire** ; le compte à rebours est ajouté par le moteur ;
   - scène 4 (50,7 %) : la surprise, sans exagérer ;
   - scène 7 (formule) : plus lent, pédagogique ;
   - scènes 12 à 14 (cryptographie) : concret, presque confidentiel ;
   - scène 16 : un sourire dans la voix.
4. Déposer les fichiers dans `audio/2026-11-lancement-actu-basics/fr/` (et `en/`), puis `python production/produire.py contenus/fiches/2026-11-lancement-actu-basics.yaml --voix manuel`.
5. Vérifier à l'image l'apparition des étapes et des formules, puis écouter la vidéo en entier.
