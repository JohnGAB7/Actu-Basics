# Conformance au doc d'architecture — état sur `claude/library-v2`

Tableau de correspondance entre le document `architecture-site-cible.md` (ChatGPT)
et l'implémentation sur la branche `claude/library-v2` (Claude).

## Principes non négociables

| Principe | État | Détail |
|---|---|---|
| Une source de vérité structurée | ✅ | YAML des fiches + `contenus/parcours.yaml` ; HTML généré. |
| Identifiants stables | ✅ | Codes `M0-01`, `S4-07`, `A0-01`, slugs parcours `stats-probas`, etc. |
| Séparation des objets (unité ≠ leçon ≠ vidéo) | 🟡 | Leçon ↔ vidéo séparées (clé `publication:` optionnelle). Unité du programme ≠ leçon : **pas encore modélisée** (le programme existe dans `programme/catalogue/*.txt` mais n'est pas encore relu par le générateur). |
| Bilinguisme natif | ✅ | FR/EN reliés, canonical + hreflang fr/en/x-default sur chaque page. |
| Disponibilité explicite | ✅ (partiel) | Badges « Fiche disponible », « Vidéo en ligne » (si URL publiée). Statuts de parcours : `en_cours` / `a_venir` / `complet`. |
| Pas de liens inventés | ✅ | Bloc vidéo masqué quand aucune URL (ligne de statut compacte « Vidéo en préparation », sans faux lecteur). |
| Progression cohérente | 🟡 | Parcours ordonnés par module (M0 → S1 → S2 → S3 → S4). Les prérequis des fiches ne sont pas encore utilisés pour imposer un ordre. |
| Accessibilité et mobile | ✅ | `:focus-visible`, `skip-link`, menu mobile avec aria-expanded + Escape, breakpoints 850 et 600px. |
| Publication contrôlée | ✅ | Aucune fusion `main` ni modif GitHub Pages sans accord explicite. |

## Pages prévues vs implémentées

| Vue | État |
|---|---|
| Accueil FR+EN | ✅ (manuel) |
| Index des parcours | ✅ (généré) |
| Page individuelle de chaque parcours | ✅ (généré) |
| Vue d'ensemble du programme | ❌ (à faire, prochain lot) |
| Bibliothèque leçons avec recherche, filtres, états | ✅ (généré, groupé par module + badges + jump-nav) |
| Page individuelle d'une leçon | ✅ (générée, avec slot vidéo) |
| Bibliothèque vidéo | ❌ (à faire quand les URLs vidéo arriveront) |
| Dossiers et actualités | ❌ (hors scope de ce lot) |
| À propos, méthode, mentions légales | ✅ (À propos manuel ; méthode + mentions à ajouter) |

## Modèle de données

Étape déjà franchie :
- Contenu pédagogique (fiche YAML) : conforme, enrichi d'une clé **optionnelle** `publication:` pour relier les médias.
- Parcours : conforme (slug, titres FR/EN, sous-titre, description, modules ordonnés, statut).

Étapes à franchir pour l'achèvement :
- **Unité du programme** : parser `programme/catalogue/*.txt` et produire une entité `programme_unit` distincte, pour que la bibliothèque affiche « unité prévue » vs « leçon disponible ».
- **Média** (identifiant distinct du contenu, type, langue, format, fournisseur, état) : pour l'instant les URLs sont inline dans `publication:` ; suffisant tant qu'une leçon = 1 vidéo YouTube + 1 vidéo TikTok. À étendre quand il faudra plusieurs médias par leçon (chapitres, transcription séparée, sous-titres).
- **Ressource pédagogique** (PDF, dataset, notebook) : non implémentée. À ajouter via une clé `ressources:` optionnelle dans la fiche.

## Schéma de la clé optionnelle `publication:` dans une fiche

Ajouter ce bloc à la racine d'un YAML de fiche existante et relancer `python3 tools/build_lessons.py` : le bloc vidéo apparaît automatiquement sur la leçon.

```yaml
publication:
  youtube:
    fr: "https://youtu.be/VIDEO_ID_FR"
    en: "https://youtu.be/VIDEO_ID_EN"
  tiktok:
    fr: "https://www.tiktok.com/@actu_basics_fr/video/XXXXX"
    en: "https://www.tiktok.com/@actu_basics/video/YYYYY"
  date: "2026-11-20"   # date de mise en ligne (information)
```

Toutes les sous-clés sont optionnelles. Si **aucune** n'est renseignée, la section vidéo n'affiche pas de lecteur vide : elle rend une ligne de statut « Vidéo en préparation ». Si une plate-forme ou une langue est renseignée et l'autre pas, le slot manquant affiche « Non disponible — en préparation » (jamais de faux lecteur).

URLs YouTube acceptées : `https://youtu.be/XYZ`, `https://www.youtube.com/watch?v=XYZ`, `https://www.youtube.com/shorts/XYZ`, `https://www.youtube.com/embed/XYZ`.

## Lots du doc de ChatGPT — où nous en sommes

| Lot | État |
|---|---|
| A — fondations et modèle | 🟡 partiellement : les schémas fiche + parcours sont stables ; schémas programme/media/ressource à formaliser. |
| B — programme et parcours | 🟡 parcours en place ; programme à parser. |
| C — pages de contenu complètes | 🟡 gabarit leçon unifié FR/EN, slot vidéo en place ; graphiques et KaTeX à finaliser. |
| D — découverte et navigation | 🟡 recherche + filtre + jump-nav en place ; accueil et liens croisés à mettre à jour selon disponibilité réelle ; bibliothèque vidéo à ajouter quand les URLs arrivent. |
| E — qualité et livraison | ❌ tests automatiques, audit visuel, mise à jour SITE-README à faire. |

## Critère de fin

Le critère formulé par ChatGPT — « ajouter une leçon = ajouter sa fiche et ses médias, sans toucher aux gabarits » — est **atteint pour une leçon ordinaire** sur `claude/library-v2`. Ajouter sa vidéo plus tard = éditer la clé `publication:` du YAML + `python3 tools/build_lessons.py`. Ajouter un nouveau module = créer les fiches et le référencer dans `parcours.yaml`. Ajouter un nouveau parcours = une entrée dans `parcours.yaml`.
