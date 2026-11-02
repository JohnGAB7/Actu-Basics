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
| Durée | FR 8 min 01 s, EN 7 min 38 s (objectif 6 à 8 min, fixé par la profondeur pédagogique) |
| Synchronisation | chaque étape, ligne de formule, phase d'animation et repère de courbe apparaît au début de la phrase qui l'annonce ; temps par phrase dans le storyboard |
| Sous-titres | calés sur les temps réels de chaque phrase (`sous-titres.srt`) |
| Lecture des nombres | normalisée pour la voix : « 50 virgule 7 pour cent », « 1 moins P zéro », « 2 puissance 64 » ; EN « 0 point four nine three » ; vérifiée par phonétisation |
| Chevauchements | planches de contact vertical et 16:9 relues image par image, voir section 4 |
| Logos | officiels, variante sombre sur fond sombre, non modifiés |
| Voix | Kokoro, prototype : **écoute de JG nécessaire** avant toute validation |

## 4. Rendu et lisibilité mobile

Aperçus vérifiés image par image (une image toutes les 8 secondes, vertical FR et EN) et planches 16:9.

| Contrôle | Résultat |
|---|---|
| Rapport du moteur | aucun avertissement ; seul blocage : la fiche est encore en « brouillon » (attend la validation de JG) |
| Chevauchements | aucun relevé ; courbes à quatre repères : étiquettes en légende |
| Coupures de ligne | les formules ne sont plus coupées au milieu (« n(n − 1) ÷ 2 », « 1 − P₀ » restent sur une ligne) |
| Sous-titres | 166 (FR) et 159 (EN), aucun chevauchement, deux lignes de 45 caractères au plus |
| Zones de sécurité | zones TikTok, Reels et Shorts vérifiées par le moteur (`inspection/zones-*.png`) |
| Logo | officiel, variante sombre sur fond sombre |
| Point d'attention | en vertical, le texte des quatre cartes de piliers est petit (36 px sur 1 080) : lisible sur téléphone, mais c'est l'écran le plus dense |
| Son | voix normalisée à −16 LUFS, nappe sous la voix, tic des comptes à rebours, carillon des révélations |
