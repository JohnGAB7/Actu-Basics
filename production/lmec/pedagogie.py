"""Fiches pédagogiques : validation, calculs vérifiés, contrôles qualité propres à l'enseignement.

Une fiche pédagogique (type_fiche: pedagogique) explique une notion de statistiques ou de probabilités.
Elle n'a pas forcément de chiffre clé ni de source (un raisonnement mathématique se vérifie par le
calcul), mais elle a des objectifs, un niveau, et des scènes dédiées : titre de chapitre, formule,
étapes de calcul, courbe calculée, exercice et correction.

Les résultats numériques annoncés peuvent être RECALCULÉS par la machine (bloc « verifier ») : c'est
la différence majeure avec les fiches d'actualité, dont les chiffres se vérifient à la source.
L'évaluateur n'accepte qu'un petit sous-ensemble d'expressions Python (arithmétique, sommes, produits,
combinaisons…) : aucun accès aux fichiers, aux modules ni aux attributs.
"""
from __future__ import annotations

import ast
import math

NIVEAUX = ("decouverte", "lycee", "licence", "master", "professionnel")
DUREES_FORMAT = {            # (min, max) en secondes, avertissement seulement
    "short": (15, 90),
    "educational": (90, 600),
    "youtube_lesson": (300, 3600),
}
MODELES_ANIMATION = ("paires",)   # paires : n points sur un cercle, reliés deux à deux

FORMATS_SCENES = {           # scènes possibles par format (au-delà : avertissement)
    "short": {"accroche", "chiffre", "texte", "graphique", "source", "fin", "formule", "etapes", "courbe",
              "exercice", "correction", "animation"},
}
LIMITE_RANGE = 1_000_000
LIMITE_FACTORIELLE = 5_000

_FONCTIONS = {
    "comb": math.comb, "perm": math.perm, "sqrt": math.sqrt, "exp": math.exp, "log": math.log,
    "log10": math.log10, "floor": math.floor, "ceil": math.ceil, "abs": abs, "round": round, "min": min,
    "max": max, "sum": sum, "prod": math.prod, "len": len, "erf": math.erf, "int": int, "float": float,
}
_CONSTANTES = {"pi": math.pi, "e": math.e}


class CalculInvalide(ValueError):
    """Expression refusée ou impossible à calculer."""


def _range(*args):
    r = range(*(int(a) for a in args))
    if len(r) > LIMITE_RANGE:
        raise CalculInvalide(f"range trop grand ({len(r)} valeurs, maximum {LIMITE_RANGE})")
    return r


def _entier_borne(nom, *args):
    for a in args:
        if not float(a).is_integer() or not 0 <= a <= LIMITE_RANGE:
            raise CalculInvalide(f"{nom} : entiers entre 0 et {LIMITE_RANGE} attendus")
    return [int(a) for a in args]


def _puissance(a, b):
    """a ** b sans risque de calcul démesuré (10**10**10…)."""
    if abs(b) > 10_000:
        raise CalculInvalide("exposant trop grand (10 000 au plus)")
    if isinstance(a, int) and isinstance(b, int) and abs(a) > 1 and b * math.log2(abs(a)) > 20_000:
        raise CalculInvalide("résultat trop grand")
    return a ** b


class _Puissances(ast.NodeTransformer):
    def visit_BinOp(self, n):
        self.generic_visit(n)
        if isinstance(n.op, ast.Pow):
            return ast.copy_location(ast.Call(ast.Name("_puissance", ast.Load()), [n.left, n.right], []), n)
        return n


def _factorielle(n):
    if not float(n).is_integer() or not 0 <= n <= LIMITE_FACTORIELLE:
        raise CalculInvalide(f"factorial({n}) : entier entre 0 et {LIMITE_FACTORIELLE} attendu")
    return math.factorial(int(n))


_NOEUDS = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Load, ast.Call,
           ast.GeneratorExp, ast.ListComp, ast.comprehension, ast.Store, ast.Tuple, ast.List, ast.Compare,
           ast.IfExp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.USub,
           ast.UAdd, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq)


