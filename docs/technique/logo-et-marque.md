# Logo et marque ACTU-BASICS dans les productions

Règles de marque : `00_STRATEGY/BRAND_IDENTITY.md` et `assets/brand/actu-basics/BRAND_GUIDELINES.md`. Fichiers : [`assets/brand/actu-basics/`](../../assets/brand/actu-basics/LISEZMOI.md).

## Où apparaît le logo (réglages par défaut)

Chaque langue a son logo, qui porte son slogan : « ÉVEILLER PAR LES CHIFFRES » en français, « ENLIGHTENING THROUGH NUMBERS » en anglais. Pour chaque langue, la variante claire ou sombre est choisie selon le fond.

| Support | Emplacement | Taille | Slogan écrit en plus |
|---|---|---|---|
| Vidéo et cours 16:9, pendant la vidéo | **Logo mobile** : glisse lentement dans le bandeau du haut (aller-retour en 40 s), jamais au-dessus d'un texte ; absent de la scène de fin | 110 px en vertical (≈ 40 px sur un téléphone, la taille d'un filigrane : signature reconnaissable à son symbole, nom et slogan lus sur la fin), 170 px en 16:9 | Non |
| Vidéo | Scène de fin, centré sous l'appel à l'action | 400 px, soit environ 145 px sur un téléphone (réduit jusqu'à 320 px si le texte est long) | Non |
| Carrousel | Dernière diapositive (fin), même mise en page | 460 px (min. 360) | Non |
| Couverture (`miniature.jpg`) | En haut à droite, dans la zone de sécurité | 260 px | Non |

**Plus de marque fixe pendant la vidéo** (décision de JG, 21/11/2026). Le nom « ACTU-BASICS » n'est plus écrit en haut de chaque image vidéo : une incrustation immobile, présente d'un bout à l'autre, ressemble au filigrane d'un contenu repris, que les plateformes peuvent pénaliser. Le logo officiel reste présent mais bouge : simple translation, sans déformation, recoloration ni effet (règle 4 du guide). Le bandeau du haut lui est réservé, donc aucun texte ne passe dessous (règle 5). Réglage : `logo.mobile` dans la charte ; `actif: false` retire toute marque pendant la vidéo, et le logo peut alors être ajouté par le filigrane de YouTube Studio. Le carrousel, fait d'images fixes, garde le nom en petit en haut de chaque diapositive.

### Lisibilité sur téléphone

Sur un écran de 390 px de large, le nom « ACTU-BASICS » occupe environ 11 % de la largeur du logo en hauteur, et le slogan 3,6 % (FR) ou 2,8 % (EN, plus long). Le slogan anglais demande donc un logo plus grand.

| Logo | À l'écran | Nom | Slogan FR | Slogan EN |
|---|---|---|---|---|
| Couverture, 260 px | 94 px | 10 px | 3,4 px | 2,6 px |
| Vidéo, 280 px (essai précédent) | 101 px | 11 px | 3,7 px | 2,8 px (illisible) |
| **Vidéo, 400 px** | 145 px | 16 px | 5,2 px | 4,0 px |
| **Carrousel, 460 px** | 166 px | 18 px | 6,0 px | 4,6 px |

Le rapport qualité signale un nom de moins de 8 px et, en fin de vidéo ou de carrousel, un slogan de moins de 4 px (réglages `logo.lisibilite`). Sur la couverture, seul le nom compte : c'est une miniature, le slogan n'y est pas exigé.

## Réglages (sans code) — `production/charte.yaml`, section `logo`

- `actif: false` : retire le logo partout (le rapport le signale).
- `fichiers.fr` et `fichiers.en` : fichiers du logo de chaque langue, `clair` et `sombre`. Une seule liste `fichiers.clair` / `fichiers.sombre` (sans langue) sert pour les deux langues.
- `variante: auto | clair | sombre` : `auto` choisit selon la luminosité réelle du fond sous le logo. La variante claire va sur un fond clair, la sombre sur un fond sombre.
- `zone_protection` : espace libre exigé autour du logo, en part de sa largeur (8 % par défaut).
- `video.scenes`, `carrousel.scenes` : scènes qui portent le logo. Par exemple, ajouter `accroche` dans `carrousel.scenes` place aussi le logo sur la couverture du carrousel.
- `largeur_px`, `largeur_min_px`, `largeur_autres_px` : tailles, en pixels de l'image (1080 px de large).
- `position` : `haut_gauche`, `haut_centre`, `haut_droite`, `centre`, `bas_gauche`, `bas_centre` ou `bas_droite`. Le logo est toujours ancré **dans** la zone de sécurité. Le texte de la scène se décale pour lui laisser la place. En bas, le logo reste au-dessus de la ligne « Source ».
- `marge_px` : retrait supplémentaire depuis le bord de la zone de sécurité.
- `slogan` : slogan écrit sous le logo dans la scène de fin, `true`/`false` ou par langue (`{fr: false, en: true}`). Par défaut `false` : chaque logo porte déjà le slogan de sa langue.

Les slogans sont dans la section `slogan` de la charte. Un test et le contrôle qualité vérifient qu'ils sont **exactement** « Éveiller par les chiffres. » et « Enlightening through numbers. ».

## Contrôles automatiques (rapport qualité)

| Contrôle | Gravité |
|---|---|
| Fichier du logo absent, pour l'une ou l'autre langue (rien n'est dessiné à sa place) | ❌ avant tout rendu |
| Logo d'une autre langue que la version produite | ❌ |
| Slogan différent du slogan officiel | ❌ |
| Logo prévu mais absent d'une image | ❌ |
| Variante inadaptée au fond (claire sur fond sombre, ou l'inverse) | ❌ |
| Texte, graphique ou pied de page dans la zone de protection du logo | ❌ |
| Logo coupé par le bord de l'image | ❌ |
| Logo sous l'interface TikTok / Reels / Shorts (vidéo, couverture) ou hors des marges (carrousel) | ⚠️ |
| Logo agrandi au-delà de la résolution du fichier (flou) | ⚠️ |
| Logo de moins de 90 px à l'écran d'un téléphone | ⚠️ |
| Nom du logo de moins de 8 px, ou slogan de moins de 4 px (fins de vidéo et de carrousel) à l'écran d'un téléphone | ⚠️ |
| Ancien nom ou ancienne signature (« Le Monde en chiffres », « un chiffre à la fois »…) dans les textes de la fiche | ⚠️ (correction éditoriale) |

Le rapport indique, pour chaque logo posé, la variante, la taille et la luminosité du fond.

## Vérification visuelle

`inspection/logo-mobile.png` montre chaque image portant le logo, à la taille d'un téléphone (390 px de large), avec la zone de protection encadrée en vert. Les images `zones-*.png` montrent la scène de fin sous l'interface simulée des plateformes.
