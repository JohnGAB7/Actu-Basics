# 11. Annexe : rapport des contrôles automatiques {#controles}

Ce document est produit par `programme/construire.py` à partir du catalogue (`programme/catalogue/*.txt`). La construction **échoue** si l'un des contrôles suivants n'est pas satisfait : identifiants uniques, champs obligatoires présents, prérequis existants, absence de cycle, aucun prérequis placé plus loin dans le tronc commun ni à un niveau plus élevé, durée compatible avec le format, réponses chiffrées exactes. Les calculs utilisent le même évaluateur que le moteur de production (`production/lmec/pedagogie.py`).

{{RAPPORT_CONTROLES}}

Pour reconstruire ce document après une modification du catalogue :

```
pip install -r programme/requirements.txt
python programme/construire.py --pdf
```
