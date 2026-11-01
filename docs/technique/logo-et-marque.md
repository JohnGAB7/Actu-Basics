# Logo et marque ACTU-BASICS dans les productions

Règles de marque : `00_STRATEGY/BRAND_IDENTITY.md` et `assets/brand/actu-basics/BRAND_GUIDELINES.md`. Fichiers : [`assets/brand/actu-basics/`](../../assets/brand/actu-basics/LISEZMOI.md).

## Où apparaît le logo (réglages par défaut)

| Support | Emplacement | Taille | Avec slogan |
|---|---|---|---|
| Vidéo | Scène de fin, centré entre l'appel à l'action et le slogan | 440 px (réduit jusqu'à 300 px si le texte est long) | Oui |
| Carrousel | Dernière diapositive (fin), même mise en page | 400 px (min. 280) | Oui |
| Couverture (`miniature.jpg`) | En haut à droite, dans la zone de sécurité | 260 px | Non |

Conformément au guide de marque, le logo n'est pas répété sur chaque scène. Le nom « ACTU-BASICS » reste écrit en petit en haut de chaque image. Il est masqué quand le logo occupe déjà le haut de l'image.

## Réglages (sans code) — `production/charte.yaml`, section `logo`

- `actif: false` : retire le logo partout (le rapport le signale).
- `variante: auto | clair | sombre` : `auto` choisit selon la luminosité réelle du fond sous le logo. La variante claire va sur un fond clair, la sombre sur un fond sombre.
- `zone_protection` : espace libre exigé autour du logo, en part de sa largeur (8 % par défaut).
- `video.scenes`, `carrousel.scenes` : scènes qui portent le logo. Par exemple, ajouter `accroche` dans `carrousel.scenes` place aussi le logo sur la couverture du carrousel.
- `largeur_px`, `largeur_min_px`, `largeur_autres_px` : tailles, en pixels de l'image (1080 px de large).
- `position` : `haut_gauche`, `haut_centre`, `haut_droite`, `centre`, `bas_gauche`, `bas_centre` ou `bas_droite`. Le logo est toujours ancré **dans** la zone de sécurité. Le texte de la scène se décale pour lui laisser la place. En bas, le logo reste au-dessus de la ligne « Source ».
- `marge_px` : retrait supplémentaire depuis le bord de la zone de sécurité.
- `slogan: true/false` : slogan sous le logo dans la scène de fin.

Les slogans sont dans la section `slogan` de la charte. Un test et le contrôle qualité vérifient qu'ils sont **exactement** « Éveiller par les chiffres. » et « Enlightening through numbers. ».

## Contrôles automatiques (rapport qualité)

| Contrôle | Gravité |
|---|---|
| Fichier du logo absent (rien n'est dessiné à sa place) | ❌ avant tout rendu |
| Slogan différent du slogan officiel | ❌ |
| Logo prévu mais absent d'une image | ❌ |
| Variante inadaptée au fond (claire sur fond sombre, ou l'inverse) | ❌ |
| Texte, graphique ou pied de page dans la zone de protection du logo | ❌ |
| Logo coupé par le bord de l'image | ❌ |
| Logo sous l'interface TikTok / Reels / Shorts (vidéo, couverture) ou hors des marges (carrousel) | ⚠️ |
| Logo agrandi au-delà de la résolution du fichier (flou) | ⚠️ |
| Logo de moins de 90 px à l'écran d'un téléphone | ⚠️ |
| Ancien nom ou ancienne signature (« Le Monde en chiffres », « un chiffre à la fois »…) dans les textes de la fiche | ⚠️ (correction éditoriale) |

Le rapport indique, pour chaque logo posé, la variante, la taille et la luminosité du fond.

## Vérification visuelle

`inspection/logo-mobile.png` montre chaque image portant le logo, à la taille d'un téléphone (390 px de large), avec la zone de protection encadrée en vert. Les images `zones-*.png` montrent la scène de fin sous l'interface simulée des plateformes.
