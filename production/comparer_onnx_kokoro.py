"""Compare la voix produite par deux fichiers ONNX de Kokoro (même fichier de voix, même texte).

But : savoir si l'on peut remplacer `kokoro-v1.0.onnx` (publication GitHub de kokoro-onnx, sans
licence écrite) par `onnx/model.onnx` du dépôt `onnx-community/Kokoro-82M-v1.0-ONNX` (licence
Apache-2.0 déclarée) sans changer le son de la chaîne. Informatif : ne décide rien, mesure.

Usage : python production/comparer_onnx_kokoro.py A.onnx B.onnx voices-v1.0.bin [--sortie rapport.md]
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

PHRASES = {
    "fr": ("ff_siwis", "fr-fr", "Avec vingt-trois personnes, la probabilité dépasse cinquante pour cent."),
    "en": ("af_heart", "en-us", "With twenty-three people, the probability is above fifty percent."),
}


def main() -> int:
    from kokoro_onnx import Kokoro

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("onnx_a")
    p.add_argument("onnx_b")
    p.add_argument("voix")
    p.add_argument("--sortie")
    a = p.parse_args()
    moteurs = {nom: Kokoro(chemin, a.voix) for nom, chemin in (("A", a.onnx_a), ("B", a.onnx_b))}
    lignes = ["## Comparaison du son produit par les deux fichiers ONNX", "",
              f"- A : `{a.onnx_a}`", f"- B : `{a.onnx_b}`", "",
              "| Langue | Voix | Durée A (s) | Durée B (s) | Corrélation | Écart max |", "|---|---|---|---|---|---|"]
    for langue, (voix, code, texte) in PHRASES.items():
        sons = {}
        for nom, k in moteurs.items():
            son, taux = k.create(texte, voice=voix, speed=1.0, lang=code)
            sons[nom] = np.asarray(son, dtype=np.float64)
        n = min(len(sons["A"]), len(sons["B"]))
        x, y = sons["A"][:n], sons["B"][:n]
        corr = float(np.corrcoef(x, y)[0, 1]) if n > 1 else float("nan")
        lignes.append(f"| {langue} | `{voix}` | {len(sons['A']) / taux:.2f} | {len(sons['B']) / taux:.2f} | "
                      f"{corr:.4f} | {float(np.max(np.abs(x - y))):.4f} |")
    lignes += ["", "Une corrélation proche de 1 et des durées égales indiquent le même modèle ; "
               "l'écoute humaine reste nécessaire avant tout changement.", ""]
    texte = "\n".join(lignes)
    print(texte)
    if a.sortie:
        with open(a.sortie, "a", encoding="utf-8") as f:
            f.write(texte + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
