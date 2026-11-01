"""Formatage typographique FR / EN des nombres et des textes."""
from __future__ import annotations

ESPACE_FINE = "\u202f"  # espace fine insécable (ponctuation FR)
ESPACE_MILLIERS = "\u00a0"  # insécable normale : la fine est trop étroite en très gros corps


def _texte_langue(valeur, langue: str) -> str:
    """Accepte soit une chaîne, soit un dictionnaire {fr: ..., en: ...}."""
    if isinstance(valeur, dict):
        valeur = valeur.get(langue)
    return "" if valeur is None else str(valeur)


def formater_nombre(valeur: float, langue: str, decimales: int | None = None) -> str:
    """8200000 -> « 8 200 000 » (fr) / « 8,200,000 » (en) ; 3.5 -> « 3,5 » / « 3.5 »."""
    if decimales is None:
        decimales = 0 if float(valeur).is_integer() else min(len(repr(float(valeur)).split(".")[1]), 3)
    texte = f"{valeur:,.{decimales}f}"
    if langue == "fr":
        texte = texte.replace(",", ESPACE_MILLIERS).replace(".", ",")
    return texte


def formater_chiffre(chiffre: dict, langue: str, valeur: float | None = None) -> str:
    """Chiffre clé complet avec préfixe/suffixe propres à la langue."""
    v = chiffre["valeur"] if valeur is None else valeur
    corps = formater_nombre(v, langue, chiffre.get("decimales"))
    prefixe = _texte_langue(chiffre.get("prefixe"), langue)
    suffixe = _texte_langue(chiffre.get("suffixe"), langue)
    return f"{prefixe}{corps}{suffixe}"


def unite(chiffre: dict, langue: str) -> str:
    return _texte_langue(chiffre.get("unite"), langue)


def typographie(texte: str, langue: str) -> str:
    """Espaces insécables avant ; : ! ? % en français."""
    if langue != "fr":
        return texte
    for signe in (";", ":", "!", "?", "%", "»"):
        texte = texte.replace(f" {signe}", f"{ESPACE_FINE}{signe}")
    return texte.replace("« ", f"«{ESPACE_FINE}")
