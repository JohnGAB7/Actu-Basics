"""Vidéo verticale 1080x1920 : images Pillow envoyées à ffmpeg (H.264 + AAC)."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image

from .fiche import Edition, Scene
from .rendu import Rendu

FONDU_S = 0.25          # fondu enchaîné entre scènes
ANIMATION_S = 1.2       # compteur du chiffre / croissance des barres
DUREES_MIN = {"accroche": 2.5, "chiffre": 3.5, "texte": 2.5, "graphique": 5.0, "source": 4.0, "fin": 3.0}


def verifier_ffmpeg() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg/ffprobe introuvables : installez ffmpeg (https://ffmpeg.org) "
                           "ou utilisez --sans-video.")


def duree_audio(chemin: Path) -> float:
    sortie = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "json", str(chemin)], capture_output=True, text=True, check=True)
    return float(json.loads(sortie.stdout)["format"]["duration"])


def duree_scene(scene: Scene) -> float:
    if scene.duree:
        return float(scene.duree)
    minimum = DUREES_MIN.get(scene.type, 2.5)
    if scene.voix_off:  # ~150 mots/minute à l'oral
        return max(minimum, len(scene.voix_off.split()) / 2.5 + 0.6)
    return max(minimum, len(scene.texte.split()) / 3.0 + 1.0)  # lecture à l'écran


def calculer_durees(edition: Edition, audio: Path | None) -> list[float]:
    durees = [duree_scene(s) for s in edition.scenes]
    if audio:
        manque = duree_audio(audio) + 0.5 - sum(durees)
        if manque > 0:  # on ne coupe jamais la voix : la dernière scène s'allonge
            durees[-1] += manque
    return durees


def produire_video(rendu: Rendu, edition: Edition, durees: list[float], audio: Path | None,
                   destination: Path) -> None:
    verifier_ffmpeg()
    fps = rendu.charte["formats"]["video"]["fps"]
    total = sum(durees)
    commande = ["ffmpeg", "-y", "-loglevel", "error",
                "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{rendu.largeur}x{rendu.hauteur}",
                "-r", str(fps), "-i", "-"]
    if audio:
        commande += ["-i", str(audio)]
    else:  # piste silencieuse : certaines plateformes refusent les vidéos sans audio
        commande += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=48000:cl=stereo"]
    commande += ["-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                 "-t", f"{total:.2f}", "-movflags", "+faststart", str(destination)]
    proc = subprocess.Popen(commande, stdin=subprocess.PIPE)
    precedente: Image.Image | None = None
    n_scenes = len(edition.scenes)
    try:
        for i, (scene, duree) in enumerate(zip(edition.scenes, durees)):
            n_images = round(duree * fps)
            anime = scene.type in ("chiffre", "graphique")
            n_fondu = round(FONDU_S * fps) if precedente is not None else 0
            n_anim = round(ANIMATION_S * fps) if anime else 0
            statique = rendu.dessiner(scene, i, n_scenes, 1.0)
            for k in range(n_images):
                image = rendu.dessiner(scene, i, n_scenes, k / n_anim) if k < n_anim else statique
                if k < n_fondu:
                    image = Image.blend(precedente, image, (k + 1) / (n_fondu + 1))
                proc.stdin.write(image.tobytes())
            precedente = statique
        proc.stdin.close()
    except BrokenPipeError:
        pass
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg a échoué (code {proc.returncode})")


def sonder_video(chemin: Path) -> dict:
    sortie = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "stream=codec_type,codec_name,width,height,r_frame_rate:format=duration",
                             "-of", "json", str(chemin)], capture_output=True, text=True, check=True)
    return json.loads(sortie.stdout)
