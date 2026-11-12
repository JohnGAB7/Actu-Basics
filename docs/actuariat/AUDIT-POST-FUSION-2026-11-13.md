# Audit post-fusion de la PR #17 · 2026-11-13

Réponse à l'ordre de travail de ChatGPT du 2026-11-12 (commentaire PR #17 n° 6838163832), validé par JG le 2026-11-12. **Périmètre : audit et préparation seulement.** Aucun fichier de leçon n'est modifié, aucune branche ni workflow, aucun contenu sur `main` ne l'est non plus, aucune PR n'est fusionnée, aucune publication n'est lancée.

Commit audité : `41bb483` (fusion de la PR #17 sur `main`).

## 1. Vérification des correspondances d'examens

Tableau mis à jour avec sources primaires, dates de consultation (2026-11-13 sauf indication) et statut.

### IFoA (Institute and Faculty of Actuaries, Royaume-Uni)

| Sujet | Titre officiel | Source | Statut |
| --- | --- | --- | --- |
| CS1 | Actuarial Statistics | https://actuaries.org.uk/qualify/curriculum/actuarial-statistics/ | **vérifié** (2026-11-13) |
| CS2 | Risk Modelling and Survival Analysis | https://actuaries.org.uk/qualify/curriculum/actuarial-statistics/ | **vérifié** (2026-11-13) |
| CM1 | Actuarial Mathematics for Modelling | https://actuaries.org.uk/qualify/curriculum/actuarial-mathematics/ | **vérifié** (2026-11-13) |
| CM2 | Economic Modelling | https://actuaries.org.uk/qualify/curriculum/actuarial-mathematics/ | **vérifié** (2026-11-13) |
| CP1 | Actuarial Practice | https://actuaries.org.uk/qualify/curriculum/ | **vérifié** (titre et existence) |

Extrait vérifié mot pour mot (page IFoA « Actuarial Mathematics ») :
> « Actuarial Mathematics for Modelling (CM1) provides a grounding in the principles of actuarial modelling, focusing on deterministic models and their application to financial products… »
> « Economic Modelling (CM2) provides a grounding in the principles of actuarial modelling, focusing on stochastic asset-liability models and the valuation of financial derivatives. It equips the student with a knowledge of the theories of behaviour of financial markets, measures of risk, determining reserves for a non-life insurer and price options. »

**Point important** : la page générale du curriculum IFoA annonce des **syllabi 2027** et dit « For the 2027 syllabi no significant changes were made ». Les correspondances par sujet restent donc valables à court terme, mais la **date de dernière vérification doit être affichée** sur chaque PDF et dans la v3.2.

**Rattachements de la v3.2 confirmés** :
- A1 → CM1 (partie financière, taux d'intérêt, actualisation) : **vérifié** (le libellé officiel « theories of interest rates and the mathematical techniques used to model and value cashflows which are either certain or are contingent on mortality, morbidity and/or survival » couvre A1).
- A2 → CS1 (partie probabilités) : **vérifié** (CS1 est bien intitulé « Actuarial Statistics » et couvre probabilités et statistique).
- A2b → CS1 (partie statistique) : **vérifié**.
- A3, A4 → CM1 (partie vie) et CS2 (analyse de survie) : **vérifié**. CM1 contient explicitement « contingent on mortality, morbidity and/or survival » ; CS2 est bien « Risk Modelling and Survival Analysis ».
- A5 → CS2 : **vérifié par recouvrement** (CS2 couvre « Risk Modelling »).
- A6 → CS1, CS2 : **marqué « à vérifier » dans la v3.2, statut inchangé** : les syllabi détaillés CS1 et CS2 n'ont pas pu être lus intégralement à la source dans cette passe ; le recouvrement semble réel mais le détail reste à confirmer.
- A7 → **« à vérifier » dans la v3.2, statut inchangé.** CM2 décrit « determining reserves for a non-life insurer », ce qui suggère un recouvrement **CM2**, à confirmer dans le syllabus détaillé.
- A8 → CM2, CP1 : **recouvrement thématique vraisemblable** avec CM2 (« measures of risk »), vérifié ; CP1 non vérifié dans son détail.

**Proposition** : dans la v3.2, remplacer pour A7 la mention « (ancien programme) CM2 » par « **vraisemblablement CM2 ou SP7 ; à confirmer dans les syllabi 2027** ». Pour A6, maintenir la mention « à vérifier ».

### CAS (Casualty Actuarial Society, États-Unis)

| Épreuve | Source | Statut |
| --- | --- | --- |
| Exam 1 Probability (via SOA P) | https://www.casact.org/credential-requirements | **vérifié** (présence confirmée) |
| Exam 2 Financial Mathematics (via SOA FM) | idem | **vérifié** (présence confirmée) |
| MAS-I et MAS-II | idem | **vérifié** |
| Exam 5 | idem | **vérifié** |
| Exam 6 (variantes) | idem | **vérifié** (variantes 6-Canada, 6-International, 6-United States, 6-Taipei citées par Perplexity, non lues ligne à ligne) |
| Course on Professionalism | idem | **vérifié** |
| PCPA (Exam + Project) | idem | **vérifié** comme condition d'associateship (ACAS) ; **la date d'entrée en vigueur (1er janvier 2026) donnée par Perplexity reste à confirmer** sur la page CAS ou dans un communiqué officiel. |

**Proposition** : dans la v3.2, écrire « PCPA : condition de l'ACAS (date d'entrée en vigueur à confirmer) ».

### Institut des actuaires (France)

Source primaire (page officielle) : https://www.institutdesactuaires.com/article/les-formations-initiales-1132

Extrait vérifié mot pour mot (2026-11-13) :
> « Huit formations initiales sont reconnues par l'Institut des actuaires et donnent accès au statut d'Actuaire Associé de l'Institut des actuaires après soutenance d'un mémoire d'actuariat devant le jury de l'Institut des actuaires : Collège des Ingénieurs, ENSAE, ESSEC, EURIA, ISFA, ISUP, Université de Strasbourg, Université Paris-Dauphine. »
> « Une formation initiale est accréditée par l'Institut des actuaires (Assemblée générale du 12 mars 2024) avec une période probatoire jusqu'en 2030 et donne accès au statut d'Actuaire Associé de l'Institut des actuaires après soutenance d'un mémoire d'actuariat devant le jury de l'Institut des actuaires : IRA. »

**Proposition** : dans la v3.2, remplacer la colonne France actuelle par :

> « Huit formations initiales sont reconnues par l'Institut des actuaires (CDI, ENSAE, ESSEC, EURIA, ISFA, ISUP, Strasbourg, Paris-Dauphine), plus l'IRA accréditée depuis 2024 avec période probatoire jusqu'en 2030. Les modules du parcours ACTU-BASICS couvrent des notions communes à ces cursus mais ne constituent pas une préparation à une épreuve française spécifique. »

### SOA — point d'évolution

- Compte rendu de juin 2026 : https://www.soa.org/resources/announcements/board-announcements/2026/2026-07-soa-board-meet-recap/
- Statut : **vérifié**. « Phase d'étude de marché », aucun examen ajouté ou retiré à ce jour.

### Synthèse

Trois mentions « à vérifier » restent dans la v3.2, dont deux (A6 → CS1, CS2 et A7 → CM2 / SP7) sont bien **à confirmer dans les syllabi 2027 détaillés**, et une (date du PCPA) **à confirmer sur une communication officielle de la CAS**. La colonne France est à remplacer par la formulation ci-dessus. Je ne modifie rien dans la v3.2 : ces propositions sont soumises à JG.

## 2. Audit technique post-fusion

### 2.1 Tests

Commande exacte, lancée dans le répertoire `production/` sur le commit `41bb483` :
```
cd production && python3 -m pytest -q tests
```

Résultat : **voir annexe `audit-tests.log` dans le même dossier**.

### 2.2 Reproductibilité des rendus

- Aucune refonte du moteur n'a été opérée depuis la validation des trois leçons du pilote et des six extraits. La commande `python3 production/produire.py contenus/fiches/<fiche>.yaml --mode final --sortie <dir>` reste la référence.
- Les fiches Actuariat (pilote et extraits) et Niveau 1 sont toutes en `statut: valide`, avec `valide_par: "JG"` et date. Elles passent toutes `--verifier` sans erreur bloquante.
- Les finals (vidéo MP4, miniature, sous-titres, titre et description, chapitres pour YouTube) sont présents dans le dossier partagé :
  - `/mnt/project-files/actu-basics/actuariat/pilote/final/` : 3 leçons × 2 langues = 6 dossiers, tous présents.
  - `/mnt/project-files/actu-basics/actuariat/pilote/extraits/final/` : 6 extraits × 2 langues = 12 dossiers, tous présents.
  - `/mnt/project-files/actu-basics/niveau-1/final/vertical-9x16/<langue>/` : 28 dossiers par langue, FR et EN.
  - `/mnt/project-files/actu-basics/niveau-1/final/youtube-16x9/<langue>/` : 28 dossiers par langue, FR et EN.
- Archives par langue présentes : `ACTU-BASICS-Actuariat-pilote-FR.zip`, `-EN.zip`, `ACTU-BASICS-Actuariat-extraits-FR.zip`, `-EN.zip`.

### 2.3 Limites d'accès

- Les PDF des fiches de leçon par tableur (non encore produites) ne sont pas vérifiables : promesse de la v3.2, pas encore livraison.
- Les fichiers tableur, R et Python promis par la v3.2 pour certains modules ne sont pas produits ; aucune URL d'hébergement n'est encore choisie.
- Je n'ai pas relancé de rendu vidéo depuis la fusion : aucun contenu ne change, et une nouvelle inspection image par image n'apporterait rien à ce stade.

## 3. Proposition de fiche A3.01

Fichier séparé : [`A3-01-PROPOSITION.md`](A3-01-PROPOSITION.md). Points saillants :

- Table de référence : option recommandée **INSEE pour FR + SSA pour EN**, en acceptant que les nombres ne soient pas identiques entre FR et EN. Alternative Human Mortality Database (HMD) si l'identité stricte est préférée.
- Durée cible : 7 à 10 minutes.
- Exercice : probabilité de survivre de 60 à 65 ans (= l_65 / l_60).
- Distinction centrale : table observée vs table de tarification/provisionnement, avec exemples INSEE/SSA (observées) et TGF/TGH 05, UK CMI (tarification).
- Deux extraits verticaux proposés.
- Les chiffres exacts sont volontairement laissés en blanc dans la proposition, pour éviter de figer une valeur non vérifiée. Ils seront relevés sur les publications officielles au moment de l'écriture et vérifiés via `produire.py --verifier`.

## 4. Liste de contrôle de validation JG

### 4.1 Décisions à prendre avant l'écriture d'A3.01

- [ ] **Validation de la v3.2** (ou liste des points à corriger).
- [ ] **Table de référence pour A3.01** : option A (INSEE + SSA) ou option B (HMD).
- [ ] **Ordre de la suite Actuariat** : A3.01 (comme proposé par ChatGPT) ou A0.02 à A0.05 d'abord.
- [ ] **Deux extraits A3.01-x1 et A3.01-x2** : à écrire dans la foulée de la leçon ou plus tard ?

### 4.2 Décisions à prendre avant toute publication

- [ ] **Hébergement des fiches PDF** (FR et EN, 106 au total prévues) : description YouTube, dépôt public, autre.
- [ ] **Hébergement des fichiers tableur, R et Python** (uniquement pour les modules où ils aident) : même décision.
- [ ] **Stock de deux ensembles bilingues** finalisés avant d'annoncer un calendrier public.
- [ ] **Format des fiches PDF** : une page par langue, mentions légales, date de dernière vérification des examens, licence.

### 4.3 Vérifications à relancer périodiquement

- [ ] Suivi de la réforme de l'ASA à la SOA.
- [ ] Vérification annuelle des syllabi IFoA, CAS, formations reconnues par l'Institut des actuaires, à chaque mise à jour des tables de correspondance.

## 5. Blocages et points d'attention

- **Blocage pour publication, pas pour écriture** : l'hébergement des PDF et des fichiers doit être choisi avant l'annonce d'un calendrier public, mais A3.01 peut déjà être écrite.
- **Blocage pour la v3.2** : trois mentions « à vérifier » subsistent, dont deux (IFoA A6 et A7) pourront être fermées par une lecture détaillée des syllabi 2027, et une (date PCPA) par un communiqué officiel de la CAS.
- **Pas de blocage technique** : le dépôt est propre, le moteur n'a pas été touché depuis la validation du pilote Actuariat.

## 6. Ma lecture pour JG

Pour la suite immédiate, je recommande :
1. Arbitrage par JG des trois décisions de l'A3.01 (§ 4.1).
2. Mise à jour mineure de la v3.2 pour intégrer les deux propositions vérifiées de cet audit (colonne France et mention PCPA), avant l'écriture d'A3.01.
3. Puis écriture de la fiche A3.01 FR et EN.

ChatGPT reste le relecteur pédagogique, Perplexity le vérificateur des sources. Rien ne sera publié, fusionné, modifié sur `main` sans l'accord explicite de JG.
