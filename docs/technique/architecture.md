# Architecture technique — ACTU-BASICS (anciennement « Le Monde en chiffres »)

*Proposition de la direction technique, novembre 2026 (mise à jour LMEC-2026-003 : voix off, contrôles renforcés, workflows aperçu / final). Les prix sont indicatifs et à revérifier au moment de souscrire.*

## 1. Audit du dépôt (avant modification)

Au 1er novembre 2026, le dépôt ne contenait qu'un `README.md` (principes éditoriaux, bilinguisme, refus de la publication automatique non contrôlée) et un seul commit sur `main`. Aucun code, aucun modèle, aucune donnée, aucun secret. Le README annonce une organisation par dossiers « documents fondateurs, processus éditorial, recherches, contenus, ressources visuelles, automatisation, publications, statistiques, monétisation », qui n'existaient pas encore.

Conséquence : on part d'une page blanche. Cette PR ne crée que ce qui sert la production (`production/`, `modeles/`, `contenus/`, `docs/technique/`) et laisse les autres dossiers à la direction éditoriale.

## 2. Principe directeur

**Un sujet = un fichier texte (la « fiche »).** Tout le reste en découle mécaniquement :

```
Fiche YAML validée ──► produire.py ──► vidéo 9:16 FR + EN
(faits, sources,                       carrousel 4:5 FR + EN
 textes FR et EN)                      sous-titres .srt, légendes, miniatures
                                       script de voix off
                                       rapport qualité
```

Pourquoi un fichier YAML plutôt qu'un outil graphique :

- ChatGPT sait produire ce format directement (voir [consignes-chatgpt.md](consignes-chatgpt.md)) : le propriétaire copie-colle, il ne ressaisit rien.
- Il est versionné dans Git : on sait qui a validé quoi et quand, et on peut revenir en arrière.
- Il est lisible sans outil, donc utilisable en mode manuel (Canva, CapCut) si la chaîne tombe en panne.

## 3. Composants

| Besoin | Choix MVP | Coût | Alternative / évolution |
|---|---|---|---|
| Fiches, modèles, historique | Dépôt GitHub | 0 € | — |
| Rendu images (carrousel, images de vidéo) | Python + Pillow (`production/lmec/rendu.py`) ; polices Anton (affichage) et Inter (texte), licence libre OFL | 0 € | Remotion ou Canva API si besoin d'animations riches |
| Montage vidéo | ffmpeg (H.264, AAC, 30 i/s, 1080×1920) | 0 € | — |
| Sous-titres | `.srt` calé sur les temps réels de chaque phrase prononcée | 0 € | Incrustation dans l'image (ffmpeg + libass) plus tard |
| Voix off | Synthèse automatique, fournisseur interchangeable : Piper (local), OpenAI, ElevenLabs, enregistrement manuel | 0 € (Piper) ; ≈ 1 $/mois (OpenAI) ; 6–22 $/mois (ElevenLabs) | Voir [voix-off.md](voix-off.md) |
| Exécution | Sur l'ordinateur du propriétaire **ou** GitHub Actions | 0 € (dépôt public) ; 2 000 min/mois gratuites (dépôt privé) | n8n en phase 3 |
| Stockage des rendus | Artefacts GitHub Actions (14 jours) | 0 € | Archivage Google Drive (15 Go gratuits) |
| Programmation des publications | Outils natifs : Meta Business Suite (Instagram/Facebook), TikTok Studio, YouTube Studio | 0 € | Metricool / Buffer (plans gratuits limités, payants ~10–20 €/mois) |
| Calendrier éditorial | Dossier `contenus/fiches/` (à produire) et `contenus/publie/` (publié) | 0 € | Google Sheets si plusieurs contributeurs |

**Coût récurrent du MVP : 0 €.** Les seuls coûts optionnels sont la voix de synthèse et, plus tard, un outil de programmation multi-plateformes ou un petit serveur n8n.

## 4. Chaîne semi-automatisée, de la fiche au fichier prêt à publier

