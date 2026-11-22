"""Calculs des laboratoires pédagogiques, sans interface.

Un laboratoire est décrit par des données fixes et des réglages (largeur de classe, valeur
déplacée…). Ces fonctions pures donnent les nombres affichés ; la vidéo (scènes du moteur) et
le site (laboratoire interactif) doivent les reprendre tels quels, pour que les deux supports
montrent exactement les mêmes résultats (revue ChatGPT, PR #50, issue #52).

Conventions, rappelées à l'écran :
- une classe [a ; b[ contient sa borne gauche et pas sa borne droite ;
- la dernière classe se termine strictement au-dessus du maximum, donc aucune valeur n'est perdue ;
- densité d'effectif = effectif / largeur ; l'aire d'un rectangle vaut son effectif ;
- densité de fréquence = effectif / (N × largeur) ; l'aire totale vaut 1 ;
- la médiane est recalculée après tri à chaque réglage, jamais figée.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Classe:
    debut: float
    fin: float
    effectif: int

    @property
    def largeur(self) -> float:
        return self.fin - self.debut

    def densite_effectif(self) -> float:
        return self.effectif / self.largeur

    def densite_frequence(self, total: int) -> float:
        return self.effectif / (total * self.largeur)


def _non_vide(valeurs: Sequence[float]) -> list[float]:
    v = [float(x) for x in valeurs]
    if not v:
        raise ValueError("série vide")
    return v


def classes_regulieres(valeurs: Sequence[float], largeur: float, origine: float = 0.0) -> list[Classe]:
    """Classes [origine + k·largeur ; origine + (k+1)·largeur[ jusqu'au-dessus du maximum."""
    v = _non_vide(valeurs)
    if largeur <= 0:
        raise ValueError("largeur de classe non positive")
    if min(v) < origine:
        raise ValueError("une valeur est sous l'origine des classes")
    n_classes = math.floor((max(v) - origine) / largeur) + 1   # la dernière dépasse strictement le maximum
    bornes = [origine + k * largeur for k in range(n_classes + 1)]
    return classes_inegales(v, bornes)


def classes_inegales(valeurs: Sequence[float], bornes: Sequence[float]) -> list[Classe]:
    """Effectifs sur des bornes croissantes quelconques ; erreur si une valeur sort des classes."""
    v = _non_vide(valeurs)
    b = [float(x) for x in bornes]
    if len(b) < 2 or any(b[i] >= b[i + 1] for i in range(len(b) - 1)):
        raise ValueError("bornes non strictement croissantes")
    hors = [x for x in v if not b[0] <= x < b[-1]]
    if hors:
        raise ValueError(f"valeurs hors des classes [{b[0]:g} ; {b[-1]:g}[ : {hors}")
    effectifs = [0] * (len(b) - 1)
    for x in v:
        for i in range(len(b) - 1):
            if b[i] <= x < b[i + 1]:
                effectifs[i] += 1
                break
    return [Classe(b[i], b[i + 1], effectifs[i]) for i in range(len(effectifs))]


def classes_depuis_effectifs(bornes: Sequence[float], effectifs: Sequence[int]) -> list[Classe]:
    if len(bornes) != len(effectifs) + 1:
        raise ValueError("il faut une borne de plus que d'effectifs")
    return [Classe(float(bornes[i]), float(bornes[i + 1]), int(effectifs[i])) for i in range(len(effectifs))]


def aire_totale(classes: Sequence[Classe], normalisation: str = "effectif") -> float:
    total = sum(c.effectif for c in classes)
    if normalisation == "effectif":
        return sum(c.densite_effectif() * c.largeur for c in classes)
    if normalisation == "frequence":
        return sum(c.densite_frequence(total) * c.largeur for c in classes)
    raise ValueError("normalisation : « effectif » ou « frequence »")


def moyenne(valeurs: Sequence[float]) -> float:
    v = _non_vide(valeurs)
    return sum(v) / len(v)


def mediane(valeurs: Sequence[float]) -> float:
    """Valeur de rang (n + 1) / 2 après tri ; n pair : moyenne des deux valeurs du milieu."""
    v = sorted(_non_vide(valeurs))
    n = len(v)
    m = n // 2
    return v[m] if n % 2 else (v[m - 1] + v[m]) / 2


def remplacer(valeurs: Sequence[float], indice: int, nouvelle: float) -> list[float]:
    """Remplace une valeur (même population, même effectif), sans en ajouter."""
    v = list(valeurs)
    v[indice] = nouvelle
    return v


def balayage(valeurs: Sequence[float], indice: int, positions: Sequence[float]) -> list[dict]:
    """État affiché à chaque position du curseur : valeur courante, série triée, moyenne, médiane."""
    etats = []
    for x in positions:
        serie = remplacer(valeurs, indice, x)
        etats.append({"valeur": x, "serie_triee": sorted(serie),
                      "moyenne": moyenne(serie), "mediane": mediane(serie)})
    return etats


def part_sous(valeurs: Sequence[float], seuil: float) -> float:
    """Part des valeurs strictement inférieures au seuil."""
    v = _non_vide(valeurs)
    return sum(x < seuil for x in v) / len(v)
