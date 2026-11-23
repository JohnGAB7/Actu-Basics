# Proposition de fiche A3.01 · Lire une table de mortalité (FR et EN)

Statut : **proposition de Claude (2026-11-13), dans le cadre de l'ordre de travail de ChatGPT du 2026-11-12.** À arbitrer par JG avant l'écriture de la fiche YAML. Aucune fiche YAML n'est écrite tant que cette proposition n'est pas validée. Conforme à la v3.2 du parcours (sous réserve de validation de la v3.2 par JG).

## 1. Fil rouge et public

Première leçon du bloc 2 (techniques actuarielles), elle ouvre A3 « Life insurance and mortality ». Public : étudiants débutants préparant SOA Exam P ou FM et abordant la vie ; CAS Exam 1 ; IFoA CM1 (partie vie), CS2 (analyse de survie, de loin) ; cursus actuariels français reconnus par l'Institut des actuaires.

Phrase de rattachement : « Ce module aborde certaines notions évaluées dans les examens indiqués ci-dessous. Il contribue à la préparation de ces examens, sans couvrir nécessairement l'ensemble de leur programme. » Date de dernière vérification : 2026-11-12.

## 2. Objectifs pédagogiques

### FR
- Lire une table de mortalité : âge x, nombre de survivants l_x, décès d_x, probabilité de décès q_x, probabilité de survie p_x, espérance de vie restante e_x.
- Comprendre l'identité l_{x+1} = l_x − d_x, et q_x = d_x / l_x.
- Distinguer **table démographique observée** (ce qui s'est passé dans une population) et **table de tarification ou de provisionnement** (ce qu'un actuaire suppose pour un contrat), avec des usages différents.
- Reconnaître les quatre éléments d'identité d'une table : organisme, population, période d'observation, usage, date.

### EN
- Read a life table: age x, survivors l_x, deaths d_x, probability of death q_x, probability of survival p_x, expected remaining lifetime e_x.
- Understand l_{x+1} = l_x − d_x and q_x = d_x / l_x.
- Tell an **observed demographic life table** (what happened in a population) from a **pricing or reserving table** (what an actuary assumes for a contract), with different uses.
- Recognise the four identity elements of a table: issuer, population, observation period, use, date.

## 3. Prérequis

- Pourcentages (Niveau 1 déjà publié).
- Lecture d'un tableau de nombres.
- Probabilités de base de A2 ; le rappel strictement nécessaire est intégré à la leçon (ligne « Rappel probabilités »).
- A2b (statistique) **n'est pas** un prérequis pour A3.01.

## 4. Hypothèses explicites de la leçon

- Les nombres sont tirés d'une **table publique, nommée**, avec son organisme, sa population, sa période d'observation et sa date. Aucun chiffre réel n'est cité sans source primaire datée.
- Toute suite construite pour l'exemple à partir de ces chiffres (ex. une rente viagère simplifiée) est présentée comme un exemple pédagogique, pas comme un tarif.
- JG's Holding sert à cadrer la question économique ; les probabilités de décès ne sont jamais présentées comme les siennes.

## 5. Table de référence proposée pour l'exemple

Deux options à arbitrer par JG, fonction de la langue qui porte l'exemple numérique visible à l'écran :

