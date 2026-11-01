# Guide d'utilisation (sans toucher au code)

Tout se fait depuis le site GitHub. Aucune installation n'est nécessaire.

## 1. Produire un contenu

| Étape | Où | Action |
|---|---|---|
| 1. Déposer la fiche | `contenus/fiches/` → *Add file* → *Create new file* | Nom `AAAA-MM-JJ-sujet.yaml`, coller la fiche de ChatGPT, *Commit* |
| 2. Regarder l'aperçu | Onglet *Actions* → « Aperçu des contenus » → dernière exécution | Le résumé s'affiche directement. Les fichiers sont en bas, dans *Artifacts* (`apercu-…`) |
| 3. Vérifier les faits | Hors machine | Section 1 du rapport : chaque chiffre retrouvé dans la source |
| 4. Valider la fiche | Éditer la fiche (icône crayon) | `statut: valide`, `valide_par: "JG"`, `date: AAAA-MM-JJ` (date du jour), *Commit* |
| 5. Rendu final | *Actions* → « Validation finale » → *Run workflow* | Chemin de la fiche + fournisseur de voix → *Run* |
| 6. Relire | Artefact `final-…` | `rapport-qc.md` sections 1 et 5, regarder les vidéos son activé |
| 7. Publier | Applications des plateformes | Vidéo + `legende.txt` ; carrousel = images `carrousel/` ; activer la mention IA si voix de synthèse |
| 8. Archiver | GitHub | Déplacer la fiche vers `contenus/publie/` |

**Règle simple** : un fichier qui porte le filigrane « BROUILLON · NON VALIDÉ » ne se publie jamais. Seul l'artefact `final-…` contient des fichiers à publier.

## 2. Contenu d'un artefact

```
resume.md                          résumé (identique à celui affiché dans GitHub)
<id>/rapport-qc.md                 rapport qualité complet
<id>/fr/ et <id>/en/
  video.mp4                        vidéo 1080×1920 avec voix
  narration.wav                    voix seule (pour réécouter ou remixer)
  sous-titres.srt                  à importer dans YouTube / TikTok si souhaité
  script-voix-off.txt              texte lu, scène par scène (sert aussi au mode manuel)
  carrousel/01-….png …             images 1080×1350
  apercu-carrousel.png             toutes les diapositives sur une image
  miniature.jpg
  legende.txt                      légende prête à coller (source + hashtags inclus)
  metadonnees.json
  inspection/planche-video.png     chaque scène en cours d'animation puis à l'état final
  inspection/apercu-mobile.png     taille réelle d'un téléphone
  inspection/zones-*.png           interface TikTok / Reels / Shorts simulée en rouge
```

## 3. Lire le rapport qualité

| Section | Sens | Que faire |
|---|---|---|
| État ✅ / ⚠️ / ❌ | Synthèse | ❌ = ne pas publier |
| 1. Vérification factuelle | **La machine ne vérifie pas la vérité des chiffres** | Cocher chaque point vous-même |
| 2. Erreurs bloquantes | Empêchent le rendu final | Corriger la fiche, puis relancer |
| 3. Avertissements | À regarder, n'empêchent rien | Décider : corriger ou assumer |
| 4. Compatibilité plateformes | Durée, légende, titre, hashtags, zones par plateforme | ⚠️ = possible mais pas idéal |
| 5. Contrôles humains | Visuel et audio | Cocher après avoir regardé |
| 6. Production | Durées, voix utilisée, temps de rendu | Information |
| 7. Contrôles réussis | Liste détaillée (dépliable) | Information |

## 4. Erreurs courantes

