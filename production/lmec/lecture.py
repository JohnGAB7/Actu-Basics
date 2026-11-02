"""Lecture à voix haute des nombres et des symboles mathématiques.

Les moteurs locaux (Kokoro et Piper passent par espeak-ng) lisent mal certains écrits :
- FR « 50,7 % » devient « cinquante, sept pour cent » (la virgule est prise pour une pause) ;
- EN « 0.493 » devient « zero. four hundred ninety three » ;
- « − » et « ≈ » sont lus en anglais même en français, les exposants (« 2⁶⁴ ») disparaissent,
  « 365/365 » n'a pas de « sur » en français et devient « slash » en anglais.

Cette normalisation ne touche QUE le texte envoyé à la synthèse : les sous-titres et les images
gardent l'écriture de la fiche. Elle s'applique après le lexique de prononciation, qui garde
donc le dernier mot sur les mots, pas sur les nombres.
"""
from __future__ import annotations

import re

EXPOSANTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")
INDICES = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")

MOTS = {
    "fr": {
        "virgule": "virgule", "pour_cent": "pour cent", "moins": "moins", "environ": "environ",
        "fois": "fois", "divise": "divisé par", "egale": "égale", "sur": "sur",
        "puissance": "puissance", "chiffres": {str(i): m for i, m in enumerate(
            "zéro un deux trois quatre cinq six sept huit neuf".split())},
    },
    "en": {
        "virgule": "point", "pour_cent": "percent", "moins": "minus", "environ": "about",
        "fois": "times", "divise": "divided by", "egale": "equals", "sur": "over",
        "puissance": "to the power of", "chiffres": {str(i): m for i, m in enumerate(
            "zero one two three four five six seven eight nine".split())},
    },
}

_ESPACE_MILLIERS = re.compile(r"(?<=\d)[   ](?=\d{3}(?!\d))")


def normaliser_lecture(texte: str, langue: str) -> str:
    m = MOTS.get(langue[:2], MOTS["fr"])
    t = _ESPACE_MILLIERS.sub("", texte)          # « 18 400 » : un seul nombre
    t = t.replace(" ", " ").replace(" ", " ")

    # Exposants et indices : « 2⁶⁴ » -> « 2 puissance 64 », « P₀ » -> « P zéro ».
    t = re.sub(r"([⁰¹²³⁴⁵⁶⁷⁸⁹]+)",
               lambda x: f" {m['puissance']} {x.group(1).translate(EXPOSANTS)}", t)
    t = re.sub(r"([₀₁₂₃₄₅₆₇₈₉]+)",
               lambda x: " " + " ".join(m["chiffres"][c] for c in x.group(1).translate(INDICES)), t)

    # Décimales. FR : virgule dite. EN : « point » puis chiffre par chiffre (0.493 -> point four nine three).
    if langue.startswith("en"):
        t = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", t)        # « 18,400,000 » : séparateur de milliers
        t = re.sub(r"(?<![\d.])(\d+)\.(\d+)(?!\d|\.\d)",
                   lambda x: f"{x.group(1)} point " + " ".join(m["chiffres"][c] for c in x.group(2)), t)
    else:
        t = re.sub(r"(?<![\d,])(\d+),(\d+)(?!\d|,\d)", rf"\1 {m['virgule']} \2", t)

    t = re.sub(r"\s*%", f" {m['pour_cent']}", t)
    t = re.sub(r"(\d)\s*/\s*(\d)", rf"\1 {m['sur']} \2", t)
    t = re.sub(r"\s*≈\s*", f" {m['environ']} ", t)
    t = re.sub(r"\s*[×]\s*", f" {m['fois']} ", t)
    t = re.sub(r"(?<=\d)\s*x\s*(?=\d)", f" {m['fois']} ", t)
    t = re.sub(r"\s*÷\s*", f" {m['divise']} ", t)
    t = re.sub(r"(?<=[\w)])\s*=\s*(?=[\w(−-])", f" {m['egale']} ", t)
    t = re.sub(r"\s*−\s*", f" {m['moins']} ", t)                 # signe moins typographique
    t = re.sub(r"(?<=\d) - (?=\d)", f" {m['moins']} ", t)         # « 41 - 40 »
    return re.sub(r"\s+", " ", t).strip()
