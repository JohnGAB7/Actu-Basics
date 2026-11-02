"""Le fichier ONNX utilisé contient-il les poids officiels de Kokoro-82M (Apache-2.0) ?

`kokoro-v1.0.onnx` (publication GitHub de kokoro-onnx) n'a pas de licence écrite. Ce script
compare ses tenseurs à ceux du fichier officiel `kokoro-v1_0.pth` de `hexgrad/Kokoro-82M`
(licence Apache-2.0 déclarée), sans torch :

1. correspondance exacte d'un tenseur, à l'ordre des valeurs près (une conversion ONNX peut
   transposer une matrice ou réordonner les portes d'un LSTM sans changer une seule valeur) ;
2. pour les couches à normalisation des poids (`weight_g`, `weight_v`), le poids effectif
   g · v / ‖v‖ est recalculé et comparé, à 1e-5 près, aux tenseurs ONNX de même forme ;
3. pour le reste, part des valeurs officielles retrouvées bit à bit dans le fichier ONNX.

C'est une preuve technique de provenance, pas un avis juridique : elle dit si le fichier est
une conversion des poids officiels, pas quelle licence son auteur lui donne.

Usage : python production/comparer_poids_onnx.py kokoro-v1_0.pth kokoro-v1.0.onnx [--sortie rapport.md]
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import io
import pickle
import sys
import zipfile

import numpy as np

TYPES = {"FloatStorage": np.float32, "HalfStorage": np.float16, "DoubleStorage": np.float64,
         "LongStorage": np.int64, "IntStorage": np.int32, "BoolStorage": np.bool_}


class _Stockage:
    def __init__(self, type_, cle):
        self.type, self.cle = type_, cle


def lire_pth(contenu: bytes) -> dict:
    """Lit un fichier torch.save (zip) sans torch ; n'accepte que tenseurs, paramètres et dictionnaires."""
    archive = zipfile.ZipFile(io.BytesIO(contenu))
    prefixe = archive.namelist()[0].split("/")[0]

    def reconstruire(st, decalage, taille, pas, *_):
        dtype = TYPES.get(st.type)
        if dtype is None:
            raise ValueError(f"type de stockage non pris en charge : {st.type}")
        brut = np.frombuffer(archive.read(f"{prefixe}/data/{st.cle}"), dtype=dtype)
        t = np.dtype(dtype).itemsize
        return np.lib.stride_tricks.as_strided(brut[decalage:], shape=tuple(taille),
                                               strides=tuple(p * t for p in pas)).copy()

    def parametre(tenseur, *_):
        return tenseur

    class Lecteur(pickle.Unpickler):
        def find_class(self, module, nom):
            if module == "torch._utils" and nom == "_rebuild_tensor_v2":
                return reconstruire
            if module == "torch._utils" and nom == "_rebuild_parameter":
                return parametre
            if module == "torch" and nom in TYPES:
                return nom
            if module == "collections" and nom == "OrderedDict":
                return collections.OrderedDict
            raise pickle.UnpicklingError(f"objet refusé : {module}.{nom}")

        def persistent_load(self, pid):
            _, type_, cle, *_ = pid
            return _Stockage(type_ if isinstance(type_, str) else getattr(type_, "__name__", str(type_)), cle)

    return Lecteur(io.BytesIO(archive.read(f"{prefixe}/data.pkl"))).load()


def aplatir(d, prefixe=""):
    for k, v in d.items():
        if isinstance(v, dict):
            yield from aplatir(v, f"{prefixe}{k}.")
        elif isinstance(v, np.ndarray):
            yield f"{prefixe}{k}", v


def empreinte(a: np.ndarray) -> str:
    return hashlib.sha256(np.sort(a.astype(np.float32).ravel()).tobytes()).hexdigest()