| # | Étape | Qui | Outil | Statut |
|---|---|---|---|---|
| 1 | Choix du sujet, recherche, vérification des faits | ChatGPT + propriétaire | — | Éditorial |
| 2 | Rédaction de la fiche YAML FR + EN selon le modèle | ChatGPT | [consignes-chatgpt.md](consignes-chatgpt.md) | ✅ Opérationnel |
| 3 | Validation : `validation.statut: valide`, `valide_par`, `date` | Propriétaire | Édition du fichier | ✅ Opérationnel |
| 4 | Dépôt dans `contenus/fiches/` (interface web GitHub, « Add file ») | Propriétaire | GitHub | ✅ Opérationnel |
| 5 | Aperçu automatique : contrôles + rendu FR/EN avec voix Piper + images d'inspection | Automatique | Workflow « Aperçu des contenus » | ✅ Opérationnel |
| 5 bis | Rendu final (refuse tout ce qui n'est pas prêt) | Propriétaire (1 clic) | Workflow « Validation finale » | ✅ Opérationnel (voix payante : secret à configurer) |
| 6 | Relecture humaine (planche d'aperçu, vidéo, légende) | Propriétaire | Rapport `rapport-qc.md` | ✅ Opérationnel |
| 7 | Programmation de la publication | Propriétaire | Outils natifs des plateformes | ⚙️ À configurer (comptes) |
| 8 | Déplacement de la fiche vers `contenus/publie/` | Propriétaire | GitHub | ✅ Opérationnel |

Garde-fous intégrés :

- Deux modes : `apercu` accepte les brouillons, sans filigrane par défaut depuis le 2026-11-03 (option `--filigrane` pour le remettre sur un rendu bloqué) ; `final` refuse toute fiche non validée ou avec une erreur bloquante, y compris une voix manquante ou de test.
- Une vidéo sans voix n'est jamais présentée comme prête, sauf choix éditorial explicite (`narration: false`).
- Les contrôles distinguent bloquants, avertissements et contrôles humains ; la vérification factuelle reste humaine ([controles-qualite.md](controles-qualite.md)).
- Rien n'est jamais publié automatiquement : la chaîne s'arrête au fichier prêt à publier.

## 5. Orchestration : options évaluées

| Option | Coût | Avantages | Limites | Verdict |
|---|---|---|---|---|
| **A. Script local** (`python production/produire.py …`) | 0 € | Simple, hors ligne, aucun compte | Demande Python + ffmpeg installés | ✅ Mode de secours |
| **B. GitHub Actions** (fourni) | 0 € à faible volume | Déjà là, déclenché par l'ajout d'une fiche, aucun serveur | Téléchargement manuel du zip ; minutes limitées en privé (~1 min par fiche) | ✅ **MVP recommandé** |
| **C. n8n auto-hébergé** | ~5–10 €/mois (petit VPS) | Visuel, connecteurs Drive/Gmail/Sheets, boutons d'approbation | Serveur à maintenir (mises à jour, sauvegardes, sécurité) | Phase 3 |
| **D. n8n Cloud** | ~20–25 €/mois (plan d'entrée, quota d'exécutions) | Pas de serveur | Coût fixe élevé pour 1 contenu/jour ; ffmpeg non disponible : le rendu reste sur GitHub Actions | Phase 3, si l'auto-hébergement rebute |
| **E. Make / Zapier** | Gratuit limité, puis ~10–30 €/mois | Simple | Mêmes limites que D, quotas d'opérations | Non retenu |

**Recommandation.** Commencer avec B, garder A en secours. n8n devient utile seulement quand il y a quelque chose à orchestrer *après* le rendu : copier sur Drive, envoyer un e-mail « prêt à relire » avec bouton d'approbation, puis, si les accès API sont obtenus, publier après clic. Cela ne se justifie qu'à partir de plusieurs contenus par jour ou de plusieurs plateformes.

### APIs de publication : ne rien supposer

| Plateforme | Publication par API | Conditions connues (à revérifier) | Mode manuel |
|---|---|---|---|
| Instagram (Reels, carrousels) | Possible | Compte professionnel, application Meta, permission de publication soumise à examen (App Review), quotas quotidiens | Meta Business Suite : programmation gratuite |
| TikTok | Possible | Content Posting API ; tant que l'application n'est pas auditée, les publications sont forcées en privé | TikTok Studio (web) : programmation native |
| YouTube Shorts | Possible | Data API v3 ; un projet non vérifié publie en privé, quota limité par jour | YouTube Studio : programmation native |
| LinkedIn | Restreinte | API de publication réservée aux partenaires ou applications approuvées | Programmation native |

Ces démarches prennent de quelques jours à plusieurs semaines et peuvent être refusées. **Le MVP n'en dépend pas** : les fichiers produits sont conformes aux formats de toutes ces plateformes et se programment à la main en 1 à 2 minutes chacun.

## 6. Voix off

Voix générée automatiquement à partir des textes de la fiche, phrase par phrase, avec un fournisseur interchangeable (Piper gratuit par défaut, OpenAI, ElevenLabs, enregistrement manuel). Les scènes s'allongent pour ne jamais couper une phrase et les sous-titres suivent les temps réels. Détails, comparatif des coûts, secrets et mode manuel : [voix-off.md](voix-off.md).

Les plateformes exigent de signaler certains contenus générés par IA : point inclus dans la checklist humaine.

## 7. Ce qui est opérationnel / ce qui reste à configurer

**Opérationnel**

- Modèle de fiche FR/EN, consignes pour ChatGPT, exemple fictif.
- `production/produire.py` : contrôles renforcés, carrousels 1080×1350, vidéos 1080×1920 animées **avec voix**, sous-titres synchronisés, légendes, métadonnées, script de voix off, miniature, images d'inspection (planche, aperçu mobile, zones TikTok / Reels / Shorts), rapport qualité en trois niveaux.
- Voix Piper gratuite (FR et EN) pour les aperçus ; intégrations OpenAI et ElevenLabs écrites et testées avec des réponses simulées (requête, gestion des erreurs), **jamais appelées avec une vraie clé : non validées en production**. Aucune voix n'est validée à l'oreille pour la publication.
- Cache des voix persistant entre exécutions GitHub (aucune phrase payée deux fois).
- Workflows GitHub : « Aperçu des contenus » (automatique) et « Validation finale » (manuel, refuse ce qui n'est pas prêt).
- 35 tests automatisés.

**À configurer par le propriétaire**

1. Choisir la voix de publication (voir [voix-off.md](voix-off.md)). Pour OpenAI ou ElevenLabs : créer le compte et ajouter le secret GitHub correspondant.
2. Valider ou modifier la charte (`production/charte.yaml`) et les limites des plateformes (`production/plateformes.yaml`).
3. Créer les comptes sur les plateformes retenues et tester une publication manuelle.
4. Pour le mode local de secours : Python 3.10+, ffmpeg, `pip install -r production/requirements.txt -r production/requirements-voix.txt`, `python production/telecharger_voix.py`.

**Points à arbitrer par la direction éditoriale** : charte graphique, structure type des scènes, appel à l'action, politique de hashtags, voix publiée, plateformes et rythme de publication.

## 8. Feuille de route

| Phase | Contenu | Prérequis |
|---|---|---|
| **0 — MVP** (cette PR) | Fiche → fichiers prêts à publier, publication manuelle | Aucun |
| **1 — Rodage** (2–4 semaines) | 10 à 20 vraies fiches, ajustement de la charte et des durées, choix de la voix | Charte et plateformes arbitrées |
| **2 — Confort** | ✅ Voix de synthèse automatique (fait). Restent : sous-titres incrustés, copie automatique vers Drive, e-mail « prêt à relire » | Choix de la voix de publication |
| **3 — Orchestration** | n8n : approbation par bouton, puis publication API **après clic humain** | Accès API accordés, ≥ 2 contenus/jour |

## 9. Risques et parades

| Risque | Parade |
|---|---|
| Erreur factuelle publiée | Blocage des fiches non validées ; source visible sur chaque contenu ; relecture humaine obligatoire |
| Panne de GitHub Actions ou du script | Mode local ; à défaut, mode manuel décrit dans [guide-quotidien.md](guide-quotidien.md) |
| Changement des règles ou des APIs des plateformes | Aucune dépendance aux APIs dans le MVP |
| Fuite de secrets | Aucun secret nécessaire au MVP ; `.env` ignoré par Git ; secrets futurs dans *Settings → Secrets* de GitHub |
| Droits sur musiques, polices, images | Police Inter sous licence libre OFL ; musique uniquement depuis les bibliothèques des plateformes ; pas d'images tierces dans le MVP |
| Texte trop long qui déborde | Réduction automatique de la taille, puis alerte dans le rapport qualité |
| Dépendance à une seule personne | Tout est documenté et versionné ; aucune configuration cachée |

## 10. Arborescence ajoutée

```
.github/workflows/apercu.yml       Aperçu automatique (brouillons acceptés, sans filigrane)
.github/workflows/validation-finale.yml  Rendu final manuel (refuse ce qui n'est pas prêt)
.env.example                       Modèle de fichier de clés local (le vrai .env n'est jamais versionné)
contenus/fiches/                   Fiches à produire (une par sujet)
contenus/publie/                   Fiches publiées (archive)
contenus/exemples/                 Exemple fictif de test
docs/technique/                    Architecture, contrôles qualité, guide quotidien, consignes ChatGPT
modeles/fiche-contenu.yaml         Modèle de fiche FR/EN
production/produire.py             Point d'entrée
production/charte.yaml             Couleurs, polices, formats, zones de sécurité
production/plateformes.yaml        Limites et zones d'interface par plateforme
production/tts.yaml                Fournisseur et voix FR/EN, lexique de prononciation
production/telecharger_voix.py     Téléchargement des voix Piper (production/voix/, non versionné)
production/lmec/                   Code (fiche, rendu, vidéo, carrousel, textes, qualité, tts, narration, inspection)
production/tests/                  Tests automatiques
```
