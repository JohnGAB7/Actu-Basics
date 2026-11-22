# Voix de synthèse : licences, versions, gratuité et ressources

> Décision de JG (novembre 2026) : **Kokoro** devient la voix prioritaire (FR `ff_siwis`, EN `af_heart`), **Piper** reste en secours. Gratuit et local uniquement : aucune clé d'API, aucun abonnement, aucun crédit.
>
> Ce document rassemble ce qui a été vérifié et ce qui ne l'a pas été. Ce n'est pas un avis juridique. **L'intégration n'est pas considérée comme validée** tant que JG n'a pas écouté les audios et accepté les points ouverts ci-dessous.

## 0. Usage commercial (publication et monétisation) : conclusion

| Composant | Peut-on publier et monétiser les vidéos ? | Preuve |
|---|---|---|
| Voix `ff_siwis` et `af_heart` | **Oui** (Apache-2.0) | identiques, valeur par valeur, aux fichiers officiels `hexgrad/Kokoro-82M` sous Apache-2.0 (section 2) |
| Poids du modèle Kokoro-82M | **Oui** (Apache-2.0) | fiche officielle du modèle |
| Fichier ONNX `kokoro-v1.0.onnx` réellement utilisé | **Pas encore établi par écrit, provenance prouvée** | aucune licence écrite pour ce fichier ; mais 99,65 % des valeurs des poids officiels Apache-2.0 y sont retrouvées ([run CI](https://github.com/JohnGAB7/le-monde-en-chiffres/actions/runs/41525279833)) : c'est une conversion de ces poids. Décision de JG en point ouvert 3 |
| Logiciels (kokoro-onnx, onnxruntime, numpy, espeak-ng, phonemizer-fork) | **Oui** | MIT, BSD ou GPL-3.0+ : la GPL vise la redistribution du logiciel, pas les vidéos produites |
| Attribution | recommandée, pas d'obligation écrite trouvée | créditer SIWIS (CC BY 4.0) pour la voix française, formule en section 3 |
| Zone grise connue | à connaître | une partie des données d'entraînement de Kokoro est de l'audio synthétique de modèles fermés (fiche du modèle) |

**Conclusion** : les deux voix choisies par JG sont commercialisables. Le fichier ONNX est prouvé techniquement être une conversion des poids officiels Apache-2.0 (99,65 % des valeurs retrouvées) ; il manque seulement une licence écrite pour ce fichier précis, à arbitrer par JG. Ce n'est pas un avis juridique.

## 1. Versions exactes utilisées

| Élément | Version | Source | Empreinte / taille |
|---|---|---|---|
| Modèle Kokoro-82M | v1.0 (publié le 27 janvier 2025 selon la fiche du modèle) | fiche Hugging Face `hexgrad/Kokoro-82M` | — |
| Conversion ONNX du modèle | `kokoro-v1.0.onnx` (float32, « optimized f32 version from taylorchu/kokoro-onnx ») | https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 (conversion faite par https://github.com/taylorchu/kokoro-onnx, publication v0.2.0) | SHA-256 `7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5`, 325 532 387 octets |
| Fichier des voix | `voices-v1.0.bin` (vecteurs de style au format npz, 54 voix dont `ff_siwis` et `af_heart`) | https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 | SHA-256 `bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d`, 28 214 398 octets |
| Code d'inférence | `kokoro-onnx` 0.5.0 | PyPI (https://github.com/thewh1teagle/kokoro-onnx) | épinglé dans `production/requirements-voix.txt` |
| Moteur ONNX | `onnxruntime` 1.32.0 dans GitHub Actions, épinglé depuis le 22/11/2026 (`production/contraintes.txt`) | PyPI | dépendance de kokoro-onnx (≥ 1.20.1) |
| Phonémisation | `phonemizer-fork` 3.3.2 | PyPI | dépendance de kokoro-onnx |
| Bibliothèque espeak-ng | `espeakng-loader` 0.2.4, qui embarque `libespeak-ng.so.1.52.0` | PyPI (https://github.com/thewh1teagle/espeakng-loader) | dépendance de kokoro-onnx |
| Calcul | `numpy` 2.5.5 dans GitHub Actions, épinglé (`production/contraintes.txt`) | PyPI | — |
| Secours : Piper | `piper-tts` 1.8.0, voix `fr-siwis-medium` et `en-us-libritts-high` (publication `rhasspy/piper` v0.0.2) | PyPI, GitHub | inchangé |

`python production/telecharger_voix.py` télécharge les deux fichiers Kokoro depuis GitHub et **refuse** un fichier dont l'empreinte SHA-256 diffère de celle de `production/tts.yaml`. Les fichiers sont rangés dans `production/voix/`, exclu de Git.

## 2. Licences, élément par élément

L'écosystème n'est **pas** couvert en bloc par Apache-2.0. Chaque élément a sa licence :

| Élément | Licence | Vérifié où | Ce que cela implique |
|---|---|---|---|
| Poids du modèle Kokoro-82M | Apache-2.0 | fiche du modèle : « License: apache-2.0 », « With Apache-licensed weights » | Usage commercial permis. Conserver la mention de licence si l'on redistribue le modèle (ce que nous ne faisons pas). |
| Code de référence `hexgrad/kokoro` | Apache-2.0 | dépôt du projet | Non utilisé directement ici. |
| Fichier converti `kokoro-v1.0.onnx` | **Non établie (point bloquant avant publication)** | La publication `model-files-v1.0` ne mentionne aucune licence. Le dépôt de conversion `taylorchu/kokoro-onnx` est sous MIT pour son **code**, et sa publication v0.2.0 ne dit rien de la licence des fichiers du modèle. Le README de `thewh1teagle/kokoro-onnx` indique « kokoro model: Apache 2.0 », sans nommer ce fichier. Le même workflow a comparé son SHA-256 aux 8 exports du dépôt `onnx-community/Kokoro-82M-v1.0-ONNX` (licence déclarée apache-2.0, révision `1939ad2a8e416c0acfeecc08a694d14ef25f2231`) : **aucun n'est identique** (`onnx/model.onnx` fait 325 532 232 octets, SHA-256 `8fbea51e…34cb`). | **Provenance mesurée** (workflow « Provenance des voix Kokoro », `production/comparer_poids_onnx.py`, [run](https://github.com/JohnGAB7/le-monde-en-chiffres/actions/runs/41525279833)) : ses tenseurs ont été comparés à ceux de `kokoro-v1_0.pth` (SHA-256 `496dba11…d1e4`) de `hexgrad/Kokoro-82M`, révision `f3ff3571…4987`, Apache-2.0. Sur 81 731 256 valeurs officielles : 320 tenseurs identiques à l'ordre près (15,58 %), 89 poids normalisés g·v/‖v‖ retrouvés à moins de 1e-5 (70,52 %), et 13,56 % de valeurs retrouvées bit à bit dans les 50 tenseurs restants. **Total : 99,65 %.** Le seul tenseur incomplet est `bert.module.pooler.weight` (51,9 %), une couche de sortie du BERT que la synthèse n'utilise pas ; son absence explique les 0,35 % manquants. Le fichier est donc une conversion des poids officiels. C'est une preuve technique de provenance, pas une licence écrite par l'auteur de la conversion. Solutions sans frais : section « Points ouverts », point 3. |
| Voix `ff_siwis` et `af_heart` (lues dans `voices-v1.0.bin`) | **Apache-2.0, établie par comparaison** | Le fichier `voices-v1.0.bin` ne porte aucune licence écrite. Le workflow « Provenance des voix Kokoro » (`production/verifier_provenance_voix.py`) télécharge les fichiers officiels `voices/ff_siwis.pt` et `voices/af_heart.pt` du dépôt `hexgrad/Kokoro-82M` (révision `f3ff3571791e39611d31c381e3a41a3af07b4987`, licence déclarée apache-2.0) et les compare valeur par valeur aux vecteurs utilisés : **identiques** (forme 510 × 1 × 256, écart maximal 0,0). SHA-256 officiels : `ff_siwis.pt` `8073bf2d2c4b9543a90f2f0fd2144de4ed157e2d4b79ddeb0d5123066171fbc9`, `af_heart.pt` `0ab5709b8ffab19bfd849cd11d98f75b60af7733253ad0d67b12382a102cb4ff`. Run : https://github.com/JohnGAB7/le-monde-en-chiffres/actions/runs/41493590215 | Les deux voix utilisées sont exactement celles que l'auteur publie sous Apache-2.0 : usage commercial permis, y compris monétisation. Les 52 autres voix du fichier ne sont pas utilisées et n'ont pas été comparées. |
| `kokoro-onnx` (code) | MIT | fichier `LICENSE` du paquet installé (« Copyright (c) 2025 github.com/thewh1teagle ») | Usage libre, mention de copyright à garder en cas de redistribution. |
| `onnxruntime` | MIT | métadonnées du paquet | Idem. |
| `numpy` | BSD-3-Clause et licences permissives associées | métadonnées du paquet | Idem. |
| `phonemizer-fork` | **GPL-3.0 ou ultérieure** | métadonnées et `LICENSE` du paquet | Voir « Copyleft » ci-dessous. |
| `espeakng-loader` (code du chargeur) | MIT | dépôt GitHub (le paquet PyPI ne déclare aucune licence dans ses métadonnées) | Usage libre. |
| espeak-ng (`libespeak-ng` 1.52.0, embarqué par `espeakng-loader`) | **GPL-3.0 ou ultérieure** | README d'espeak-ng : « released under the GPL version 3 or later license » ; un fichier (`getopt.c`) est sous BSD-2 | Voir « Copyleft » ci-dessous. Le chargeur ne mentionne pas la licence de la bibliothèque qu'il embarque. |
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

1. **VOICES.md** (notes de qualité et durée d'entraînement par voix) n'a pas pu être lu : Hugging Face est inaccessible depuis l'environnement de travail (le workflow GitHub, lui, y accède). À consulter par JG : https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md. Ce document informe sur la qualité, il ne change pas la licence.
2. **Audio synthétique de modèles fermés** dans les données d'entraînement : la fiche l'assume ; les conditions d'utilisation de ces services tiers ne nous lient pas directement, mais c'est une zone grise à connaître.
3. **Licence du fichier ONNX `kokoro-v1.0.onnx`** : non écrite par ses auteurs (voir section 2). Les voix, elles, sont établies. C'est **le seul point bloquant** avant une publication monétisée. **Mesure du 2 novembre** ([run](https://github.com/JohnGAB7/le-monde-en-chiffres/actions/runs/41525279833)) : le fichier contient 99,65 % des valeurs des poids officiels Apache-2.0 (détail en section 2), donc c'est une conversion de ces poids. La licence Apache-2.0 autorise les œuvres dérivées et leur usage commercial, avec mention de la licence. Le point reste ouvert jusqu'à la décision de JG, car aucune licence n'est écrite pour ce fichier précis. Trois façons de le lever, sans frais : (a) obtenir une confirmation écrite des auteurs de `kokoro-onnx` (une question sur leur dépôt GitHub, gratuite) ; (b) convertir nous-mêmes les poids officiels Apache-2.0 de `hexgrad/Kokoro-82M` avec le script de conversion publié ; (c) utiliser `onnx/model.onnx` du dépôt `onnx-community/Kokoro-82M-v1.0-ONNX` (Apache-2.0 déclarée). **Essai (c) mesuré en CI** (run https://github.com/JohnGAB7/le-monde-en-chiffres/actions/runs/41498402358) : avec kokoro-onnx 0.5.0, ce fichier ne produit aucun son (durée 0 s, en FR comme en EN), même après correction du type de la vitesse. Il n'est donc pas interchangeable sans travail supplémentaire. Recommandation : (a), puis (b) si les auteurs ne répondent pas. Rien de tout cela n'a été fait sans l'accord de JG.
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
| Synthèse de la voix | **0 €** | Locale, sur CPU, sans service ni clé. |
| Téléchargement | ≈ 354 Mo une fois (modèle 326 Mo + voix 28 Mo) | Puis gardé en cache. |
| Cache GitHub Actions | ≈ 350 Mo pour Kokoro, plus les voix Piper (≈ 200 Mo) | Le cache GitHub est gratuit jusqu'à 10 Go par dépôt. |
| Minutes GitHub Actions | Mesuré : un aperçu complet de la leçon (FR et EN, tests compris) a pris **36 minutes** (run 33, voix synthétisées sans cache) ; la limite est de 60 minutes. Le rendu des images d'une langue prend environ 10 minutes en local. Un seul rendu par push. Le contrôle de provenance prend environ 1 minute. | Gratuit et illimité pour un dépôt public ; pour un dépôt privé, compté dans le quota du compte GitHub (2 000 minutes par mois sur le plan gratuit, à revérifier sur la page des tarifs GitHub). C'est le seul coût indirect possible : la synthèse elle-même coûte 0 €, mais je ne promets pas « 0 € au total ». |
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
