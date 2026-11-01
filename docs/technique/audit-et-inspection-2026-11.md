# Audit technique et inspection du premier sujet — LMEC-2026-003

*1er novembre 2026. Fiche inspectée : `contenus/fiches/2026-11-pic-population-mondiale.yaml` (statut brouillon, non modifiée).*

## 1. Audit de l'existant (après la PR #4)

Aucun problème d'architecture majeur : la séparation fiche → contrôles → rendu → rapport tenait. Les manques ont été comblés par ajout de modules, sans refonte.

| Zone | Constat | Risque | Traitement |
|---|---|---|---|
| `fiche.py` | Date de validation jamais contrôlée ; statut libre ; valeurs du modèle (`https://`) acceptées comme remplies ; textes de scène vides acceptés | Fiche « valide » sans date ni traçabilité | Contrôles structurels renforcés + cohérence date/statut dans `qc.py` |
| `qc.py` | Une seule limite de durée (60 s) pour toutes les plateformes ; erreurs et alertes mélangées ; seule la scène `source` exigée | Faux refus ou faux feu vert selon la plateforme | Trois niveaux séparés ; limites par plateforme dans `plateformes.yaml` ; scènes accroche/chiffre/source/fin exigées |
| Cohérence | Aucun contrôle croisé chiffre clé / graphique / textes FR-EN | Chiffre différent entre FR et EN non détecté | Contrôles de cohérence (voir [controles-qualite.md](controles-qualite.md)) |
| Voix | Un fichier audio fourni à la main ; une vidéo silencieuse ne déclenchait qu'une alerte | **Vidéo sans voix considérée comme prête** | Voix automatique ; absence de voix = bloquant |
| Sous-titres | Temps estimés sur la longueur du texte, pas sur la voix | Désynchronisation | Repères calés sur la durée réelle de chaque phrase |
| Durées | Ne tenaient pas compte du temps d'apparition du texte animé | Texte long à peine affiché | Durée = max(animation + lecture, voix + respiration) |
| Workflow | Un seul workflow, toujours en mode brouillon, code de sortie ambigu | Impossible de distinguer un aperçu d'un fichier à publier | Deux workflows : aperçu (automatique) et validation finale (manuelle, stricte) |
| Zones de sécurité | Marge droite 150 px < interface YouTube Shorts (~190 px) | Texte sous les boutons | Marges portées à haut 250 / bas 480 / droite 190 ; contrôle par plateforme ; images de simulation |
| Sources | Nom de source dans une seule langue | « ONU » affiché dans la version anglaise | Le nom peut désormais être `{fr: …, en: …}` (voir §3, point éditorial) |

## 2. Rendus produits

Rendu d'aperçu FR et EN avec voix Piper, filigrane « brouillon » car la fiche n'est pas validée.

| | FR | EN |
|---|---|---|
| Durée | 46,0 s | 42,5 s |
| Écart vidéo / audio | 0,04 s | 0,03 s |
| Scènes | 7 | 7 |
| Temps de rendu (machine de test) | ≈ 35 s | ≈ 35 s |
| Erreurs bloquantes | 1 : fiche non validée (attendu) | idem |
| Avertissements | 0 | 0 |

## 3. Inspection

