"""Chargement et validation d'une fiche de contenu (YAML).

La fiche est le contrat entre l'éditorial (ChatGPT + propriétaire) et la
production. Ce module vérifie qu'elle est exploitable (structure, types,
champs réellement renseignés). Les contrôles de cohérence sont dans qc.py.
Aucun module ne vérifie la véracité d'un chiffre : c'est un contrôle humain.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field
from pathlib import Path

import yaml

LANGUES = ("fr", "en")
TYPES_SCENE_ACTUALITE = ("accroche", "chiffre", "texte", "graphique", "source", "fin")
# Scènes propres aux fiches pédagogiques (voir lmec/pedagogie.py).
TYPES_SCENE_PEDAGOGIE = ("titre", "formule", "etapes", "courbe", "exercice", "correction", "animation")
TYPES_SCENE = TYPES_SCENE_ACTUALITE + TYPES_SCENE_PEDAGOGIE
TYPES_FICHE = ("actualite", "pedagogique")
FAMILLES = ("comprendre_le_monde", "apprendre_les_statistiques", "comprendre_les_probabilites",
            "statistiques_en_pratique", "presentation")
# Format éditorial -> format d'image de la charte (charte.yaml, section formats).
FORMATS = {"short": "video", "educational": "video", "youtube_lesson": "lecon"}
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
    extra: dict = field(default_factory=dict)   # champs propres au type (formule, étapes, courbe…)


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
    type_fiche: str = "actualite"
    famille: str = "comprendre_le_monde"
    format: str = "short"
    pedagogie: dict = field(default_factory=dict)   # niveau, objectifs, prérequis (fiches pédagogiques)
    habillage_sonore: bool = False
    langues: tuple = ("fr", "en")   # langues produites ; une fiche peut être EN seule (parcours Actuariat)
    format_image_impose: str = ""   # « lecon » : déclinaison 16:9 YouTube d'une fiche verticale (--horizontal)
    palette_video: str = ""         # nom d'une palette de charte.yaml → palettes ; vide = palette par défaut

    @property
    def pedagogique(self) -> bool:
        return self.type_fiche == "pedagogique"

    @property
    def format_image(self) -> str:
        """Format d'image de la charte : « video » (vertical) ou « lecon » (16:9)."""
        return self.format_image_impose or FORMATS.get(self.format, "video")

    def contexte(self, cle: str, langue: str) -> str:
        """periode / perimetre / definition : chaîne commune ou {fr: ..., en: ...}."""
        valeur = getattr(self, cle)
        if isinstance(valeur, dict):
            valeur = valeur.get(langue)
        return "" if valeur is None else str(valeur)

    @property
    def est_validee(self) -> bool:
        return self.statut == "valide" and bool(self.valide_par)


def _vide(valeur) -> bool:
    return valeur is None or valeur == [] or valeur == {} or (
        isinstance(valeur, str) and valeur.strip() in VALEURS_VIDES)


def _exiger(dico, cle: str, contexte: str, erreurs: list[str]):
    valeur = dico.get(cle) if isinstance(dico, dict) else None
    if _vide(valeur):
        erreurs.append(f"{contexte} : champ « {cle} » manquant ou vide")
        return None
    return valeur


def _nom_type(valeur) -> str:
    return {dict: "un dictionnaire", list: "une liste", str: "un texte", bool: "un booléen (oui/non)",
            int: "un nombre", float: "un nombre"}.get(type(valeur), type(valeur).__name__)


def _dict(valeur, contexte: str, erreurs: list[str]) -> dict:
    """Un bloc qui doit être un dictionnaire (clé: valeur). Sinon : erreur explicite et {}."""
    if valeur is None:
        return {}
    if not isinstance(valeur, dict):
        erreurs.append(f"{contexte} doit être un bloc « clé: valeur », pas {_nom_type(valeur)}")
        return {}
    return valeur


def _liste(valeur, contexte: str, erreurs: list[str]) -> list:
    if valeur is None:
        return []
    if not isinstance(valeur, list):
        erreurs.append(f"{contexte} doit être une liste (lignes commençant par « - »), pas {_nom_type(valeur)}")
        return []
    return valeur