| Message | Cause | Solution |
|---|---|---|
| « Fiche inexploitable : … champ manquant » | Champ absent ou laissé vide dans la fiche | Compléter le champ cité |
| « YAML illisible (ligne 12, colonne 5) » | Indentation, deux-points ou guillemet manquant | Corriger à la ligne indiquée ; comparer avec `modeles/fiche-contenu.yaml` |
| « … doit être un bloc « clé: valeur », pas un texte » / « … doit être une liste » | Mauvaise forme d'un champ | Reprendre la forme du modèle (tirets pour les listes, retrait pour les blocs) |
| « … doit valoir true ou false » | `oui`/`non` écrit à la place de `true`/`false` | Écrire `true` ou `false` |
| « Unité du chiffre clé différente entre FR et EN » | Ex. « milliards » en FR, « million » en EN | Corriger la traduction (« milliard » = « billion ») |
| « Période différente entre FR et EN » | Années différentes dans `contexte.periode` | Aligner les deux langues |
| « … ne correspond pas au chiffre clé » | Le point mis en avant n'a pas la même valeur, même après conversion d'échelle | Vérifier valeur et unité (décision éditoriale) |
| « Erreur inattendue du programme » | Défaut du programme, pas de la fiche | Transmettre le message à la direction technique |
| « Fiche non validée (statut « brouillon ») » | Normal avant validation | Étape 4 du §1 |
| « Statut « valide » mais la date de validation est absente » | `date:` vide | Mettre la date du jour `AAAA-MM-JJ` |
| « Date … dans le futur » | Faute de frappe | Corriger la date |
| « Scène obligatoire « fin » absente » | Scène manquante dans une langue | Ajouter la scène (accroche, chiffre, source, fin) |
| « Nombres différents entre FR et EN » | Un chiffre n'apparaît que dans une langue | Vérifier : oubli ou erreur de traduction ? |
| « Nombre au format anglais dans le texte français » | « 8.2 » au lieu de « 8,2 » | Corriger |
| « Astérisque non fermé » | `*mot` sans second `*` | Fermer la mise en valeur |
| « Narration impossible (openai) : Variable OPENAI_API_KEY absente » | Secret non configuré | Ajouter le secret (voir [voix-off.md](voix-off.md)) ou choisir `piper` |
| « … a répondu 401 / 429 » | Clé invalide / quota ou crédit épuisé | Vérifier la clé ou le crédit chez le fournisseur ; relancer plus tard ; ou `piper` |
| ⚠️ « … plafond interne de production, non confirmé … » | Un plafond prudent (non officiel) est dépassé ; ce n'est pas bloquant | Raccourcir, ou vérifier la limite actuelle sur la plateforme et mettre à jour `plateformes.yaml` |
| « … doit être un nombre fini » | `.nan`, `.inf` ou texte à la place d'un nombre | Écrire le nombre (point décimal, sans unité) |
| « Modèle Piper introuvable » | Voix non téléchargée (en local) | `python production/telecharger_voix.py` |
| « Voix « test » réservée aux tests » | Fournisseur de test utilisé | Choisir `piper`, `openai` ou `elevenlabs` |
| « Texte trop long (…) » | Le texte ne tient pas, même réduit | Raccourcir la scène (décision éditoriale si le sens change) |
| « durée … > maximum » | Vidéo trop longue pour une plateforme | Raccourcir les textes ou retirer une scène |

## 5. Mode de secours

**GitHub Actions indisponible** — sur un ordinateur avec Python 3.10+ et ffmpeg :

```bash
pip install -r production/requirements.txt -r production/requirements-voix.txt
python production/telecharger_voix.py
python production/produire.py contenus/fiches/AAAA-MM-JJ-sujet.yaml                 # aperçu
python production/produire.py contenus/fiches/AAAA-MM-JJ-sujet.yaml --mode final    # fichiers à publier
```

**Voix de synthèse en panne** (quota, réseau, clé) — trois options, par ordre de préférence :
1. Relancer avec `--voix piper` (gratuit, hors ligne) ;
2. Enregistrer la voix soi-même (`--voix manuel`, voir [voix-off.md](voix-off.md#mode-manuel-secours-ou-voix-humaine)) ;
3. Décider éditorialement d'une vidéo sans voix : `narration: false` dans la fiche.

Ne jamais publier un aperçu filigrané pour « rattraper » un retard.

**Script inutilisable** — mode entièrement manuel : la fiche contient tous les textes. Les recopier dans un modèle Canva ou CapCut (1080×1920 vidéo, 1080×1350 carrousel), garder la diapositive « source », enregistrer la voix à partir du script, et faire les contrôles humains de [controles-qualite.md](controles-qualite.md).

## 6. Commandes utiles (pour qui utilise le terminal)

```bash
python production/produire.py FICHE --verifier          # contrôle la fiche, ne produit rien (quelques secondes)
python production/produire.py FICHE --voix openai       # change de fournisseur de voix
python production/produire.py FICHE --langues fr        # une seule langue (aperçu uniquement)
python production/produire.py FICHE --sans-video        # carrousels et textes seulement
python -m pytest production/tests -q                    # tests automatiques
```
