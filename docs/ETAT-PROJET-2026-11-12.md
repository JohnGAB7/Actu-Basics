# État opérationnel du projet ACTU-BASICS · 2026-11-12

Réponse à la demande de ChatGPT sur la PR #17 (commentaire 6837296878). Ce document ne modifie rien dans le dépôt, ne publie rien et ne fusionne aucune PR.

Commit HEAD de la branche `claude/project-thread-1jvp67` au moment de la rédaction : `56c7918` (sera remplacé par le commit qui intègre ce document et la v3.2).

## 1. État global : les chantiers présents dans le dépôt

| Chantier | État | Entrée dans `main` |
| --- | --- | --- |
| Programme éditorial v1.12 | Validé par JG, publié. | Fusionné (PR #14). |
| Pilote Niveau 1 : 5 vidéos de la vague 1 | Validé par JG, rendu. | Fusionné (PR #15). |
| Niveau 1 · lot 1 : leçons S1.01 à S1.05 FR et EN | **Validées par JG le 2026-11-08**, rendues en final en FR et EN. | Non fusionné (dans la PR #17). |
| Niveau 1 · lot 2 : leçons S1.09 à S2.04 FR et EN | **Validées par JG**, rendues en final en FR et EN. | Non fusionné (dans la PR #17). |
| Niveau 1 · lot 3 : leçons S2.06 à S3.05 FR et EN | **Validées par JG**, rendues en final en FR et EN. | Non fusionné (dans la PR #17). |
| Parcours Actuariat · pilote (A0.01, A1.01, A2.01) | **Validé par JG le 2026-11-11**, rendu en final FR et EN. | Non fusionné (dans la PR #17). |
| Parcours Actuariat · six extraits verticaux | **Validés par JG le 2026-11-11**, rendus en final FR et EN. | Non fusionné (dans la PR #17). |
| Parcours Actuariat v3.2 (programme du parcours) | **Proposition** : v3 débattue avec Perplexity (2026-11-12), relue par ChatGPT (2026-11-12), retours intégrés. En attente de validation JG. | Non fusionné. |

**Décompte vérifiable** : 44 fiches `.yaml`, dont **42 en statut `valide`** (par JG, avec date) et **2 en statut `brouillon`** (`2026-11-lancement-actu-basics`, `2026-11-pic-population-mondiale`). Les leçons S1.01 à S1.05 sont donc validées, contrairement à ce qu'annonce la description de la PR #17.

Les deux brouillons restants ne sont pas des leçons éditoriales : ce sont une fiche de lancement et un repère qui n'ont pas été remis à l'ordre du jour.

## 2. Production éditoriale

| Code | Langue | Statut fiche | Statut rendu final | Dossier de livraison |
| --- | --- | --- | --- | --- |
| S1.01 à S1.05 (5) | FR + EN | valide | livré | `/mnt/project-files/actu-basics/niveau-1/` |
| S1.09 à S2.04 (8) | FR + EN | valide | livré | idem |
| S2.06 à S3.05 (10) | FR + EN | valide | livré | idem |
| A0.01, A1.01, A2.01 | FR + EN | valide | livré | `/mnt/project-files/actu-basics/actuariat/pilote/final/` |
| A0.01-x1/x2, A1.01-x1/x2, A2.01-x1/x2 | FR + EN | valide | livré | `/mnt/project-files/actu-basics/actuariat/pilote/extraits/final/` |

- Toutes les leçons rendues en final passent par le mode `final` de `produire.py` (refus de toute fiche non validée ou avec une erreur bloquante).
- Les relectures de ChatGPT (3 pour le pilote Actuariat, plusieurs pour les lots du Niveau 1) sont intégrées, les intégrations sont écrites dans les commentaires de la PR #17.
- Les archives par langue sont créées : `ACTU-BASICS-Actuariat-pilote-FR.zip` et `-EN.zip`, `ACTU-BASICS-Actuariat-extraits-FR.zip` et `-EN.zip`, et les zips des lots Niveau 1.
- Les dossiers partagés (`/mnt/project-files/actu-basics/…`) contiennent les vidéos MP4, miniatures JPG, sous-titres SRT, titres et descriptions à coller.
- `LISEZMOI.md` du dossier partagé est à jour.
- **Aucune vidéo n'a été publiée sur les chaînes** : JG publie lui-même.

## 3. Technique

**Moteur de production**
- Fichier principal : `production/produire.py` (modes aperçu et final).
- Évolutions depuis le pilote : un rendu horizontal 16:9 YouTube depuis la fiche verticale (`--horizontal`), les chapitres YouTube, les fiches en une seule langue, la double échelle et les animations de courbe, l'étiquetage des valeurs de barres (`etiquettes_valeurs`), des cartes de quatre sources raccourcies pour le vertical, le respect des zones de sécurité par plateforme.
- La règle est respectée : **chaque évolution du moteur passe par une branche et une PR**, jamais directement sur `main`.

**Tests**
- Commande de référence : `cd production && python3 -m pytest -q tests`.
- Dernier passage réussi en local : 254 tests, environ 21 minutes (avant la série actuariat).
- Un nouveau passage complet devrait être relancé avant la fusion. Je n'en ai pas de preuve CI datée pour le commit HEAD de la branche actuelle.

**CI**
- Le dépôt a volontairement un CI restreint : `[skip ci]` sur tous les commits de contenu, et les rendus vidéo tournent uniquement en local ou sur lancement manuel. Les crédits GitHub Actions sont ainsi préservés, comme JG l'a demandé.
- Trois workflows présents : `apercu.yml`, `validation-finale.yml` (déclenchement manuel) et `provenance-voix.yml` (sur PR).
- Un workflow déclenché automatiquement sur ce commit n'apparaît donc pas : ce n'est pas un signe de défaut, c'est la politique du dépôt.

**Dette technique connue**
- Documents de relecture (PDF des scripts) générés par un générateur à part, qui a provoqué plusieurs faux problèmes vus par les relecteurs (artéfacts de rendu plutôt qu'erreurs du contenu). À factoriser quand une occasion se présente.
- Trois rattachements d'examen marqués **à vérifier** dans la v3.2 : les syllabi CS2, CM1, CM2 (IFoA 2026) n'ont pas pu être lus à la source, et la date d'entrée en vigueur du PCPA de la CAS n'est pas confirmée.
- Avant toute annonce publique d'un calendrier Actuariat, l'hébergement des fiches PDF et des fichiers de tableur/R/Python doit être choisi.

## 4. Parcours Actuariat v3.2 : ce qui existe réellement

Au stade de **document de proposition** :
- `docs/actuariat/PARCOURS-ACTUARIAT-v3.md` (v3.2, intégrant le retour de ChatGPT du 2026-11-12).
- `docs/actuariat/PROMPT-debat-perplexity-v3.md` (consigne du débat Perplexity).
- `docs/actuariat/PROMPT-relecture-chatgpt-v3.md` (consigne de la relecture ChatGPT).
- Copies dans `/mnt/project-files/actu-basics/actuariat/`.

**Au stade de proposition seulement** :
- A2b (statistique pour l'assurance) : pas de fiche écrite, pas de rendu.
- Les deux nouvelles vidéos A0 (différences SOA/CAS/IFoA/France, et comment lire un syllabus) : pas de fiche écrite.
- Les vidéos d'exercices de type examen : pas de fiche écrite.
- Les fiches PDF par leçon : pas produites.
- Les fichiers tableur, R et Python : pas produits.

Le pilote (A0.01, A1.01, A2.01, et leurs six extraits) est le seul contenu Actuariat réellement livré.

## 5. Priorités et décisions en attente

**Attend une décision de JG**
1. **Fusion ou non de la PR #17** et calendrier de publication des vidéos Niveau 1 et pilote Actuariat.
2. **Validation de la v3.2** du parcours Actuariat (ou liste des points à corriger).
3. **Suite de la production Actuariat** : terminer A0 (A0.02 à A0.05, incluant les deux nouvelles vidéos d'orientation) ou ouvrir A3.01 comme prévu dans la v2.
4. **Hébergement des fiches PDF et des fichiers de manipulation** : description YouTube, dépôt public, autre.
5. **Reprise du lot 4 du Niveau 1** après le pilote Actuariat, comme prévu.

**Pas d'action nécessaire de JG**
- Le moteur, les tests, la structure des fiches, les workflows CI sont en ordre.
- Rien ne sera publié, fusionné ou modifié sur `main` sans accord explicite de JG.

## 6. Ma lecture

Le projet n'est pas éclaté : les 51 commits de la PR #17 racontent une seule histoire, du lot 1 du Niveau 1 jusqu'à la v3.2 du parcours Actuariat, en passant par le pilote Actuariat livré. Mais ChatGPT a raison sur un point : la **PR #17 est devenue trop large** pour une relecture, et son titre et sa description ne reflètent plus son contenu.

Deux options s'offrent à JG :
- **Continuer sur cette PR** jusqu'à la validation de la v3.2 et de la fusion globale (simple, mais une relecture par PR est perdue).
- **Scinder la PR #17** en lots déjà prêts à fusionner (Niveau 1 lots 1, 2 et 3 ; pilote Actuariat ; v3.2) et laisser cette PR ne contenir que la v3.2 ou le prochain chantier. Plus de travail, mais historique plus lisible et relecture par PR préservée.

Je ne prends aucune initiative sur ce choix.

---

Document rédigé par Claude. Ni modification du dépôt, ni publication, ni fusion.
