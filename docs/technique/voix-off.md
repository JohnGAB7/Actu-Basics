# Voix off : fonctionnement, choix du fournisseur, réglages

## En bref

- La voix est **générée automatiquement** à partir des textes de la fiche, en FR et en EN.
- Le fournisseur est **interchangeable** sans toucher au code : `piper` (gratuit, local), `openai`, `elevenlabs`, `manuel` (vos enregistrements), `test` (bip, pour les tests uniquement).
- Par défaut : **Piper**, gratuit et sans compte, **pour les aperçus**. Aucune dépense n'a été engagée.
- **La qualité de publication n'est validée pour aucune voix.** Elle se juge à l'oreille, par une personne, sur la vidéo finale (voir l'état ci-dessous).
- Une vidéo **sans voix n'est jamais présentée comme prête** : si la voix échoue, le rapport passe en ❌ BLOQUÉ, l'aperçu porte le filigrane et le mode final refuse de produire.

## État réel des intégrations (novembre 2026)

| Fournisseur | Ce qui a été testé | Ce qui ne l'a pas été | Usage |
|---|---|---|---|
| Piper | Synthèse réelle FR et EN, en local et dans GitHub Actions ; durées, sous-titres et montage vérifiés | **Écoute humaine** : la prononciation n'a pas été jugée à l'oreille | ✅ Aperçus. Publication : seulement après écoute et accord |
| OpenAI | Le code est écrit d'après la documentation de l'API. Tests automatiques : clé absente, erreurs réseau et HTTP (refus clair, jamais de vidéo muette présentée comme prête) | **Aucun appel réel** : pas de clé, aucune dépense engagée. Format de réponse, qualité FR et coût réel non vérifiés | ⚠️ Non validé en production. Premier essai à faire sur un aperçu, puis écoute |
| ElevenLabs | Idem : code écrit d'après la documentation, erreurs testées sans clé | **Aucun appel réel** (pas d'abonnement) | ⚠️ Non validé en production |
| Manuel | Assemblage de fichiers enregistrés, erreur si une prise manque | Qualité de vos enregistrements | ✅ Secours |

Avant d'utiliser OpenAI ou ElevenLabs pour une publication : lancer un aperçu avec la clé (`--voix openai`), vérifier que la vidéo est produite sans erreur, l'écouter en entier, puis seulement passer en validation finale.

## Ce qui est dit

Pour chaque scène, la voix lit :

| Scène | Texte lu |
|---|---|
| `chiffre` | le chiffre clé + son unité, puis le texte de la scène |
| `source` | « Source : » + nom des sources |
| autres | le texte affiché |

Si une scène a un champ `voix_off`, c'est lui qui est lu à la place (choix éditorial). Les astérisques de mise en valeur ne sont jamais lus.

Le fichier `script-voix-off.txt` de chaque rendu montre, scène par scène, le texte écrit et, s'il diffère, le texte réellement envoyé à la synthèse (ligne « Dit »).

## Synchronisation

