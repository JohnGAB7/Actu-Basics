"""Conducteur lisible d'une fiche (texte à l'écran, animations, légendes, voix), pour la relecture.
Usage : python3 -I contenus/assemblage/conducteur.py <fiche.yaml> <langue> <sortie.md>"""
import sys

import yaml

fiche, langue, sortie = sys.argv[1], sys.argv[2], sys.argv[3]
f = yaml.safe_load(open(fiche, encoding="utf-8"))
ed = f["editions"][langue]
sc = ed["scenes"]
L = [f"# Conducteur {f['id']} ({langue.upper()}) : « {ed['titre']} »", "",
     f"Généré depuis `{fiche}` ({len(sc)} scènes, données fictives). Pour chaque scène : type, univers visuel, "
     "texte à l'écran, animation, légendes successives, puis la voix off. Les calculs écrits à l'écran "
     "apparaissent terme à terme pendant que la voix les dit.", ""]
for i, s in enumerate(sc, 1):
    L.append(f"### {i}. {s['type']}" + (f" {s['numero']}" if s.get("numero") else "")
             + (" · univers immersif (fond sombre)" if s.get("univers") == "immersif" else ""))
    if s.get("texte"):
        L.append(f"- Écran : {s['texte']}")
    if s.get("animation"):
        a = s["animation"]
        L.append(f"- Animation « {a['modele']} » : " + ", ".join(f"{k}={v}" for k, v in a.items() if k != "modele"))
    if s.get("courbe"):
        L.append(f"- Graphique {s['courbe'].get('style')} : points {s['courbe'].get('points')}")
    if s.get("formule"):
        L.append(f"- Formule : {s['formule']}")
    if s.get("valeur") is not None:
        L.append(f"- Chiffre clé : {s['valeur']}")
    for e in s.get("etapes") or []:
        L.append(f"  - {e}")
    if s.get("reponse"):
        L.append(f"- Réponse : {s['reponse']}")
    if s.get("note"):
        L.append(f"- Note à l'écran : {s['note']}")
    L.append(f"- Voix : {s.get('voix_off', '')}")
    L.append("")
open(sortie, "w", encoding="utf-8").write("\n".join(L))
print(sortie, len(sc), "scènes")
