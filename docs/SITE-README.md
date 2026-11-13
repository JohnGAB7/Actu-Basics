# Site public ACTU-BASICS

Site pédagogique bilingue (français / anglais), servi de manière statique par GitHub Pages.

## Positionnement

- **Hybride** : YouTube sert à découvrir les notions ; le site permet de les approfondir, de retrouver les méthodes et de pratiquer.
- **Progressif** : une leçon n'est affichée comme disponible que lorsqu'une page existe et que son contenu a été vérifié.
- **Sans backend** : pas de compte utilisateur ni de base de données pour cette première version.
- **Publication** : GitHub Pages, « Deploy from a branch », branche `chatgpt/actu-basics-site-v1`, dossier `/docs` (configuration de la V1 confirmée le 13 novembre 2026). Le workflow GitHub Pages Build and Deployment a également terminé avec succès. Ne pas supposer que `main` est la source publiée.

## Structure actuelle

Le site est désormais **généré** depuis les données :

```
docs/                             (toutes les pages HTML sont écrites par le générateur
                                   SAUF index.html, a-propos/ et en/about/, qui restent manuels)
├── index.html                    Accueil FR (manuel)
├── en/index.html                 Home EN (manuel)
├── parcours/index.html           Index des parcours FR (généré)
├── parcours/<slug>/index.html    Détail d'un parcours FR (généré)
├── en/paths/index.html           Learning paths index EN (généré)
├── en/paths/<slug>/index.html    Learning path detail EN (généré)
├── bibliotheque/index.html       Bibliothèque FR (générée)
├── en/library/index.html         Library EN (générée)
├── a-propos/index.html           À propos FR (manuel)
├── en/about/index.html           About EN (manuel)
├── lecons/<CODE>/index.html      Leçon FR, une par fiche valide (générée)
├── en/lessons/<CODE>/index.html  Lesson EN, une par fiche valide (générée)
└── assets/{css,js,img}           Ressources statiques (manuelles)
```

Sources de vérité :
- `contenus/fiches/*.yaml` — les fiches pédagogiques (une par leçon).
- `contenus/parcours.yaml` — la liste des parcours et leurs modules.

## Ajouter / modifier du contenu

Le site est **généré**. On n'écrit plus de HTML à la main pour une leçon, la bibliothèque ou un parcours. Toute l'édition passe par les YAML.

**Ajouter une leçon** :
1. Créer le fichier `contenus/fiches/<id>.yaml` avec ses éditions FR et EN.
2. Passer sa validation à `valide` (`validation.statut: valide`).
3. Lancer `python3 tools/build_lessons.py`.

La leçon apparaît automatiquement dans la bibliothèque, dans la section du bon module, et dans tous les parcours qui référencent ce module.

**Ajouter une vidéo à une leçon existante** : ajouter la clé `publication:` à la racine du YAML (voir `docs/technique/architecture-site-conformance.md` pour le schéma détaillé). Puis régénérer.

**Ajouter un nouveau module** (ex: `A3`) :
1. Créer les fiches YAML du module.
2. L'ajouter dans la liste `modules:` d'un parcours de `contenus/parcours.yaml`.
3. Régénérer.

**Ajouter un nouveau parcours** : une entrée dans `contenus/parcours.yaml`, puis régénérer.

**Commandes utiles** :
```bash
python3 tools/build_lessons.py        # génère le site
python3 tools/test_build_site.py      # tests du générateur (CI en fait autant)
```

## Principes

- Pages orphelines automatiquement nettoyées (une fiche supprimée ou renommée → son répertoire `docs/lecons/<CODE>/` est retiré au prochain build).
- Les fiches `format: short` (TikTok/YouTube Shorts) **ne** produisent **pas** de page web : elles existent comme média court rattaché à leur leçon mère.
- Ne pas afficher de lien vidéo, PDF, tableur ou script tant que la ressource correspondante n'existe pas et n'a pas été vérifiée. Le générateur applique une whitelist stricte sur les URLs YouTube/TikTok et refuse de rendre une `<iframe>` pour une URL hors whitelist.

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


## V1.1 — améliorations intégrées

Les améliorations suivantes sont déjà intégrées dans la branche du site :

- liens sociaux officiels YouTube et TikTok pour les éditions française et anglaise ;
- métadonnées de partage Open Graph, URL canonique et liens de langue ;
- navigation mobile avec fermeture par Échap, clic extérieur et retour du focus ;
- indicateurs de focus clavier visibles ;
- harmonisation de la devise de l'exemple A0.01 en euros dans les deux langues.

Les pages de leçons sont générées depuis les fiches YAML validées. Les emplacements vidéo restent facultatifs : aucun lecteur ni lien individuel n'est affiché sans URL vérifiée.
