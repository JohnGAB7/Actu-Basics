"""Chargement et validation d'une fiche de contenu (YAML).

La fiche est le contrat entre l'éditorial (ChatGPT + propriétaire) et la
production. Ce module vérifie qu'elle est exploitable (structure, types,
champs réellement renseignés). Les contrôles de cohérence sont dans qc.py.
Aucun module ne vérifie la véracité d'un chiffre : c'est un contrôle humain.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

LANGUES = ("fr", "en")
TYPES_SCENE = ("accroche", "chiffre", "texte", "graphique", "source", "fin")
STATUTS = ("brouillon", "valide")
# Valeurs laissées par le modèle qui ne comptent pas comme « renseignées ».
VALEURS_VIDES = {"", "https://", "http://", "AAAA-MM-JJ", "AAAA-MM-JJ-sujet-court"}


class FicheInvalide(Exception):
    """La fiche ne respecte pas le modèle : la production est bloquée."""


@dataclass
class Scene:
    type: str
    texte: str = ""
    voix_off: str = ""
    duree: float | None = None


@dataclass
class Edition:
    langue: str
    titre: str
    legende: str
    hashtags: list[str]
    scenes: list[Scene]
    audio: str | None = None
    narration: bool = True  # False = choix éditorial explicite d'une vidéo sans voix


@dataclass
class Fiche:
    chemin: Path
    id: str
    theme: str
    statut: str
    valide_par: str
    date_validation: str
    chiffre: dict
    periode: str | dict
    perimetre: str | dict
    definition: str | dict
    sources: list[dict]
    donnees: dict | None
    editions: dict[str, Edition] = field(default_factory=dict)
    brut: dict = field(default_factory=dict, repr=False)

    def contexte(self, cle: str, langue: str) -> str:
        """periode / perimetre / definition : chaîne commune ou {fr: ..., en: ...}."""
        valeur = getattr(self, cle)
        return str(valeur.get(langue, "")) if isinstance(valeur, dict) else str(valeur)

    @property
    def est_validee(self) -> bool:
        return self.statut == "valide" and bool(self.valide_par)


def _exiger(dico: dict, cle: str, contexte: str, erreurs: list[str]):
    valeur = dico.get(cle) if isinstance(dico, dict) else None
    if valeur is None or valeur == [] or (isinstance(valeur, str) and valeur.strip() in VALEURS_VIDES):
        erreurs.append(f"{contexte} : champ « {cle} » manquant ou vide")
    return valeur


def charger_fiche(chemin: str | Path) -> Fiche:
    chemin = Path(chemin)
    try:
        brut = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise FicheInvalide(f"YAML illisible : {exc}") from exc
    if not isinstance(brut, dict):
        raise FicheInvalide("La fiche doit être un dictionnaire YAML")

    erreurs: list[str] = []
    ident = _exiger(brut, "id", "fiche", erreurs)
    validation = brut.get("validation") or {}
    chiffre = _exiger(brut, "chiffre_cle", "fiche", erreurs) or {}
    if chiffre:
        _exiger(chiffre, "valeur", "chiffre_cle", erreurs)
        v = chiffre.get("valeur", 0)
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            erreurs.append("chiffre_cle.valeur doit être un nombre (sans unité ni espace)")
    contexte = brut.get("contexte") or {}
    for cle in ("periode", "perimetre", "definition"):
        _exiger(contexte, cle, "contexte", erreurs)
    sources = _exiger(brut, "sources", "fiche", erreurs) or []
    for i, src in enumerate(sources):
        _exiger(src, "nom", f"sources[{i}]", erreurs)
        _exiger(src, "url", f"sources[{i}]", erreurs)

    donnees = brut.get("donnees")
    if donnees:
        points = donnees.get("points") or []
        if not points:
            erreurs.append("donnees : « points » manquant")
        for i, p in enumerate(points):
            if isinstance(p.get("valeur"), bool) or not isinstance(p.get("valeur"), (int, float)):
                erreurs.append(f"donnees.points[{i}].valeur doit être un nombre")

    editions: dict[str, Edition] = {}
    brut_editions = brut.get("editions") or {}
    for langue in LANGUES:
        ed = brut_editions.get(langue)
        ctx = f"editions.{langue}"
        if not ed:
            erreurs.append(f"{ctx} : édition manquante (FR et EN sont obligatoires)")
            continue
        titre = _exiger(ed, "titre", ctx, erreurs)
        legende = _exiger(ed, "legende", ctx, erreurs)
        scenes_brutes = _exiger(ed, "scenes", ctx, erreurs) or []
        scenes = []
        for i, s in enumerate(scenes_brutes):
            t = (s or {}).get("type")
            if t not in TYPES_SCENE:
                erreurs.append(f"{ctx}.scenes[{i}] : type « {t} » inconnu ({', '.join(TYPES_SCENE)})")
                continue
            if t == "graphique" and not donnees:
                erreurs.append(f"{ctx}.scenes[{i}] : scène graphique sans bloc « donnees »")
            if t not in ("source",) and not str(s.get("texte") or "").strip():
                erreurs.append(f"{ctx}.scenes[{i}] ({t}) : texte vide")
            scenes.append(Scene(type=t, texte=str(s.get("texte") or "").strip(),
                                voix_off=str(s.get("voix_off") or "").strip(),
                                duree=s.get("duree")))
        editions[langue] = Edition(
            langue=langue, titre=str(titre or ""), legende=str(legende or "").strip(),
            hashtags=[h if h.startswith("#") else f"#{h}" for h in (ed.get("hashtags") or [])],
            scenes=scenes, audio=ed.get("audio"), narration=ed.get("narration", True) is not False)

    statut = str(validation.get("statut") or "brouillon").strip()
    if statut not in STATUTS:
        erreurs.append(f"validation.statut « {statut} » inconnu ({' | '.join(STATUTS)})")

    if erreurs:
        raise FicheInvalide("\n".join(f"- {e}" for e in erreurs))

    return Fiche(
        chemin=chemin, id=str(ident), theme=str(brut.get("theme", "")),
        statut=statut,
        valide_par=str(validation.get("valide_par") or ""),
        date_validation=str(validation.get("date") or ""),
        chiffre=chiffre, periode=contexte["periode"],
        perimetre=contexte["perimetre"], definition=contexte["definition"],
        sources=sources, donnees=donnees, editions=editions, brut=brut)
