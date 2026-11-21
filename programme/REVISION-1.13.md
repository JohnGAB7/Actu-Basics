# Révision 1.13 du programme : des vidéos longues qui regroupent les notions

**Statut : proposition de Claude, à valider par JG. Relecture éditoriale des titres : ChatGPT.**
Demande de JG du 21/11/2026 : des vidéos longues, dont chacune aborde plusieurs concepts quand c'est cohérent, et plus de vidéos courtes qui définissent un seul concept. YouTube devient l'endroit où l'on se forme de façon complète. Les Shorts servent seulement à rediriger vers les vidéos complètes.

## Ce qui change

| | V1.12 | V1.13 |
|---|---|---|
| Unité publiée | 320 vidéos de 3 à 16 min, une notion chacune | **93 épisodes** (89 au 21/11, 4 ajoutés le 22/11 pour le niveau expert), qui regroupent 2 à 7 notions |
| Rôle des 320 entrées | Une entrée = une vidéo | Une entrée = un **chapitre** d'un épisode (objectifs, intuition, exemple, exercice inchangés) |
| Format principal | `educational` vertical | `youtube_lesson` 16:9, avec des chapitres YouTube horodatés |
| Formats courts | SHORT dérivés, hors catalogue | Shorts et TikTok = **bandes-annonces** d'un épisode, qui renvoient vers lui. Plus de vidéo courte qui définit seule une notion |
| Lien avec la plateforme | Aucun | Correspondance interne avec un bloc Programme-B (champ `programme_b`) pour vérifier les sources ; aucun lien public, le site ACTU-BASICS se suffit à lui-même |

Le volume total est d'environ 44 h (42 h pour les 320 entrées de la V1.12, plus les 13 chapitres ajoutés le 22/11). C'est une estimation haute, car un épisode n'a qu'une ouverture et qu'une fin, au lieu d'une par notion. Les durées seront recalculées après l'écriture des premiers scripts.

## Ce qui ne change pas

Les 320 entrées, leurs prérequis et leurs contrôles. Les 4 niveaux, les 3 piliers et la boîte à outils. La rigueur de la V1.12 : intuition d'abord, formule expliquée, exercice corrigé, chiffres recalculés par le moteur, double relecture. Et le bilinguisme FR et EN, publiés en même temps.

## Règles de regroupement

1. Un épisode regroupe des notions qui répondent à **une même question** (« pourquoi un échantillon peut mentir », « comment tester une hypothèse »).
2. Il reste dans un seul module de la V1.12, sauf exception justifiée (pilier Quotidien : Q9 rejoint l'argent, Q15 rejoint les risques et les pièges de l'intuition).
3. **Ordre pédagogique contrôlé** : dans le cursus, aucun chapitre ne demande une notion traitée plus loin (script `episodes.py`).
4. Durée cible de 20 à 45 min, bornes contrôlées entre 10 et 50 min. Au-delà, l'épisode est coupé en deux.
5. Chaque chapitre garde son exercice. L'épisode se termine par un exercice de synthèse qui mobilise plusieurs chapitres.
6. **Complétude** : chaque fiche de conception liste toutes les notions utilisées, et pour chacune l'épisode antérieur qui l'enseigne ou le rappel intégré. Sans l'un ni l'autre, pas de script (champ `notions_utilisees`).

## Structure d'un épisode