| Point demandé | Méthode | Résultat |
|---|---|---|
| Lisibilité mobile | `apercu-mobile.png` (390 px de large, taille réelle) | ✅ Accroches, chiffres et textes lisibles. ⚠️ Pied de page « Source » et ligne « Définition » petits (26–30 px) : lisibles en pause, pas en défilement. Acceptable pour des mentions |
| Débordements, chevauchements | `planche-video.png`, carrousels | ✅ Aucun débordement ni chevauchement détecté (contrôle automatique + visuel) |
| Animations, transitions | Images en cours d'animation | ✅ Apparition mot à mot, compteur, barres décalées, fondus de 0,25 s |
| Lisibilité des chiffres | Planche | ✅ Chiffre clé en très gros corps, séparateurs adaptés à chaque langue (10,3 / 10.3) |
| Graphique | Planche | ✅ Barres à partir de zéro (honnête). ⚠️ Point éditorial : 8,2 / 10,3 / 10,2 donnent des barres proches ; le « pic » se voit peu. Une échelle tronquée serait trompeuse : je ne la propose pas |
| Synchronisation audio / sous-titres | `sous-titres.srt` comparé aux durées de phrase | ✅ Chaque sous-titre commence avec sa phrase ; aucun chevauchement ; aucun sous-titre ne déborde sur la scène suivante |
| Prononciation | Lecture du « texte dit » ; **écoute non faite** (pas d'écoute possible dans mon environnement) | ⚠️ À écouter. Risques identifiés : (1) voyelles nasales mal rendues par la voix Piper FR ; (2) titre anglais « World Population Prospects » lu par la voix française ; (3) « ONU DESA » lu dans la version anglaise ; (4) « mid-2080s » corrigé par le lexique en « mid twenty-eighties » |
| Longueurs FR / EN | Durées par scène | ✅ Écart total 8 % ; aucune scène deux fois plus longue dans une langue |
| Zones TikTok / Reels / Shorts | `zones-*.png` + contrôle automatique | ✅ Tout le contenu reste hors des zones d'interface simulées (valeurs approximatives, à confirmer sur un vrai téléphone) |

## 4. Points éditoriaux à arbitrer (la fiche n'a pas été modifiée)

1. **Nom de la source en anglais** : la fiche indique « ONU DESA, World Population Prospects 2024 » pour les deux langues. Proposition : `nom: {fr: "ONU DESA, World Population Prospects 2024", en: "UN DESA, World Population Prospects 2024"}`.
2. **Voix de la scène source en français** : la voix lit le titre anglais. Proposition : `voix_off: "Source : les Nations unies, perspectives de la population mondiale 2024."` dans la scène source FR.
3. **Répétition dans la scène chiffre FR** : « 10,3 milliards d'humains au maximum. C'est le maximum attendu… ». Proposition : reformuler le texte de la scène, par exemple « C'est le pic attendu par l'ONU… ».
4. **Hashtags** : 4 par langue. YouTube Shorts en conseille 3 au plus (avertissement seulement).
5. **Graphique** : barres proches visuellement (voir §3). Garder tel quel, ou remplacer par une autre série (par exemple la fécondité 3,3 → 2,3, plus parlante en barres).

## 5. Corrections après la revue de JG (1er novembre 2026)

| Demande | Traitement | Tests ajoutés |
|---|---|---|
| Cache TTS dans GitHub Actions | `.cache-tts/` restauré et sauvegardé dans les deux workflows (un cache par fournisseur, sauvegarde même en cas de refus). Empreinte = fournisseur + langue + configuration complète de la voix + modèle Piper + texte exact envoyé | Clé sensible au texte, à la voix, à la vitesse, au modèle, aux consignes, à la langue, au fournisseur et au fichier du modèle Piper ; lexique ; nettoyage ; présence du cache dans les workflows |
| Cohérence des données | Unités lues (nature + échelle, faux ami « billion »), comparaison chiffre clé / graphique après conversion, périodes FR/EN, années du chiffre et des libellés, pourcentages hors bornes, arrondis. Le rapport liste ce qui n'a **pas** pu être vérifié | 13 tests (unités FR/EN, échelles, pourcentage contre valeur, périodes, libellés, arrondis, rapport) |
| Robustesse | Contrôle de type de chaque bloc et champ ; YAML illisible avec ligne et colonne ; filet de sécurité « Structure inattendue » ; une erreur du programme n'arrête pas les autres fiches | 23 cas de types incorrects, 4 YAML mal formés, ~1 600 variantes aléatoires sans plantage, exécution sans trace Python |
| Voix | Piper conservé pour les aperçus. État réel des intégrations documenté : OpenAI et ElevenLabs **jamais appelés avec une vraie clé** | Réponses d'API simulées (sans réseau) : requête envoyée, clé hors du corps, erreurs 401/429/réseau/réponse non audio |
| Plateformes | Référence, date de lecture et statut (`officiel`, `non_confirme`, `estimation`) pour chaque limite. Corrections : légende TikTok 4 000 → 2 200 (API officielle), carrousel 20 → 10 images (API officielle), YouTube 60 hashtags au maximum | Toute limite doit avoir une référence datée ; une erreur fondée sur une limite non officielle le signale |

La fiche démographique n'a pas été modifiée.
