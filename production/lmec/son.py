"""Habillage sonore ACTU-BASICS (prototype) : signature sonore et nappe discrète sous la voix.

Tout est synthétisé ici (aucun fichier ni service extérieur, aucun droit à payer) :
- signature : quatre notes de cloche ascendantes (la, do#, mi, la), l'« éveil » ;
- nappe : accord tenu très doux, qui s'efface quand la voix parle (ducking).
Réglages dans charte.yaml, section « son ». Activé par fiche avec « habillage_sonore: true ».
À remplacer par une identité sonore composée et validée par JG avant toute publication.
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

TAUX = 48000


def _lire(chemin: Path) -> np.ndarray:
    with wave.open(str(chemin), "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (1, 2, TAUX):
            raise ValueError(f"Format audio inattendu : {chemin.name}")
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768


def _ecrire(chemin: Path, signal: np.ndarray) -> None:
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TAUX)
        w.writeframes((np.clip(signal, -1, 1) * 32767).astype(np.int16).tobytes())


def _db(v: float) -> float:
    return 10 ** (v / 20)


def signature(duree: float = 2.6) -> np.ndarray:
    """Quatre notes de cloche ascendantes, la dernière tenue."""
    n = int(duree * TAUX)
    t = np.arange(n) / TAUX
    sortie = np.zeros(n)
    notes = [(0.00, 440.00, 0.55), (0.14, 554.37, 0.55), (0.28, 659.26, 0.6), (0.46, 880.00, 1.0)]
    for debut, f, amp in notes:
        tt = t - debut
        actif = tt >= 0
        tt = np.where(actif, tt, 0)
        decroissance = 1.4 if f < 880 else 0.9
        attaque = np.minimum(1, tt / 0.004)
        cloche = (np.sin(2 * np.pi * f * tt) * np.exp(-tt * decroissance * 2)
                  + 0.45 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * decroissance * 4)
                  + 0.25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * decroissance * 6)
                  + 0.10 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * decroissance * 10))
        sortie += np.where(actif, amp * attaque * cloche, 0)
    fin = np.minimum(1, (duree - t) / 0.4)   # extinction douce
    return sortie * fin / np.max(np.abs(sortie))


def nappe(n: int) -> np.ndarray:
    """n échantillons d'un accord de la majeur (avec neuvième) tenu, respiration lente, fondus."""
    t = np.arange(n) / TAUX
    duree = n / TAUX
    frequences = [110.0, 164.81, 220.0, 277.18, 329.63, 493.88]
    gains = [0.9, 0.6, 0.55, 0.4, 0.35, 0.18]
    sortie = np.zeros(n)
    for i, (f, g) in enumerate(zip(frequences, gains)):
        respiration = 0.75 + 0.25 * np.sin(2 * np.pi * (0.05 + i * 0.013) * t + i)
        sortie += g * respiration * (np.sin(2 * np.pi * f * t) + 0.15 * np.sin(2 * np.pi * 2 * f * t + i))
    fondu = np.minimum(1, np.minimum(t / 3.0, (duree - t) / 3.0))
    return sortie * np.clip(fondu, 0, 1) / np.max(np.abs(sortie))


def _enveloppe(signal: np.ndarray, fenetre_s: float = 0.25) -> np.ndarray:
    """Présence de la voix (0–1), lissée."""
    k = max(1, int(fenetre_s * TAUX))
    energie = np.convolve(np.abs(signal), np.ones(k) / k, mode="same")
    return np.clip(energie / (np.percentile(energie, 95) or 1), 0, 1)


def habiller(narration: Path | None, durees: list[float], conf: dict, destination: Path,
             index_fin: int | None = None) -> Path:
    """Mélange voix + nappe + signature(s). Sans voix, produit l'habillage seul."""
    total = sum(durees)
    n = int(round(total * TAUX))
    voix = _lire(narration)[:n] if narration else np.zeros(n)
    voix = np.pad(voix, (0, n - len(voix)))
    mix = voix.copy()
    if conf.get("nappe", True):
        base = _db(conf.get("nappe_db", -30))
        sous_voix = _db(conf.get("nappe_sous_voix_db", -38))
        presence = _enveloppe(voix) if narration else np.zeros(n)
        gain = base + (sous_voix - base) * presence
        mix += nappe(n) * gain
    sig = signature()
    gain_sig = _db(conf.get("signature_db", -12))
    instants = []
    if conf.get("signature_debut", True):
        instants.append((0.0, sig[: int(0.9 * TAUX)] * np.minimum(1, (0.9 - np.arange(int(0.9 * TAUX)) / TAUX) / 0.3)))
    if conf.get("signature_fin", True) and index_fin is not None:
        instants.append((sum(durees[:index_fin]) + 0.2, sig))
    for debut, s in instants:
        i = int(debut * TAUX)
        j = min(n, i + len(s))
        mix[i:j] += s[: j - i] * gain_sig
    crete = np.max(np.abs(mix)) or 1
    if crete > _db(-1):
        mix *= _db(-1) / crete
    _ecrire(destination, mix)
    return destination
