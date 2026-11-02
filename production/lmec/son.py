"""Habillage sonore ACTU-BASICS (prototype) : signature sonore et nappe discrète sous la voix.

Tout est synthétisé ici (aucun fichier ni service extérieur, aucun droit à payer) :
- signature : quatre notes de cloche ascendantes (la, do#, mi, la), l'« éveil », avec une montée
  de souffle avant la dernière note, un accord tenu et une réverbération simple ;
- nappe : accord tenu très doux, qui s'efface quand la voix parle (ducking) ;
- repères : tic discret à chaque seconde du compte à rebours, petit carillon à chaque révélation
  (chiffre qui s'arrête, réponse d'une correction).
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


def _cloche(f: float, tt: np.ndarray, decroissance: float) -> np.ndarray:
    """Cloche : partiels inharmoniques + légère modulation de fréquence (brillance de l'attaque)."""
    fm = 1 + 0.002 * np.sin(2 * np.pi * 5.2 * tt) * np.exp(-tt * 3)
    attaque = np.minimum(1, tt / 0.004)
    return attaque * (np.sin(2 * np.pi * f * fm * tt) * np.exp(-tt * decroissance * 2)
                      + 0.45 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * decroissance * 4)
                      + 0.25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * decroissance * 6)
                      + 0.10 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * decroissance * 10))


def _note(sortie: np.ndarray, t: np.ndarray, debut: float, f: float, amp: float, decroissance: float) -> None:
    tt = t - debut
    actif = tt >= 0
    sortie += np.where(actif, amp * _cloche(f, np.where(actif, tt, 0), decroissance), 0)


def _reverb(signal: np.ndarray, mix: float = 0.22) -> np.ndarray:
    """Réverbération simple (quatre échos amortis en parallèle, décalés), sans dépendance."""
    sortie = signal.copy()
    for retard_ms, gain in ((37, 0.5), (53, 0.42), (71, 0.36), (97, 0.3)):
        k = int(TAUX * retard_ms / 1000)
        echo = np.zeros_like(signal)
        echo[k:] = signal[:-k]
        for _ in range(4):           # quelques réinjections, de plus en plus faibles
            plus = np.zeros_like(echo)
            plus[k:] = echo[:-k] * gain
            echo = echo + plus * 0.5
        sortie += mix * gain * echo
    return sortie


def signature(duree: float = 3.2) -> np.ndarray:
    """Quatre notes de cloche ascendantes (la, do#, mi, la) : un souffle monte avant la dernière,
    qui s'ouvre sur un accord tenu (la majeur). Réverbération légère."""
    n = int(duree * TAUX)
    t = np.arange(n) / TAUX
    sortie = np.zeros(n)
    for debut, f, amp in ((0.00, 440.00, 0.5), (0.14, 554.37, 0.5), (0.28, 659.26, 0.55)):
        _note(sortie, t, debut, f, amp, 1.4)
    # Montée de souffle (bruit filtré, enveloppe croissante) vers la dernière note.
    gen = np.random.default_rng(7)           # graine fixe : signature identique à chaque rendu
    bruit = np.convolve(gen.standard_normal(n), np.ones(24) / 24, mode="same")
    montee = np.clip((t - 0.2) / 0.36, 0, 1) ** 2 * (t < 0.56)
    sortie += 0.18 * bruit * montee
    # Dernière note et accord tenu, plus long.
    _note(sortie, t, 0.56, 880.00, 1.0, 0.8)
    for f, amp in ((440.00, 0.28), (554.37, 0.22), (659.26, 0.22)):
        _note(sortie, t, 0.58, f, amp, 0.55)
    sortie = _reverb(sortie)
    fin = np.clip((duree - t) / 0.6, 0, 1)   # extinction douce
    return sortie * fin / np.max(np.abs(sortie))


def tic() -> np.ndarray:
    """Tic de compte à rebours : clic boisé très court."""
    n = int(0.09 * TAUX)
    t = np.arange(n) / TAUX
    s = (np.sin(2 * np.pi * 1850 * t) + 0.5 * np.sin(2 * np.pi * 2900 * t)) * np.exp(-t * 70)
    return s / np.max(np.abs(s))


def carillon() -> np.ndarray:
    """Révélation : deux notes de cloche (mi puis la), brèves."""
    n = int(1.3 * TAUX)
    t = np.arange(n) / TAUX
    s = np.zeros(n)
    _note(s, t, 0.0, 1318.51, 0.6, 2.2)
    _note(s, t, 0.09, 1760.00, 0.8, 2.0)
    s = _reverb(s, 0.18)
    return s * np.clip((1.3 - t) / 0.3, 0, 1) / np.max(np.abs(s))


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
    # Moyenne glissante par somme cumulée : O(n). np.convolve (O(n·k)) prenait plus d'une heure
    # sur une vidéo de 8 minutes.
    a = np.abs(signal)
    c = np.concatenate(([0.0], np.cumsum(a)))
    gauche = np.arange(len(a)) - k // 2
    haut, bas = np.clip(gauche + k, 0, len(a)), np.clip(gauche, 0, len(a))
    energie = (c[haut] - c[bas]) / k
    return np.clip(energie / (np.percentile(energie, 95) or 1), 0, 1)


def habiller(narration: Path | None, durees: list[float], conf: dict, destination: Path,
             index_fin: int | None = None, reperes: list[tuple[float, str]] | None = None) -> Path:
    """Mélange voix + nappe + signature(s) + repères sonores ((instant, « tic » | « revele »)).
    Sans voix, produit l'habillage seul."""
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
    instants = [(debut, s * gain_sig) for debut, s in instants]
    if conf.get("reperes", True):
        sons = {"tic": tic() * _db(conf.get("tic_db", -26)), "revele": carillon() * _db(conf.get("revele_db", -20))}
        instants += [(debut, sons[nature]) for debut, nature in (reperes or []) if nature in sons]
    for debut, s in instants:
        i = int(debut * TAUX)
        j = min(n, i + len(s))
        if j > i:
            mix[i:j] += s[: j - i]
    crete = np.max(np.abs(mix)) or 1
    if crete > _db(-1):
        mix *= _db(-1) / crete
    _ecrire(destination, mix)
    return destination
