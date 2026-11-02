# Contrôle qualité : vidéo de lancement « Le paradoxe des anniversaires »

> Aperçu de relecture, **non validé, non publiable**. Voix Kokoro (FR `ff_siwis`, EN `af_heart`), prototype. Le storyboard détaillé est dans [STORYBOARD_LANCEMENT.md](STORYBOARD_LANCEMENT.md). La relecture humaine de JG reste nécessaire pour le fond, la voix et le rythme.

## 1. Vérification mathématique

Chaque nombre dit ou affiché a été recalculé deux fois : par les blocs `verifier` de la fiche (évaluateur du moteur, contrôle bloquant), puis à part, en Python, pour ce rapport.

| Affirmation de la vidéo | Calcul | Résultat | État |
|---|---|---|---|
| 4 personnes forment 6 paires | 3 + 2 + 1 = C(4, 2) | 6 | ✅ |
| 23 personnes forment 253 paires | 22 + 21 + … + 1 = 23 × 22 ÷ 2 | 253 | ✅ |
| 10 personnes forment 45 paires (exercice) | 10 × 9 ÷ 2 | 45 | ✅ |
| On ne peut pas additionner les paires | 40 personnes : 780 paires, 780 ÷ 365 ≈ 2,14 > 1 | une « probabilité » supérieure à 100 %, absurde | ✅ |
| Tous différents avec 23 personnes | 365/365 × 364/365 × … × 343/365 | 0,4927 ≈ 0,493 | ✅ |
| Au moins une coïncidence | 1 − 0,4927 | 0,5073 ≈ 50,7 % | ✅ |
| Votre propre anniversaire face aux 22 autres | 1 − (364/365)²² | ≈ 5,9 %, dit « environ 6 % » | ✅ |
| 40 personnes | 1 − P₀(40) | 89,1 % (sous 90 %) | ✅ |
| 41 personnes | 1 − P₀(41) | 90,3 % (premier au-dessus de 90 %) | ✅ |
| 50 personnes | 1 − P₀(50) | 97,0 % | ✅ |
| La 41ᵉ personne apporte 40 nouvelles paires | C(41, 2) − C(40, 2) | 40 | ✅ |
| Empreinte de 64 bits | 2⁶⁴ | ≈ 1,84 × 10¹⁹, soit environ 18 milliards de milliards | ✅ |
| Environ 5 milliards de fichiers pour une chance sur deux | 1 − exp(−n² / (2 × 2⁶⁴)), n = 5 × 10⁹ | ≈ 0,49 (approximation classique) | ✅ |

Hypothèses dites à l'écran et à la voix : 365 jours également probables, 29 février ignoré. L'approximation exponentielle de la partie cryptographie est présentée comme un ordre de grandeur.

## 2. Contrôle pédagogique

| Objectif de JG | Où dans la vidéo | État |
|---|---|---|
| 1. Expliquer pourquoi 23 personnes donnent environ 50,7 % | défi (scène 3), construction (B à D), révélation (scène 20) | ✅ |
| 2. Compter les paires et comprendre la division par 2 | A, B, C, D une paire à la fois (scène 7), A–B = B–A (scène 8), formule ligne par ligne (scène 10), exercice à 10 personnes | ✅ |
| 3. Comprendre pourquoi on calcule d'abord « aucun anniversaire ne coïncide » | scène 15 | ✅ |
| 4. Produit des probabilités conditionnelles et complément | calendrier une personne après l'autre (16), produit (17), barre P₀ / 1 − P₀ (18), complément (19) | ✅ |
| 5. Le seuil de 90 % à 41 personnes | exercice (26), correction 40 / 41 (27), courbe avec seuil (28), explication par les nouvelles paires (29) | ✅ |
| 6. Pourquoi l'intuition se trompe | vos 22 paires contre 253 (22), « 23/365 » possible mais incomplet (23) | ✅ |

Test du débutant (« peut-il réexpliquer le raisonnement et refaire un calcul simple ? ») : la vidéo donne deux exercices avec correction pas à pas (10 personnes, seuil de 90 %) et un récapitulatif en trois gestes (scène 30). **À confirmer par un vrai spectateur débutant** : ce test ne peut pas être automatisé.

Prudence sur la cryptographie : la voix ne dit jamais que le paradoxe « sécurise » des données ni qu'il « détecte » la fraude (test automatique `test_application_cryptographie_verifiee`). Les quatre piliers apparaissent sur quatre cartes distinctes.

## 3. Production

| Point | Résultat |
|---|---|
| Durée | **FR 7 min 57,7 s** (477,7 s), **EN 7 min 35,4 s** (455,4 s) |
| Format | 1080 × 1920, 30 images/s, H.264 ; audio AAC 48 kHz mono (mesuré avec ffprobe sur les deux MP4) |
| Synchronisation | chaque étape, ligne de formule, phase d'animation et repère de courbe apparaît au début de la phrase qui l'annonce ; temps par phrase dans le storyboard |
| Sous-titres | calés sur les temps réels de chaque phrase, deux lignes de 42 caractères au plus |
| Logos | officiels, variante sombre sur fond sombre, non modifiés (contrôles automatiques du moteur réussis) |
| Rapport du moteur | aucun avertissement ; seul blocage : la fiche est encore en « brouillon », volontairement |

## 4. Rendu et lisibilité mobile

Les deux vidéos complètes ont été relues **image par image, une image toutes les 2 secondes** (239 images FR, 228 EN, dans `revue-image-par-image/`), puis les scènes corrigées ont été rendues et relues à nouveau.