def evaluer(expression: str, variables: dict | None = None) -> float:
    """Calcule une expression arithmétique sûre, par ex. « 1 - prod((365-k)/365 for k in range(23)) »."""
    if not isinstance(expression, str) or not expression.strip():
        raise CalculInvalide("expression vide")
    if len(expression) > 500:
        raise CalculInvalide("expression trop longue (500 caractères au plus)")
    try:
        arbre = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as exc:
        raise CalculInvalide(f"syntaxe invalide : {exc.msg}") from exc
    noms_locaux = {n.id for n in ast.walk(arbre) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    for n in ast.walk(arbre):
        if not isinstance(n, _NOEUDS):
            raise CalculInvalide(f"élément non autorisé : {type(n).__name__}")
        if isinstance(n, ast.Constant) and (isinstance(n.value, bool) or not isinstance(n.value, (int, float))):
            raise CalculInvalide("seuls les nombres sont autorisés (pas de texte)")
        if isinstance(n, ast.Call) and not isinstance(n.func, ast.Name):
            raise CalculInvalide("seules les fonctions mathématiques simples sont autorisées")
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            if n.id not in _FONCTIONS and n.id not in _CONSTANTES and n.id not in ("range", "factorial") \
                    and n.id not in (variables or {}) and n.id not in noms_locaux:
                raise CalculInvalide(f"nom inconnu « {n.id} »")
    contexte = {"__builtins__": {}, **_FONCTIONS, **_CONSTANTES, "range": _range, "factorial": _factorielle,
                "comb": lambda n, k: math.comb(*_entier_borne("comb", n, k)),
                "perm": lambda n, k=None: math.perm(*_entier_borne("perm", n, *(() if k is None else (k,)))),
                "_puissance": _puissance, **(variables or {})}
    arbre = ast.fix_missing_locations(_Puissances().visit(arbre))
    try:
        valeur = eval(compile(arbre, "<calcul>", "eval"), contexte)  # noqa: S307 (arbre filtré ci-dessus)
    except CalculInvalide:
        raise
    except Exception as exc:
        raise CalculInvalide(f"{type(exc).__name__} : {exc}") from exc
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)) or not math.isfinite(valeur):
        raise CalculInvalide(f"le résultat n'est pas un nombre fini ({valeur!r})")
    return float(valeur)


def tolerance_par_defaut(attendu: float) -> float:
    """Moitié de la dernière décimale écrite : 0.507 -> 0.0005 ; 253 -> 0.5."""
    texte = repr(float(attendu))
    if "e" in texte:
        return abs(attendu) * 1e-6
    decimales = len(texte.split(".")[1].rstrip("0")) if "." in texte else 0
    return 0.5 * 10 ** (-decimales)


def points_courbe(courbe: dict) -> list[tuple[float, float]]:
    """Points [x, y] écrits dans la fiche, ou calculés à partir d'une expression de la variable."""
    if courbe.get("points"):
        return [(float(x), float(y)) for x, y in courbe["points"]]
    var = courbe.get("variable", "n")
    de, a = courbe["de"], courbe["a"]
    pas = courbe.get("pas", 1)
    n = int(round((a - de) / pas)) + 1
    if not 2 <= n <= 2000:
        raise CalculInvalide(f"courbe : {n} points (entre 2 et 2000)")
    xs = [de + i * pas for i in range(n)]
    return [(x, evaluer(courbe["expression"], {var: x})) for x in xs]


# --------------------------------------------------------------------------- validation de la fiche
def valider_entete(brut: dict, erreurs: list[str]) -> dict:
    p = brut.get("pedagogie")
    if not isinstance(p, dict):
        erreurs.append("pedagogie : bloc manquant (niveau, objectifs, prerequis) pour une fiche pédagogique")
        return {}
    niveau = p.get("niveau")
    if niveau not in NIVEAUX:
        erreurs.append(f"pedagogie.niveau « {niveau} » inconnu ({' | '.join(NIVEAUX)})")
    objectifs = p.get("objectifs")
    if not isinstance(objectifs, dict) or not all(isinstance(objectifs.get(l), list) and objectifs.get(l)
                                                  for l in ("fr", "en")):
        erreurs.append("pedagogie.objectifs : listes « fr » et « en » d'objectifs (« À la fin, vous saurez… »)")
    prerequis = p.get("prerequis", {})
    if prerequis is not None and not isinstance(prerequis, dict):
        erreurs.append("pedagogie.prerequis doit être un bloc {fr: [...], en: [...]}")
    return {"niveau": niveau, "objectifs": objectifs or {}, "prerequis": prerequis or {}}


