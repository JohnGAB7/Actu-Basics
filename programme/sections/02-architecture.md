# 2. Architecture éditoriale globale {#architecture}

## 2.1 Une promesse, trois piliers

La promesse reste celle de la marque : **« Éveiller par les chiffres. » / “Enlightening through numbers.”** Partir d'un chiffre ou d'une question, et repartir avec une compréhension que l'on peut réutiliser.

Les trois piliers ne sont pas trois chaînes séparées. Ils se répondent :

- le **pilier 3** (quotidien et actualité) attire et donne envie : « d'où vient ce chiffre ? » ;
- le **pilier 1** (statistiques) donne les outils pour répondre ;
- le **pilier 2** (économétrie) pousse ces outils jusqu'à la question la plus difficile : mesurer un effet causal avec des données qui ne viennent pas d'une expérience.

Chaque vidéo du pilier 3 renvoie vers la leçon qui explique sa notion (« pour aller plus loin »). Chaque leçon des piliers 1 et 2 peut s'appuyer sur un fait réel sourcé. Les fiches gardent ces liens : la fiche d'une leçon liste les vidéos du quotidien qui l'illustrent.

## 2.2 Correspondance avec l'architecture existante

Le moteur de production et `00_STRATEGY/ARCHITECTURE_EDITORIALE.md` utilisent quatre **familles** (champ `famille` des fiches). Ce programme ne les remplace pas. Il les range sous les trois piliers, sans modifier le moteur :

| Pilier du programme | Famille dans la fiche (moteur) | Type de fiche |
|---|---|---|
| 1 · Statistiques, modules S1 à S3, S6 à S19 | `apprendre_les_statistiques` | `pedagogique` |
| 1 · Statistiques, modules S4 et S5 (probabilités) | `comprendre_les_probabilites` | `pedagogique` |
| 1 · Branches appliquées (S10.06, S17) | `statistiques_en_pratique` | `pedagogique` |
| 2 · Économétrie | `statistiques_en_pratique` *(arbitrage A1 : piliers au-dessus des familles, moteur inchangé)* | `pedagogique` |
| 3 · Quotidien (intemporel) | `statistiques_en_pratique` ou `comprendre_le_monde` selon l'angle | `pedagogique` |
| 3 · Actualité | `comprendre_le_monde` | `actualite` |
| Boîte à outils maths | `apprendre_les_statistiques` | `pedagogique` |

**Deux points touchaient des décisions déjà écrites.** JG les a tranchés (arbitrages A2 et A3, section 10) :

- la section 5 d'`ARCHITECTURE_EDITORIALE.md` proposait un rythme de publication dès le lancement (3 SHORT par semaine, etc.). Le ticket n° 10 décide au contraire de **ne rien publier avant d'avoir un stock suffisant**. Ce programme suit le ticket, plus récent et validé par JG. Le document existant sera mis à jour dans une PR distincte, après la validation de ce programme ;
- la répartition par thèmes de la constitution éditoriale (démographie 20 %, économie 20 %, etc.) est appliquée ici **aux seules vidéos d'actualité**, et non au cursus.

## 2.3 Quatre niveaux, avec des branches

{{TABLEAU_NIVEAUX}}

Les niveaux 1 à 3 forment un **tronc commun** linéaire : un spectateur peut les suivre dans l'ordre sans jamais rencontrer une notion qui n'a pas été expliquée. Le niveau 4 est un ensemble de **branches**, chacune avec ses propres prérequis. Il n'existe pas de parcours unique qui serait le prérequis de toutes les spécialités. Par exemple, on peut suivre les séries temporelles (S14) sans l'analyse multivariée (S13).

Pour chaque module, on vise trois seuils de maîtrise, comme le propose la revue de ChatGPT :

- **comprendre** : réexpliquer l'idée avec ses mots ;
- **appliquer** : refaire le calcul sur un nouvel exemple ;
- **critiquer** : dire quand la méthode ne s'applique pas et ce qui pourrait fausser la conclusion.

Les objectifs de chaque vidéo sont écrits avec des verbes observables (calculer, distinguer, interpréter, repérer, expliquer pourquoi) pour que l'exercice final puisse les vérifier.

## 2.4 Un format principal : l'épisode long