def comparer(officiels: dict[str, np.ndarray], onnx_t: dict[str, np.ndarray]) -> dict:
    flottants = {k: v.astype(np.float32) for k, v in onnx_t.items() if v.dtype.kind == "f"}
    par_empreinte = collections.defaultdict(list)
    for k, v in flottants.items():
        par_empreinte[empreinte(v)].append(k)
    par_forme = collections.defaultdict(list)
    for k, v in flottants.items():
        par_forme[v.shape].append(k)
    tous_bits = np.unique(np.concatenate([v.ravel() for v in flottants.values()]).view(np.uint32))

    exacts, normalises, restants = {}, {}, {}
    vus_g = {k for k in officiels if k.endswith("weight_g")}
    for k, v in officiels.items():
        if v.dtype.kind != "f" or k.endswith("weight_g"):
            continue
        if k.endswith("weight_v") and k[:-1] + "g" in vus_g:
            g = officiels[k[:-1] + "g"].astype(np.float64)
            vv = v.astype(np.float64)
            norme = np.sqrt((vv ** 2).reshape(vv.shape[0], -1).sum(axis=1)).reshape(g.shape)
            w = (g * vv / norme).astype(np.float32)
            trouve = None
            for cand in par_forme.get(w.shape, []):
                if np.max(np.abs(flottants[cand] - w)) < 1e-5:
                    trouve = cand
                    break
            (normalises if trouve else restants)[k[:-2] + "(g·v/‖v‖)"] = (w.size, trouve)
            continue
        cands = par_empreinte.get(empreinte(v))
        if cands:
            exacts[k] = (v.size, cands[0])
        else:
            bits = v.astype(np.float32).ravel().view(np.uint32)
            # tous_bits est trié (np.unique) : recherche dichotomique, sans retrier 81 M de valeurs
            # à chaque tenseur comme le ferait np.isin (cause du dépassement de délai en CI).
            pos = np.minimum(np.searchsorted(tous_bits, bits), tous_bits.size - 1)
            part = float((tous_bits[pos] == bits).mean()) if bits.size else 0.0
            restants[k] = (v.size, part)
    total = sum(v.size for k, v in officiels.items() if v.dtype.kind == "f" and not k.endswith("weight_g"))
    return {"exacts": exacts, "normalises": normalises, "restants": restants, "total": total,
            "n_onnx": sum(v.size for v in flottants.values())}


def rapport(res: dict, sha_pth: str, sha_onnx: str) -> str:
    n_ex = sum(n for n, _ in res["exacts"].values())
    n_no = sum(n for n, _ in res["normalises"].values())
    rest = res["restants"]
    n_bits = sum(n * p for n, p in rest.values() if isinstance(p, float))
    total = res["total"] or 1
    lignes = ["## Poids du fichier ONNX comparés aux poids officiels", "",
              f"- Fichier officiel `kokoro-v1_0.pth` : SHA-256 `{sha_pth}`",
              f"- Fichier utilisé `kokoro-v1.0.onnx` : SHA-256 `{sha_onnx}`",
              f"- Valeurs officielles comparées : {res['total']:,} ; valeurs flottantes du fichier ONNX : {res['n_onnx']:,}".replace(",", " "),
              "", "| Correspondance | Tenseurs | Part des valeurs officielles |", "|---|---|---|",
              f"| tenseur identique (à l'ordre près) | {len(res['exacts'])} | {100 * n_ex / total:.2f} % |",
              f"| poids normalisé recalculé, écart < 1e-5 | {len(res['normalises'])} | {100 * n_no / total:.2f} % |",
              f"| autres tenseurs : valeurs retrouvées bit à bit | {len(rest)} | {100 * n_bits / total:.2f} % |",
              f"| **total retrouvé** | | **{100 * (n_ex + n_no + n_bits) / total:.2f} %** |", ""]
    pires = sorted(((k, n, p) for k, (n, p) in rest.items() if isinstance(p, float)), key=lambda x: x[2])[:10]
    if pires:
        lignes += ["Tenseurs les moins bien retrouvés :", ""] + [f"- `{k}` ({n} valeurs) : {100 * p:.1f} %" for k, n, p in pires] + [""]
    absents = [k for k, (_, t) in rest.items() if t is None]
    if absents:
        lignes += [f"Poids normalisés non retrouvés : {len(absents)}", ""]
    return "\n".join(lignes)


def main() -> int:
    import onnx
    from onnx import numpy_helper

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("pth")
    p.add_argument("onnx")
    p.add_argument("--sortie")
    a = p.parse_args()
    brut = open(a.pth, "rb").read()
    officiels = dict(aplatir(lire_pth(brut)))
    modele = onnx.load(a.onnx)
    onnx_t = {i.name: numpy_helper.to_array(i) for i in modele.graph.initializer}
    res = comparer(officiels, onnx_t)
    texte = rapport(res, hashlib.sha256(brut).hexdigest(),
                    hashlib.sha256(open(a.onnx, "rb").read()).hexdigest())
    print(texte)
    if a.sortie:
        with open(a.sortie, "a", encoding="utf-8") as f:
            f.write(texte + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
