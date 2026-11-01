# ACTU-BASICS — guide d'utilisation des logos

## Ressources officielles
- `logo-light.webp` : utiliser sur les fonds clairs ou blancs.
- `logo-dark.webp` : utiliser sur les fonds sombres, notamment bleu nuit.

## Slogan
- Français : **Éveiller par les chiffres.**
- Anglais : **Enlightening through numbers.**

## Règles obligatoires pour les productions
1. Utiliser les fichiers de logo fournis, jamais une reconstitution générée par IA.
2. Choisir la variante offrant le meilleur contraste avec le fond.
3. Préserver les proportions, les couleurs et la zone de protection du logo.
4. Ne pas étirer, incliner, recadrer, recolorer ou ajouter d'effets au logo.
5. Ne pas placer le logo sur un texte, un graphique ou une zone visuellement chargée.
6. Prévoir une présence cohérente du logo dans chaque vidéo, chaque carrousel et chaque couverture ACTU-BASICS. Par défaut, le placer discrètement en fin de vidéo et sur une couverture ou une dernière slide de carrousel ; ne pas le répéter à chaque scène si cela nuit à la lisibilité.
7. Le slogan peut accompagner le logo sur les couvertures et supports institutionnels. Il n'est pas obligatoire sur chaque écran.
8. Conserver des marges adaptées aux interfaces TikTok, Instagram et YouTube Shorts.

## Contrôle qualité
Avant de déclarer un rendu prêt :
- vérifier que le logo correspond au fond ;
- vérifier qu'il est net, non déformé et entièrement visible ;
- vérifier qu'il reste dans les zones de sécurité des plateformes ;
- vérifier que le slogan affiché est exactement celui de la langue de l'édition.

## Intégration technique à réaliser
Le moteur de rendu doit charger ces assets depuis `assets/brand/actu-basics/`. Prévoir un paramètre de configuration pour activer/désactiver le logo et ajuster sa position/taille sans modifier les fichiers sources. Ajouter un test de présence des fichiers et un contrôle visuel dans les aperçus.