| Format (clé moteur) | Image | Durée | Rôle dans le programme (version 1.13) |
|---|---|---|---|
| **YOUTUBE_LESSON** (`youtube_lesson`) | horizontal 1920 × 1080 | 10–50 min | **Le format principal** : un épisode qui traite plusieurs notions cohérentes, avec chapitres YouTube horodatés, exercices et synthèse. C'est là que l'on se forme de façon complète. |
| **SHORT** (`short`) | vertical 1080 × 1920 | 30–60 s | **Bande-annonce** d'un épisode : son meilleur moment (paradoxe, résultat surprenant), qui renvoie toujours vers l'épisode complet. Jamais une définition isolée. |
| **EDUCATIONAL** (`educational`) | vertical 1080 × 1920 | 1 min 30–10 min | Réservé aux extraits d'un épisode (un chapitre publié à part sur une plateforme verticale) ; plus produit comme vidéo autonome. |

Les {{NB_VIDEOS}} entrées du catalogue gardent leur format d'origine dans les sections 3 à 5 : il indique la place que prend la notion à l'écran, et non plus une vidéo séparée. Leur durée s'additionne dans l'épisode. Les trois anciens SHORT autonomes (Q1.03, Q2.04, Q3.02) deviennent des chapitres courts de leurs épisodes et restent de bons candidats de bande-annonce.

La durée d'un épisode découle de ce qu'il faut pour atteindre ses objectifs, jamais d'un plafond arbitraire (constitution éditoriale, section 10). Au-delà de 50 min, il est coupé en deux épisodes. Les durées sont des **estimations de conception**, corrigées après l'écriture du script.

**Règles de regroupement.** (1) Un épisode regroupe des notions qui répondent à une même question. (2) Il reste dans un seul module, sauf exception justifiée dans le pilier Quotidien. (3) Dans le cursus, aucun chapitre ne demande une notion traitée plus loin. (4) Chaque chapitre garde son exercice, et l'épisode se termine par un exercice de synthèse. (5) **Complétude** (demande de JG du 22/11/2026) : l'apprenant n'est jamais privé d'une notion indispensable. Chaque fiche de conception dresse l'inventaire de **toutes** les notions que l'épisode utilise, y compris celles qui semblent évidentes (un pourcentage, une moyenne, une puissance), et indique pour chacune où elle est enseignée : un épisode antérieur du parcours, ou un rappel intégré dans l'épisode lui-même. Une notion sans l'un ni l'autre bloque l'écriture du script. Les règles 1 et 2 relèvent de la relecture ; les règles 3 et 4 sont contrôlées par script ; la règle 5 l'est à la relecture de chaque fiche, et le sera par script dès que les fiches de conception des épisodes existeront.

**Plateformes.** Les contrôles hérités du diagnostic TikTok du 21/11/2026 s'appliquent à tous les formats : première image pleine, aucun plan figé de plus de 2 s, aucun logo ni nom de marque fixe à l'écran (logo mobile, voir 2.5), étiquette « contenu généré par IA » pour la voix de synthèse, aucun lien dans les légendes, vocabulaire sensible cadré (jeux d'argent, argent, santé, poids, élections, mortalité).

## 2.5 La structure d'un épisode

1. **Ouverture** (15 à 30 s) : la question concrète de l'épisode, montrée et non seulement dite, avec du mouvement dès la première image. On ne commence pas par saluer : les premières secondes décident si le spectateur reste.
2. **Accueil** (10 à 20 s, scène `accueil`) : on salue le spectateur, on le remercie d'être là et on dit ce qu'il saura faire à la fin de l'épisode. Exemple : « Bonjour, et merci d'être là. Dans cet épisode, vous allez apprendre à… ».
3. **Plan à l'écran** : les chapitres, qui deviennent les chapitres YouTube.
4. **Chaque chapitre** suit l'arc déjà mis en œuvre dans le moteur et dans la vidéo de lancement :
    1. **Question** concrète, paradoxe ou situation familière ;
    2. **Intuition** : ce que l'on croit spontanément, avec une estimation demandée au spectateur ;
    3. **Données ou exemple minuscule**, que l'on peut suivre de tête ;
    4. **Raisonnement pas à pas**, montré à l'écran (« la voix raconte, l'image démontre ») ;
    5. **Formalisation** : la formule arrive après l'idée, et chaque symbole est expliqué ;
    6. **Exercice** avec un temps de réflexion, puis **correction** détaillée ;
    7. **Application** réelle et **limites** de la méthode.
