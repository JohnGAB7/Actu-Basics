# Voix de synthèse : licences, versions, gratuité et ressources

> Décision de JG (novembre 2026) : **Kokoro** devient la voix prioritaire (FR `ff_siwis`, EN `af_heart`), **Piper** reste en secours. Gratuit et local uniquement : aucune clé d'API, aucun abonnement, aucun crédit.
>
> Ce document rassemble ce qui a été vérifié et ce qui ne l'a pas été. Ce n'est pas un avis juridique. **L'intégration n'est pas considérée comme validée** tant que JG n'a pas écouté les audios et accepté les points ouverts ci-dessous.

## 1. Versions exactes utilisées

| Élément | Version | Source | Empreinte / taille |
|---|---|---|---|
| Modèle Kokoro-82M | v1.0 (publié le 27 janvier 2025 selon la fiche du modèle) | fiche Hugging Face `hexgrad/Kokoro-82M` | — |
| Conversion ONNX du modèle | `kokoro-v1.0.onnx` (float32, « optimized f32 version from taylorchu/kokoro-onnx ») | publication GitHub `thewh1teagle/kokoro-onnx`, tag `model-files-v1.0` | SHA-256 `7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5`, 325 532 387 octets |
| Fichier des voix | `voices-v1.0.bin` (vecteurs de style au format npz, 54 voix dont `ff_siwis` et `af_heart`) | même publication | SHA-256 `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`, 28 214 398 octets |
| Code d'inférence | `kokoro-onnx` 0.5.0 | PyPI | épinglé dans `production/requirements-voix.txt` |
| Moteur ONNX | `onnxruntime` 1.29.0 | PyPI | dépendance de kokoro-onnx |
| Phonémisation | `phonemizer-fork` 3.3.2 | PyPI | dépendance de kokoro-onnx |
| Bibliothèque espeak-ng | `espeakng-loader` 0.2.4, qui embarque `libespeak-ng.so.1.52.0` | PyPI | dépendance de kokoro-onnx |
| Calcul | `numpy` 2.5.3 | PyPI | — |
| Secours : Piper | `piper-tts` 1.8.0, voix `fr-siwis-medium` et `en-us-libritts-high` (publication `rhasspy/piper` v0.0.2) | PyPI, GitHub | inchangé |

`python production/telecharger_voix.py` télécharge les deux fichiers Kokoro depuis GitHub et **refuse** un fichier dont l'empreinte SHA-256 diffère de celle de `production/tts.yaml`. Les fichiers sont rangés dans `production/voix/`, exclu de Git.

## 2. Licences, élément par élément

L'écosystème n'est **pas** couvert en bloc par Apache-2.0. Chaque élément a sa licence :