def _nombre(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _liste_textes(v, ctx, erreurs) -> list[str]:
    if not isinstance(v, list) or not v or not all(isinstance(e, (str, int, float)) for e in v):
        erreurs.append(f"{ctx} doit être une liste de textes non vide")
        return []
    return [str(e) for e in v]


def valider_scene(type_: str, s: dict, ctx: str, erreurs: list[str]) -> dict:
    """Champs propres au type de scène. Retourne Scene.extra."""
    extra: dict = {}
    if type_ == "titre" and s.get("numero") is not None:
        extra["numero"] = str(s["numero"])
    if type_ == "formule":
        f = s.get("formule")
        lignes = [f] if isinstance(f, str) else f
        if not isinstance(lignes, list) or not lignes or not all(isinstance(l, str) and l.strip() for l in lignes):
            erreurs.append(f"{ctx} : champ « formule » manquant (notation LaTeX, ex. P = \\frac{{a}}{{b}}, "
                           "ou liste de lignes qui apparaissent une à une)")
        else:
            extra["formule"] = [l.strip() for l in lignes]
        if not str(s.get("voix_off") or "").strip():
            erreurs.append(f"{ctx} : une formule doit avoir une « voix_off » (une formule ne se lit pas telle quelle)")
    if type_ in ("etapes", "correction") and s.get("etapes") is not None:
        extra["etapes"] = _liste_textes(s.get("etapes"), f"{ctx}.etapes", erreurs)
    if type_ == "etapes" and "etapes" not in extra:
        erreurs.append(f"{ctx} : champ « etapes » manquant (liste des lignes qui apparaissent une à une)")
    if type_ == "correction":
        if s.get("reponse") is not None:
            extra["reponse"] = str(s["reponse"])
        elif "etapes" not in extra:
            erreurs.append(f"{ctx} : une correction a une « reponse » ou des « etapes »")
    if type_ == "exercice":
        pause = s.get("pause", 3)
        if not _nombre(pause) or not 0 <= pause <= 20:
            erreurs.append(f"{ctx}.pause : nombre de secondes de réflexion entre 0 et 20")
            pause = 3
        extra["pause"] = float(pause)
        if s.get("etiquette") is not None:
            extra["etiquette"] = str(s["etiquette"])
    if type_ == "animation":
        a = s.get("animation")
        if not isinstance(a, dict) or a.get("modele") not in MODELES_ANIMATION:
            erreurs.append(f"{ctx} : bloc « animation » avec « modele » parmi {', '.join(MODELES_ANIMATION)}")
        else:
            n = a.get("n")
            if not isinstance(n, int) or isinstance(n, bool) or not 2 <= n <= 60:
                erreurs.append(f"{ctx}.animation.n : nombre entier de points entre 2 et 60")
            else:
                extra["animation"] = {"modele": a["modele"], "n": n}
    if s.get("note") is not None:   # petite mention en bas d'écran (hypothèse, précision), non lue
        if not isinstance(s["note"], str) or not s["note"].strip() or len(s["note"]) > 140:
            erreurs.append(f"{ctx}.note : texte court (140 caractères au plus)")
        else:
            extra["note"] = s["note"].strip()
    if type_ == "chiffre":
        for cle in ("valeur", "unite", "prefixe", "suffixe", "decimales"):
            if s.get(cle) is not None:
                extra[cle] = s[cle]
        if "valeur" in extra and not _nombre(extra["valeur"]):
            erreurs.append(f"{ctx}.valeur doit être un nombre fini")
    if type_ == "courbe":
        c = s.get("courbe")
        if not isinstance(c, dict):
            erreurs.append(f"{ctx} : bloc « courbe » manquant (points, ou expression + de + a)")
        else:
            try:
                pts = points_courbe(c)
                extra["courbe"] = dict(c, _points=pts)
            except (CalculInvalide, KeyError, TypeError, ValueError) as exc:
                erreurs.append(f"{ctx}.courbe : {exc}")
    if s.get("verifier") is not None:
        verifs = s["verifier"]
        if not isinstance(verifs, list):
            erreurs.append(f"{ctx}.verifier doit être une liste de {{expression, attendu}}")
        else:
            extra["verifier"] = []
            for j, v in enumerate(verifs):
                if not isinstance(v, dict) or not isinstance(v.get("expression"), str) or not _nombre(v.get("attendu")):
                    erreurs.append(f"{ctx}.verifier[{j}] : « expression » (texte) et « attendu » (nombre) requis")
                    continue
                extra["verifier"].append(v)
    return extra


# --------------------------------------------------------------------------- contrôles qualité
def controler_pedagogie(fiche, r, langues=("fr", "en")) -> None:
    """Contrôles propres aux fiches pédagogiques (s'ajoutent aux contrôles communs)."""
    from .qc import BLOQUANT
    p = fiche.pedagogie
    r.ok.append(f"Fiche pédagogique : famille {fiche.famille}, format {fiche.format}, niveau {p.get('niveau')}")
    objectifs = p.get("objectifs") or {}
    if len(objectifs.get("fr", [])) != len(objectifs.get("en", [])):
        r.avertir("Nombre d'objectifs différent entre FR et EN")
    for l in langues:
        ed = fiche.editions[l]
        types = [s.type for s in ed.scenes]
        # Chaque exercice est suivi d'une correction, ou d'un chiffre révélé dont le calcul est
        # vérifié (bloc « verifier ») : la réponse d'un test peut être un grand chiffre.
        attente = 0
        for s in ed.scenes:
            if s.type == "exercice":
                attente += 1
            elif s.type == "correction" or (s.type == "chiffre" and attente and s.extra.get("verifier")):
                if attente == 0:
                    r.avertir("Correction sans exercice avant elle", l)
                attente = max(0, attente - 1)
        r.verifier(attente == 0, f"[{l}] Chaque exercice a sa correction",
                   f"[{l}] {attente} exercice(s) sans correction", BLOQUANT)
        if fiche.format in FORMATS_SCENES:
            hors = sorted(set(types) - FORMATS_SCENES[fiche.format])
            if hors:
                r.avertir(f"Scènes {', '.join(hors)} inhabituelles pour un format {fiche.format}", l)
        if types and types[0] not in ("accroche", "exercice", "titre"):
            r.avertir("La vidéo ne commence ni par une accroche ni par une question", l)
        if types and types[-1] != "fin":
            r.avertir("La vidéo ne se termine pas par une scène de fin", l)
        for i, s in enumerate(ed.scenes, 1):
            for v in s.extra.get("verifier", []):
                libelle = v.get("libelle") or v["expression"]
                try:
                    calcule = evaluer(v["expression"])
                except CalculInvalide as exc:
                    r.bloquant(f"Scène {i} : calcul impossible « {v['expression']} » ({exc})", l)
                    continue
                tol = float(v.get("tolerance", tolerance_par_defaut(v["attendu"])))
                r.verifier(abs(calcule - v["attendu"]) <= tol,
                           f"[{l}] Scène {i} : {libelle} = {v['attendu']} (recalculé : {calcule:.6g})",
                           f"[{l}] Scène {i} : {libelle} annoncé {v['attendu']}, recalculé {calcule:.6g} "
                           f"(écart > {tol:g})", BLOQUANT)
            if s.type == "formule" and "formule" in s.extra:
                from .formules import formule_valide
                for ligne in s.extra["formule"]:
                    erreur = formule_valide(ligne)
                    if erreur:
                        r.bloquant(f"Scène {i} : formule illisible par le moteur « {ligne[:40]} » ({erreur})", l)
    nb_verifs = sum(len(s.extra.get("verifier", [])) for s in fiche.editions["fr"].scenes)
    if not nb_verifs:
        r.avertir("Aucun résultat numérique n'est recalculé par la machine (bloc « verifier »)")
    r.a_verifier.append("Exactitude pédagogique : définitions, notations et raisonnements relus par une "
                        "personne compétente (la machine ne recalcule que les nombres déclarés)")
    if not fiche.sources:
        r.a_verifier.append("Aucune source : vérifier qu'aucun fait (étude, statistique publiée) n'est cité "
                            "sans référence")


def controler_duree_format(fiche, langue: str, duree: float, r) -> None:
    mini, maxi = DUREES_FORMAT.get(fiche.format, (0, 10_000))
    if not mini <= duree <= maxi:
        r.avertir(f"Durée {duree:.0f} s hors de la plage du format {fiche.format} ({mini}–{maxi} s)", langue)
    else:
        r.ok.append(f"[{langue}] Durée {duree:.0f} s dans la plage du format {fiche.format} ({mini}–{maxi} s)")