5. **Synthèse** : comment les notions de l'épisode s'articulent, avec un schéma récapitulatif.
6. **Exercice de synthèse**, qui mobilise plusieurs chapitres, puis sa correction.
7. **Clôture** (30 à 45 s, scène `cloture`) : le rappel mémorable en une phrase, puis l'orientation et les invitations, dans cet ordre :
    1. **orientation** : l'épisode suivant du parcours (titre dit et affiché), les autres épisodes utiles et la page de l'épisode sur le site ACTU-BASICS, qui contient le cours écrit complet ;
    2. **abonnement** : s'abonner pour suivre le parcours dans l'ordre ;
    3. **like** : laisser un like si l'épisode a aidé ;
    4. **partage** : partager l'épisode à quelqu'un à qui il servira ;
    5. **aide gratuite aux exercices** (proposition de JG du 21/11/2026, canal décidé le 22/11/2026) : un étudiant bloqué sur un exercice ou une notion de l'épisode pose sa question **en commentaire sous la vidéo YouTube**, et l'équipe l'aide gratuitement. On aide à comprendre la méthode sur les exercices liés à l'épisode ; on ne fait pas un devoir noté ou un examen à la place de l'étudiant, et on ne demande aucune donnée personnelle.
8. **Fin de marque** (3 à 5 s, scène `fin`) : logo officiel et slogan de la langue de l'édition (« Éveiller par les chiffres. » ou « Enlightening through numbers. »), avec l'écran de fin YouTube par-dessus (épisode suivant, abonnement).

Les invitations restent sobres et une seule fois par épisode, en fin de parcours : pas de demande de like au début ni au milieu, et jamais de formule qui promet un résultat ou qui culpabilise. Le moteur de rendu bloque un épisode long sans accueil après l'ouverture, sans clôture juste avant la fin, ou dont la clôture oublie l'une des quatre invitations (`production/charte.yaml`, section `parcours_spectateur`).

**Laboratoires et simulations** (proposition de JG du 22/11/2026). Quand une notion se comprend mieux en la voyant varier, l'épisode montre une **simulation à l'écran** : pièces lancées par milliers pour la loi des grands nombres, moyennes d'échantillons qui dessinent une courbe en cloche, rééchantillonnage pour le bootstrap. Chaque simulation est tirée avec une graine fixée, donc reproductible : les chiffres affichés peuvent être recalculés et vérifiés. Sur le site, la page de l'épisode propose le même **laboratoire interactif**, où l'apprenant change lui-même les paramètres. Les quinze laboratoires de Programme-B (probabilités, statistique descriptive, inférence) servent de point de départ ; ils sont repris dans le site ACTU-BASICS, aux couleurs de la marque, et vérifiés avant publication.