| Contrôle | Résultat |
|---|---|
| Barre d'accent sous les grands chiffres | **corrigée par une règle commune** : la barre se place sous le bas réel du glyphe (numéros de chapitre « 1 » à « 5 », chiffre clé « 50,7 % »), en FR et en EN, vertical et 16:9. Deux tests vérifient qu'aucun pixel de la barre ne touche le chiffre ; ils échouaient sur l'ancien code |
| Coupures de ligne | les expressions ne sont plus coupées : « n(n − 1) ÷ 2 », « 1 − P₀ », « 780 ÷ 365 > 2 » restent sur une ligne |
| Chevauchements | aucun relevé sur les 467 images relues |
| Formules sur mobile | ligne la plus petite de la formule du produit : 85 px (seuil 70 px), y compris avec la police du runner GitHub |
| Zones de sécurité | zones TikTok, Reels et Shorts vérifiées par le moteur (`inspection/zones-*.png`) |
| Point d'attention | en vertical, le texte des quatre cartes de piliers reste petit (36 px sur 1 080) : lisible, mais c'est l'écran le plus dense |

### Scènes faibles corrigées (« la voix raconte, l'image démontre »)

| Scène | Problème vu à la relecture | Correction |
|---|---|---|
| 13 · « 253 paires, mais pas 253 chances » | un écran fixe pendant environ 20 s | trois étapes : les paires se chevauchent, donc 253 ÷ 365 n'est pas la réponse, 780 ÷ 365 > 2 est impossible |
| 17 · « On multiplie ces probabilités » | environ 8 s d'écran vide avant le produit | le produit apparaît dès la première phrase ; la condition « pas encore de coïncidence » est écrite sous la formule, puis vient ≈ 0,493 |
| 19 · « Le complément à 1 » | 6 s sur le seul titre | introduction raccourcie : 1 − P₀, puis = 1 − 0,493, puis ≈ 0,507 arrivent tout de suite, et 50,7 % suit |
| 33 · « Le même calcul, en très grand » | l'analogie n'était dite qu'à la voix | nouvelle étape « Codes = jours, fichiers = personnes » |

Les 37 scènes, le storyboard, les animations et l'architecture sont conservés.

## 5. Voix

| Point | Résultat |
|---|---|
| Voix | Kokoro v1.0 : FR `ff_siwis`, EN `af_heart` (confirmé dans `production/tts.yaml` et dans les métadonnées des vidéos) |
| Nombres, décimales, %, signes | écrits en toutes lettres dans le texte dit, et normalisés pour la voix (`lmec/lecture.py`) : « 50 virgule 7 pour cent », « 1 moins P zéro », « 2 puissance 64 » ; EN « zero point four nine three » |
| ACTU-BASICS | FR : lexique de prononciation « Actu Bèyssixe » (phonèmes aktˈy bɛisˈiks au lieu de aktybazik) ; EN : prononcé correctement sans lexique (ˈæktuːbˈeɪsɪks). La marque reste écrite ACTU-BASICS partout à l'écran et dans les sous-titres (test automatique) |
| Limite de la vérification | contrôlé **par phonétisation automatique seulement** : aucune transcription automatique ni écoute n'est possible depuis l'environnement de travail. **Ce n'est pas une validation de la voix : l'écoute de JG est nécessaire** (narrations complètes et extrait de comparaison livrés) |

## 6. Exécution

| Point | Résultat |
|---|---|
| Cause des annulations CI | chaque image d'une scène formule recalculait le rendu mathtext (environ 4,5 s par image, plus d'une heure et demie par langue). Images de formule calculées une fois par scène ; le délai CI est revenu à 60 min (il n'a pas été augmenté) |
| Preuve | run 33, commit `0bb1711` : **success** en 36 min, les deux vidéos dans l'artefact `apercu-33` |
| Runs 34 et 35 | échec du test de lisibilité de la formule de la scène 17 en CI (note trop longue avec la police du runner), corrigé par `3047721` ; tests verts en CI au run 36 |
| Commit final testé | `1a6d9f0` : run 41 **success** en 32 min (tests verts, FR et EN rendus, artefact `apercu-41`, 71 fichiers), https://github.com/JohnGAB7/le-monde-en-chiffres/actions/runs/41498402407 ; les commits suivants ne touchent que la documentation |
| Rendu local | FR 671 s, EN 604 s (en parallèle) ; `python3 production/produire.py contenus/fiches/2026-11-lancement-actu-basics.yaml --voix kokoro --langues fr` (puis `en`) |
| Tests | `python3 -m pytest production/tests -q` : 184 réussis en local |
| Provenance des voix | workflow « Provenance des voix Kokoro » : voix identiques aux fichiers officiels Apache-2.0 ; détails dans `docs/voice-licenses.md` |

## 7. Ce qui n'est pas vérifié

- L'écoute humaine des deux narrations (prononciation, rythme, naturel).
- Le test du débutant (un vrai spectateur).
- La licence du fichier ONNX réellement utilisé (`kokoro-v1.0.onnx`) : point bloquant avant une publication monétisée, réduit le 2 novembre : le fichier contient 99,65 % des valeurs des poids officiels Apache-2.0 ([run](https://github.com/JohnGAB7/le-monde-en-chiffres/actions/runs/41525279833)). Preuve technique de provenance, pas licence écrite ; décision de JG. Détail dans `docs/voice-licenses.md`.
- La fiche reste en « brouillon » : aucune vidéo n'est publiable en l'état, et rien n'a été publié.