### Option A · INSEE pour la version FR, SSA pour la version EN (recommandée)
- **FR** : Table de mortalité **INSEE 2019–2021** (ou édition la plus récente disponible au moment de l'écriture), France métropolitaine, les deux sexes confondus. Usage : démographique (observée).
- **EN** : Table de mortalité **US Social Security Administration (Period Life Table)**, population des États-Unis, année la plus récente publiée. Usage : démographique (observée).

Avantages : sources primaires bien identifiées, en accès libre, régulièrement citées ; le passage FR/EN reste lisible car chaque version cite la table de son pays.

Inconvénient : les deux versions n'affichent plus **exactement les mêmes nombres**. Il faut maintenir l'**identité FR/EN sur les égalités mathématiques** (l_{x+1} = l_x − d_x ; q_x = d_x / l_x) et sur les **arrondis** présentés, mais accepter que q_30 peut différer de quelques centièmes entre FR et EN.

### Option B · Même table dans les deux versions
- Table **Human Mortality Database (HMD)** pour un pays et une année choisis, par exemple France 2019 ou États-Unis 2019. Mêmes nombres FR et EN.

Avantages : identité parfaite des nombres entre FR et EN.

Inconvénients : HMD cite les sources nationales, moins reconnue par le grand public FR ; adhérents gratuits mais inscription requise.

**Recommandation** : option A, parce qu'elle correspond à l'habitude de la chaîne (adaptation FR en euros/sources françaises, adaptation EN en dollars/sources américaines). Les vidéos ne promettent pas la stricte identité des nombres entre FR et EN, elles promettent l'identité des idées et des méthodes.

Les valeurs exactes de l_x, d_x, q_x, p_x et e_x seront relevées sur les publications officielles au moment de l'écriture ; aucune n'est écrite ici pour éviter de figer un chiffre non vérifié.

## 6. Déroulé proposé (durée cible 7 à 10 minutes)

| # | Type | Durée | Contenu à l'écran | Notes |
| --- | --- | --- | --- | --- |
| 1 | accroche | 20 s | « À 65 ans, combien d'années vous reste-t-il *en moyenne* ? » | Question sincère, pas de promesse. |
| 2 | texte | 25 s | Chapitres de la leçon | Prérequis, objectifs, chapitres. |
| 3 | etapes | 70 s | « Une **table de mortalité**, c'est : âge x · l_x · d_x · q_x · p_x · e_x » | Définitions brèves, avec unités. Une étape par colonne. |
| 4 | tableau | 60 s | Extrait de 6 lignes : x = 0, 20, 40, 60, 80, 100 ; colonnes l_x, d_x, q_x | Chiffres relevés à la source au moment de l'écriture, avec citation. |
| 5 | formule | 45 s | l_{x+1} = l_x − d_x ; q_x = d_x / l_x ; p_x = 1 − q_x | Lien entre colonnes. |
| 6 | etapes | 70 s | « Rappel probabilités : q_x est la probabilité qu'un individu d'âge x décède avant l'âge x+1 » | Une seule ligne utile ; le reste reste dans la description. |
| 7 | exercice | 20 s (pause) | « À 60 ans, quelle est la probabilité de survivre jusqu'à 65 ans ? » | Pause pour que le spectateur calcule. |
| 8 | correction | 70 s | Calcul : p = l_65 / l_60 (avec chiffres de la table) ; résultat affiché à deux chiffres après la virgule. | Correction vérifiée par le vérificateur. |
| 9 | etapes | 90 s | « Deux familles de tables, deux usages » : observée vs tarification/provisionnement. | Jamais interchangeables ; chacune a son organisme, sa population, sa période, sa date. |
| 10 | tableau | 60 s | Exemples : INSEE/SSA (observées) ; TGF/TGH 05 en France (tarification rentes viagères) ; UK CMI (assurance vie) | Trois lignes, avec organisme, population, période, usage, date. |
| 11 | texte | 45 s | « Ce que la table **ne dit pas** » : évolution future, hétérogénéité, sélection d'assurés. | Précautions avant la suite (A3.02). |
| 12 | fin | 20 s | « Abonnez-vous pour apprendre à lire les chiffres. » | Fin standard ACTU-BASICS. |

Durée totale visée : environ **8 min 30 s**, dans la plage 6 à 12 min de la v3.2.

## 7. Exemple numérique entièrement vérifiable

L'exercice « probabilité de survivre de 60 à 65 ans » = l_65 / l_60.

Vérificateur attendu dans la fiche :
```
verifier:
  - {expression: "l65 / l60", attendu: VALEUR, libelle: "P(T_60 > 5)"}
```

Les valeurs l_65 et l_60 seront remplacées par les nombres de la table citée au moment de l'écriture. Le vérificateur de `produire.py` recalculera l'expression et refusera la fiche si la valeur attendue est fausse.

## 8. Fiches PDF (une FR, une EN)

Chaque fiche contient :
- la table extraite (6 lignes) avec citation complète : organisme, population, période, usage, date, URL ;
- les trois identités l_{x+1} = l_x − d_x, q_x = d_x / l_x, p_x = 1 − q_x ;
- l'exercice corrigé ;
- les repères de recouvrement thématique avec les examens (SOA FAM, CAS DISC/ ?, IFoA CM1 et CS2, France : notions communes) ;
- la **date de dernière vérification des correspondances d'examens**.

Les PDF ne sont pas produits tant que leur hébergement n'est pas choisi (décision en attente, v3.2 § 7).

## 9. Démonstration tableur (idée, pas livrable immédiat)

Fichier `A3-01-table-mortalite.xlsx` :
- Colonnes x, l_x, d_x, q_x, p_x calculées depuis l_x seul.
- Formule p(T_x > k) = l_{x+k} / l_x.
- Un graphique simple de l_x en fonction de x.

Fichier livré **quand l'hébergement est choisi**, pas avant.

## 10. Extraits verticaux proposés (après la leçon)

- **A3.01-x1 · « Combien d'années à 65 ans ? »** : lire e_65 dans une table ; précautions.
- **A3.01-x2 · « Table observée ou table de tarif ? »** : pourquoi un actuaire ne mélange pas les deux.

Un troisième extrait, « Probabilité de survivre de 60 à 65 ans », n'est **pas** proposé pour éviter de refaire l'exercice de la leçon longue.

## 11. Rôles de relecture

- **ChatGPT** : langue, pédagogie, typographie FR et anglais naturel, cohérence FR/EN.
- **Perplexity** : vérification des sources des tables, de leurs organismes et de leurs dates.
- **JG** : validation finale, puis production.

## 12. Décisions à arbitrer par JG avant l'écriture

1. Option A (INSEE + SSA) ou option B (HMD) pour la table de référence.
2. L'ordre : A3.01 comme prochaine leçon (comme proposé ici), ou finir A0 d'abord (A0.02 à A0.05, avec les deux nouvelles vidéos d'orientation de la v3.2).
3. Les deux extraits verticaux : les écrire dès que la leçon est validée, ou attendre.

## 13. Blocages et points d'attention

- Aucun chiffre réel n'est écrit dans cette proposition pour éviter de figer une valeur non vérifiée.
- L'hébergement des fiches PDF et du fichier tableur doit être choisi avant publication, mais pas avant l'écriture de la fiche YAML.
- La v3.2 du parcours doit être validée par JG avant que ses règles (fiches PDF FR + EN, formule « contribue à la préparation ») soient appliquées à A3.01. Si la v3.2 reste en attente, A3.01 peut être écrite à partir de la v2 en premier jet et harmonisée ensuite.

## 14. Alignement avec la séance a3/s01 du parcours actuariel (ajout du 2026-11-23)

La vidéo A3.01 servira à l'étape 1 de la séance `a3/s01` « Force de mortalité et espérance de vie » du parcours actuariel de JG (voir `PARCOURS-PLUS-ET-SEANCES.md`). Ce que cela change :

- **Le déroulé ne change pas.** La séance va plus loin (force de mortalité, espérance complète, code) ; la vidéo reste au niveau débutant : lire une table, passer de lₓ à une probabilité, puis à une espérance de vie. La force de mortalité est annoncée en une phrase à la fin (« la suite : A3+ ») et traitée dans A3+.01.
- **L'accroche est la même** dans la séance et la vidéo : « À 65 ans, combien d'années vous reste-t-il, en moyenne ? ».
- **La séance calcule avec la table belge MK** (loi de Makeham). Ses nombres sont déjà recalculés par les tests du parcours. Recalcul de contrôle avec ses paramètres : l₆₀ = 801 043, l₆₅ = 716 046, probabilité de survivre de 60 à 65 ans = 0,894, e₆₅ abrégée = 12,3 ans.

**Point d'attention éditorial.** MK est une table **de tarification** (réglementaire, pour des garanties décès), pas une table observée. Son e₆₅ d'environ 12 ans est très inférieure à l'espérance de vie réelle à 65 ans en France ou aux États-Unis. Répondre à l'accroche avec MK serait faux pour le spectateur. C'est en revanche l'exemple idéal de la scène 9 « Deux familles de tables, deux usages ».

### Option C · MK pour l'exercice, une table observée pour l'accroche (recommandée)

- **Exercice et correction (scènes 7 et 8)** : table MK, mêmes nombres en FR et en EN, et mêmes nombres que la séance. Le spectateur du parcours retrouve en vidéo le calcul qu'il refait à la main.
- **Réponse à l'accroche et scène 10** : une table observée et sourcée, INSEE pour la version FR, SSA pour la version EN (comme l'option A), avec son e₆₅ relevée à la source.
- **Scène 9** : la comparaison des deux e₆₅ (MK contre table observée) montre pourquoi on ne mélange jamais les deux familles.
- Sources à vérifier par Perplexity : le texte réglementaire belge qui définit MK et ses paramètres, la table INSEE et la table SSA les plus récentes.

**Décision 1 de la section 12 : option C choisie par JG le 2026-11-23.** Brouillon de la fiche : `contenus/conception/A3.01.yaml`. Les décisions 2 et 3 restent ouvertes ; l'ordre des séances du parcours plaide pour A3.01 comme prochaine leçon.
