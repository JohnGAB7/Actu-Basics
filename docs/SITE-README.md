# Site public ACTU-BASICS

Site pédagogique bilingue (français / anglais), servi de manière statique par GitHub Pages.

## Positionnement

- **Hybride** : YouTube sert à découvrir les notions ; le site permet de les approfondir, de retrouver les méthodes et de pratiquer.
- **Progressif** : une leçon n'est affichée comme disponible que lorsqu'une page existe et que son contenu a été vérifié.
- **Sans backend** : pas de compte utilisateur ni de base de données pour cette première version.
- **Publication** : GitHub Pages, « Deploy from a branch », branche `main`, dossier `/docs`. Aucun workflow GitHub Actions requis.

## Structure actuelle

```
docs/
├── index.html                  Accueil FR
├── en/index.html               Home EN
├── parcours/index.html         Parcours FR
├── en/paths/index.html         Learning paths EN
├── bibliotheque/index.html     Bibliothèque FR
├── en/library/index.html       Library EN
├── a-propos/index.html         À propos FR
├── en/about/index.html         About EN
├── lecons/A0-01/index.html     Leçon A0.01 FR
├── en/lessons/A0-01/index.html Lesson A0.01 EN
└── assets/
    ├── css/main.css
    ├── js/site.js
    └── img/                    Logos officiels copiés depuis assets/brand/actu-basics/
```

## Ajouter une leçon

1. Créer la page française dans `docs/lecons/<CODE>/index.html`.
2. Créer la version anglaise dans `docs/en/lessons/<CODE>/index.html`.
3. Ajouter la leçon dans les deux bibliothèques seulement lorsque les deux pages sont prêtes.
4. Vérifier que les nombres, hypothèses, formules et conclusions sont cohérents entre les langues.
5. Tester tous les liens relatifs et l'affichage mobile.

Ne pas afficher de lien vidéo, PDF, tableur ou script tant que la ressource correspondante n'existe pas et n'a pas été vérifiée.

## Identité visuelle

Les pages utilisent les logos officiels issus de `assets/brand/actu-basics/`. Ne jamais reconstituer ou modifier le logo. Palette du site : bleu profond, or/ambre et fond ivoire. La mise en page est responsive et privilégie la lisibilité.

## Mise en ligne (action de JG)

1. Ouvrir [Settings → Pages](https://github.com/JohnGAB7/Actu-Basics/settings/pages).
2. Choisir « Deploy from a branch ».
3. Choisir la branche `main` et le dossier `/docs`.
4. Enregistrer.

Après fusion des changements et activation de Pages, l'adresse attendue est :
`https://johngab7.github.io/Actu-Basics/` (ancienne adresse `https://johngab7.github.io/le-monde-en-chiffres/` : plus servie après le renommage du dépôt, aucune redirection automatique)

Le site n'est pas considéré comme publié avant vérification de son URL publique.

## Évolutions ultérieures

- recherche et filtres du catalogue (première version déjà intégrée) ;
- exercices et corrections pour les leçons qui en disposent ;
- ressources téléchargeables uniquement après validation et hébergement ;
- simulations et visualisations interactives si elles apportent une valeur pédagogique réelle.

Les évolutions doivent rester incrémentales et préserver l'accès direct aux pages, la navigation clavier, la lisibilité mobile et l'équivalence FR/EN.
