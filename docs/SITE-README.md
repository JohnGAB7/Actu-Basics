# Site public ACTU-BASICS

Site pédagogique bilingue (français / anglais), servi de manière statique par GitHub Pages.

## Positionnement

- **Hybride** : YouTube sert à découvrir les notions ; le site permet de les approfondir, de retrouver les méthodes et de pratiquer.
- **Progressif** : une leçon n'est affichée comme disponible que lorsqu'une page existe et que son contenu a été vérifié.
- **Sans backend** : pas de compte utilisateur ni de base de données pour cette première version.
- **Publication** : GitHub Pages, « Deploy from a branch », branche `chatgpt/actu-basics-site-v1`, dossier `/docs` (configuration de la V1 confirmée le 13 novembre 2026). Le workflow GitHub Pages Build and Deployment a également terminé avec succès. Ne pas supposer que `main` est la source publiée.

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

## Mise en ligne (configuration V1 confirmée)

1. Ouvrir [Settings → Pages](https://github.com/JohnGAB7/le-monde-en-chiffres/settings/pages).
2. Choisir « Deploy from a branch ».
3. Pour la V1 actuelle, choisir la branche `chatgpt/actu-basics-site-v1` et le dossier `/docs`.
4. Enregistrer.

Après publication depuis la branche configurée, l'adresse du site est :
`https://johngab7.github.io/le-monde-en-chiffres/`

Le site n'est pas considéré comme publié avant vérification de son URL publique.

## Évolutions ultérieures

- recherche et filtres du catalogue (première version déjà intégrée) ;
- exercices et corrections pour les leçons qui en disposent ;
- ressources téléchargeables uniquement après validation et hébergement ;
- simulations et visualisations interactives si elles apportent une valeur pédagogique réelle.

Les évolutions doivent rester incrémentales et préserver l'accès direct aux pages, la navigation clavier, la lisibilité mobile et l'équivalence FR/EN.


## V1.1 — améliorations proposées

Les changements en cours sur la branche `chatgpt/actu-basics-v1-1-social` sont soumis à revue avant toute intégration dans la branche de publication :

- liens sociaux officiels YouTube et TikTok pour les éditions française et anglaise ;
- métadonnées de partage (Open Graph), URL canonique et liens de langue ;
- navigation mobile avec fermeture par Échap, clic extérieur et retour du focus ;
- indicateurs de focus clavier visibles ;
- harmonisation de la devise de l'exemple A0.01 en euros dans les deux langues.

Aucune page de nouvelle leçon ni aucun lien vidéo individuel n'est ajouté tant que les pages et URL de vidéos correspondantes ne sont pas confirmées.


## Catalogue du lot 4 — candidate V1.1 — 13 novembre 2026

Le lot 4 du Niveau 1 a été intégré au catalogue bilingue sur une branche candidate distincte, à partir des fiches YAML de la PR #19.

- 10 leçons concernées : S3.07 à S3.09 et S4.01 à S4.07.
- 20 pages de présentation pédagogique créées : 10 en français et 10 en anglais.
- Les bibliothèques FR et EN affichent désormais les 10 nouvelles fiches en plus de A0.01.
- Chaque page présente le résumé, les objectifs pédagogiques, les prérequis lorsqu'ils sont renseignés dans la fiche source et les notions abordées.
- Les statuts YAML sont conservés tels qu'ils apparaissent sur la branche de la PR #19 : `valide`, `valide_par: JG`, date du 13 novembre 2026.
- Les URL YouTube individuelles ne sont pas présentes dans le dépôt consulté. Les pages signalent donc que le rendu vidéo existe selon la PR #19, mais que son lien public individuel reste à renseigner. Aucun lien vidéo n'a été inventé.

### Séparation des changements

- PR #21 : améliorations techniques et sociales du site, base `chatgpt/actu-basics-site-v1`.
- Branche catalogue : `chatgpt/actu-basics-v1-1-catalogue-lot4`, créée depuis la branche de la PR #21.
- La PR catalogue cible la branche de la PR #21 ; elle est donc dépendante de celle-ci.
- Aucune de ces PR n'est fusionnée dans `main` et aucune publication n'est déclenchée par ce travail.
- Les tests réalisés sont des vérifications statiques des fichiers et liens internes. Les tests visuels réels, multi-navigateurs, mobiles et clavier restent à effectuer.