| Élément | Licence | Vérifié où | Ce que cela implique |
|---|---|---|---|
| Poids du modèle Kokoro-82M | Apache-2.0 | fiche du modèle : « License: apache-2.0 », « With Apache-licensed weights » | Usage commercial permis. Conserver la mention de licence si l'on redistribue le modèle (ce que nous ne faisons pas). |
| Code de référence `hexgrad/kokoro` | Apache-2.0 | dépôt du projet | Non utilisé directement ici. |
| Conversion ONNX (`kokoro-v1.0.onnx`) et `voices-v1.0.bin` | **Non indiquée** sur la page de publication | page `model-files-v1.0` | Ce sont des conversions des poids Apache-2.0, ce que cette licence autorise. Point ouvert : la publication ne restate pas la licence. |
| `kokoro-onnx` (code) | MIT | fichier `LICENSE` du paquet installé (« Copyright (c) 2025 github.com/thewh1teagle ») | Usage libre, mention de copyright à garder en cas de redistribution. |
| `onnxruntime` | MIT | métadonnées du paquet | Idem. |
| `numpy` | BSD-3-Clause et licences permissives associées | métadonnées du paquet | Idem. |
| `phonemizer-fork` | **GPL-3.0 ou ultérieure** | métadonnées et `LICENSE` du paquet | Voir « Copyleft » ci-dessous. |
| espeak-ng (`libespeak-ng` 1.52.0, embarqué par `espeakng-loader`) | **GPL-3.0 ou ultérieure** | projet espeak-ng ; le paquet `espeakng-loader` ne déclare aucune licence dans ses métadonnées | Voir « Copyleft » ci-dessous. |
| Piper (`piper-tts`) | GPL-3.0 ou ultérieure | métadonnées du paquet | Idem, déjà le cas avant Kokoro. |
| Voix Piper `fr-siwis-medium`, `en-us-libritts-high` | CC BY 4.0 (données d'entraînement) | fiches des voix Piper | Attribution, déjà le cas avant Kokoro. |

### Copyleft (GPL-3.0) : ce qui est concerné et ce qui ne l'est pas

- La GPL s'applique au **logiciel** (espeak-ng, phonemizer-fork, Piper) quand on le **redistribue**. Nous l'installons et l'exécutons, sur nos machines et dans GitHub Actions, sans le redistribuer : aucune obligation supplémentaire à ce stade.
- Les **fichiers audio produits** ne sont pas du code du programme : la GPL ne s'étend pas aux vidéos publiées.
- Si un jour ACTU-BASICS distribue le moteur de production (paquet, image Docker, application), il faudra revoir ce point : les composants GPL imposeraient de fournir leur code source et leur licence.

## 3. Obligations d'attribution

### SIWIS (voix française `ff_siwis`)

La fiche du modèle Kokoro indique, dans une section « Creative Commons Attribution », que l'audio de la base **SIWIS** (moins de 11 h, **CC BY 4.0**) fait partie des données d'entraînement de Kokoro v1.0. La licence publiée sur le dépôt de la base (DataShare, Université d'Édimbourg) est le texte CC BY 4.0 sans clause particulière.

La fiche ne précise pas de formule d'attribution, et la question de savoir si une voix de synthèse entraînée sur ces données est un « matériel adapté » au sens de CC BY 4.0 n'est pas tranchée. **Recommandation prudente : créditer la base**, ce qui ne coûte rien, dans la description des vidéos et sur la page « crédits » du site :

> Voix de synthèse : Kokoro-82M (hexgrad, licence Apache-2.0). Voix française entraînée notamment sur The SIWIS French Speech Synthesis Database (Yamagishi, Honnet, Garner, Lazaridis, University of Edinburgh, 2017, CC BY 4.0, https://doi.org/10.7488/ds/1705).

> Synthetic voice: Kokoro-82M (hexgrad, Apache-2.0 licence). French voice trained in part on The SIWIS French Speech Synthesis Database (Yamagishi, Honnet, Garner, Lazaridis, University of Edinburgh, 2017, CC BY 4.0, https://doi.org/10.7488/ds/1705).

La même mention vaut déjà pour la voix Piper `fr-siwis-medium`, entraînée sur la même base.

### `af_heart` (voix anglaise)

Aucune attribution particulière n'est indiquée. La fiche du modèle décrit les données d'entraînement en général : audio du domaine public, audio sous licences permissives (Apache, MIT…), et **audio synthétique produit par des modèles de synthèse fermés**. La provenance exacte de chaque voix n'est pas publiée dans les pages lues.

### Points ouverts

1. **VOICES.md** (notes de qualité et durée d'entraînement par voix) n'a pas pu être lu : Hugging Face est inaccessible depuis l'environnement de travail. À consulter par JG : https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
2. **Audio synthétique de modèles fermés** dans les données d'entraînement : la fiche l'assume ; les conditions d'utilisation de ces services tiers ne nous lient pas directement, mais c'est une zone grise à connaître.
3. La publication des fichiers ONNX ne restate pas la licence Apache-2.0 (point mineur, mentionné par transparence).
4. Ne pas confondre avec les sites commerciaux qui reprennent le nom « kokoro » : la fiche du modèle précise qu'ils ne sont pas liés au projet. Nous n'en utilisons aucun.

## 4. Gratuité : preuve qu'aucun service payant n'est appelé

- `production/tts.yaml` contient `gratuit_uniquement: true`. Avec cette valeur, `creer_fournisseur` **refuse** `openai` et `elevenlabs` (exception `ServicePayantRefuse`) et la fonction d'appel réseau lève une erreur **avant** toute connexion.
- Kokoro et Piper n'ouvrent aucune connexion pendant la synthèse : le test `test_kokoro_local_sans_reseau` coupe toute connexion réseau et vérifie que la synthèse FR et EN réussit quand même.
- `test_service_payant_refuse_par_defaut` et `test_qc_bloque_un_service_payant` font échouer la suite si un fournisseur payant est appelé sans décision explicite de JG.
- Le seul accès réseau est le téléchargement initial des fichiers (GitHub), vérifié par empreinte. Ensuite tout fonctionne hors ligne.
- Aucune clé d'API n'est nécessaire, ni dans le dépôt ni dans les secrets GitHub.

## 5. Coûts indirects

| Poste | Estimation | Commentaire |
|---|---|---|
| Licences | 0 € | — |
| Téléchargement | ≈ 354 Mo une fois (modèle 326 Mo + voix 28 Mo) | Puis gardé en cache. |
| Cache GitHub Actions | ≈ 350 Mo pour Kokoro, plus les voix Piper (≈ 200 Mo) | Le cache GitHub est gratuit jusqu'à 10 Go par dépôt. |
| Minutes GitHub Actions | Un aperçu complet de la leçon de 8 minutes (FR et EN) prend environ 70 à 90 minutes sur un exécuteur standard ; la limite est fixée à 120 minutes. Un seul rendu par push (les rendus « push » et « pull_request » de la même branche ne se cumulent plus) | Gratuit et illimité pour un dépôt public ; pour un dépôt privé, compté dans le quota du compte GitHub (2 000 minutes par mois sur le plan gratuit, à revérifier sur la page des tarifs GitHub). C'est le seul coût indirect possible. |
| GPU, cloud | Aucun | Kokoro tourne sur CPU. |

## 6. Ressources matérielles

Mesures faites sur la machine de travail (4 processeurs virtuels, sans GPU), pendant que deux rendus vidéo tournaient en parallèle :

| | Kokoro | Piper |
|---|---|---|
| Vitesse (temps de calcul / durée de l'audio) | 0,6 à 0,7 | 0,16 à 0,85 (très sensible à la charge) |
| Mémoire | ≈ 1,6 Go au maximum avec les deux moteurs chargés | — |
| Disque | 354 Mo | ≈ 200 Mo pour les deux voix |

Sur une machine libre, Kokoro est plus rapide que le temps réel. Un ordinateur portable récent avec 4 Go de mémoire libre suffit.

## 7. Configuration

- Choix du moteur : `fournisseur: kokoro` dans `production/tts.yaml`, ou `--voix kokoro|piper` à la ligne de commande.
- Voix par langue : `voix.fr.kokoro` (`ff_siwis`, `fr-fr`, vitesse 1.0) et `voix.en.kokoro` (`af_heart`, `en-us`, vitesse 1.0).
- Secours : `secours: {kokoro: piper}`. Si Kokoro est absent ou cassé, Piper prend le relais et le rapport de rendu le signale.
- Lecture des nombres : `production/lmec/lecture.py` transforme, dans le texte envoyé à la voix uniquement, « 50,7 % » en « 50 virgule 7 pour cent », « 0.493 » en « 0 point four nine three », « − » en « moins », « ≈ » en « environ », « 365/365 » en « 365 sur 365 », « 2⁶⁴ » en « 2 puissance 64 ». Les sous-titres gardent l'écriture d'origine.
- Installation : `pip install -r production/requirements-voix.txt`, puis `python production/telecharger_voix.py`.