def _est_nombre(v) -> bool:
    """Vrai nombre fini : refuse les booléens, NaN (.nan) et l'infini (.inf) que YAML sait lire."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _texte(valeur, contexte: str, erreurs: list[str], bilingue: bool = True):
    """Texte simple ou, si `bilingue`, {fr: …, en: …}. Les nombres et dates sont acceptés comme texte."""
    if valeur is None:
        return valeur
    if isinstance(valeur, (str, int, float, dt.date)) and not isinstance(valeur, bool):
        return valeur
    if bilingue and isinstance(valeur, dict):
        inconnues = sorted(set(map(str, valeur)) - set(LANGUES))
        if inconnues:
            erreurs.append(f"{contexte} : langue(s) inconnue(s) {inconnues} (attendu : fr, en)")
        for l in LANGUES:
            v = valeur.get(l)
            if v is not None and (isinstance(v, (dict, list, bool))):
                erreurs.append(f"{contexte}.{l} doit être un texte, pas {_nom_type(v)}")
        return valeur
    attendu = "un texte ou {fr: …, en: …}" if bilingue else "un texte"
    erreurs.append(f"{contexte} doit être {attendu}, pas {_nom_type(valeur)}")
    return None


def charger_fiche(chemin: str | Path) -> Fiche:
    """Charge une fiche. Toute anomalie lève FicheInvalide avec la liste des problèmes, jamais
    une exception Python brute."""
    chemin = Path(chemin)
    try:
        brut = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FicheInvalide(f"Fichier introuvable : {chemin}") from exc
    except UnicodeDecodeError as exc:
        raise FicheInvalide("Fichier illisible : il doit être enregistré en UTF-8") from exc
    except yaml.YAMLError as exc:
        position = getattr(exc, "problem_mark", None)
        ou = f" (ligne {position.line + 1}, colonne {position.column + 1})" if position else ""
        raise FicheInvalide(f"YAML illisible{ou} : vérifier l'indentation, les deux-points et les guillemets. "
                            f"Détail : {getattr(exc, 'problem', None) or exc}") from exc
    if not isinstance(brut, dict):
        raise FicheInvalide("La fiche doit être un dictionnaire YAML (une suite de « clé: valeur »)"
                            + (" ; le fichier est vide" if brut is None else ""))
    try:
        return _construire(chemin, brut)
    except FicheInvalide:
        raise
    except Exception as exc:  # filet de sécurité : un cas non prévu reste une erreur lisible
        raise FicheInvalide(f"- Structure inattendue ({type(exc).__name__} : {exc}). Comparer la fiche avec "
                            "modeles/fiche-contenu.yaml.") from exc


def _construire(chemin: Path, brut: dict) -> Fiche:
    from . import pedagogie
    erreurs: list[str] = []
    type_fiche = str(brut.get("type_fiche") or "actualite").strip()
    if type_fiche not in TYPES_FICHE:
        erreurs.append(f"type_fiche « {type_fiche} » inconnu ({' | '.join(TYPES_FICHE)})")
    pedago = type_fiche == "pedagogique"
    famille = str(brut.get("famille") or ("comprendre_le_monde" if not pedago else "")).strip()
    if famille not in FAMILLES:
        erreurs.append(f"famille « {famille} » inconnue ({' | '.join(FAMILLES)})")
    format_ = str(brut.get("format") or "short").strip().lower()
    if format_ not in FORMATS:
        erreurs.append(f"format « {format_} » inconnu ({' | '.join(FORMATS)})")
    habillage = brut.get("habillage_sonore", False)
    if not isinstance(habillage, bool):
        erreurs.append("habillage_sonore doit valoir true ou false")
    palette_video = str(brut.get("palette_video") or "").strip()
    infos_pedago = pedagogie.valider_entete(brut, erreurs) if pedago else {}
    ident = _exiger(brut, "id", "fiche", erreurs)
    if ident is not None and not isinstance(ident, str):
        ident = str(ident)
    _texte(brut.get("theme"), "theme", erreurs, bilingue=False)
    validation = _dict(brut.get("validation"), "validation", erreurs)
    for cle in ("statut", "valide_par", "date"):
        _texte(validation.get(cle), f"validation.{cle}", erreurs, bilingue=False)

    if pedago and brut.get("chiffre_cle") is None:
        chiffre = {}
    else:
        chiffre = _dict(_exiger(brut, "chiffre_cle", "fiche", erreurs), "chiffre_cle", erreurs)
    if chiffre:
        v = _exiger(chiffre, "valeur", "chiffre_cle", erreurs)
        if v is not None and not _est_nombre(v):
            erreurs.append(f"chiffre_cle.valeur doit être un nombre fini (sans unité, ni espace, ni .nan/.inf), "
                           f"pas « {v} »")
        for cle in ("unite", "suffixe", "prefixe"):
            _texte(chiffre.get(cle), f"chiffre_cle.{cle}", erreurs)
        d = chiffre.get("decimales")
        if d is not None and (not isinstance(d, int) or isinstance(d, bool) or not 0 <= d <= 6):
            erreurs.append("chiffre_cle.decimales doit être un nombre entier entre 0 et 6")

    contexte = _dict(brut.get("contexte"), "contexte", erreurs)
    for cle in ("periode", "perimetre", "definition"):
        if pedago and contexte.get(cle) is None:   # facultatif : une notion n'a pas de période
            contexte[cle] = ""
            continue
        _texte(_exiger(contexte, cle, "contexte", erreurs), f"contexte.{cle}", erreurs)

    if pedago and not brut.get("sources"):
        sources = []   # un raisonnement mathématique n'a pas de source ; un fait cité en exige une (QC)
    else:
        sources = _liste(_exiger(brut, "sources", "fiche", erreurs), "sources", erreurs)
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            erreurs.append(f"sources[{i}] doit être un bloc avec « nom » et « url », pas {_nom_type(src)}")
            continue
        _texte(_exiger(src, "nom", f"sources[{i}]", erreurs), f"sources[{i}].nom", erreurs)
        url = _exiger(src, "url", f"sources[{i}]", erreurs)
        if url is not None and not isinstance(url, str):
            erreurs.append(f"sources[{i}].url doit être un texte")
        for cle in ("publication", "date_consultation"):
            _texte(src.get(cle), f"sources[{i}].{cle}", erreurs, bilingue=False)

    donnees = brut.get("donnees")
    if donnees is not None:
        donnees = _dict(donnees, "donnees", erreurs) or None
    if donnees:
        _texte(donnees.get("unite"), "donnees.unite", erreurs)
        d = donnees.get("decimales")
        if d is not None and (not isinstance(d, int) or isinstance(d, bool) or not 0 <= d <= 6):
            erreurs.append("donnees.decimales doit être un nombre entier entre 0 et 6")
        points = _liste(donnees.get("points"), "donnees.points", erreurs)
        if not points:
            erreurs.append("donnees : « points » manquant")
        for i, p in enumerate(points):
            if not isinstance(p, dict):
                erreurs.append(f"donnees.points[{i}] doit être un bloc {{label: …, valeur: …}}, pas {_nom_type(p)}")
                continue
            if not _est_nombre(p.get("valeur")):
                erreurs.append(f"donnees.points[{i}].valeur doit être un nombre fini (ni .nan ni .inf)")
            if _vide(p.get("label")):
                erreurs.append(f"donnees.points[{i}] : champ « label » manquant ou vide")
            else:
                _texte(p.get("label"), f"donnees.points[{i}].label", erreurs)
            if not isinstance(p.get("mis_en_avant", False), bool):
                erreurs.append(f"donnees.points[{i}].mis_en_avant doit valoir true ou false")

    langues_fiche = brut.get("langues", list(LANGUES))
    if (not isinstance(langues_fiche, list) or not langues_fiche
            or any(l not in LANGUES for l in langues_fiche) or len(set(langues_fiche)) != len(langues_fiche)):
        erreurs.append(f"langues doit être une liste de langues distinctes parmi {list(LANGUES)}")
        langues_fiche = list(LANGUES)
    langues_fiche = tuple(l for l in LANGUES if l in langues_fiche)

    editions: dict[str, Edition] = {}
    brut_editions = _dict(brut.get("editions"), "editions", erreurs)
    for langue in sorted(set(brut_editions) - set(langues_fiche)):
        erreurs.append(f"editions.{langue} : langue absente de « langues » {list(langues_fiche)}")
    for langue in langues_fiche:
        ctx = f"editions.{langue}"
        ed = brut_editions.get(langue)
        if not ed:
            erreurs.append(f"{ctx} : édition manquante"
                           + (" (FR et EN sont obligatoires)" if langues_fiche == LANGUES
                              else f" (langues : {', '.join(langues_fiche)})"))
            continue
        ed = _dict(ed, ctx, erreurs)
        if not ed:
            continue
        titre = _texte(_exiger(ed, "titre", ctx, erreurs), f"{ctx}.titre", erreurs, bilingue=False)
        legende = _texte(_exiger(ed, "legende", ctx, erreurs), f"{ctx}.legende", erreurs, bilingue=False)
        hashtags = []
        for h in _liste(ed.get("hashtags"), f"{ctx}.hashtags", erreurs):
            if isinstance(h, (dict, list, bool)) or h is None:
                erreurs.append(f"{ctx}.hashtags : « {h} » n'est pas un mot-clé")
                continue
            h = str(h).strip()
            hashtags.append(h if h.startswith("#") else f"#{h}")
        narration = ed.get("narration", True)
        if not isinstance(narration, bool):
            erreurs.append(f"{ctx}.narration doit valoir true ou false")
        audio = ed.get("audio")
        if audio is not None and not isinstance(audio, str):
            erreurs.append(f"{ctx}.audio doit être un chemin de dossier (texte)")
        scenes = []
        for i, s in enumerate(_liste(_exiger(ed, "scenes", ctx, erreurs), f"{ctx}.scenes", erreurs)):
            if not isinstance(s, dict):
                erreurs.append(f"{ctx}.scenes[{i}] doit être un bloc {{type: …, texte: …}}, pas {_nom_type(s)}")
                continue
            t = s.get("type")
            permis = TYPES_SCENE if pedago else TYPES_SCENE_ACTUALITE
            if t not in permis:
                erreurs.append(f"{ctx}.scenes[{i}] : type « {t} » inconnu ({', '.join(permis)})"
                               + ("" if t not in TYPES_SCENE else " : réservé aux fiches pédagogiques"))
                continue
            if t == "chiffre" and not chiffre and s.get("valeur") is None:
                erreurs.append(f"{ctx}.scenes[{i}] : scène chiffre sans « valeur » (ni chiffre_cle)")
            if t == "graphique" and not donnees:
                erreurs.append(f"{ctx}.scenes[{i}] : scène graphique sans bloc « donnees »")
            texte = _texte(s.get("texte"), f"{ctx}.scenes[{i}].texte", erreurs, bilingue=False)
            voix = _texte(s.get("voix_off"), f"{ctx}.scenes[{i}].voix_off", erreurs, bilingue=False)
            if t not in ("source", "correction") and not str(texte or "").strip():
                erreurs.append(f"{ctx}.scenes[{i}] ({t}) : texte vide")
            duree = s.get("duree")
            if duree is not None and (not _est_nombre(duree) or not 0.5 <= duree <= 120):
                erreurs.append(f"{ctx}.scenes[{i}].duree doit être un nombre de secondes entre 0,5 et 120")
                duree = None
            extra = pedagogie.valider_scene(t, s, f"{ctx}.scenes[{i}]", erreurs) if pedago else {}
            scenes.append(Scene(type=t, texte=str(texte or "").strip(), voix_off=str(voix or "").strip(),
                                duree=duree, extra=extra))
        editions[langue] = Edition(
            langue=langue, titre=str(titre or ""), legende=str(legende or "").strip(), hashtags=hashtags,
            scenes=scenes, audio=audio if isinstance(audio, str) else None, narration=narration is not False)

    statut = str(validation.get("statut") or "brouillon").strip()
    if statut not in STATUTS:
        erreurs.append(f"validation.statut « {statut} » inconnu ({' | '.join(STATUTS)})")

    if erreurs:
        raise FicheInvalide("\n".join(f"- {e}" for e in dict.fromkeys(erreurs)))

    return Fiche(
        chemin=chemin, id=str(ident), theme=str(brut.get("theme") or ""),
        statut=statut,
        valide_par=str(validation.get("valide_par") or ""),
        date_validation=str(validation.get("date") or ""),
        chiffre=chiffre, periode=contexte["periode"],
        perimetre=contexte["perimetre"], definition=contexte["definition"],
        sources=sources, donnees=donnees, editions=editions, brut=brut,
        type_fiche=type_fiche, famille=famille, format=format_, pedagogie=infos_pedago,
        habillage_sonore=habillage is True, langues=langues_fiche,
        palette_video=palette_video)
