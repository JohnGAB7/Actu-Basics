"""Compare trois voix gratuites sur le même extrait (ouverture de la démo EP-S1A), pour que JG choisisse à l'oreille.

  A  Kokoro ff_siwis tel qu'aujourd'hui : une seule synthèse, vitesse 1,0, pas de pause ajoutée.
  B  Kokoro ff_siwis retravaillé : phrase par phrase, vitesse adaptée (nombres plus lents), pauses
     choisies (après une question, avant une révélation).
  C  Chatterbox Multilingual V3 (Resemble AI, licence MIT, local et gratuit), mêmes phrases et mêmes
     pauses, timbre calqué sur un extrait de la voix A (référence de 10 s), expressivité modérée.

Informatif : ne change rien à la chaîne de production. Sortie : un MP3 par voix et un rapport.
Usage : python production/comparer_voix_demo.py --sortie sortie/comparaison-voix [--sans-chatterbox]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent
TAUX = 24000

# (phrase, vitesse Kokoro pour B, pause après en secondes)
PHRASES = [
    ("Paris. Combien d'habitants ?", 0.95, 0.9),
    ("L'Insee, l'institut officiel de la statistique, publie trois réponses.", 1.02, 0.5),
    ("Deux virgule un millions.", 0.90, 0.6),
    ("Onze millions.", 0.90, 0.6),
    ("Treize virgule trois millions.", 0.90, 0.9),
    ("Même institut, même année, même ville.", 1.0, 0.4),
    ("Et pourtant, entre le premier et le dernier, on multiplie par plus de six.", 1.0, 0.8),
    ("Alors, qui s'est trompé ?", 0.95, 0.5),
    ("Faites une hypothèse.", 0.95, 1.6),
    ("Personne.", 0.92, 0.7),
    ("Ces trois chiffres sont justes. Ils ne répondent simplement pas à la même question.", 1.0, 0.6),
    ("Dans cet épisode, vous allez apprendre à démasquer n'importe quel chiffre, avec trois questions simples.", 1.02, 0.3),
]


def _silence(s: float, taux: int = TAUX) -> np.ndarray:
    return np.zeros(int(s * taux), dtype=np.float32)


def _ecrire(chemin: Path, x: np.ndarray, taux: int) -> None:
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taux)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def _mp3(wav: Path) -> Path:
    mp3 = wav.with_suffix(".mp3")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5",
                    "-b:a", "160k", str(mp3)], check=True)
    return mp3


def kokoro():
    from kokoro_onnx import Kokoro
    return Kokoro(str(RACINE / "voix/kokoro-v1.0.onnx"), str(RACINE / "voix/voices-v1.0.bin"))


def voix_a(k, dossier: Path) -> tuple[Path, float]:
    t0 = time.time()
    x, taux = k.create(" ".join(p for p, _, _ in PHRASES), voice="ff_siwis", speed=1.0, lang="fr-fr")
    w = dossier / "A-kokoro-actuelle.wav"
    _ecrire(w, x, taux)
    return w, time.time() - t0


def voix_b(k, dossier: Path) -> tuple[Path, float]:
    t0 = time.time()
    morceaux = [_silence(0.3)]
    for p, v, pause in PHRASES:
        x, _ = k.create(p, voice="ff_siwis", speed=v, lang="fr-fr")
        morceaux += [x.astype(np.float32), _silence(pause)]
    w = dossier / "B-kokoro-retravaillee.wav"
    _ecrire(w, np.concatenate(morceaux), TAUX)
    return w, time.time() - t0


def voix_c(reference: Path, dossier: Path) -> tuple[Path, float]:
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    t0 = time.time()
    try:
        m = ChatterboxMultilingualTTS.from_pretrained(device="cpu", t3_model="v3")
    except TypeError:                                   # version sans le paramètre t3_model
        m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
    morceaux = [np.zeros(int(0.3 * m.sr), dtype=np.float32)]
    torch.manual_seed(7)
    for p, _, pause in PHRASES:
        y = m.generate(p, language_id="fr", audio_prompt_path=str(reference), exaggeration=0.6, cfg_weight=0.5)
        morceaux += [y.squeeze().cpu().numpy().astype(np.float32), np.zeros(int(pause * m.sr), dtype=np.float32)]
    w = dossier / "C-chatterbox-v3.wav"
    _ecrire(w, np.concatenate(morceaux), m.sr)
    return w, time.time() - t0


def main() -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--sortie", type=Path, default=Path("sortie/comparaison-voix"))
    a.add_argument("--sans-chatterbox", action="store_true")
    args = a.parse_args()
    args.sortie.mkdir(parents=True, exist_ok=True)
    k = kokoro()
    lignes = ["# Comparaison de voix, ouverture de la démo EP-S1A", "",
              "Même texte pour les trois voix. Toutes gratuites et locales (tts.yaml : gratuit_uniquement).", "",
              "| Voix | Fichier | Durée | Temps de calcul |", "|---|---|---|---|"]
    w, s = voix_a(k, args.sortie)
    resultats = [("A, Kokoro actuelle", w, s)]
    w, s = voix_b(k, args.sortie)
    resultats.append(("B, Kokoro retravaillée (rythme, pauses)", w, s))
    reference = args.sortie / "reference-10s.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(resultats[0][1]), "-t", "10", str(reference)], check=True)
    if not args.sans_chatterbox:
        try:
            w, s = voix_c(reference, args.sortie)
            resultats.append(("C, Chatterbox Multilingual V3 (MIT)", w, s))
        except Exception as exc:                        # informatif : on rend A et B quoi qu'il arrive
            lignes.insert(4, f"Chatterbox indisponible : {exc!r}\n")
    for nom, w, s in resultats:
        with wave.open(str(w)) as f:
            duree = f.getnframes() / f.getframerate()
        mp3 = _mp3(w)
        lignes.append(f"| {nom} | {mp3.name} | {duree:.1f} s | {s:.0f} s |")
    lignes += ["", "Texte :", ""] + [f"> {p}" for p, _, _ in PHRASES]
    (args.sortie / "rapport.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