**Bandes-annonces (SHORT) et extraits.** Pas d'accueil, qui ferait partir le spectateur dès la première seconde. La dernière scène renvoie vers l'épisode complet par son titre (« L'épisode complet est sur la chaîne YouTube ACTU-BASICS »), sans lien dans la légende. Le moteur le signale s'il manque.

**Logo.** Plus de marque fixe pendant la vidéo : le nom « ACTU-BASICS » posé en haut de chaque image disparaît, car une incrustation statique peut être traitée par les plateformes comme un filigrane de contenu repris. Le logo officiel reste présent mais **mobile** : il glisse lentement dans le bandeau du haut (un aller-retour toutes les 40 s), sans être déformé, recoloré ni recouvert, et s'efface avant la fin de marque. Le réglage se fait dans `production/charte.yaml` (`logo.mobile`) ; on peut le couper et utiliser à la place le filigrane de YouTube Studio.

## 2.6 Principes non négociables, traduits en règles de production

| Principe (ticket n° 10) | Règle appliquée dans le programme |
|---|---|
| La compréhension prime sur la durée | Durée estimée par épisode selon le contenu ; un épisode de plus de 50 min est découpé en deux, pas comprimé. |
| Intuition d'abord, formalisation ensuite | Champ « Intuition d'abord » obligatoire dans chaque fiche. |
| Expliquer les formules | Toute formule a une voix off qui la lit et l'explique (contrôle bloquant du moteur). |
| Pouvoir réutiliser la notion | Chaque fiche a un exercice ; un exercice sans correction bloque la production. |
| Pas de prérequis implicites | Prérequis listés par identifiant et contrôlés par script ; niveau mathématique (M0 à M4) indiqué partout. |
| Corrélation ≠ causalité, description ≠ inférence, prédiction ≠ explication | Trois vidéos dédiées (S3.06, S6.01, S17.01), et le champ « Idées fausses à prévenir » les rappelle là où le piège existe. |
| Accessible sans sacrifier la rigueur | Relecture humaine des définitions (ChatGPT) et contrôle automatique des calculs (moteur). |
| FR et EN naturels, pas traduits | Titre de travail anglais propre à chaque vidéo ; scripts écrits dans chaque langue à partir de la même fiche de conception. |

## 2.7 Correspondance avec les recommandations GAISE (révision 2025)

Le rapport GAISE de l'American Statistical Association, révisé en 2025 et publié par étapes, formule dix recommandations pour l'enseignement de la statistique et de la science des données. Le tableau indique comment le programme les applique, et où il s'en écarte à cause du format vidéo.

| Recommandation GAISE (résumé) | Application dans ACTU-BASICS |
|---|---|
| 1. Enseigner la statistique comme un processus qui va des données à la décision | Cycle d'enquête en 9 étapes dans chaque fiche de conception (section 6) ; S3.09 en démonstration complète |
| 2. Communiquer les résultats, avec leur portée et leurs limites | Étape « limites » obligatoire dans l'arc d'un épisode ; champ « hypothèses et limites » |
| 3. Viser la compréhension plutôt que la manipulation de formules | Intuition d'abord, formule ensuite, chaque symbole expliqué |
| 4. Utiliser des données réelles, avec un contexte | Choix explicite dans chaque fiche : données réelles, simulation ou calcul pur, avec la raison |
| 5. Encourager la pensée multivariée | Tableaux croisés et Simpson dès le niveau 1 (S3.02, S3.03), régression multiple, graphes causaux (E1.05) |
| 6. Utiliser des logiciels pour explorer | Simulations à l'écran ; scripts reproductibles fournis en description (arbitrage A9) |
| 7. Collecte et usage éthiques des données | S1.10, S17.06, prudence de la constitution éditoriale |
| 8. Pédagogies actives | Estimation demandée, exercice avec temps de réflexion dans chaque vidéo. **Limite du format** : une vidéo reste moins interactive qu'un cours |
| 9. Évaluations formatives et sommatives variées | Exercice dans chaque vidéo (formatif) ; tests de transfert et de diagnostic d'erreur pendant le pilote (section 7.2). La section « Assessment » de GAISE 2025 est encore en préparation : à intégrer dès sa parution |
| 10. Stratégies inclusives | Éditions FR et EN autonomes, exemples variés, formulation non stigmatisante. À renforcer : sous-titres et accessibilité visuelle sont contrôlés, la diversité des exemples ne l'est pas encore |

## 2.8 Bilinguisme

Chaque vidéo existe en deux éditions, française et anglaise, produites à partir de la **même fiche de conception**. Les scripts sont écrits séparément. Les exemples peuvent être adaptés à chaque public (Insee et Eurostat d'un côté, BLS, ONS ou Banque mondiale de l'autre), à condition que **le raisonnement et les nombres calculés restent identiques**. Le moteur signale déjà un écart de nombres entre les deux éditions. Les titres anglais suivent l'orthographe américaine (-ize, -er : *optimization*, *kilometer*), majoritaire dans le catalogue. Une première relecture des 320 titres anglais a été faite en version 1.12 (cohérence orthographique, titres ambigus corrigés). Ce sont encore des titres de travail : une relecture par un locuteur natif reste prévue avant les fiches bilingues, avec celle des scripts.

## 2.9 Les {{NB_EPISODES}} épisodes

Liste produite par `programme/episodes.py` à partir de `catalogue/episodes.txt`. Durée : somme des fourchettes des chapitres. La colonne Programme-B est une correspondance interne : elle indique le bloc dont le registre des sources et la carte des notions servent à vérifier l'épisode. Elle n'est jamais un lien public (décision de JG du 22/11/2026 : le site ACTU-BASICS se suffit à lui-même). Les titres sont des titres de travail, relus par l'éditorial avant production.

{{CATALOGUE_EPISODES}}
