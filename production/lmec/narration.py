"""Narration : texte des scènes -> phrases synthétisées -> durées de scènes -> piste audio + repères de sous-titres.

Principe de synchronisation : chaque PHRASE est synthétisée séparément, donc on connaît
exactement quand elle commence et finit. Les sous-titres suivent ces temps réels ; à
l'intérieur d'une phrase longue, les morceaux de sous-titres sont répartis au prorata
des caractères. Une scène dure toujours au moins le temps de sa voix : rien n'est coupé.
"""
from __future__ import annotations

import re
import subprocess
import wave
from dataclasses import dataclass, field
from pathlib import Path

from .fiche import Edition, Fiche
from .lecture import normaliser_lecture
from .textes import texte_parle
from .tts import Cache, ErreurTTS, Fournisseur, duree_wav

AMORCE_S = 0.35      # silence avant la voix au début de chaque scène (le texte commence à apparaître)
ENTRE_PHRASES_S = 0.25
# Silence après une phrase selon sa ponctuation : une question laisse le temps de réfléchir,
# un deux-points annonce la suite sans casser l'élan.
PAUSES_PONCTUATION = {"?": 0.6, "!": 0.4, ".": 0.32, "…": 0.5, ":": 0.12, ";": 0.2}


def pause_apres(phrase: str) -> float:
    fin = phrase.rstrip()[-1:]
    return PAUSES_PONCTUATION.get(fin, ENTRE_PHRASES_S)


FIN_SCENE_S = 0.5    # respiration après la dernière phrase d'une scène
TAUX = 48000
CIBLE_LUFS = -16     # volume homogène, adapté aux réseaux sociaux


@dataclass
class Phrase:
    texte: str        # texte affiché en sous-titre (tel qu'écrit dans la fiche)
    debut: float      # secondes depuis le début de la scène
    fin: float


@dataclass
class VoixScene:
    wav: Path
    duree_voix: float
    phrases: list[Phrase]


@dataclass
class Narration:
    fournisseur: str
    publiable: bool
    scenes: list[VoixScene]
    synthese: int = 0        # phrases réellement synthétisées (hors cache)
    depuis_cache: int = 0    # phrases reprises du cache (aucun coût)
    caracteres: int = 0      # volume envoyé au fournisseur (pour estimer le coût)
    notes: list[str] = field(default_factory=list)


def decouper_phrases(texte: str) -> list[str]:
    texte = re.sub(r"\s+", " ", texte).strip()
    return [p for p in re.split(r"(?<=[.!?…;:])\s+(?=\S)", texte) if p.strip()]


def preparer_pour_voix(texte: str, langue: str, lexique: dict) -> str:
    """Texte réellement envoyé à la synthèse : espaces normalisées + lexique de prononciation."""
    t = texte.replace(" ", " ").replace(" ", " ")
    for ecrit, dit in (lexique.get(langue) or {}).items():
        t = re.sub(rf"(?<!\w){re.escape(ecrit)}(?!\w)", dit, t)
    # Puis lecture des nombres et symboles (virgule décimale, %, −, ≈, fractions, exposants).
    return normaliser_lecture(t, langue)


def _assembler(parties: list[tuple[Path | None, float]], destination: Path) -> None:
    """Concatène des WAV mono 48 kHz ; (None, d) = silence de d secondes."""
    with wave.open(str(destination), "wb") as sortie:
        sortie.setnchannels(1)
        sortie.setsampwidth(2)
        sortie.setframerate(TAUX)
        for chemin, duree in parties:
            if chemin is None:
                sortie.writeframes(b"\x00\x00" * int(round(duree * TAUX)))
                continue
            with wave.open(str(chemin), "rb") as w:
                if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, TAUX):
                    raise ErreurTTS(f"Format audio inattendu : {chemin.name}")
                sortie.writeframes(w.readframes(w.getnframes()))