1. **Ouverture (15 à 30 s)** : la question concrète de l'épisode, montrée et non seulement dite, avec du mouvement dès la première image.
2. **Accueil (10 à 20 s)** : saluer, remercier le spectateur d'être là, dire ce qu'il saura faire à la fin.
3. **Plan à l'écran** : les chapitres, qui deviennent les chapitres YouTube.
4. **Chaque chapitre** suit l'arc de la V1.12 : intuition, exemple minuscule, raisonnement à l'écran, formule expliquée, exercice avec pause, correction.
5. **Synthèse** : comment les notions s'articulent, avec un schéma récapitulatif.
6. **Exercice de synthèse**, puis sa correction.
7. **Clôture (30 à 45 s)** : rappel en une phrase, puis orientation (épisode suivant, autres épisodes utiles, page de l'épisode sur le site) et invitations à s'abonner, liker et partager, et offre d'aide gratuite aux exercices de l'épisode (en commentaire sous la vidéo), une seule fois, sans formule qui culpabilise.
8. **Fin de marque (3 à 5 s)** : logo officiel et slogan de la langue de l'édition, sous l'écran de fin YouTube.

Le moteur bloque un épisode long sans accueil après l'ouverture ou sans clôture complète (`production/charte.yaml`, `parcours_spectateur`).

**Logo mobile.** Plus de nom de marque ni de logo fixe pendant la vidéo : le logo officiel glisse lentement dans le bandeau du haut, sans déformation ni recoloration, et peut être coupé au profit du filigrane YouTube Studio (`logo.mobile` dans la charte).

## Formats courts : bandes-annonces seulement

- Chaque épisode produit 1 à 3 Shorts de 30 à 60 s, extraits de son meilleur moment (un paradoxe, un résultat surprenant).
- Un Short ne commence jamais par un accueil et se termine toujours par l'épisode complet, cité par son titre : vidéo associée sur YouTube Shorts, « lien en bio » sur TikTok.
- Contrôles anti-blocage conservés pour toutes les plateformes : première image pleine, aucun plan figé plus de 2 s, aucune marque fixe à l'écran (logo mobile), étiquette « contenu généré par IA », pas de lien en légende, vocabulaire sensible cadré (voir le document de diagnostic TikTok du 21/11).

## Sources : ce qui est couvert et ce qui manque

Chaque épisode s'appuie sur le registre des sources de Programme-B (`docs/SOURCE-REGISTER.md`, version 1.0 du 21/11/2026), par l'intermédiaire de son champ `programme_b`. Une page de catalogue universitaire situe le niveau mais ne permet pas de vérifier un contenu : seuls les cours détaillés (notes, polycopiés, manuels ouverts) comptent comme sources de vérification.

| Bloc Programme-B | Épisodes concernés | Cours détaillés déjà au registre | État |
|---|---|---|---|
| B01, B03, B04, B05 | EP-M01 à EP-M05 | OpenStax (S18 à S21, S31, S32), MIT 18.06, 18.065, 18.01SC, 18.02SC, 18.03SC, 18.100B, Strang, Axler | Couvert |
| B08 Probabilités | EP-S4A à EP-S5D, une partie du Quotidien | Harvard Stat 110 (S03, S46), MIT 18.05 (S04, S48), MIT 6.041SC (S47) | Couvert |
| B09 Processus | EP-S16 | MIT 18.445, 6.262, 15.070J (S50 à S53) | Couvert |
| B10 Descriptif et sondage | EP-S1A à EP-S3C, EP-S6B | MIT 15.075J (S54), NIST e-Handbook (S55), Lohr (S56) | Couvert |
| B11 Inférence | EP-S6A, EP-S7A à EP-S8C, EP-S11A, EP-S12A, EP-S12B | MIT 18.05 seulement (niveau introductif) | Partiel : manque un cours de statistique mathématique et un cours bayésien |
| B12 Régression et modèles | EP-S9A à EP-S10B, EP-S11C | MIT 18.05 seulement | Partiel : manquent la régression multiple, les GLM et les modèles mixtes |
| B13 Multivarié | EP-S13A à EP-S13D | MIT 18.065 et 18.657 | Partiel : manquent l'analyse des correspondances, les copules et les données fonctionnelles |
| B14 Causalité et expériences | EP-S9D, EP-E7A, EP-E7B | Aucun | Lacune |
| B15 Apprentissage | EP-S17A à EP-S17D, EP-S19A à EP-S19C, EP-Q5 | MIT 18.657 (théorie seulement) | Partiel : manquent les arbres, le boosting et les réseaux de neurones |
| B16 Séries temporelles | EP-S14A à EP-S14C, EP-E8A, EP-E8B | Aucun | Lacune |
| B17 Reproductibilité | EP-S11B, EP-S19C | Documentation technique seulement | Lacune |
| B18 Actuariat et survie | EP-S15, pilier A | Aucun | Lacune |
| B19 Économétrie | EP-E1 à EP-E11D | Aucun | Lacune |
| B20 Théorie avancée | EP-S18A, EP-S18B | MIT 18.100B et 18.657 | Partiel |
| Quotidien (chiffres réels) | EP-Q1 à EP-Q13 | Sans objet : sources statistiques officielles (Insee, Eurostat, OMS, etc.), vérifiées et datées à la préparation, selon le protocole V1.12 | Par fiche |

Règle : aucun épisode marqué « lacune » ou « partiel » ne passe en fiche de conception avant que le registre contienne au moins un cours détaillé pour ses chapitres. JG fournit ou valide ces cours spécialisés.

## À décider ensuite

- Valider les 93 épisodes et leurs titres (les titres restent des titres de travail, relus par ChatGPT).
- L'ordre de publication. Proposition : alterner un épisode du cursus et un épisode du Quotidien.
- Les 10 fiches du lot 5 déjà produites deviennent des extraits ou des Shorts des épisodes correspondants (EP-S2A, EP-S3B, EP-Q2, EP-Q3). Le pilier A (Actuariat) garde son parcours propre, hors de ces 89 épisodes, et suivra les mêmes règles.
- Le PDF V1.13 est reconstruit (`PROGRAMME_EDITORIAL_ACTU-BASICS_v1-13.pdf`) : synthèse, sections 2.4, 2.5, 2.9, 7 et 10.14 réécrites, épisode affiché sur chaque chapitre.

## Les 93 épisodes

Tableau produit par `python programme/episodes.py`. Durées : somme des fourchettes des chapitres de la V1.12.


