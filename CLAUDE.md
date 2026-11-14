# Instructions de marque — ACTU-BASICS

Ce dépôt porte désormais la marque ACTU-BASICS. « Le Monde en chiffres / The World in Numbers » était le nom de travail précédent du même projet.

Avant toute modification du moteur de rendu ou production de contenu :
- lire `00_STRATEGY/BRAND_IDENTITY.md` ;
- lire `assets/brand/actu-basics/BRAND_GUIDELINES.md` ;
- utiliser les logos officiels présents dans `assets/brand/actu-basics/` ;
- pour une fiche pédagogique (statistiques, probabilités) : lire `00_STRATEGY/ARCHITECTURE_EDITORIALE.md` et `docs/technique/fiches-pedagogiques.md` ;
- respecter les slogans : FR « Éveiller par les chiffres. » ; EN « Enlightening through numbers. ».

Ne jamais générer une approximation du logo, le déformer ou modifier ses couleurs. Utiliser la variante claire sur fond clair et la variante sombre sur fond sombre. Prévoir une intégration configurable dans les vidéos, carrousels et couvertures, avec vérification des zones de sécurité et de la lisibilité mobile.

Ne pas fusionner automatiquement ces changements. Toute modification du moteur de rendu doit passer par une branche et une pull request.

Parcours Actuariat (pilier A) : l'entreprise fictive des exemples s'appelle « JG's Holding » (demande de JG, 2026-11-11), toujours annoncée comme fictive. Les vidéos sortent en français et en anglais en même temps (décision de JG, 2026-11-11, qui remplace « anglais d'abord »).

Palette vidéo (décision de JG, 2026-11-14) : la playlist « Statistiques — les bases » reste dans l'ancienne palette (bleu nuit + jaune) jusqu'à S1-12 inclus, ainsi que M0. À partir du pilier A (A0-01 et suivantes), chaque nouvelle fiche porte en tête `palette_video: site` pour adopter la palette du site (bleu profond `#0f2130`, ivoire `#f8f6ef`, or mat `#c89046`, teal `#1c7a84`). La bascule tombe sur une frontière de pilier, pour lire comme « nouvelle saison » et non comme une incohérence. Les palettes nommées sont définies dans `production/charte.yaml` (section `palettes:`).

Voix off FR — sigles (décision de JG, 2026-11-14) : pour toute nouvelle fiche, un sigle (INSEE, BIT, Dares, PIB, IPC, OCDE, ONU, UE, …) est écrit en toutes lettres dans la `voix_off`, à sa première occurrence dans la vidéo : « l'Insee, l'Institut national de la statistique et des études économiques, … ». Les occurrences suivantes peuvent reprendre le sigle seul. Le texte à l'écran (`texte`, cartes, étiquettes) peut rester au sigle. Cette règle ne s'applique **pas** rétroactivement aux fiches déjà publiées. Côté EN, la règle habituelle reste : développer à la première occurrence si l'audience EN ne connaît pas le sigle (Insee, Dares, …).