def produire_voix(fiche: Fiche, edition: Edition, fournisseur: Fournisseur, cache: Cache,
                  travail: Path, lexique: dict) -> Narration:
    """Synthétise toutes les scènes. Lève ErreurTTS à la première phrase impossible à produire."""
    fournisseur.verifier()
    travail.mkdir(parents=True, exist_ok=True)
    n = Narration(fournisseur.nom, fournisseur.publiable, [])
    for i, scene in enumerate(edition.scenes, 1):
        ecrit = texte_parle(scene, fiche, edition.langue)
        wav_scene = travail / f"scene-{i:02d}.wav"
        if fournisseur.par_scene:  # enregistrement manuel : une prise par scène
            fournisseur.synthetiser_scene(i, wav_scene)
            d = duree_wav(wav_scene)
            n.scenes.append(VoixScene(wav_scene, d, [Phrase(ecrit, 0.0, d)]))
            continue
        parties, phrases, t = [], [], 0.0
        for k, phrase in enumerate(decouper_phrases(ecrit)):
            dite = preparer_pour_voix(phrase, edition.langue, lexique)
            wav = travail / f"scene-{i:02d}-{k:02d}.wav"
            if cache.obtenir(fournisseur, dite, wav):
                n.depuis_cache += 1
            else:
                n.synthese += 1
                n.caracteres += len(dite)
            d = duree_wav(wav)
            if k:
                pause = pause_apres(phrases[-1].texte)
                parties.append((None, pause))
                t += pause
            parties.append((wav, d))
            phrases.append(Phrase(phrase, t, t + d))
            t += d
        _assembler(parties, wav_scene)
        n.scenes.append(VoixScene(wav_scene, t, phrases))
    return n


def durees_avec_voix(durees_visuelles: list[float], narration: Narration, explicites: list) -> tuple[list[float], list[str]]:
    """Chaque scène dure max(besoin visuel, amorce + voix + respiration) ; une durée imposée trop courte est allongée."""
    durees, notes = [], []
    for i, (dv, vs, impose) in enumerate(zip(durees_visuelles, narration.scenes, explicites), 1):
        besoin = AMORCE_S + vs.duree_voix + FIN_SCENE_S
        d = max(dv, besoin)
        if impose and impose < besoin:
            notes.append(f"Scène {i} : durée imposée {impose} s allongée à {besoin:.1f} s pour ne pas couper la voix")
        durees.append(round(d, 3))
    return durees, notes


def piste_complete(narration: Narration, durees: list[float], travail: Path) -> Path:
    """Piste unique calée sur les scènes, puis volume normalisé (EBU R128).

    loudnorm peut perdre quelques dizaines de ms en fin de piste : apad complète jusqu'à la durée exacte."""
    parties = []
    for vs, d in zip(narration.scenes, durees):
        parties += [(None, AMORCE_S), (vs.wav, vs.duree_voix), (None, max(0.0, d - AMORCE_S - vs.duree_voix))]
    brute = travail / "narration-brute.wav"
    _assembler(parties, brute)
    finale = travail / "narration.wav"
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(brute),
                        "-af", f"loudnorm=I={CIBLE_LUFS}:TP=-1.5:LRA=11,aresample={TAUX},apad=whole_dur={sum(durees):.3f}",
                        "-ar", str(TAUX), "-ac", "1", str(finale)], capture_output=True, text=True)
    if r.returncode != 0:
        raise ErreurTTS(f"Normalisation du volume impossible : {r.stderr.strip()[:200]}")
    return finale


def reperes_sous_titres(narration: Narration, durees: list[float]) -> list[tuple[float, float, str]]:
    """(début, fin, texte) en temps absolu, calés sur les phrases réellement prononcées."""
    from .textes import decouper_sous_titres
    reperes, t0 = [], 0.0
    for vs, d in zip(narration.scenes, durees):
        for ph in vs.phrases:
            morceaux = decouper_sous_titres(ph.texte)
            total = sum(len(m) for m in morceaux) or 1
            debut = t0 + AMORCE_S + ph.debut
            for m in morceaux:
                fin = debut + (ph.fin - ph.debut) * len(m) / total
                reperes.append((debut, fin, m))
                debut = fin
        t0 += d
    return reperes