1. Chaque **phrase** est synthétisée séparément : on connaît sa durée exacte.
2. Chaque scène dure au moins : 0,35 s d'amorce + la voix + 0,5 s de respiration. **Une phrase n'est jamais coupée** ; une durée imposée (`duree:`) trop courte est allongée et signalée.
3. Les sous-titres suivent les temps réels de chaque phrase. À l'intérieur d'une phrase longue, les deux morceaux de sous-titre sont répartis au prorata des caractères (précision de l'ordre de quelques dixièmes de seconde).
4. La piste complète est normalisée à −16 LUFS (volume homogène d'une vidéo à l'autre).

## Comparatif des fournisseurs

Volume estimé : 1 sujet par jour × 2 langues × ~550 caractères ≈ **33 000 caractères / 45 minutes d'audio par mois**.

| | Piper (défaut) | OpenAI TTS | ElevenLabs |
|---|---|---|---|
| Qualité FR | Correcte, timbre synthétique ; **voyelles nasales mal rendues** (an, on, in) avec le modèle actuel | Bonne, naturelle ; accent parfois anglo-saxon selon la voix | Très bonne, la plus naturelle en FR |
| Qualité EN | Correcte | Très bonne | Très bonne |
| Coût mensuel estimé | **0 €** | **≈ 0,50 à 1 $** (`tts-1` 15 $/M caractères ; `gpt-4o-mini-tts` ≈ 0,015 $/min) | **6 $** (Starter, 30 000 crédits : juste) à **22 $** (Creator, 121 000 crédits) |
| Compte / clé | Aucun | Clé API, paiement à l'usage | Abonnement + clé API ; licence commerciale à partir de Starter |
| Intégration | Paquet Python + modèle de 60 à 120 Mo | Une requête HTTP par phrase | Une requête HTTP par phrase ; choisir un `voice_id` |
| Hors ligne / panne | Fonctionne hors ligne | Dépend du service | Dépend du service |
| Licence des voix | Modèles CC BY 4.0 (siwis FR, LibriTTS EN) ; logiciel GPL-3.0 | Conditions OpenAI | Conditions ElevenLabs |

Prix relevés en novembre 2026 sur des comparateurs tiers ([CostGoat](https://costgoat.com/pricing/openai-tts), [NoCode MBA](https://www.nocode.mba/articles/elevenlabs-pricing)) : **à revérifier sur les pages officielles avant de souscrire.** Les qualités indiquées pour OpenAI et ElevenLabs sont des réputations, non vérifiées à l'écoute (voir l'état des intégrations).

## Cache : ne jamais payer deux fois la même phrase

Chaque phrase synthétisée est gardée dans `.cache-tts/` (jamais versionné). Le nom du fichier est une empreinte SHA-256 de :

- le fournisseur et la langue ;
- **toute** la configuration de la voix dans `tts.yaml` (voix, modèle, consignes, vitesse, réglages…) ;
- pour Piper, le nom et la taille du modèle téléchargé ;
- le **texte exact envoyé** à la synthèse, après le lexique de prononciation.

Changer un mot, une virgule, une voix, une consigne ou une règle de prononciation produit une nouvelle empreinte : un ancien audio n'est jamais réutilisé pour un texte différent. Relancer un rendu sans changement ne coûte rien.

Dans GitHub Actions, le dossier est conservé entre les exécutions (`actions/cache`), séparément pour chaque fournisseur, et sauvegardé **même quand la validation finale refuse** la fiche : une voix déjà payée n'est pas perdue. Les audios inutilisés depuis 90 jours sont supprimés automatiquement. Le rapport indique, par langue, combien de phrases ont été synthétisées, combien viennent du cache et combien de caractères ont été facturables.

GitHub supprime de lui-même un cache inutilisé pendant 7 jours : après une longue pause, la première exécution resynthétise tout (coût OpenAI estimé : quelques centimes).

**Recommandation technique.** Garder Piper pour les aperçus. Pour la publication, OpenAI semble offrir le meilleur rapport qualité/prix (environ 1 $ par mois d'après les tarifs publics) ; ElevenLabs a la réputation d'une voix française plus naturelle, pour 6 à 22 $ par mois. **Ces appréciations de qualité viennent de la réputation des services, pas d'une écoute faite ici** : aucune des deux intégrations n'a été appelée avec une vraie clé. Le choix de la voix publiée est éditorial, se fait à l'oreille, et reste à votre décision.

## Configurer un fournisseur

Tout se règle dans [`production/tts.yaml`](../../production/tts.yaml) :

```yaml
fournisseur: piper          # fournisseur par défaut
voix:
  fr:
    openai: {modele: gpt-4o-mini-tts, voix: nova, consignes: "Voix de journaliste française…"}
    elevenlabs: {voice_id: "…", modele: eleven_multilingual_v2}
  en:
    piper: {modele: en-us-libritts-high.onnx, locuteur: 0}
```

- **Changer de voix** : modifier `voix` (OpenAI : alloy, ash, coral, echo, fable, nova, onyx, sage, shimmer…), `voice_id` (ElevenLabs, copié depuis leur bibliothèque) ou `locuteur` (Piper anglais : 0 à 903).
- **Changer de fournisseur pour un rendu** : `--voix openai`, ou dans GitHub le menu « Fournisseur de voix » du workflow *Validation finale*.
- **Prononciation** : la section `prononciation` remplace un mot par sa graphie phonétique, **seulement dans ce qui est envoyé à la voix** (jamais dans les images ni les sous-titres). Exemple : `DESA: "Désa"`.

## Secrets (clés d'API)

Les clés ne vont **jamais** dans le dépôt.

- **En local** : copier `.env.example` en `.env` à la racine du dépôt et y coller la clé. `.env` est ignoré par Git.
- **Sur GitHub** : *Settings → Secrets and variables → Actions → New repository secret*, nommé `OPENAI_API_KEY` ou `ELEVENLABS_API_KEY`. Seul le workflow *Validation finale* les utilise. Le workflow d'aperçu n'en reçoit aucune.
- Une clé exposée par erreur se révoque immédiatement depuis le tableau de bord du fournisseur.

## Voix Piper (gratuite)

```bash
pip install -r production/requirements-voix.txt
python production/telecharger_voix.py     # télécharge les modèles dans production/voix/ (non versionné)
```

Limite connue : les modèles Piper français disponibles ici n'ont pas de phonème pour la nasalisation. « Population », « mondiale », « enfants » risquent d'être prononcés sans nasale. **À écouter avant toute publication** ; c'est la principale raison de recommander un fournisseur payant pour le FR publié.

## Mode manuel (secours ou voix humaine)

1. Ouvrir `script-voix-off.txt` (dans l'artefact d'aperçu) : il liste les scènes `[01]`, `[02]`…
2. Enregistrer une prise par scène (téléphone) : `01.mp3`, `02.mp3`… (wav, m4a, aac, ogg acceptés).
3. Les déposer dans `audio/<id-de-la-fiche>/fr/` et `audio/<id>/en/`, ou dans le dossier indiqué par le champ `audio` de l'édition.
4. Lancer `python production/produire.py FICHE --voix manuel`.

Il faut un enregistrement par scène : s'il en manque un, le rendu s'arrête et indique lequel. Avec des prises manuelles, les sous-titres sont répartis sur toute la durée de chaque prise, ce qui est moins précis qu'avec une voix de synthèse.

## Vidéo volontairement sans voix

Mettre `narration: false` dans l'édition (`editions.fr` / `editions.en`). C'est un choix éditorial explicite : le rapport le signale en avertissement, et la vidéo reçoit une piste silencieuse (à habiller avec une musique de la bibliothèque de la plateforme).
