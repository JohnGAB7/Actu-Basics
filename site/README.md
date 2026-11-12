# Site public ACTU-BASICS

Site static servi par GitHub Pages. **Pas de workflow GitHub Actions** : la publication utilise l'option « Deploy from a branch » de GitHub, qui ne consomme pas de crédits.

## Mise en route (une fois, par JG)

1. Aller dans https://github.com/JohnGAB7/le-monde-en-chiffres/settings/pages
2. Choisir **Source** : « Deploy from a branch »
3. Choisir **Branch** : `main` et **Folder** : `/site`
4. Cliquer **Save**

Le site sera accessible à `https://johngab7.github.io/le-monde-en-chiffres/` quelques minutes plus tard.

## Nom de domaine propre (facultatif, plus tard)

Acheter un nom de domaine (par exemple `actu-basics.com`), puis dans la même page Settings > Pages ajouter le domaine comme « Custom domain » et suivre les instructions DNS.

## Structure

```
site/
├── index.html          Accueil FR
├── en/index.html       Accueil EN
├── assets/
│   ├── css/main.css    Style unique
│   └── img/            Logos à ajouter
├── lecons/
│   └── A0-01/index.html   Une page par leçon FR
└── en/lessons/
    └── A0-01/index.html   Une page par leçon EN
```

## Ajouter une leçon

Copier `lecons/A0-01/` dans `lecons/A3-01/` et son équivalent EN. Mettre à jour le titre, le lien vers la vidéo, les téléchargements, et le repère d'examens avec sa date de dernière vérification. Ajouter une carte sur la page d'accueil.

## Fiches PDF, tableurs et fichiers R/Python

Ils sont servis directement depuis le dossier `site/lecons/<code>/` (ou `site/en/lessons/<code>/`). Nommer les fichiers avec le code de la leçon : `A0-01-fiche-fr.pdf`, `A3-01-table-mortalite.xlsx`, etc.

## Logo

Les logos officiels sont dans `assets/brand/actu-basics/`. Ils seront copiés dans `site/assets/img/` dans un prochain commit, avec le CSS adapté.
