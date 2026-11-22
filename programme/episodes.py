"""Contrôle et résumé des épisodes longs (révision 1.13 du programme).

Un épisode est une vidéo longue qui regroupe plusieurs entrées du catalogue.
Les entrées restent les chapitres de l'épisode.

Contrôles bloquants :
- chaque entrée du catalogue appartient à exactement un épisode ;
- tout épisode cite des entrées qui existent ;
- dans le cursus (piliers S et E), un chapitre ne demande jamais une notion
  traitée dans un épisode plus loin, ni plus loin dans le même épisode ;
- la durée estimée d'un épisode reste dans les bornes du format long.

Usage : python programme/episodes.py            (contrôles + tableau Markdown)
        python programme/episodes.py --sortie F  (écrit le tableau dans F)
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from construire import RACINE, lire_catalogue

FICHIER = RACINE / "catalogue" / "episodes.txt"
DUREE_MIN = 10   # minutes, en dessous : épisode trop court pour le format long
DUREE_MAX = 50   # minutes, au-dessus : à couper en deux épisodes
CURSUS = ("S", "E")


@dataclass
class Episode:
    id: str
    partie: str
    champs: dict = field(default_factory=dict)

    @property
    def contient(self) -> list[str]:
        return [x.strip() for x in self.champs.get("contient", "").split("|") if x.strip()]


def lire_episodes() -> tuple[list[Episode], list[str]]:
    episodes: list[Episode] = []
    erreurs: list[str] = []
    partie = ""
    for n, ligne in enumerate(FICHIER.read_text(encoding="utf-8").splitlines(), 1):
        if m := re.match(r"^# PARTIE (.+)$", ligne):
            partie = m.group(1).strip()
        elif m := re.match(r"^## (\S+)\s*$", ligne):
            episodes.append(Episode(m.group(1), partie))
        elif ligne.startswith("#") or not ligne.strip():
            continue
        elif m := re.match(r"^([a-z_]+):\s?(.*)$", ligne):
            if not episodes:
                erreurs.append(f"episodes.txt:{n} champ hors épisode")
                continue
            episodes[-1].champs[m.group(1)] = m.group(2).strip()
        else:
            erreurs.append(f"episodes.txt:{n} ligne illisible : {ligne[:60]}")
    return episodes, erreurs


def controler() -> tuple[list[Episode], dict, list[str]]:
    _, unites, erreurs = lire_catalogue()
    episodes, err = lire_episodes()
    erreurs += err
    position: dict[str, tuple[int, int]] = {}
    ids_vus: set[str] = set()
    for i, ep in enumerate(episodes):
        if ep.id in ids_vus:
            erreurs.append(f"{ep.id} : identifiant d'épisode en double")
        ids_vus.add(ep.id)
        for champ in ("titre", "titre_en", "contient", "programme_b"):
            if not ep.champs.get(champ):
                erreurs.append(f"{ep.id} : champ « {champ} » manquant")
        for j, uid in enumerate(ep.contient):
            if uid not in unites:
                erreurs.append(f"{ep.id} : entrée inconnue {uid}")
            elif uid in position:
                erreurs.append(f"{uid} figure dans deux épisodes ({episodes[position[uid][0]].id} et {ep.id})")
            else:
                position[uid] = (i, j)
    for uid in unites:
        if uid not in position:
            erreurs.append(f"{uid} n'appartient à aucun épisode")
    for uid, (i, j) in position.items():
        u = unites[uid]
        if u.pilier not in CURSUS:
            continue
        for p in u.prerequis:
            if p in position and unites[p].pilier in CURSUS and position[p] >= (i, j):
                erreurs.append(
                    f"{uid} ({episodes[i].id}) demande {p}, traité plus loin ({episodes[position[p][0]].id})"
                )
    for ep in episodes:
        a, b = duree(ep, unites)
        milieu = (a + b) / 2
        if not DUREE_MIN <= milieu <= DUREE_MAX:
            erreurs.append(f"{ep.id} : durée estimée {milieu:.0f} min hors des bornes {DUREE_MIN}-{DUREE_MAX}")
    erreurs += controler_compteurs(len(episodes))
    return episodes, unites, erreurs


# Fichiers qui annoncent l'état ACTUEL du programme : le nombre d'épisodes qu'ils citent doit être
# celui du catalogue (revue ChatGPT, PR #50, issue #54). Les historiques (REVISION, tableau des
# versions de 01-synthese.md) citent d'anciens nombres à dessein et ne sont pas contrôlés.
FICHIERS_ETAT = ["LISEZMOI.md"]


def controler_compteurs(n_episodes: int) -> list[str]:
    import re
    erreurs = []
    dossier = Path(__file__).resolve().parent
    for nom in FICHIERS_ETAT:
        texte = (dossier / nom).read_text(encoding="utf-8")
        for m in re.finditer(r"(\d+) épisodes longs", texte):
            if int(m.group(1)) != n_episodes:
                erreurs.append(f"{nom} annonce {m.group(1)} épisodes longs, le catalogue en compte {n_episodes}")
    return erreurs


def duree(ep: Episode, unites: dict) -> tuple[float, float]:
    us = [unites[x] for x in ep.contient if x in unites]
    return sum(u.duree[0] for u in us), sum(u.duree[1] for u in us)


def tableau(episodes: list[Episode], unites: dict) -> str:
    lignes = []
    partie = None
    for ep in episodes:
        if ep.partie != partie:
            partie = ep.partie
            lignes += ["", f"### {partie}", "", "| Épisode | Titre | Chapitres (entrées V12) | Durée | Programme-B |", "|---|---|---|---|---|"]
        a, b = duree(ep, unites)
        lignes.append(
            f"| {ep.id} | {ep.champs['titre']} | {', '.join(ep.contient)} | {a:.0f}–{b:.0f} min | {', '.join(x.strip() for x in ep.champs['programme_b'].split('|'))} |"
        )
    return "\n".join(lignes).strip() + "\n"


def main() -> int:
    episodes, unites, erreurs = controler()
    if erreurs:
        print("Contrôles des épisodes : ÉCHEC")
        for e in erreurs:
            print(" -", e)
        return 1
    total = sum(sum(duree(ep, unites)) / 2 for ep in episodes)
    print(f"Contrôles des épisodes : OK · {len(episodes)} épisodes, {len(unites)} chapitres, ≈ {total / 60:.0f} h")
    texte = tableau(episodes, unites)
    if "--sortie" in sys.argv:
        Path(sys.argv[sys.argv.index("--sortie") + 1]).write_text(texte, encoding="utf-8")
    else:
        print(texte)
    return 0


if __name__ == "__main__":
    sys.exit(main())
