"""Vidéo verticale 1080x1920 ou cours 16:9 1920x1080 : images Pillow envoyées à ffmpeg (H.264 + AAC)."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from .fiche import Edition, Scene
from .rendu import Rendu

FONDU_S = 0.4           # fondu enchaîné entre scènes (direction artistique : 350 à 500 ms)
HAUTEUR_BARRE = 10      # barre de progression (pixels)
DUREES_MIN = {"accroche": 2.5, "chiffre": 3.5, "texte": 2.5, "graphique": 5.0, "source": 4.0, "fin": 3.0, "accueil": 3.0, "cloture": 5.0,
              "titre": 2.5, "formule": 5.0, "etapes": 4.0, "courbe": 5.0, "exercice": 5.0, "correction": 4.0, "animation": 5.0}


def verifier_ffmpeg() -> None:
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("ffmpeg/ffprobe introuvables : installez ffmpeg (https://ffmpeg.org) "
                           "ou utilisez --sans-video.")


def duree_audio(chemin: Path) -> float:
    sortie = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "json", str(chemin)], capture_output=True, text=True, check=True)
    return float(json.loads(sortie.stdout)["format"]["duration"])


def duree_scene(scene: Scene, animation_s: float = 0.0) -> float:
    """Durée visuelle minimale : temps d'apparition du texte + temps de lecture."""
    if scene.duree:
        return float(scene.duree)
    minimum = DUREES_MIN.get(scene.type, 2.5)
    lecture = len(scene.texte.split()) / 3.0 + 1.0
    return max(minimum, lecture, animation_s + 1.5)


def durees_visuelles(edition: Edition, rendu: Rendu | None = None) -> list[float]:
    return [duree_scene(s, rendu.duree_animation(s) if rendu else 0.0) for s in edition.scenes]


def _zoomer(image: Image.Image, facteur: float) -> Image.Image:
    """Agrandit l'image de `facteur` autour de son centre, à taille constante (caméra lente)."""
    if facteur <= 1.0005:
        return image.copy()
    l, h = image.size
    cl, ch = l / facteur, h / facteur
    x0, y0 = (l - cl) / 2, (h - ch) / 2
    return image.resize((l, h), Image.BICUBIC, box=(x0, y0, x0 + cl, y0 + ch))


def produire_video(rendu: Rendu, edition: Edition, durees: list[float], audio: Path | None,
                   destination: Path) -> None:
    verifier_ffmpeg()
    fps = rendu.charte["formats"][rendu.format].get("fps", 30)
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
    n_total = round(total * fps)
    accent = rendu.c["progression"]
    image_globale = 0
    derniere: Image.Image | None = None
    mobile_precedent = False
    camera = rendu.charte.get("camera") or {}
    zoom = float(camera.get("zoom", 0)) if camera.get("actif") and rendu.format in camera.get("formats", []) else 0.0
    camera_sauf = set(camera.get("sauf_scenes") or [])
    try:
        for i, (scene, duree) in enumerate(zip(edition.scenes, durees)):
            n_images = round(duree * fps)
            n_fondu = round(FONDU_S * fps) if precedente is not None else 0
            n_anim = round(rendu.duree_animation(scene) * fps) + 1
            statique = rendu.dessiner(scene, i, n_scenes, None)
            decor = rendu.decor if rendu.decor_prevu(scene) else None
            libre_statique = decor.masque_libre(statique) if decor else None
            for k in range(n_images):
                temps = image_globale / fps
                image = rendu.dessiner(scene, i, n_scenes, k / fps) if k < n_anim else statique
                # Décor en mouvement : aucune image n'est figée, même quand le contenu est posé.
                if decor:
                    image = decor.appliquer(image, temps, None if k < n_anim else libre_statique)
                elif k >= n_anim:
                    image = image.copy()
                # Caméra lente : léger zoom continu vers le centre, pour que l'image ne reste jamais posée.
                if zoom and scene.type not in camera_sauf:
                    image = _zoomer(image, 1 + zoom * k / max(1, n_images - 1))
                if k == n_images - 1:   # départ du fondu suivant : sans logo ni barre de progression
                    derniere = image.copy()
                if k < n_fondu:
                    image = Image.blend(precedente, image, (k + 1) / (n_fondu + 1))
                # Logo mobile, posé après le fondu : il glisse en continu d'une scène à l'autre et
                # s'efface pendant le fondu vers une scène qui n'en porte pas (scène de fin).
                if rendu.mobile_prevu(scene):
                    rendu.poser_mobile(image, temps, scene, i)
                elif k < n_fondu and mobile_precedent:
                    rendu.poser_mobile(image, temps, scene, i, opacite=1 - (k + 1) / (n_fondu + 1))
                # Barre de progression en haut : incite à regarder jusqu'au bout.
                image_globale += 1
                ImageDraw.Draw(image).rectangle(
                    (0, 0, round(rendu.largeur * image_globale / n_total), HAUTEUR_BARRE), fill=accent)
                proc.stdin.write(image.tobytes())
            precedente = derniere
            mobile_precedent = rendu.mobile_prevu(scene)
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
