"""Images d'inspection tirées de la VRAIE vidéo encodée (pas des images intermédiaires).

- planche-video.png   : chaque scène, en cours d'animation puis à l'état final
- apercu-mobile.png   : les mêmes images à la taille réelle d'un téléphone (≈ 390 px de large)
- zones-<plateforme>.png : interface de l'application simulée par-dessus (zones masquées en rouge)
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LARGEUR_MOBILE = 390  # largeur CSS d'un téléphone courant


def extraire_image(video: Path, t: float, destination: Path) -> Image.Image:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(video),
                    "-frames:v", "1", str(destination)], check=True)
    return Image.open(destination).convert("RGB")


def _police(taille):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", taille)
    except OSError:
        return ImageFont.load_default()


def _legende(im: Image.Image, texte: str) -> Image.Image:
    cadre = Image.new("RGB", (im.width, im.height + 44), "white")
    cadre.paste(im, (0, 44))
    ImageDraw.Draw(cadre).text((8, 10), texte, font=_police(22), fill="black")
    return cadre


def _grille(images: list[Image.Image], colonnes: int, marge: int = 12) -> Image.Image:
    w, h = images[0].size
    lignes = -(-len(images) // colonnes)
    planche = Image.new("RGB", (colonnes * (w + marge) + marge, lignes * (h + marge) + marge), (230, 230, 230))
    for i, im in enumerate(images):
        planche.paste(im, (marge + (i % colonnes) * (w + marge), marge + (i // colonnes) * (h + marge)))
    return planche


def produire_inspection(video: Path, scenes, durees: list[float], animations: list[float],
                        plateformes: dict, dossier: Path) -> list[Path]:
    dossier.mkdir(parents=True, exist_ok=True)
    tmp = dossier / "_image.png"
    finales, etapes = [], []
    t0 = 0.0
    for i, (scene, d, a) in enumerate(zip(scenes, durees, animations), 1):
        milieu = t0 + min(a * 0.5, d * 0.4)
        fin = t0 + min(a + 0.4, d - 0.15)
        im_m = extraire_image(video, milieu, tmp)
        im_f = extraire_image(video, fin, tmp)
        finales.append((scene.type, im_f))
        etapes += [_legende(im_m.resize((360, 640)), f"{i}. {scene.type} · {milieu:.1f}s"),
                   _legende(im_f.resize((360, 640)), f"{i}. {scene.type} · {fin:.1f}s")]
        t0 += d
    tmp.unlink(missing_ok=True)
    sorties = []
    planche = dossier / "planche-video.png"
    _grille(etapes, 6).save(planche, optimize=True)
    sorties.append(planche)

    h_mobile = round(1920 * LARGEUR_MOBILE / 1080)
    mobile = dossier / "apercu-mobile.png"
    _grille([im.resize((LARGEUR_MOBILE, h_mobile), Image.LANCZOS) for _, im in finales], 4).save(mobile, optimize=True)
    sorties.append(mobile)

    for cle in plateformes["cibles"]:
        p = plateformes["plateformes"][cle]
        z = p["zone_ui"]
        vues = []
        for type_, im in finales:
            calque = Image.new("RGBA", im.size, (0, 0, 0, 0))
            dc = ImageDraw.Draw(calque)
            rouge = (230, 40, 40, 110)
            dc.rectangle((0, 0, im.width, z["haut"]), fill=rouge)
            dc.rectangle((0, im.height - z["bas"], im.width, im.height), fill=rouge)
            dc.rectangle((0, 0, z["gauche"], im.height), fill=rouge)
            dc.rectangle((im.width - z["droite"], 0, im.width, im.height), fill=rouge)
            vue = Image.alpha_composite(im.convert("RGBA"), calque).convert("RGB")
            vues.append(_legende(vue.resize((360, 640)), f"{p['nom']} · {type_}"))
        chemin = dossier / f"zones-{cle}.png"
        _grille(vues, 4).save(chemin, optimize=True)
        sorties.append(chemin)
    return sorties
