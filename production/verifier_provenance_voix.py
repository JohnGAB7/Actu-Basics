"""Preuve de provenance des voix Kokoro utilisées par ACTU-BASICS.

Le fichier `voices-v1.0.bin` (publication GitHub de kokoro-onnx) ne porte aucune licence écrite.
Ce script compare ses vecteurs `ff_siwis` et `af_heart` aux fichiers officiels publiés par
l'auteur du modèle sur Hugging Face (`hexgrad/Kokoro-82M`, dossier `voices/`, licence Apache-2.0
déclarée sur la fiche du modèle). S'ils sont identiques, les voix utilisées sont bien celles du
dépôt officiel sous Apache-2.0, et non une version modifiée d'origine inconnue.

Il relève aussi, depuis l'API Hugging Face, la licence déclarée et la révision exacte du dépôt.

Usage : python production/verifier_provenance_voix.py [--sortie rapport.md]
Réseau : Hugging Face uniquement (lecture publique, sans compte ni clé). Aucun coût.
Torch n'est pas nécessaire : les fichiers .pt sont lus directement (archive zip + pickle restreint).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pickle
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent
sys.path.insert(0, str(RACINE))
from lmec.tts import DOSSIER_VOIX  # noqa: E402

DEPOT = "hexgrad/Kokoro-82M"
DEPOT_ONNX = "onnx-community/Kokoro-82M-v1.0-ONNX"   # export ONNX publié sur Hugging Face
SHA_ONNX_UTILISE = "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5"
VOIX = ("ff_siwis", "af_heart")
TYPES = {"FloatStorage": np.float32, "HalfStorage": np.float16, "DoubleStorage": np.float64,
         "BFloat16Storage": None}


def _telecharger(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "actu-basics"}),
                                timeout=120) as rep:
        return rep.read()


class _Stockage:
    def __init__(self, type_, cle):
        self.type, self.cle = type_, cle


def lire_tenseur_pt(contenu: bytes) -> np.ndarray:
    """Lit un tenseur sauvegardé par torch.save (format zip) sans importer torch.

    N'accepte que les objets nécessaires à un tenseur : tout autre objet est refusé
    (le pickle d'un fichier téléchargé n'exécute donc aucun code)."""
    archive = zipfile.ZipFile(io.BytesIO(contenu))
    noms = archive.namelist()
    prefixe = noms[0].split("/")[0]
    donnees = {}

    def stockage(cle):
        if cle not in donnees:
            donnees[cle] = archive.read(f"{prefixe}/data/{cle}")
        return donnees[cle]

    def reconstruire(st, decalage, taille, pas, *_):
        dtype = TYPES.get(st.type)
        if dtype is None:
            raise ValueError(f"type de stockage non pris en charge : {st.type}")
        brut = np.frombuffer(stockage(st.cle), dtype=dtype)
        taille_el = np.dtype(dtype).itemsize
        return np.lib.stride_tricks.as_strided(brut[decalage:], shape=tuple(taille),
                                               strides=tuple(p * taille_el for p in pas)).copy()

    class Lecteur(pickle.Unpickler):
        def find_class(self, module, nom):
            if module == "torch._utils" and nom == "_rebuild_tensor_v2":
                return reconstruire
            if module == "torch" and nom in TYPES:
                return nom
            if module == "collections" and nom == "OrderedDict":
                import collections
                return collections.OrderedDict
            raise pickle.UnpicklingError(f"objet refusé : {module}.{nom}")

        def persistent_load(self, pid):
            _, type_, cle, *_ = pid
            return _Stockage(type_ if isinstance(type_, str) else getattr(type_, "__name__", str(type_)), cle)

    return Lecteur(io.BytesIO(archive.read(f"{prefixe}/data.pkl"))).load()


def _section_onnx() -> list[str]:
    """Informatif : le fichier ONNX utilisé est-il l'un des fichiers publiés par onnx-community ?

    Ne fait pas échouer la vérification : l'export ONNX n'a pas d'équivalent officiel chez
    hexgrad, c'est un point ouvert documenté dans docs/voice-licenses.md."""
    lignes = ["## Fichier ONNX", "", f"- SHA-256 du fichier utilisé (`kokoro-v1.0.onnx`) : `{SHA_ONNX_UTILISE}`"]
    try:
        info = json.loads(_telecharger(f"https://huggingface.co/api/models/{DEPOT_ONNX}"))
        licence = (info.get("cardData") or {}).get("license") or "?"
        arbre = json.loads(_telecharger(f"https://huggingface.co/api/models/{DEPOT_ONNX}/tree/main/onnx"))
        lignes += [f"- Dépôt comparé : https://huggingface.co/{DEPOT_ONNX} (licence déclarée : **{licence}**, "
                   f"révision `{info.get('sha', '?')}`)", "", "| Fichier publié | Taille | SHA-256 |", "|---|---|---|"]
        trouve = None
        for f in arbre:
            sha = (f.get("lfs") or {}).get("oid", "")
            lignes.append(f"| `{f.get('path')}` | {f.get('size')} | `{sha}` |")
            if sha == SHA_ONNX_UTILISE:
                trouve = f.get("path")
        lignes += ["", f"**Le fichier utilisé est identique à `{trouve}` de ce dépôt.**" if trouve else
                   "**Le fichier utilisé n'est identique à aucun fichier de ce dépôt** (point ouvert maintenu)."]
    except Exception as exc:   # informatif seulement
        lignes.append(f"- Comparaison impossible : {exc}")
    return lignes + [""]


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("--sortie", type=Path, default=None)
    args = parseur.parse_args()

    lignes = ["# Provenance des voix Kokoro", ""]
    info = json.loads(_telecharger(f"https://huggingface.co/api/models/{DEPOT}"))
    licence = (info.get("cardData") or {}).get("license") or "?"
    revision = info.get("sha", "?")
    lignes += [f"- Dépôt officiel : https://huggingface.co/{DEPOT}",
               f"- Révision vérifiée : `{revision}`",
               f"- Licence déclarée par le dépôt : **{licence}**", ""]

    locales = np.load(DOSSIER_VOIX / "voices-v1.0.bin")
    lignes += ["| Voix | Fichier officiel | SHA-256 officiel | Identique à `voices-v1.0.bin` |", "|---|---|---|---|"]
    ok = licence.lower().startswith("apache")
    for voix in VOIX:
        url = f"https://huggingface.co/{DEPOT}/resolve/{revision}/voices/{voix}.pt"
        contenu = _telecharger(url)
        officiel = lire_tenseur_pt(contenu)
        local = locales[voix]
        identique = officiel.shape == local.shape and np.array_equal(officiel.astype(np.float32), local)
        ecart = float(np.max(np.abs(officiel.astype(np.float32) - local))) if officiel.shape == local.shape else None
        ok &= identique
        lignes.append(f"| `{voix}` | {url} | `{hashlib.sha256(contenu).hexdigest()}` | "
                      f"{'oui' if identique else 'NON'} (forme {officiel.shape}, écart max {ecart}) |")
    lignes += ["", "**Résultat (voix) : provenance confirmée.**" if ok
               else "**Résultat (voix) : provenance NON confirmée.**", ""]
    lignes += _section_onnx()
    texte = "\n".join(lignes)
    print(texte)
    if args.sortie:
        args.sortie.write_text(texte + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
