#!/usr/bin/env python3
"""Génère les pages leçons ACTU-BASICS depuis les fiches YAML.

Lit `contenus/fiches/2026-11-n1-*.yaml` au statut `valide` et produit :
  - `docs/lecons/<CODE>/index.html`    (version FR)
  - `docs/en/lessons/<CODE>/index.html` (version EN)
  - `docs/bibliotheque/index.html`     (liste FR)
  - `docs/en/library/index.html`       (liste EN)

Rien à installer : stdlib + PyYAML.

Préserve la leçon manuelle A0.01 (celle qui n'a pas de YAML).
"""
from __future__ import annotations
import html
import re
import sys
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:
    sys.exit("PyYAML requis. pip install pyyaml")


ROOT = Path(__file__).resolve().parent.parent
FICHES = ROOT / "contenus" / "fiches"
DOCS = ROOT / "docs"

CATEGORY_LABELS_FR = {
    "fondations":    "Fondations",
    "statistiques":  "Statistiques",
    "probabilites":  "Probabilités",
    "actuariat":     "Actuariat",
    "finance":       "Mathématiques financières",
    "autre":         "Autres",
}
CATEGORY_LABELS_EN = {
    "fondations":    "Foundations",
    "statistiques":  "Statistics",
    "probabilites":  "Probability",
    "actuariat":     "Actuarial science",
    "finance":       "Financial mathematics",
    "autre":         "Other",
}

# Libellés des modules connus. Un module inconnu (ex: S5, A1, MF1…) reçoit
# un libellé générique dérivé de son code (voir module_meta()).
MODULE_META_FR_KNOWN: dict[str, dict] = {
    "M0": {"titre": "Fondations", "sous_titre": "Rappels mathématiques pour démarrer en confiance.", "category": "fondations"},
    "S1": {"titre": "Statistiques · lire un chiffre", "sous_titre": "Vocabulaire, pourcentages, lecture des chiffres du quotidien.", "category": "statistiques"},
    "S2": {"titre": "Statistiques · indicateurs", "sous_titre": "Moyennes, médianes, taux et comparaisons entre groupes.", "category": "statistiques"},
    "S3": {"titre": "Statistiques · séries et dispersion", "sous_titre": "Écart-type, séries chronologiques et interprétation des graphiques.", "category": "statistiques"},
    "S4": {"titre": "Probabilités", "sous_titre": "Événements, indépendance, probabilités conditionnelles.", "category": "probabilites"},
    "A0": {"titre": "Actuariat · premiers pas", "sous_titre": "Métier d'actuaire, risque, prime pure.", "category": "actuariat"},
}

MODULE_META_EN_KNOWN: dict[str, dict] = {
    "M0": {"titre": "Foundations", "sous_titre": "A math refresher to start with confidence.", "category": "fondations"},
    "S1": {"titre": "Statistics · reading numbers", "sous_titre": "Vocabulary, percentages, making sense of everyday numbers.", "category": "statistiques"},
    "S2": {"titre": "Statistics · indicators", "sous_titre": "Averages, medians, rates and group comparisons.", "category": "statistiques"},
    "S3": {"titre": "Statistics · series and spread", "sous_titre": "Standard deviation, time series and chart interpretation.", "category": "statistiques"},
    "S4": {"titre": "Probability", "sous_titre": "Events, independence, conditional probability.", "category": "probabilites"},
    "A0": {"titre": "Actuarial science · first steps", "sous_titre": "The actuary's role, risk, pure premium.", "category": "actuariat"},
}


def _letters_and_number(prefix: str) -> tuple[str, int]:
    """'S4' -> ('S', 4) ; 'MF12' -> ('MF', 12) ; 'A0' -> ('A', 0) ; 'M0' -> ('M', 0)."""
    m = re.match(r"^([A-Za-z]+)(\d+)$", prefix)
    if m:
        return m.group(1).upper(), int(m.group(2))
    return (prefix.upper(), 0)


def module_sort_key(prefix: str) -> tuple:
    """Ordre déterministe pour les modules : M*, S*, A*, MF*, F*, puis alpha.
    Le module M0 vient en premier, puis les S croissants, puis A croissants,
    puis MF croissants, puis tout le reste par alphabet.
    """
    letters, num = _letters_and_number(prefix)
    bucket = {
        "M":  0,   # fondations
        "S":  1,   # statistiques / probas
        "A":  2,   # actuariat
        "MF": 3,   # finance (si utilisé)
        "F":  4,
    }.get(letters, 99)
    return (bucket, letters, num, prefix)


def module_of(code: str) -> str:
    """S4-07 -> S4 ; A0-01 -> A0 ; MF2-03 -> MF2 ; M0-01 -> M0.
    Accepte n'importe quel préfixe lettres+chiffres suivi d'un tiret.
    """
    m = re.match(r"^([A-Za-z]+\d+)[-_]", code)
    if m:
        return m.group(1).upper()
    return code.upper()


# Taxonomie des piliers : lettre(s) de préfixe -> catégorie.
# Un préfixe non listé renvoie "autre" plutôt qu'une catégorie par défaut :
# on refuse de classer silencieusement un module inconnu dans « statistiques ».
PILLAR_BY_LETTERS: dict[str, str] = {
    "M":  "fondations",
    # S : voir category_for (S1-S3 = statistiques, S4+ = probabilités).
    "A":  "actuariat",
    "MF": "finance",
    "F":  "finance",
}


def category_for(code: str) -> str:
    letters, num = _letters_and_number(module_of(code))
    if letters == "S":
        # Convention explicite : S1-S3 = statistiques, S4+ = probabilités.
        return "statistiques" if num <= 3 else "probabilites"
    return PILLAR_BY_LETTERS.get(letters, "autre")


def module_meta(mod: str, lang: str) -> dict:
    """Retourne {titre, sous_titre, category} pour un module, connu ou pas."""
    known = (MODULE_META_FR_KNOWN if lang == "fr" else MODULE_META_EN_KNOWN).get(mod)
    if known:
        return known
    # Fallback générique pour un module inconnu : on affiche au moins proprement.
    letters, num = _letters_and_number(mod)
    cat = category_for(f"{mod}-00")
    if lang == "fr":
        gen_title = {
            "M": f"Fondations · M{num}",
            "S": f"Statistiques · S{num}" if num <= 3 else f"Probabilités · S{num}",
            "A": f"Actuariat · A{num}",
            "MF": f"Mathématiques financières · MF{num}",
            "F": f"Finance · F{num}",
        }.get(letters, mod)
    else:
        gen_title = {
            "M": f"Foundations · M{num}",
            "S": f"Statistics · S{num}" if num <= 3 else f"Probability · S{num}",
            "A": f"Actuarial science · A{num}",
            "MF": f"Financial mathematics · MF{num}",
            "F": f"Finance · F{num}",
        }.get(letters, mod)
    return {"titre": gen_title, "sous_titre": "", "category": cat}


def module_order_from(lessons: list[dict], extra: list[str] | None = None) -> list[str]:
    """Liste ordonnée des modules à partir des leçons chargées, plus d'éventuels
    modules référencés par un parcours mais pas encore pourvus de leçons."""
    mods = {L["module"] for L in lessons}
    if extra:
        mods.update(x for x in extra if x)
    return sorted(mods, key=module_sort_key)


def module_code(fiche_id: str) -> str:
    """Extrait le code module d'un id fiche.

    Reconnaît les schémas courants :
    - `2026-11-n1-s2-04-xxx`         -> `S2-04`
    - `2026-11-act-a3-01-xxx`        -> `A3-01`
    - `YYYY-MM-<slot>-<code>-<slug>` -> `<CODE>`
    - À défaut, scanne la chaîne pour un `<lettres><chiffres>-<chiffres>`.
    """
    # Forme explicite : AAAA-MM-<slot>-<lettres><chiffres>-<chiffres>-<slug>
    m = re.match(r"^\d{4}-\d{2}-[a-z0-9]+-([a-z]+\d+)-(\d+)-", fiche_id.lower())
    if m:
        return f"{m.group(1).upper()}-{m.group(2)}"
    # Forme libre : premier motif <lettres+chiffres>-<chiffres> trouvé dans l'id.
    m = re.search(r"([a-z]+\d+)-(\d+)", fiche_id.lower())
    if m:
        return f"{m.group(1).upper()}-{m.group(2)}"
    return fiche_id.upper()


# --- Rendu Markdown léger -> HTML ------------------------------------------

def pick_lang(v, lang: str, default: str = "") -> str:
    """Résout une valeur per-langue en chaîne.

    - `{fr: "a", en: "b"}`      -> "a" ou "b" selon lang.
    - "foo"                      -> "foo"
    - None / autre               -> default.
    Évite le rendu brut d'un dict dans un f-string (bug observé sur `suffixe`).
    """
    if v is None:
        return default
    if isinstance(v, dict):
        got = v.get(lang)
        if got is None:
            # Repli : autre langue si dispo, sinon default.
            other = "en" if lang == "fr" else "fr"
            got = v.get(other)
        return "" if got is None else str(got)
    return str(v)


def md_inline(text, lang: str = "fr") -> str:
    """Rend l'emphase *...* en <em>, échappe le reste.

    Accepte aussi un dict per-langue : {fr: "...", en: "..."}.
    """
    if isinstance(text, dict):
        text = pick_lang(text, lang)
    if not text:
        return ""
    text = html.escape(str(text))
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def md_items(items) -> str:
    if not items:
        return ""
    lis = "".join(f"<li>{md_inline(i)}</li>" for i in items)
    return f"<ul>{lis}</ul>"


# --- Rendu d'un graphique (SVG inline) --------------------------------------
#
# Chaque scène `type: courbe` porte un bloc `courbe:` dont `style` vaut
# `points`, `ligne`, `barres`, `histogramme` ou `boites` (ou rien quand il
# s'agit d'une courbe définie par une `expression` continue). Le rendu produit
# un <svg> accessible avec `role="img"` et un `aria-label` issu du titre.
# Les couleurs sont tirées de variables CSS du site (via currentColor et
# classes), de sorte que le thème clair/sombre est respecté sans JS.

COURBE_W = 640
COURBE_H = 320
COURBE_PAD_L = 56
COURBE_PAD_R = 24
COURBE_PAD_T = 24
COURBE_PAD_B = 48


def _fmt_num(v) -> str:
    """Format court pour les étiquettes d'axe."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if abs(f - round(f)) < 1e-9 and abs(f) < 1e6:
        return str(int(round(f)))
    # 2 décimales max, trim
    s = f"{f:.2f}".rstrip("0").rstrip(".")
    return s or "0"


def _safe_eval_expr(expr: str, x: float) -> float | None:
    """Évalue une expression YAML simple en ne laissant passer que
    l'arithmétique de base et quelques fonctions math. Retourne None sur erreur.
    """
    import math
    allowed = {
        "abs": abs, "min": min, "max": max, "round": round,
        "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "pi": math.pi, "e": math.e,
    }
    # Extraction de la variable : la plupart des expressions utilisent `t`
    # ou `x` ou `n`. On expose x sous ces trois noms.
    env = {"__builtins__": {}, "t": x, "x": x, "n": x, **allowed}
    try:
        # Interdire tout caractère suspect
        if re.search(r"[;@]|__", str(expr)):
            return None
        return float(eval(str(expr), env, {}))  # noqa: S307
    except Exception:
        return None


def _nice_step(span: float, n: int) -> float:
    """Choisit un pas « lisible » proche de span/n (parmi 1, 2, 2.5, 5 × 10^k)."""
    import math
    if span <= 0:
        return 1.0
    raw = span / max(1, n)
    mag = 10 ** math.floor(math.log10(raw))
    for mult in (1, 2, 2.5, 5, 10):
        if mult * mag >= raw:
            return mult * mag
    return 10 * mag


def _axis_labels(v_min: float, v_max: float, n: int = 5) -> list[float]:
    if v_max <= v_min:
        return [v_min]
    step = _nice_step(v_max - v_min, n)
    import math
    start = math.floor(v_min / step) * step
    out: list[float] = []
    t = start
    # Bornes incluant v_max avec tolérance
    while t <= v_max + step * 1e-6:
        if t >= v_min - step * 1e-6:
            out.append(round(t, 10))
        t += step
    return out or [v_min, v_max]


def render_courbe_svg(courbe: dict, lang: str, aria_label: str = "") -> str:
    """Rend un graphique SVG à partir d'un bloc `courbe:` YAML.

    Styles pris en charge :
      - `points` : nuage de points
      - `ligne`  : polyligne entre les points (par défaut sans `style` + `points`)
      - `barres` : barres discrètes, avec `etiquettes` et éventuellement
                    `valeurs: true` / `etiquettes_valeurs` / `mis_en_avant`
      - `histogramme` : barres contiguës, largeur `largeur_classe`
      - `boites` : boîtes à moustaches (`boites: [{etiquette, valeurs:[min,q1,med,q3,max]}]`)
      - (sans style, avec `expression`) : courbe continue évaluée sur [de,a]

    Options communes : `axe_x`, `axe_y`, `x_min`, `x_max`, `y_min`, `y_max`,
    `reperes` (annotations), `serie_2` (points), `seuil`/`seuils` (ligne(s) y).
    """
    if not isinstance(courbe, dict):
        return ""

    style = (courbe.get("style") or "").strip().lower()
    axe_x = pick_lang(courbe.get("axe_x"), lang) or ""
    axe_y = pick_lang(courbe.get("axe_y"), lang) or ""

    W, H = COURBE_W, COURBE_H
    pl, pr, pt, pb = COURBE_PAD_L, COURBE_PAD_R, COURBE_PAD_T, COURBE_PAD_B
    inner_h = H - pt - pb

    # Expression continue (style par défaut si `expression` présent)
    if courbe.get("expression") and not style:
        style = "ligne"
        var_from = float(courbe.get("de", 0))
        var_to = float(courbe.get("a", 10))
        expr = courbe["expression"]
        n_samples = 80
        pts: list[list[float]] = []
        for i in range(n_samples + 1):
            x = var_from + (var_to - var_from) * i / n_samples
            y = _safe_eval_expr(expr, x)
            if y is not None:
                pts.append([x, y])
    else:
        pts = []
        for p in (courbe.get("points") or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                try:
                    pts.append([float(p[0]), float(p[1])])
                except (TypeError, ValueError):
                    pass

    # serie_2 accepte soit une liste de points (même échelle Y), soit un
    # objet {points, y_min, y_max, axe_y} pour une véritable double échelle.
    serie_2_cfg = courbe.get("serie_2") or []
    serie_2_secondary_axis = isinstance(serie_2_cfg, dict)
    serie_2_source = serie_2_cfg.get("points", []) if serie_2_secondary_axis else serie_2_cfg
    serie_2 = []
    for p in (serie_2_source or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                serie_2.append([float(p[0]), float(p[1])])
            except (TypeError, ValueError):
                pass
    if serie_2_secondary_axis and serie_2:
        pr = 64  # réserve les graduations et le titre de l'axe droit
    inner_w = W - pl - pr

    # Domaines -------------------------------------------------------------
    def _bounds(key_min, key_max, values, pad_lo=False, pad_hi=False):
        v_min = courbe.get(key_min)
        v_max = courbe.get(key_max)
        if v_min is None or v_max is None:
            if values:
                dmin = min(values)
                dmax = max(values)
            else:
                dmin, dmax = 0.0, 1.0
            if dmin == dmax:
                dmin -= 1.0
                dmax += 1.0
            if v_min is None:
                v_min = dmin - (0.05 * (dmax - dmin) if pad_lo else 0)
            if v_max is None:
                v_max = dmax + (0.05 * (dmax - dmin) if pad_hi else 0)
        return float(v_min), float(v_max)

    # Calcul des bornes selon style
    if style == "boites":
        boites = courbe.get("boites") or []
        all_y: list[float] = []
        for b in boites:
            vs = b.get("valeurs") if isinstance(b, dict) else None
            if isinstance(vs, list):
                for v in vs:
                    try:
                        all_y.append(float(v))
                    except (TypeError, ValueError):
                        pass
        y_min, y_max = _bounds("y_min", "y_max", all_y, pad_lo=True, pad_hi=True)
        x_min, x_max = 0.0, float(max(1, len(boites)))
    elif style in ("barres", "histogramme"):
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if style == "histogramme":
            lw = float(courbe.get("largeur_classe", 1))
            x_min, x_max = _bounds("x_min", "x_max", xs + [max(xs) + lw if xs else 1])
        else:
            x_min = (min(xs) - 0.5) if xs else 0
            x_max = (max(xs) + 0.5) if xs else 1
        y_min, y_max = _bounds("y_min", "y_max", ys + [0], pad_hi=True)
        if y_min > 0:
            y_min = 0  # les barres partent de 0
    else:
        xs = [p[0] for p in pts] + [p[0] for p in serie_2]
        ys = [p[1] for p in pts] + ([] if serie_2_secondary_axis else [p[1] for p in serie_2])
        x_min, x_max = _bounds("x_min", "x_max", xs, pad_lo=False, pad_hi=True)
        # Pour points/ligne : si toutes les valeurs y >= 0, on ancre l'axe en 0.
        # Cela évite des graduations décimales étranges (1.4, 4.32…) et
        # correspond à l'intuition pédagogique habituelle.
        if ys and all(v >= 0 for v in ys) and courbe.get("y_min") is None:
            y_min = 0.0
            if courbe.get("y_max") is not None:
                y_max = float(courbe["y_max"])
            else:
                y_max = max(ys) * 1.1 if max(ys) > 0 else 1.0
        else:
            y_min, y_max = _bounds("y_min", "y_max", ys, pad_lo=True, pad_hi=True)

    if x_max == x_min:
        x_max = x_min + 1
    if y_max == y_min:
        y_max = y_min + 1

    # La seconde série peut avoir sa propre échelle verticale. On conserve
    # une échelle commune uniquement pour l'ancien format liste.
    secondary_y_min = secondary_y_max = None
    axe_y_2 = ""
    if serie_2_secondary_axis and serie_2:
        secondary_values = [p[1] for p in serie_2]
        secondary_y_min = float(serie_2_cfg.get("y_min", min(secondary_values)))
        secondary_y_max = float(serie_2_cfg.get("y_max", max(secondary_values)))
        if secondary_y_max == secondary_y_min:
            secondary_y_max = secondary_y_min + 1
        axe_y_2 = pick_lang(serie_2_cfg.get("axe_y"), lang) or ""

    def sx(x: float) -> float:
        return pl + (x - x_min) / (x_max - x_min) * inner_w

    def sy(y: float) -> float:
        return pt + inner_h - (y - y_min) / (y_max - y_min) * inner_h

    def sy2(y: float) -> float:
        if secondary_y_min is None or secondary_y_max is None:
            return sy(y)
        return pt + inner_h - (y - secondary_y_min) / (secondary_y_max - secondary_y_min) * inner_h

    # ---------------------------------------------------------------- SVG
    parts: list[str] = []
    label_attr = html.escape(aria_label) if aria_label else (
        "Graphique" if lang == "fr" else "Chart"
    )
    parts.append(
        f'<figure class="courbe-figure">'
        f'<svg class="courbe-svg{" courbe-svg-dual" if secondary_y_min is not None else ""}" viewBox="0 0 {W} {H}" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-label="{label_attr}">'
    )

    # Grille et graduations Y
    y_ticks = _axis_labels(y_min, y_max, 5)
    for t in y_ticks:
        y = sy(t)
        parts.append(
            f'<line x1="{pl}" y1="{y:.1f}" x2="{W - pr}" y2="{y:.1f}" '
            f'class="courbe-grid" />'
        )
        parts.append(
            f'<text x="{pl - 6}" y="{y + 4:.1f}" class="courbe-tick" '
            f'text-anchor="end">{_fmt_num(t)}</text>'
        )

    # Graduations de droite : elles appartiennent à la seconde série.
    if secondary_y_min is not None and secondary_y_max is not None:
        for t in _axis_labels(secondary_y_min, secondary_y_max, 5):
            y = sy2(t)
            parts.append(
                f'<line x1="{W - pr}" y1="{y:.1f}" x2="{W - pr + 5}" y2="{y:.1f}" class="courbe-axis" />'
                f'<text x="{W - pr + 8}" y="{y + 4:.1f}" class="courbe-tick" text-anchor="start">{_fmt_num(t)}</text>'
            )

    # Axes
    parts.append(
        f'<line x1="{pl}" y1="{pt}" x2="{pl}" y2="{H - pb}" class="courbe-axis" />'
        f'<line x1="{pl}" y1="{H - pb}" x2="{W - pr}" y2="{H - pb}" class="courbe-axis" />'
        + (f'<line x1="{W - pr}" y1="{pt}" x2="{W - pr}" y2="{H - pb}" class="courbe-axis courbe-axis-right" />'
           if secondary_y_min is not None else "")
    )

    # Graduations X : pour barres/boites on utilise les étiquettes ; sinon 5 ticks
    if style in ("barres", "boites"):
        etiquettes = []
        if style == "boites":
            boites = courbe.get("boites") or []
            etiquettes = [pick_lang(b.get("etiquette"), lang) if isinstance(b, dict) else "" for b in boites]
            n = max(1, len(boites))
            for i, lbl in enumerate(etiquettes):
                xc = sx(i + 0.5)
                parts.append(
                    f'<text x="{xc:.1f}" y="{H - pb + 18}" class="courbe-tick" '
                    f'text-anchor="middle">{html.escape(str(lbl or ""))}</text>'
                )
        else:
            etiquettes_src = courbe.get("etiquettes") or []
            etiquettes = [pick_lang(e, lang) if isinstance(e, dict) else e for e in etiquettes_src]
            for i, p in enumerate(pts):
                if i < len(etiquettes):
                    xc = sx(p[0])
                    parts.append(
                        f'<text x="{xc:.1f}" y="{H - pb + 18}" class="courbe-tick" '
                        f'text-anchor="middle">{html.escape(str(etiquettes[i] or ""))}</text>'
                    )
    else:
        x_ticks = _axis_labels(x_min, x_max, 5)
        for t in x_ticks:
            xc = sx(t)
            parts.append(
                f'<text x="{xc:.1f}" y="{H - pb + 18}" class="courbe-tick" '
                f'text-anchor="middle">{_fmt_num(t)}</text>'
            )

    # Seuils horizontaux
    seuils = courbe.get("seuils") or ([courbe["seuil"]] if courbe.get("seuil") is not None else [])
    for s_val in seuils:
        try:
            yv = float(s_val)
        except (TypeError, ValueError):
            continue
        y = sy(yv)
        parts.append(
            f'<line x1="{pl}" y1="{y:.1f}" x2="{W - pr}" y2="{y:.1f}" '
            f'class="courbe-seuil" />'
        )

    # --- Dessin principal selon style ------------------------------------
    if style == "boites":
        boites = courbe.get("boites") or []
        for i, b in enumerate(boites):
            if not isinstance(b, dict):
                continue
            vs = b.get("valeurs") or []
            if len(vs) < 5:
                continue
            try:
                vmin, q1, med, q3, vmax = [float(v) for v in vs[:5]]
            except (TypeError, ValueError):
                continue
            xc = sx(i + 0.5)
            box_w = inner_w / max(1, len(boites)) * 0.45
            x_left = xc - box_w / 2
            x_right = xc + box_w / 2
            y_q1 = sy(q1)
            y_q3 = sy(q3)
            y_med = sy(med)
            y_min_v = sy(vmin)
            y_max_v = sy(vmax)
            # moustaches
            parts.append(
                f'<line x1="{xc:.1f}" y1="{y_min_v:.1f}" x2="{xc:.1f}" y2="{y_max_v:.1f}" class="courbe-whisker" />'
                f'<line x1="{x_left:.1f}" y1="{y_min_v:.1f}" x2="{x_right:.1f}" y2="{y_min_v:.1f}" class="courbe-whisker" />'
                f'<line x1="{x_left:.1f}" y1="{y_max_v:.1f}" x2="{x_right:.1f}" y2="{y_max_v:.1f}" class="courbe-whisker" />'
            )
            # boîte
            parts.append(
                f'<rect x="{x_left:.1f}" y="{min(y_q1, y_q3):.1f}" '
                f'width="{box_w:.1f}" height="{abs(y_q1 - y_q3):.1f}" class="courbe-box" />'
            )
            # médiane
            parts.append(
                f'<line x1="{x_left:.1f}" y1="{y_med:.1f}" x2="{x_right:.1f}" y2="{y_med:.1f}" class="courbe-median" />'
            )
            if courbe.get("valeurs"):
                for yv, lbl in ((vmin, _fmt_num(vmin)), (q1, _fmt_num(q1)),
                                (med, _fmt_num(med)), (q3, _fmt_num(q3)),
                                (vmax, _fmt_num(vmax))):
                    parts.append(
                        f'<text x="{x_right + 4:.1f}" y="{sy(yv) + 4:.1f}" '
                        f'class="courbe-value" text-anchor="start">{lbl}</text>'
                    )

    elif style in ("barres", "histogramme"):
        mis = set(courbe.get("mis_en_avant") or [])
        etiquettes_valeurs = courbe.get("etiquettes_valeurs") or []
        show_values = bool(courbe.get("valeurs"))
        y0 = sy(0)
        if style == "histogramme":
            lw = float(courbe.get("largeur_classe", 1))
            for i, p in enumerate(pts):
                x0 = sx(p[0])
                x1 = sx(p[0] + lw)
                y = sy(p[1])
                cls = "courbe-bar courbe-bar-highlight" if i in mis else "courbe-bar"
                parts.append(
                    f'<rect x="{x0:.1f}" y="{min(y, y0):.1f}" '
                    f'width="{max(1, x1 - x0 - 1):.1f}" height="{abs(y0 - y):.1f}" class="{cls}" />'
                )
                if show_values:
                    parts.append(
                        f'<text x="{(x0 + x1) / 2:.1f}" y="{y - 6:.1f}" '
                        f'class="courbe-value" text-anchor="middle">{_fmt_num(p[1])}</text>'
                    )
        else:
            n = len(pts)
            if n > 0:
                slot = inner_w / n
                bw = slot * 0.6
                for i, p in enumerate(pts):
                    xc = pl + (i + 0.5) * slot
                    y = sy(p[1])
                    cls = "courbe-bar courbe-bar-highlight" if i in mis else "courbe-bar"
                    parts.append(
                        f'<rect x="{xc - bw / 2:.1f}" y="{min(y, y0):.1f}" '
                        f'width="{bw:.1f}" height="{abs(y0 - y):.1f}" class="{cls}" />'
                    )
                    lbl = None
                    if i < len(etiquettes_valeurs):
                        lbl = pick_lang(etiquettes_valeurs[i], lang) if isinstance(etiquettes_valeurs[i], dict) else etiquettes_valeurs[i]
                    elif show_values:
                        lbl = _fmt_num(p[1])
                    if lbl:
                        parts.append(
                            f'<text x="{xc:.1f}" y="{y - 6:.1f}" '
                            f'class="courbe-value" text-anchor="middle">{html.escape(str(lbl))}</text>'
                        )

    elif style == "ligne" or (style == "" and pts):
        if pts:
            d = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in pts)
            parts.append(f'<polyline points="{d}" class="courbe-line" />')
        if serie_2:
            d2 = " ".join(f"{sx(x):.1f},{sy2(y):.1f}" for x, y in serie_2)
            parts.append(f'<polyline points="{d2}" class="courbe-line courbe-line-alt" />')

    else:  # points (défaut)
        for x, y in pts:
            parts.append(
                f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4" class="courbe-point" />'
            )
        for x, y in serie_2:
            parts.append(
                f'<circle cx="{sx(x):.1f}" cy="{sy2(y):.1f}" r="4" class="courbe-point courbe-point-alt" />'
            )

    # Repères (annotations) -----------------------------------------------
    for r in (courbe.get("reperes") or []):
        if not isinstance(r, dict):
            continue
        try:
            rx = float(r["x"]) if "x" in r else None
        except (TypeError, ValueError):
            rx = None
        try:
            ry = float(r["y"]) if "y" in r else None
        except (TypeError, ValueError):
            ry = None
        label = pick_lang(r.get("label"), lang) or ""
        if rx is None:
            continue
        # Si y absent mais expression connue, évaluer
        if ry is None and courbe.get("expression"):
            ry = _safe_eval_expr(courbe["expression"], rx)
        # Pour un point explicite [x,y] on cherche le y le plus proche
        if ry is None and pts:
            same = [p for p in pts if abs(p[0] - rx) < 1e-6]
            if same:
                ry = same[0][1]
        if ry is None:
            continue
        cx = sx(rx)
        cy = sy(ry)
        if r.get("guide_y"):
            parts.append(
                f'<line x1="{cx:.1f}" y1="{H - pb}" x2="{cx:.1f}" y2="{cy:.1f}" class="courbe-guide" />'
                f'<line x1="{pl}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" class="courbe-guide" />'
            )
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" class="courbe-repere" />'
        )
        if label:
            parts.append(
                f'<text x="{cx + 8:.1f}" y="{cy - 6:.1f}" class="courbe-label">{html.escape(str(label))}</text>'
            )

    # Titres d'axes --------------------------------------------------------
    if axe_x:
        parts.append(
            f'<text x="{pl + inner_w / 2:.1f}" y="{H - 6}" '
            f'class="courbe-axis-title" text-anchor="middle">{html.escape(str(axe_x))}</text>'
        )
    if axe_y:
        parts.append(
            f'<text x="{14}" y="{pt + inner_h / 2:.1f}" '
            f'class="courbe-axis-title" text-anchor="middle" '
            f'transform="rotate(-90 14 {pt + inner_h / 2:.1f})">{html.escape(str(axe_y))}</text>'
        )

    if axe_y_2:
        parts.append(
            f'<text x="{W - 8}" y="{pt + inner_h / 2:.1f}" class="courbe-axis-title courbe-axis-title-right" '
            f'text-anchor="middle" transform="rotate(90 {W - 8} {pt + inner_h / 2:.1f})">{html.escape(str(axe_y_2))}</text>'
        )

    parts.append("</svg></figure>")
    return "".join(parts)


# --- Rendu d'une scène ------------------------------------------------------

def render_surface_svg(lang: str) -> str:
    """Illustre la différence entre une valeur et la surface d'un dessin."""
    labels = (
        ("Valeur ×1", "Aire ×1", "Valeur ×2", "Aire ×4", "Valeur ×2", "Aire ×2")
        if lang == "fr" else
        ("Value ×1", "Area ×1", "Value ×2", "Area ×4", "Value ×2", "Area ×2")
    )
    aria = (
        "Comparer une surface : doubler les côtés multiplie l'aire par quatre"
        if lang == "fr" else
        "Comparing area: doubling both sides multiplies area by four"
    )
    parts = [
        '<figure class="surface-figure">',
        f'<svg class="surface-svg" viewBox="0 0 720 270" role="img" xmlns="http://www.w3.org/2000/svg" aria-label="{html.escape(aria)}">',
        '<line x1="240" y1="24" x2="240" y2="238" class="surface-divider" />',
        '<line x1="480" y1="24" x2="480" y2="238" class="surface-divider" />',
        '<rect x="76" y="58" width="64" height="64" rx="5" class="surface-cell" />',
        '<rect x="308" y="26" width="128" height="128" rx="5" class="surface-cell surface-cell-warn" />',
        '<path d="M372 26V154 M308 90H436" class="surface-grid" />',
        '<rect x="548" y="58" width="128" height="64" rx="5" class="surface-cell surface-cell-good" />',
        '<path d="M612 58V122" class="surface-grid" />',
        f'<text x="108" y="184" class="surface-label" text-anchor="middle">{html.escape(labels[0])}</text>',
        f'<text x="108" y="207" class="surface-value" text-anchor="middle">{html.escape(labels[1])}</text>',
        f'<text x="372" y="184" class="surface-label" text-anchor="middle">{html.escape(labels[2])}</text>',
        f'<text x="372" y="207" class="surface-value surface-value-warn" text-anchor="middle">{html.escape(labels[3])}</text>',
        f'<text x="612" y="184" class="surface-label" text-anchor="middle">{html.escape(labels[4])}</text>',
        f'<text x="612" y="207" class="surface-value surface-value-good" text-anchor="middle">{html.escape(labels[5])}</text>',
        '</svg>',
        '</figure>',
    ]
    return "".join(parts)


def render_scene(s: dict, lang: str) -> str:
    """Convertit une scène YAML en un fragment HTML."""
    if not isinstance(s, dict):
        return ""
    t = s.get("type", "")
    parts: list[str] = []

    # Résolution systématique des champs qui peuvent être soit un scalaire,
    # soit un dict {fr/en}. Sans ce passage, un dict est rendu tel quel par
    # f-string (bug observé : `24{'fr': ' %', 'en': '%'}` dans S1-05).
    texte = pick_lang(s.get("texte"), lang)
    voix = pick_lang(s.get("voix_off"), lang)
    etapes = s.get("etapes") or []
    if isinstance(etapes, dict):
        etapes = etapes.get(lang) or etapes.get("en" if lang == "fr" else "fr") or []
    formule = s.get("formule")
    etiquette = pick_lang(s.get("etiquette"), lang)
    reponse = pick_lang(s.get("reponse"), lang)
    note = pick_lang(s.get("note"), lang)
    prefixe = pick_lang(s.get("prefixe"), lang)
    suffixe = pick_lang(s.get("suffixe"), lang)
    valeur = pick_lang(s.get("valeur"), lang)

    if t == "accroche":
        if texte:
            parts.append(f'<p class="lesson-opener">{md_inline(texte)}</p>')
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        return "".join(parts)

    if t == "titre":
        head_text = texte or voix or ""
        parts.append(f"<h2>{md_inline(head_text)}</h2>")
        if texte and voix and voix != texte:
            parts.append(f"<p>{md_inline(voix)}</p>")
        return "".join(parts)

    if t == "etapes":
        if texte:
            parts.append(f"<h3>{md_inline(texte)}</h3>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        parts.append(md_items(etapes))
        if note:
            parts.append(f'<p class="muted"><small>{md_inline(note)}</small></p>')
        return "".join(parts)

    if t == "texte":
        if texte:
            parts.append(f"<h3>{md_inline(texte)}</h3>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        return "".join(parts)

    if t == "formule":
        if texte:
            parts.append(f"<h3>{md_inline(texte)}</h3>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        if formule:
            raw = formule[0] if isinstance(formule, list) else formule
            # LaTeX display math : rendu client-side par KaTeX (CDN, voir head/footer).
            # Fallback sans JS : la source LaTeX reste visible dans un <code>.
            latex = str(raw)
            parts.append(
                f'<div class="formula katex-block">'
                f'<span class="katex-src">\\[{html.escape(latex)}\\]</span>'
                f'<noscript><code>{html.escape(latex)}</code></noscript>'
                f'</div>'
            )
        return "".join(parts)

    if t == "courbe":
        if texte:
            parts.append(f"<h3>{md_inline(texte)}</h3>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        courbe = s.get("courbe") or {}
        if courbe:
            parts.append(render_courbe_svg(courbe, lang, aria_label=texte or voix or ""))
        else:
            placeholder = "Graphique associé à cette étape" if lang == "fr" else "Chart for this step"
            parts.append(f'<p class="muted"><em>[{placeholder}]</em></p>')
        if note:
            parts.append(f'<p class="muted"><small>{md_inline(note)}</small></p>')
        return "".join(parts)

    if t == "chiffre":
        if texte:
            parts.append(f"<h3>{md_inline(texte)}</h3>")
        display = f"{prefixe}{valeur}{suffixe}".strip()
        if display:
            parts.append(f'<div class="formula"><strong>{md_inline(display)}</strong></div>')
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        return "".join(parts)

    if t == "exercice":
        heading_src = etiquette or ("Exercice" if lang == "fr" else "Exercise")
        parts.append(f'<div class="notice"><h3>{md_inline(heading_src)}</h3>')
        if texte:
            parts.append(f"<p><strong>{md_inline(texte)}</strong></p>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        parts.append("</div>")
        return "".join(parts)

    if t == "correction":
        heading = "Correction" if lang == "fr" else "Solution"
        parts.append(f"<h3>{heading}</h3>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        parts.append(md_items(etapes))
        if reponse:
            label = "Réponse" if lang == "fr" else "Answer"
            parts.append(f'<div class="notice"><strong>{label} :</strong> {md_inline(reponse)}</div>')
        return "".join(parts)

    if t == "fin":
        if texte:
            parts.append(f'<p class="lesson-closer"><strong>{md_inline(texte)}</strong></p>')
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        return "".join(parts)

    if t == "animation":
        if texte:
            parts.append(f"<h3>{md_inline(texte)}</h3>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
        animation = s.get("animation") or {}
        if isinstance(animation, dict) and animation.get("modele") == "surface":
            parts.append(render_surface_svg(lang))
        parts.append(md_items(etapes))
        return "".join(parts)

    # fallback
    if texte:
        parts.append(f"<p><strong>{md_inline(texte)}</strong></p>")
    if voix:
        parts.append(f"<p>{md_inline(voix)}</p>")
    return "".join(parts)


# --- Templates HTML --------------------------------------------------------

# Google Fonts : Source Serif 4 (serif éditoriale sobre, classique) + Inter.
# Variable fonts chargées en WOFF2 par Google. `display=swap` évite le FOIT.
# Source Serif 4 est une serif de référence utilisée par Adobe et beaucoup
# de publications : élégante sans être « fantaisiste ».
FRAUNCES_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Source+Serif+4:ital,opsz,wght@0,8..60,300..700;1,8..60,300..700"
    "&family=Inter:wght@400;500;600;700;850&display=swap"
)


def _premium_head_assets(base: str) -> str:
    """Les feuilles et polices premium à charger dans chaque <head>.

    Les tokens sont chargés AVANT main.css pour que les variables soient
    définies quand les règles historiques s'appliquent. `premium.css`
    est chargé APRÈS pour pouvoir surcharger. `theme-init.js` est un
    petit script bloquant qui pose `data-theme` sur <html> avant la
    première peinture, ce qui évite un flash clair en mode sombre.
    """
    return (
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link rel="stylesheet" href="{FRAUNCES_URL}">'
        f'<link rel="stylesheet" href="{base}assets/css/tokens.css">'
        f'<link rel="stylesheet" href="{base}assets/css/main.css">'
        f'<link rel="stylesheet" href="{base}assets/css/premium.css">'
        f'<link rel="stylesheet" href="{base}assets/css/print.css" media="print">'
        f'<script>'
        f'(function(){{try{{var t=localStorage.getItem("ab-theme");'
        f'if(t==="dark"||t==="light"){{'
        f'document.documentElement.setAttribute("data-theme",t);'
        f'}}}}catch(e){{}}}})();'
        f'</script>'
    )


KATEX_VERSION = "0.16.11"
KATEX_CSS_URL  = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.css"
KATEX_JS_URL   = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/katex.min.js"
KATEX_AUTO_URL = f"https://cdn.jsdelivr.net/npm/katex@{KATEX_VERSION}/dist/contrib/auto-render.min.js"


def _katex_head() -> str:
    """Lien stylesheet KaTeX chargé en <head> des pages leçon."""
    return (
        f'<link rel="stylesheet" href="{KATEX_CSS_URL}" crossorigin="anonymous">'
    )


def _katex_footer_scripts() -> str:
    """Scripts KaTeX + auto-render, chargés en fin de <body> sur les pages leçon.
    Grâce à defer, ils s'exécutent dans l'ordre d'apparition. L'auto-render ne
    reconnaît que les délimiteurs display `\\[...\\]` et inline `\\(...\\)`.
    throwOnError:false évite qu'une faute de frappe LaTeX casse le reste.
    """
    return (
        f'<script defer src="{KATEX_JS_URL}" crossorigin="anonymous"></script>'
        f'<script defer src="{KATEX_AUTO_URL}" crossorigin="anonymous" '
        f'onload="renderMathInElement(document.body,{{delimiters:[{{left:\'\\\\[\',right:\'\\\\]\',display:true}},{{left:\'\\\\(\',right:\'\\\\)\',display:false}}],throwOnError:false}});"></script>'
    )


def head_fr(titre: str, code: str, description: str, depth: int) -> str:
    base = "../" * depth
    page_url = f"https://johngab7.github.io/le-monde-en-chiffres/lecons/{code}/"
    en_url = f"https://johngab7.github.io/le-monde-en-chiffres/en/lessons/{code}/"
    return (
        f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{html.escape(description)}">'
        f'<meta name="theme-color" content="#102638">'
        f'<link rel="canonical" href="{page_url}">'
        f'<link rel="alternate" hreflang="fr" href="{page_url}">'
        f'<link rel="alternate" hreflang="en" href="{en_url}">'
        f'<link rel="alternate" hreflang="x-default" href="{page_url}">'
        f'<meta property="og:type" content="article">'
        f'<meta property="og:locale" content="fr_BE">'
        f'<meta property="og:title" content="{html.escape(titre)} · ACTU-BASICS">'
        f'<meta property="og:description" content="{html.escape(description)}">'
        f'<meta property="og:url" content="{page_url}">'
        f'<meta name="twitter:card" content="summary">'
        f'<title>{code} — {html.escape(titre)} · ACTU-BASICS</title>'
        f'{_premium_head_assets(base)}'
        f'{_katex_head()}'
        f'</head>'
    )


def head_en(titre: str, code: str, description: str, depth: int) -> str:
    base = "../" * depth
    page_url = f"https://johngab7.github.io/le-monde-en-chiffres/en/lessons/{code}/"
    fr_url = f"https://johngab7.github.io/le-monde-en-chiffres/lecons/{code}/"
    return (
        f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{html.escape(description)}">'
        f'<meta name="theme-color" content="#102638">'
        f'<link rel="canonical" href="{page_url}">'
        f'<link rel="alternate" hreflang="fr" href="{fr_url}">'
        f'<link rel="alternate" hreflang="en" href="{page_url}">'
        f'<link rel="alternate" hreflang="x-default" href="{fr_url}">'
        f'<meta property="og:type" content="article">'
        f'<meta property="og:locale" content="en_US">'
        f'<meta property="og:title" content="{html.escape(titre)} · ACTU-BASICS">'
        f'<meta property="og:description" content="{html.escape(description)}">'
        f'<meta property="og:url" content="{page_url}">'
        f'<meta name="twitter:card" content="summary">'
        f'<title>{code} — {html.escape(titre)} · ACTU-BASICS</title>'
        f'{_premium_head_assets(base)}'
        f'{_katex_head()}'
        f'</head>'
    )


_THEME_TOGGLE_FR = (
    '<button class="theme-toggle" type="button" data-theme-toggle '
    'aria-label="Changer de thème" title="Changer de thème">'
    '<svg class="ico-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
    '<svg class="ico-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"/></svg>'
    '</button>'
)
_THEME_TOGGLE_EN = _THEME_TOGGLE_FR.replace(
    'aria-label="Changer de thème" title="Changer de thème"',
    'aria-label="Switch theme" title="Switch theme"',
)


def header_fr(depth: int, current: str = "") -> str:
    b = "../" * depth
    def cls(name): return ' aria-current="page"' if current == name else " "
    return (
        f'<header class="site-header"><div class="nav-wrap">'
        f'<a class="brand" href="{b}index.html" aria-label="ACTU-BASICS">'
        f'<img src="{b}assets/img/logo-light.png" alt="" '
        f'onerror="this.style.display=\'none\'">'
        f'<span class="brand-name">ACTU-BASICS</span>'
        f'</a>'
        f'<nav id="site-navigation" class="nav-links" aria-label="Navigation principale">'
        f'<a href="{b}programme/"{cls("programme")}>Programme</a>'
        f'<a href="{b}parcours/"{cls("parcours")}>Parcours</a>'
        f'<a href="{b}bibliotheque/"{cls("bibliotheque")}>Bibliothèque</a>'
        f'<a href="{b}a-propos/"{cls("apropos")}>À propos</a>'
        f'</nav>'
        f'<div class="nav-actions">'
        f'{_THEME_TOGGLE_FR}'
        f'<a class="lang" href="{b}en/" lang="en" aria-label="Switch to English">EN</a>'
        f'<button class="menu-toggle" type="button" aria-controls="site-navigation" aria-expanded="false" aria-label="Ouvrir le menu">☰</button>'
        f'</div></div></header>'
    )


def header_en(depth: int, current: str = "") -> str:
    b = "../" * depth
    def cls(name): return ' aria-current="page"' if current == name else " "
    return (
        f'<header class="site-header"><div class="nav-wrap">'
        f'<a class="brand" href="{b}en/" aria-label="ACTU-BASICS">'
        f'<img src="{b}assets/img/logo-light-en.png" alt="" '
        f'onerror="this.style.display=\'none\'">'
        f'<span class="brand-name">ACTU-BASICS</span>'
        f'</a>'
        f'<nav id="site-navigation" class="nav-links" aria-label="Main navigation">'
        f'<a href="{b}en/programme/"{cls("programme")}>Programme</a>'
        f'<a href="{b}en/paths/"{cls("paths")}>Learning paths</a>'
        f'<a href="{b}en/library/"{cls("library")}>Library</a>'
        f'<a href="{b}en/about/"{cls("about")}>About</a>'
        f'</nav>'
        f'<div class="nav-actions">'
        f'{_THEME_TOGGLE_EN}'
        f'<a class="lang" href="{b}index.html" lang="fr" aria-label="Passer en français">FR</a>'
        f'<button class="menu-toggle" type="button" aria-controls="site-navigation" aria-expanded="false" aria-label="Open menu">☰</button>'
        f'</div></div></header>'
    )


# --- Icônes SVG officielles des réseaux ----------------------------------
# Chaque icône reste minimaliste (24x24, currentColor) pour s'adapter au
# thème clair/sombre. Les tracés sont des simplifications des marques
# officielles, sans texte ni logo complet.

_ICON_YOUTUBE = (
    '<svg class="social-ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 0 0 .5 6.2C0 8.1 0 12 0 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1c.5-1.9.5-5.8.5-5.8s0-3.9-.5-5.8zM9.6 15.6V8.4L15.8 12l-6.2 3.6z"/>'
    '</svg>'
)

_ICON_TIKTOK = (
    '<svg class="social-ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M19.3 6.6a5.5 5.5 0 0 1-3.7-1.4 5.3 5.3 0 0 1-1.7-3H10V15a2.6 2.6 0 1 1-2.6-2.6c.3 0 .5 0 .8.1V8.7a6.4 6.4 0 1 0 5.7 6.3V9.1a8.5 8.5 0 0 0 5.4 2v-3.9c-.3.1-.6.1-1 .1z"/>'
    '</svg>'
)

_ICON_GITHUB = (
    '<svg class="social-ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M12 .5A11.5 11.5 0 0 0 .5 12c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.2.8-.6v-2c-3.2.7-3.9-1.5-3.9-1.5-.5-1.3-1.3-1.7-1.3-1.7-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.3.8-1.6-2.6-.3-5.3-1.3-5.3-5.8 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.3 1.2a11 11 0 0 1 6 0C17.7 4.6 18.6 5 18.6 5c.7 1.6.2 2.8.1 3.1.8.8 1.2 1.8 1.2 3.1 0 4.5-2.7 5.5-5.3 5.8.4.4.8 1.1.8 2.2v3.3c0 .3.2.7.8.6a11.5 11.5 0 0 0 7.9-10.9A11.5 11.5 0 0 0 12 .5z"/>'
    '</svg>'
)

# Icône Gmail stylisée : enveloppe à rabat ouvert, coloration officielle.
# Reste une interprétation (pas le logo exact), compatible currentColor.
_ICON_GMAIL = (
    '<svg class="social-ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path fill="currentColor" d="M3 5h18a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zm1.5 2.6V17.5h3V11l4.5 3.6L16.5 11v6.5h3V7.6l-7.5 6-7.5-6z"/>'
    '</svg>'
)


def _follow_links(lang: str) -> str:
    """Liens de la colonne « Suivre / Follow » : YouTube, TikTok (dédiés par
    langue) et GitHub (commun)."""
    if lang == "fr":
        yt = "https://www.youtube.com/channel/UC3MrzU4G6UnSfDsYSci9BuQ"
        tk = "https://www.tiktok.com/@actu_basics_fr"
        yt_label = "YouTube · Français"
        tk_label = "TikTok · Français"
    else:
        yt = "https://www.youtube.com/channel/UC9AkR6xNGl9S9XHuFnbFCGg"
        tk = "https://www.tiktok.com/@actu_basics"
        yt_label = "YouTube · English"
        tk_label = "TikTok · English"
    gh = "https://github.com/JohnGAB7/le-monde-en-chiffres"
    return (
        f'<a class="social-link" href="{yt}" target="_blank" rel="noopener" aria-label="{yt_label}">'
        f'{_ICON_YOUTUBE}<span>YouTube</span></a>'
        f'<a class="social-link" href="{tk}" target="_blank" rel="noopener" aria-label="{tk_label}">'
        f'{_ICON_TIKTOK}<span>TikTok</span></a>'
        f'<a class="social-link" href="{gh}" target="_blank" rel="noopener" aria-label="GitHub">'
        f'{_ICON_GITHUB}<span>GitHub</span></a>'
    )


def _contact_links(lang: str) -> str:
    """Liens de la colonne « Contact » : email dédié par langue."""
    mail = "actubasics.officiel@gmail.com" if lang == "fr" else "actubasics.official@gmail.com"
    label = f"Email · {mail}"
    return (
        f'<a class="social-link" href="mailto:{mail}" aria-label="{label}">'
        f'{_ICON_GMAIL}<span>{mail}</span></a>'
    )


def footer_fr(depth: int) -> str:
    b = "../" * depth
    return (
        f'<footer class="footer"><div class="footer-inner">'
        f'<div><h3>ACTU-BASICS</h3>'
        f'<p>Éveiller par les chiffres. Comprendre les méthodes derrière les résultats.</p>'
        f'<p>Un projet éducatif indépendant consacré aux statistiques, aux probabilités et à l\'actuariat.</p></div>'
        f'<div><h3>Explorer</h3><div class="footer-links">'
        f'<a href="{b}programme/">Programme</a>'
        f'<a href="{b}parcours/">Parcours</a>'
        f'<a href="{b}bibliotheque/">Bibliothèque</a>'
        f'<a href="{b}a-propos/">À propos</a>'
        f'</div></div>'
        f'<div><h3>Suivre</h3><div class="social-links">'
        f'{_follow_links("fr")}'
        f'</div></div>'
        f'<div><h3>Contact</h3><div class="social-links">'
        f'{_contact_links("fr")}'
        f'</div></div></div>'
        f'<div class="footer-bottom">'
        f'<span>© ACTU-BASICS · Projet éducatif indépendant</span>'
        f'<span>Les contenus sont pédagogiques et ne constituent pas un conseil personnalisé.</span>'
        f'</div></footer>'
        f'<script src="{b}assets/js/site.js" defer></script>'
    )


def footer_en(depth: int) -> str:
    b = "../" * depth
    return (
        f'<footer class="footer"><div class="footer-inner">'
        f'<div><h3>ACTU-BASICS</h3>'
        f'<p>Enlightening through numbers. Understand the methods behind the results.</p>'
        f'<p>An independent educational project about statistics, probability and actuarial science.</p></div>'
        f'<div><h3>Explore</h3><div class="footer-links">'
        f'<a href="{b}en/programme/">Programme</a>'
        f'<a href="{b}en/paths/">Learning paths</a>'
        f'<a href="{b}en/library/">Library</a>'
        f'<a href="{b}en/about/">About</a>'
        f'</div></div>'
        f'<div><h3>Follow</h3><div class="social-links">'
        f'{_follow_links("en")}'
        f'</div></div>'
        f'<div><h3>Contact</h3><div class="social-links">'
        f'{_contact_links("en")}'
        f'</div></div></div>'
        f'<div class="footer-bottom">'
        f'<span>© ACTU-BASICS · Independent educational project</span>'
        f'<span>Content is educational and does not constitute personal advice.</span>'
        f'</div></footer>'
        f'<script src="{b}assets/js/site.js" defer></script>'
    )


# --- Vidéos : slots YouTube 16:9 et TikTok 9:16 ---------------------------

_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,32}$")
_YOUTUBE_HOSTS = ("www.youtube.com", "youtube.com", "youtu.be", "m.youtube.com")
_TIKTOK_HOSTS = ("www.tiktok.com", "tiktok.com", "vm.tiktok.com")


def _youtube_embed_url(url: str) -> str | None:
    """Convertit une URL YouTube reconnue en URL d'embed sûre.

    - Domaine obligatoirement dans la whitelist (`youtube.com` / `youtu.be`).
    - HTTPS requis.
    - L'ID vidéo doit matcher ``[A-Za-z0-9_-]{6,32}`` (filtre les injections).
    - Formes reconnues : youtu.be/<id>, youtube.com/watch?v=<id>,
      youtube.com/shorts/<id>, youtube.com/embed/<id>.
    Retourne None (et donc pas d'iframe rendu) pour toute autre URL.
    """
    if not url:
        return None
    try:
        from urllib.parse import urlparse, parse_qs
    except Exception:  # pragma: no cover
        return None
    try:
        u = urlparse(str(url).strip())
    except Exception:
        return None
    if u.scheme != "https" or u.netloc.lower() not in _YOUTUBE_HOSTS:
        return None

    vid: str | None = None
    host = u.netloc.lower()
    path = u.path or ""
    if host == "youtu.be":
        vid = path.lstrip("/").split("/", 1)[0] or None
    elif path.startswith("/watch"):
        qs = parse_qs(u.query)
        vid = (qs.get("v") or [None])[0]
    elif path.startswith("/shorts/"):
        vid = path[len("/shorts/"):].split("/", 1)[0] or None
    elif path.startswith("/embed/"):
        vid = path[len("/embed/"):].split("/", 1)[0] or None

    if not vid or not _VIDEO_ID_RE.match(vid):
        return None
    return f"https://www.youtube.com/embed/{vid}"


def _tiktok_safe_url(url: str) -> str | None:
    """Vérifie qu'une URL TikTok est bien hébergée sur tiktok.com en HTTPS.

    On ne rend jamais un iframe TikTok : seulement un lien externe. Cette
    fonction sert donc à valider que l'URL mérite d'être affichée.
    """
    if not url:
        return None
    try:
        from urllib.parse import urlparse
    except Exception:  # pragma: no cover
        return None
    try:
        u = urlparse(str(url).strip())
    except Exception:
        return None
    if u.scheme != "https" or u.netloc.lower() not in _TIKTOK_HOSTS:
        return None
    return u.geturl()


def _video_urls(data: dict | None, lang: str) -> tuple[str | None, str | None]:
    pub = {} if not isinstance(data, dict) else (data.get("publication") or {})
    yt = (pub.get("youtube") or {}) if isinstance(pub, dict) else {}
    tt = (pub.get("tiktok") or {}) if isinstance(pub, dict) else {}
    yt_url = yt.get(lang) if isinstance(yt, dict) else None
    tt_url = tt.get(lang) if isinstance(tt, dict) else None
    return yt_url, tt_url


def has_any_video(data: dict | None) -> bool:
    """Vrai si au moins une URL vidéo validée (whitelist de domaine) est renseignée."""
    for lg in ("fr", "en"):
        yt, tt = _video_urls(data, lg)
        if (yt and _youtube_embed_url(yt)) or (tt and _tiktok_safe_url(tt)):
            return True
    return False


def has_publication_intent(data: dict | None) -> bool:
    """Vrai si la fiche a UNE clé `publication:` (même avec des URLs invalides).

    On veut montrer le gabarit vidéo dès qu'une intention de publication est
    déclarée : les slots invalides tombent proprement en « non disponible ».
    """
    if not isinstance(data, dict):
        return False
    return bool(data.get("publication"))


def build_video_block(data: dict | None, lang: str) -> str:
    """Rend le bloc Vidéos.

    Principe (alignement sur le doc d'architecture) :
    - Aucune URL renseignée du tout : on affiche une ligne honnête
      « Vidéo en préparation » (pas de faux lecteur, pas de 16:9 vide).
    - Au moins une URL renseignée : on affiche le bloc complet et chaque
      slot indique explicitement son état.
    """
    yt_url, tt_url = _video_urls(data, lang)
    # Afficher la section dès qu'il y a UNE intention de publication (clé
    # publication: présente) : les URLs invalides tombent en « non disponible ».
    any_intent = has_publication_intent(data) or has_any_video(data)

    L = {
        "fr": {
            "heading": "Vidéos",
            "yt_h": "YouTube · format long",
            "tt_h": "TikTok · format court",
            "preparing_short": "Vidéo en préparation",
            "not_yet": "Non disponible — en préparation",
            "watch_yt": "Regarder sur YouTube ↗",
            "watch_tt": "Regarder sur TikTok ↗",
            "hint": "Les vidéos apparaîtront ici dès leur publication officielle.",
        },
        "en": {
            "heading": "Videos",
            "yt_h": "YouTube · long form",
            "tt_h": "TikTok · short form",
            "preparing_short": "Video in preparation",
            "not_yet": "Not yet available — in preparation",
            "watch_yt": "Watch on YouTube ↗",
            "watch_tt": "Watch on TikTok ↗",
            "hint": "Videos will appear here once officially published.",
        },
    }[lang]

    # Aucune intention de publication — ligne d'état compacte, pas de faux lecteur.
    if not any_intent:
        return (
            f'<aside class="video-status" aria-label="{html.escape(L["heading"])}">'
            f'<span class="video-status-dot" aria-hidden="true"></span>'
            f'<span class="video-status-text"><strong>{html.escape(L["heading"])}</strong> · {html.escape(L["preparing_short"])}</span>'
            f'</aside>'
        )

    def slot_youtube(url: str | None) -> str:
        embed = _youtube_embed_url(url) if url else None
        if embed:
            return (
                f'<div class="video-frame video-frame-16x9">'
                f'<iframe src="{html.escape(embed)}" '
                f'title="YouTube" loading="lazy" '
                f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                f'allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>'
                f'</div>'
                f'<a class="text-link" href="{html.escape(url)}" target="_blank" rel="noopener">{L["watch_yt"]}</a>'
            )
        # URL absente OU non reconnue par la whitelist : pas d'iframe.
        return (
            f'<div class="video-frame video-frame-16x9 video-frame-soon">'
            f'<span class="video-soon">{L["not_yet"]}</span>'
            f'</div>'
        )

    def slot_tiktok(url: str | None) -> str:
        safe = _tiktok_safe_url(url) if url else None
        if safe:
            return (
                f'<div class="video-frame video-frame-9x16 video-frame-link">'
                f'<a class="video-link" href="{html.escape(safe)}" target="_blank" rel="noopener">'
                f'<span class="video-link-label">TikTok</span>'
                f'<span class="video-link-cta">{L["watch_tt"]}</span>'
                f'</a></div>'
            )
        return (
            f'<div class="video-frame video-frame-9x16 video-frame-soon">'
            f'<span class="video-soon">{L["not_yet"]}</span>'
            f'</div>'
        )

    return (
        f'<section class="video-section" aria-label="{html.escape(L["heading"])}">'
        f'<h2>{html.escape(L["heading"])}</h2>'
        f'<div class="video-grid">'
        f'<figure class="video-slot video-slot-yt">'
        f'<figcaption class="video-caption">{html.escape(L["yt_h"])}</figcaption>'
        f'{slot_youtube(yt_url)}'
        f'</figure>'
        f'<figure class="video-slot video-slot-tt">'
        f'<figcaption class="video-caption">{html.escape(L["tt_h"])}</figcaption>'
        f'{slot_tiktok(tt_url)}'
        f'</figure>'
        f'</div>'
        f'<p class="muted"><small>{html.escape(L["hint"])}</small></p>'
        f'</section>'
    )


def parcours_for_lesson(code: str, parcours_list: list[dict]) -> list[dict]:
    """Retourne la liste de tous les parcours contenant le module de cette leçon.

    Une leçon peut légitimement appartenir à plusieurs parcours (p.ex. un module
    partagé entre un parcours thématique et un parcours de spécialisation).
    """
    mod = module_of(code)
    return [p for p in parcours_list if mod in (p.get("modules") or [])]


# --- Page leçon ------------------------------------------------------------

def render_lesson_page(data: dict, lang: str, parcours_list: list[dict] | None = None) -> str:
    code = module_code(data["id"])
    ed = data.get("editions", {}).get(lang, {})
    titre = ed.get("titre", code)
    legende = ed.get("legende", "")
    description = (legende or titre).replace("\n", " ").strip()[:300]
    scenes = ed.get("scenes", [])
    ped = data.get("pedagogie", {})

    def by_lang(node):
        if isinstance(node, dict):
            v = node.get(lang, [])
        else:
            v = node
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return v
        return []
    objectifs = by_lang(ped.get("objectifs"))
    prerequis = by_lang(ped.get("prerequis"))
    hypotheses = by_lang(ped.get("hypotheses"))

    scene_html = "".join(render_scene(s, lang) for s in scenes)

    if lang == "fr":
        L = {
            "skip": "Aller au contenu",
            "home": "Accueil",
            "home_href": "../../",
            "lib_label": "Bibliothèque",
            "lib_href": "../../bibliotheque/",
            "lib_back": "← Bibliothèque",
            "other_lang_href": f"../../en/lessons/{code}/",
            "other_lang_label": "Read in English",
            "obj_h": "Objectifs",
            "pre_h": "Prérequis",
            "hyp_h": "Hypothèses",
            "at_a_glance": "En bref",
            "tag_available": "Leçon disponible",
        }
        depth_lesson = 2
    else:
        L = {
            "skip": "Skip to content",
            "home": "Home",
            "home_href": "../../../",
            "lib_label": "Library",
            "lib_href": "../../library/",
            "lib_back": "← Library",
            "other_lang_href": f"../../../lecons/{code}/",
            "other_lang_label": "Lire en français",
            "obj_h": "Learning objectives",
            "pre_h": "Prerequisites",
            "hyp_h": "Assumptions",
            "at_a_glance": "At a glance",
            "tag_available": "Available lesson",
        }
        depth_lesson = 3

    head = (head_fr if lang == "fr" else head_en)(titre, code, description, depth_lesson)
    header = (header_fr if lang == "fr" else header_en)(depth_lesson, current="library" if lang == "en" else "bibliotheque")
    footer = (footer_fr if lang == "fr" else footer_en)(depth_lesson)

    obj_block = f'<h2>{L["obj_h"]}</h2>{md_items(objectifs)}' if objectifs else ""
    pre_block = f'<h2>{L["pre_h"]}</h2>{md_items(prerequis)}' if prerequis else ""
    hyp_block = f'<h2>{L["hyp_h"]}</h2>{md_items(hypotheses)}' if hypotheses else ""

    # --- Méta leçon : temps de lecture estimé + date de révision --------
    #
    # Temps de lecture : ~230 mots/minute en lecture informée. On compte les
    # mots du texte des scènes (voix_off + texte + étapes), pas des formules.
    def _count_words(obj) -> int:
        if obj is None:
            return 0
        if isinstance(obj, dict):
            return _count_words(obj.get(lang) or obj.get("fr") or obj.get("en") or "")
        if isinstance(obj, list):
            return sum(_count_words(x) for x in obj)
        if isinstance(obj, str):
            return len(re.findall(r"\w+", obj))
        return 0

    total_words = 0
    for scn in (scenes or []):
        if isinstance(scn, dict):
            for key in ("texte", "voix_off", "etapes", "note", "etiquette", "reponse"):
                total_words += _count_words(scn.get(key))
    reading_minutes = max(1, round(total_words / 230))

    date_update = (data.get("validation", {}) or {}).get("date") or data.get("date_maj") or data.get("date")
    date_str = str(date_update) if date_update else ""
    author = (data.get("validation", {}) or {}).get("valide_par") or data.get("auteur") or "JG"

    if lang == "fr":
        meta_parts = [
            f'<span>⏱ <strong>{reading_minutes} min</strong> de lecture</span>',
            f'<span>✎ Rédigé par <strong>{html.escape(author)}</strong></span>',
        ]
        if date_str:
            meta_parts.append(f'<span>↻ Mis à jour le <strong>{html.escape(date_str)}</strong></span>')
    else:
        meta_parts = [
            f'<span>⏱ <strong>{reading_minutes} min</strong> read</span>',
            f'<span>✎ Written by <strong>{html.escape(author)}</strong></span>',
        ]
        if date_str:
            meta_parts.append(f'<span>↻ Updated <strong>{html.escape(date_str)}</strong></span>')
    lesson_meta = f'<div class="lesson-meta">{"".join(meta_parts)}</div>'

    # --- Bloc « À retenir » : dérivé du scène `fin` si présent ---------
    takeaway_html = ""
    for scn in reversed(scenes or []):
        if isinstance(scn, dict) and scn.get("type") == "fin":
            msg = pick_lang(scn.get("texte"), lang) or pick_lang(scn.get("voix_off"), lang)
            if msg:
                label = "À retenir" if lang == "fr" else "Takeaway"
                takeaway_html = (
                    f'<aside class="lesson-takeaway" aria-label="{label}">'
                    f'<strong>{label}</strong>'
                    f'<p>{md_inline(msg)}</p>'
                    f'</aside>'
                )
            break

    page_hero = (
        f'<section class="page-hero"><div class="container">'
        f'<div class="breadcrumb">'
        f'<a href="{L["home_href"]}">{L["home"]}</a> / '
        f'<a href="{L["lib_href"]}">{L["lib_label"]}</a> / {code}</div>'
        f'<span class="eyebrow">{code}</span>'
        f'<h1>{md_inline(titre)}</h1>'
        f'{f"<p>{md_inline(legende)}</p>" if legende else ""}'
        f'</div></section>'
    )

    video_block = build_video_block(data, lang)

    # Parcours auxquels appartient cette leçon (0, 1 ou plusieurs).
    parcours_matching = parcours_for_lesson(code, parcours_list or [])
    parcours_aside = ""
    if parcours_matching:
        if lang == "fr":
            path_label = "Parcours" if len(parcours_matching) == 1 else "Parcours concernés"
            see_first = "Voir le parcours →"
        else:
            path_label = "Learning path" if len(parcours_matching) == 1 else "Related learning paths"
            see_first = "See first learning path →"
        items = []
        hrefs = []
        for p in parcours_matching:
            p_slug = p.get("slug", "")
            p_titre = (p.get("titre") or {}).get(lang) or p.get("slug") or ""
            if lang == "fr":
                href = f"../../parcours/{p_slug}/"
            else:
                href = f"../../../en/paths/{p_slug}/"
            hrefs.append(href)
            items.append(f'<li><a class="text-link" href="{href}">{html.escape(p_titre)}</a></li>')
        parcours_aside = (
            f'<p><strong>{path_label}</strong></p>'
            f'<ul class="aside-list">{"".join(items)}</ul>'
            f'<a class="button button-outline" href="{hrefs[0]}">{see_first}</a>'
        )

    toc_label = "Dans cette leçon" if lang == "fr" else "In this lesson"
    lesson_section = (
        f'<section class="section"><div class="container lesson-layout">'
        f'<article class="lesson-content">'
        f'{lesson_meta}'
        f'{video_block}'
        f'{obj_block}{pre_block}'
        f'{scene_html}'
        f'{hyp_block}'
        f'{takeaway_html}'
        f'</article>'
        f'<aside class="lesson-aside">'
        f'<span class="tag">{L["tag_available"]}</span>'
        f'<h3>{L["at_a_glance"]}</h3>'
        f'<p><strong>Code</strong><br>{code}</p>'
        f'<nav data-lesson-toc aria-label="{toc_label}" class="lesson-toc"><p><strong>{toc_label}</strong></p></nav>'
        f'{parcours_aside}'
        f'<a class="button button-dark" href="{L["lib_href"]}">{L["lib_back"]}</a>'
        f'<a class="button button-outline" href="{L["other_lang_href"]}">{L["other_lang_label"]}</a>'
        f'</aside></div></section>'
    )

    return (
        f'{head}<body>'
        f'<a class="skip-link" href="#contenu">{L["skip"]}</a>'
        f'{header}'
        f'<main id="contenu">{page_hero}{lesson_section}</main>'
        f'{footer}'
        f'{_katex_footer_scripts()}'
        f'</body></html>'
    )


# --- Bibliothèque ----------------------------------------------------------

def _prereq_count(data: dict | None, lang: str) -> int:
    if not isinstance(data, dict):
        return 0
    ped = data.get("pedagogie", {}) or {}
    pre = ped.get("prerequis")
    if isinstance(pre, dict):
        v = pre.get(lang, [])
    else:
        v = pre
    if not v:
        return 0
    if isinstance(v, str):
        # Une entrée comme « Aucun : rappel de calcul de base » compte 0.
        lowered = v.lower()
        if "aucun" in lowered or "none" in lowered:
            return 0
        return 1
    if isinstance(v, list):
        n = 0
        for item in v:
            if not item:
                continue
            txt = str(item).lower()
            if "aucun" in txt or "none" in txt:
                continue
            n += 1
        return n
    return 0


def _niveau_label(data: dict | None, lang: str) -> str:
    """Retourne le label de niveau. decouverte -> Découverte / Intro."""
    if not isinstance(data, dict):
        return "Découverte" if lang == "fr" else "Intro"
    ped = data.get("pedagogie", {}) or {}
    niv = (ped.get("niveau") or "decouverte").lower()
    mapping_fr = {
        "decouverte": "Découverte",
        "intermediaire": "Intermédiaire",
        "avance": "Avancé",
    }
    mapping_en = {
        "decouverte": "Intro",
        "intermediaire": "Intermediate",
        "avance": "Advanced",
    }
    return (mapping_fr if lang == "fr" else mapping_en).get(niv, niv.title())


def build_lesson_card(L: dict, lang: str, depth: int = 1) -> str:
    """Rend une carte de leçon.

    ``depth`` est la profondeur de la page conteneur par rapport à la racine :
    - 1 pour /bibliotheque/ ou /parcours/<slug>/ (FR, depth=1)
    - 2 pour /en/library/ ou /en/paths/<slug>/ (EN, depth=2)
    Il détermine combien de ``../`` ajouter devant ``lecons/`` ou ``lessons/``
    pour produire un lien valide vers la page leçon.
    """
    code = L["code"]
    ed = L["ed_fr"] if lang == "fr" else L["ed_en"]
    titre = ed.get("titre", code)
    legende = (ed.get("legende", "") or "").strip()
    legende_short = legende.split(".")[0] if legende else ""
    if len(legende_short) > 180:
        legende_short = legende_short[:177] + "…"
    tags = ed.get("hashtags", []) or []
    keywords = " ".join(str(t) for t in tags)
    cat = L["category"]
    up = "../" * depth
    path = f"{up}lecons/{code}/" if lang == "fr" else f"{up}lessons/{code}/"
    open_label = "Consulter la leçon →" if lang == "fr" else "Open lesson →"

    data = L.get("data")
    prereq_n = _prereq_count(data, lang)
    niveau = _niveau_label(data, lang)
    if lang == "fr":
        prereq_label = "Sans prérequis" if prereq_n == 0 else (
            "1 prérequis" if prereq_n == 1 else f"{prereq_n} prérequis"
        )
    else:
        prereq_label = "No prerequisite" if prereq_n == 0 else (
            "1 prerequisite" if prereq_n == 1 else f"{prereq_n} prerequisites"
        )

    module = L["module"]
    search_blob = f"{code} {module} {titre} {keywords} {legende}"

    # Badges d'état explicites (alignement sur le doc d'architecture : disponibilité explicite).
    fiche_label = "Fiche disponible" if lang == "fr" else "Lesson available"
    video_label = "Vidéo en ligne" if lang == "fr" else "Video online"
    state_badges = [f'<span class="badge badge-state badge-state-lesson">{html.escape(fiche_label)}</span>']
    if has_any_video(data):
        state_badges.append(
            f'<span class="badge badge-state badge-state-video">{html.escape(video_label)}</span>'
        )

    badges = (
        f'<span class="badge badge-level">{html.escape(niveau)}</span>'
        f'<span class="badge badge-prereq">{html.escape(prereq_label)}</span>'
        + "".join(state_badges)
    )

    return (
        f'<article class="card lesson-card" data-lesson '
        f'data-category="{html.escape(cat)}" '
        f'data-module="{html.escape(module)}" '
        f'data-keywords="{html.escape(keywords)}">'
        f'<div class="card-top"><span class="lesson-code">{code}</span></div>'
        f'<h3>{md_inline(titre)}</h3>'
        f'<p>{md_inline(legende_short)}</p>'
        f'<div class="card-badges">{badges}</div>'
        f'<div class="card-bottom">'
        f'<a class="text-link" href="{path}">{open_label}</a>'
        f'</div></article>'
    )


def build_modules_sections(lessons: list[dict], lang: str) -> str:
    """Regroupe par module avec en-têtes et compte. Modules dérivés des leçons."""
    by_mod: dict[str, list[dict]] = {}
    for L in lessons:
        by_mod.setdefault(L["module"], []).append(L)

    lessons_word = ("leçon", "leçons") if lang == "fr" else ("lesson", "lessons")
    module_word = "Module" if lang == "fr" else "Module"

    out = []
    for mod in module_order_from(lessons):
        bucket = by_mod.get(mod) or []
        if not bucket:
            continue
        bucket = sorted(bucket, key=lambda x: x["code"])
        m = module_meta(mod, lang)
        count = len(bucket)
        count_label = f"{count} {lessons_word[0] if count == 1 else lessons_word[1]}"
        cards_html = "".join(build_lesson_card(L, lang) for L in bucket)
        out.append(
            f'<section class="module-section" id="mod-{mod}" '
            f'data-module-section="{mod}" data-category="{html.escape(m["category"])}">'
            f'<div class="module-head">'
            f'<div class="module-head-text">'
            f'<span class="eyebrow">{module_word} {mod}</span>'
            f'<h2>{md_inline(m["titre"])}</h2>'
            f'<p>{md_inline(m["sous_titre"])}</p>'
            f'</div>'
            f'<span class="module-count" data-visible-count>{count_label}</span>'
            f'</div>'
            f'<div class="grid-3 module-grid">{cards_html}</div>'
            f'</section>'
        )
    return "".join(out)


def build_modules_overview(lessons: list[dict], lang: str) -> str:
    """Barre de navigation inter-modules affichée en tête de la bibliothèque.

    Distincte des pages parcours : ici c'est un simple jump-nav par module.
    """
    by_mod: dict[str, int] = {}
    for L in lessons:
        by_mod[L["module"]] = by_mod.get(L["module"], 0) + 1

    title_fr = "Explorer par module"
    title_en = "Browse by module"
    jump_label_fr = "Aller au module"
    jump_label_en = "Jump to module"

    items = []
    for i, mod in enumerate([m for m in module_order_from(lessons) if by_mod.get(m)], start=1):
        count = by_mod[mod]
        m = module_meta(mod, lang)
        title_text = m["titre"]
        label_lessons = "leçons" if lang == "fr" else "lessons"
        label_lesson = "leçon" if lang == "fr" else "lesson"
        n_label = f"{count} {label_lesson if count == 1 else label_lessons}"
        items.append(
            f'<a class="parcours-step" href="#mod-{mod}" '
            f'aria-label="{html.escape((jump_label_fr if lang == "fr" else jump_label_en))} {mod} — {html.escape(title_text)}">'
            f'<span class="parcours-index">{i:02d}</span>'
            f'<span class="parcours-body">'
            f'<span class="parcours-code">{mod}</span>'
            f'<span class="parcours-title">{html.escape(title_text)}</span>'
            f'<span class="parcours-count">{n_label}</span>'
            f'</span>'
            f'</a>'
        )

    overview_title = title_fr if lang == "fr" else title_en
    module_count = len(by_mod)
    overview_sub = (
        f"{module_count} portes d'entrée. Clique pour sauter directement au module qui t'intéresse."
        if lang == "fr"
        else f"{module_count} entry points. Jump straight to the module you want."
    )
    return (
        f'<section class="parcours-overview modules-overview" aria-label="{html.escape(overview_title)}">'
        f'<div class="parcours-head">'
        f'<span class="eyebrow">{html.escape(overview_title)}</span>'
        f'<p class="muted">{html.escape(overview_sub)}</p>'
        f'</div>'
        f'<div class="parcours-steps">{"".join(items)}</div>'
        f'</section>'
    )


def render_library_page(lessons: list[dict], lang: str) -> str:
    overview_html = build_modules_overview(lessons, lang)
    sections_html = build_modules_sections(lessons, lang)
    cats_in_use = sorted({L["category"] for L in lessons})
    cat_labels = CATEGORY_LABELS_FR if lang == "fr" else CATEGORY_LABELS_EN
    cat_labels = dict(cat_labels)  # local copy
    label_all = "Tous les domaines" if lang == "fr" else "All subjects"

    if lang == "fr":
        head = (
            '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="Rechercher les leçons ACTU-BASICS en statistiques, probabilités, fondations et actuariat.">'
            '<meta name="theme-color" content="#102638">'
            '<link rel="canonical" href="https://johngab7.github.io/le-monde-en-chiffres/bibliotheque/">'
            '<link rel="alternate" hreflang="fr" href="https://johngab7.github.io/le-monde-en-chiffres/bibliotheque/">'
            '<link rel="alternate" hreflang="en" href="https://johngab7.github.io/le-monde-en-chiffres/en/library/">'
            '<link rel="alternate" hreflang="x-default" href="https://johngab7.github.io/le-monde-en-chiffres/bibliotheque/">'
            '<meta property="og:type" content="website">'
            '<meta property="og:locale" content="fr_BE">'
            '<meta property="og:title" content="Bibliothèque des leçons · ACTU-BASICS">'
            '<meta property="og:description" content="Toutes les leçons ACTU-BASICS, cherchables par mot-clé et par domaine.">'
            '<meta property="og:url" content="https://johngab7.github.io/le-monde-en-chiffres/bibliotheque/">'
            '<meta name="twitter:card" content="summary">'
            '<title>Bibliothèque des leçons · ACTU-BASICS</title>'
            f'{_premium_head_assets("../")}</head>'
        )
        header = header_fr(depth=1, current="bibliotheque")
        footer = footer_fr(depth=1)
        skip = "Aller au contenu"
        hero_title = "La bibliothèque."
        hero_eyebrow = "Toutes les ressources au même endroit"
        hero_body = "Retrouve les leçons disponibles et accède directement aux notions que tu souhaites travailler."
        search_label = "Rechercher une leçon"
        search_placeholder = "Rechercher une leçon, une notion…"
        filter_label = "Filtrer par domaine"
        empty_msg = "Aucune leçon ne correspond à ta recherche. Modifie les mots-clés ou le domaine sélectionné."
        breadcrumb = "ACTU-BASICS / Bibliothèque"
    else:
        head = (
            '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="Search ACTU-BASICS lessons in statistics, probability, foundations and actuarial science.">'
            '<meta name="theme-color" content="#102638">'
            '<link rel="canonical" href="https://johngab7.github.io/le-monde-en-chiffres/en/library/">'
            '<link rel="alternate" hreflang="fr" href="https://johngab7.github.io/le-monde-en-chiffres/bibliotheque/">'
            '<link rel="alternate" hreflang="en" href="https://johngab7.github.io/le-monde-en-chiffres/en/library/">'
            '<link rel="alternate" hreflang="x-default" href="https://johngab7.github.io/le-monde-en-chiffres/bibliotheque/">'
            '<meta property="og:type" content="website">'
            '<meta property="og:locale" content="en_US">'
            '<meta property="og:title" content="Lesson library · ACTU-BASICS">'
            '<meta property="og:description" content="All ACTU-BASICS lessons, searchable by keyword and by subject.">'
            '<meta property="og:url" content="https://johngab7.github.io/le-monde-en-chiffres/en/library/">'
            '<meta name="twitter:card" content="summary">'
            '<title>Lesson library · ACTU-BASICS</title>'
            f'{_premium_head_assets("../../")}</head>'
        )
        header = header_en(depth=2, current="library")
        footer = footer_en(depth=2)
        skip = "Skip to content"
        hero_title = "The library."
        hero_eyebrow = "Learning resources in one place"
        hero_body = "Find available lessons and jump straight into the topics you want to explore."
        search_label = "Search lessons"
        search_placeholder = "Search a lesson or topic…"
        filter_label = "Filter by subject"
        empty_msg = "No lessons match your search. Try different keywords or choose another subject."
        breadcrumb = "ACTU-BASICS / Library"

    options = [f'<option value="all">{html.escape(label_all)}</option>']
    for cat in cats_in_use:
        label = cat_labels.get(cat, cat)
        options.append(f'<option value="{html.escape(cat)}">{html.escape(label)}</option>')

    return (
        f'{head}<body>'
        f'<a class="skip-link" href="#contenu">{skip}</a>'
        f'{header}'
        f'<main id="contenu">'
        f'<section class="page-hero"><div class="container">'
        f'<div class="breadcrumb">{breadcrumb}</div>'
        f'<span class="eyebrow">{hero_eyebrow}</span>'
        f'<h1>{hero_title}</h1><p>{hero_body}</p>'
        f'</div></section>'
        f'<section class="section"><div class="container">'
        f'{overview_html}'
        f'<div class="catalog-tools">'
        f'<label class="skip-link" for="search-{lang}">{search_label}</label>'
        f'<input id="search-{lang}" class="search-input" type="search" placeholder="{html.escape(search_placeholder)}" data-search>'
        f'<label class="skip-link" for="filter-{lang}">{filter_label}</label>'
        f'<select id="filter-{lang}" class="filter-select" data-filter>{"".join(options)}</select>'
        f'</div>'
        f'{sections_html}'
        f'<p class="empty-state" data-empty role="status" aria-live="polite" hidden>{empty_msg}</p>'
        f'</div></section>'
        f'</main>{footer}</body></html>'
    )


# --- Pages parcours --------------------------------------------------------

def _parcours_statut_label(statut: str, lang: str) -> str:
    key = (statut or "en_cours").lower()
    labels_fr = {
        "en_cours": "En cours",
        "a_venir":  "À venir",
        "complet":  "Complet",
    }
    labels_en = {
        "en_cours": "In progress",
        "a_venir":  "Coming soon",
        "complet":  "Complete",
    }
    return (labels_fr if lang == "fr" else labels_en).get(key, key)


def render_parcours_index(parcours_list: list[dict], lessons: list[dict], lang: str) -> str:
    # Compte de leçons disponibles par parcours.
    by_mod: dict[str, list[dict]] = {}
    for L in lessons:
        by_mod.setdefault(L["module"], []).append(L)

    L = {
        "fr": {
            "head_title": "Parcours d'apprentissage · ACTU-BASICS",
            "head_desc": "Parcours progressifs ACTU-BASICS en statistiques, probabilités et actuariat.",
            "canon": "https://johngab7.github.io/le-monde-en-chiffres/parcours/",
            "alt": "https://johngab7.github.io/le-monde-en-chiffres/en/paths/",
            "og_locale": "fr_BE",
            "og_title": "Parcours d'apprentissage · ACTU-BASICS",
            "og_desc": "Trois parcours pour progresser étape par étape.",
            "css_base": "../",
            "breadcrumb": "ACTU-BASICS / Parcours",
            "eyebrow": "Apprendre avec un fil conducteur",
            "h1": "Les parcours.",
            "intro": "Trois chemins pour organiser tes apprentissages et relier les notions, étape par étape.",
            "skip": "Aller au contenu",
            "lessons_label": "leçons disponibles",
            "lesson_label_1": "leçon disponible",
            "open": "Ouvrir le parcours →",
            "current": "parcours",
        },
        "en": {
            "head_title": "Learning paths · ACTU-BASICS",
            "head_desc": "ACTU-BASICS progressive paths in statistics, probability and actuarial science.",
            "canon": "https://johngab7.github.io/le-monde-en-chiffres/en/paths/",
            "alt": "https://johngab7.github.io/le-monde-en-chiffres/parcours/",
            "og_locale": "en_US",
            "og_title": "Learning paths · ACTU-BASICS",
            "og_desc": "Three paths to progress step by step.",
            "css_base": "../../",
            "breadcrumb": "ACTU-BASICS / Learning paths",
            "eyebrow": "A guided way to learn",
            "h1": "Learning paths.",
            "intro": "Three paths to organize your learning and connect ideas, one step at a time.",
            "skip": "Skip to content",
            "lessons_label": "lessons available",
            "lesson_label_1": "lesson available",
            "open": "Open path →",
            "current": "paths",
        },
    }[lang]

    head = (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{html.escape(L["head_desc"])}">'
        f'<meta name="theme-color" content="#102638">'
        f'<link rel="canonical" href="{L["canon"]}">'
        f'<link rel="alternate" hreflang="fr" href="https://johngab7.github.io/le-monde-en-chiffres/parcours/">'
        f'<link rel="alternate" hreflang="en" href="https://johngab7.github.io/le-monde-en-chiffres/en/paths/">'
        f'<link rel="alternate" hreflang="x-default" href="https://johngab7.github.io/le-monde-en-chiffres/parcours/">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="{L["og_locale"]}">'
        f'<meta property="og:title" content="{html.escape(L["og_title"])}">'
        f'<meta property="og:description" content="{html.escape(L["og_desc"])}">'
        f'<meta property="og:url" content="{L["canon"]}">'
        f'<meta name="twitter:card" content="summary">'
        f'<title>{html.escape(L["head_title"])}</title>'
        f'{_premium_head_assets(L["css_base"])}</head>'
    )
    header = (header_fr if lang == "fr" else header_en)(depth=1 if lang == "fr" else 2, current=L["current"])
    footer = (footer_fr if lang == "fr" else footer_en)(depth=1 if lang == "fr" else 2)

    cards = []
    for i, p in enumerate(parcours_list, start=1):
        slug = p.get("slug", "")
        titre = (p.get("titre") or {}).get(lang, slug)
        sous_titre = (p.get("sous_titre") or {}).get(lang, "")
        modules = p.get("modules") or []
        n_lessons = sum(len(by_mod.get(m, [])) for m in modules)
        statut = _parcours_statut_label(p.get("statut", "en_cours"), lang)

        if lang == "fr":
            lessons_txt = (
                f"{n_lessons} {L['lesson_label_1']}" if n_lessons == 1
                else f"{n_lessons} {L['lessons_label']}"
            )
            href = f"../parcours/{slug}/"
        else:
            lessons_txt = (
                f"{n_lessons} {L['lesson_label_1']}" if n_lessons == 1
                else f"{n_lessons} {L['lessons_label']}"
            )
            href = f"../paths/{slug}/"

        mods_chips = "".join(
            f'<span class="mod-chip">{m}</span>' for m in modules
        ) or '<span class="mod-chip mod-chip-empty">—</span>'

        cards.append(
            f'<article class="card path-card parcours-card" data-number="{i:02d}">'
            f'<div class="card-top"><span class="icon-tile">{i:02d}</span>'
            f'<span class="tag">{html.escape(statut)}</span></div>'
            f'<h3>{md_inline(titre)}</h3>'
            f'<p>{md_inline(sous_titre)}</p>'
            f'<div class="mod-chips">{mods_chips}</div>'
            f'<div class="card-bottom">'
            f'<span class="muted"><small>{lessons_txt}</small></span>'
            f'<a class="text-link" href="{href}">{L["open"]}</a>'
            f'</div></article>'
        )

    return (
        f'{head}<body>'
        f'<a class="skip-link" href="#contenu">{L["skip"]}</a>'
        f'{header}'
        f'<main id="contenu">'
        f'<section class="page-hero"><div class="container">'
        f'<div class="breadcrumb">{L["breadcrumb"]}</div>'
        f'<span class="eyebrow">{L["eyebrow"]}</span>'
        f'<h1>{L["h1"]}</h1><p>{L["intro"]}</p>'
        f'</div></section>'
        f'<section class="section"><div class="container">'
        f'<div class="grid-3">{"".join(cards)}</div>'
        f'</div></section>'
        f'</main>{footer}</body></html>'
    )


def render_parcours_detail(p: dict, lessons: list[dict], lang: str) -> str:
    """Page d'un parcours : liste ordonnée des modules et leçons."""
    slug = p.get("slug", "")
    titre = (p.get("titre") or {}).get(lang, slug)
    sous_titre = (p.get("sous_titre") or {}).get(lang, "")
    description = (p.get("description") or {}).get(lang, "")
    modules = p.get("modules") or []
    statut = _parcours_statut_label(p.get("statut", "en_cours"), lang)

    by_mod: dict[str, list[dict]] = {}
    for L in lessons:
        by_mod.setdefault(L["module"], []).append(L)

    L = {
        "fr": {
            "head_title": f"{titre} · Parcours · ACTU-BASICS",
            "canon": f"https://johngab7.github.io/le-monde-en-chiffres/parcours/{slug}/",
            "alt":   f"https://johngab7.github.io/le-monde-en-chiffres/en/paths/{slug}/",
            "og_locale": "fr_BE",
            "og_title": f"{titre} · Parcours · ACTU-BASICS",
            "css_base": "../../",
            "breadcrumb": f'<a href="../../index.html">ACTU-BASICS</a> / <a href="../">Parcours</a> / {slug}',
            "skip": "Aller au contenu",
            "lesson_word": "leçon",
            "lessons_word": "leçons",
            "modules_title": "Les modules de ce parcours",
            "open": "Consulter →",
            "soon": "À venir",
            "empty_mod": "Les leçons de ce module seront ajoutées progressivement.",
            "back": "← Tous les parcours",
            "current": "parcours",
            "home_href": "../../",
        },
        "en": {
            "head_title": f"{titre} · Learning path · ACTU-BASICS",
            "canon": f"https://johngab7.github.io/le-monde-en-chiffres/en/paths/{slug}/",
            "alt":   f"https://johngab7.github.io/le-monde-en-chiffres/parcours/{slug}/",
            "og_locale": "en_US",
            "og_title": f"{titre} · Learning path · ACTU-BASICS",
            "css_base": "../../../",
            "breadcrumb": f'<a href="../../../en/">ACTU-BASICS</a> / <a href="../">Learning paths</a> / {slug}',
            "skip": "Skip to content",
            "lesson_word": "lesson",
            "lessons_word": "lessons",
            "modules_title": "Modules in this path",
            "open": "Open →",
            "soon": "Coming soon",
            "empty_mod": "Lessons for this module will be added progressively.",
            "back": "← All learning paths",
            "current": "paths",
            "home_href": "../../../",
        },
    }[lang]

    head = (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{html.escape(description[:300])}">'
        f'<meta name="theme-color" content="#102638">'
        f'<link rel="canonical" href="{L["canon"]}">'
        f'<link rel="alternate" hreflang="fr" href="https://johngab7.github.io/le-monde-en-chiffres/parcours/{slug}/">'
        f'<link rel="alternate" hreflang="en" href="https://johngab7.github.io/le-monde-en-chiffres/en/paths/{slug}/">'
        f'<link rel="alternate" hreflang="x-default" href="https://johngab7.github.io/le-monde-en-chiffres/parcours/{slug}/">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="{L["og_locale"]}">'
        f'<meta property="og:title" content="{html.escape(L["og_title"])}">'
        f'<meta property="og:description" content="{html.escape(description[:300])}">'
        f'<meta property="og:url" content="{L["canon"]}">'
        f'<meta name="twitter:card" content="summary">'
        f'<title>{html.escape(L["head_title"])}</title>'
        f'{_premium_head_assets(L["css_base"])}</head>'
    )
    depth_detail = 2 if lang == "fr" else 3
    header = (header_fr if lang == "fr" else header_en)(depth=depth_detail, current=L["current"])
    footer = (footer_fr if lang == "fr" else footer_en)(depth=depth_detail)

    # Barre de progression modulaire.
    steps = []
    for i, mod in enumerate(modules, start=1):
        m = module_meta(mod, lang)
        n = len(by_mod.get(mod, []))
        count_label = (
            f"{n} {L['lesson_word'] if n == 1 else L['lessons_word']}"
            if n > 0 else L["soon"]
        )
        state_class = "parcours-step-ready" if n > 0 else "parcours-step-pending"
        steps.append(
            f'<a class="parcours-step {state_class}" href="#mod-{mod}">'
            f'<span class="parcours-index">{i:02d}</span>'
            f'<span class="parcours-body">'
            f'<span class="parcours-code">{mod}</span>'
            f'<span class="parcours-title">{html.escape(m["titre"])}</span>'
            f'<span class="parcours-count">{count_label}</span>'
            f'</span>'
            f'</a>'
        )
    progress_html = (
        f'<section class="parcours-overview parcours-progress" aria-label="Progression">'
        f'<div class="parcours-steps">{"".join(steps)}</div>'
        f'</section>'
    )

    # Un bloc par module.
    sections = []
    for mod in modules:
        m = module_meta(mod, lang)
        bucket = sorted(by_mod.get(mod, []), key=lambda x: x["code"])
        if bucket:
            # Les pages parcours sont une profondeur plus bas que la biblio :
            # /parcours/<slug>/ et /en/paths/<slug>/ -> depth=2.
            cards_html = "".join(build_lesson_card(x, lang, depth=2) for x in bucket)
            inner = f'<div class="grid-3 module-grid">{cards_html}</div>'
        else:
            inner = f'<p class="empty-state">{L["empty_mod"]}</p>'
        sections.append(
            f'<section class="module-section" id="mod-{mod}">'
            f'<div class="module-head">'
            f'<div class="module-head-text">'
            f'<span class="eyebrow">Module {mod}</span>'
            f'<h2>{md_inline(m["titre"])}</h2>'
            f'<p>{md_inline(m["sous_titre"])}</p>'
            f'</div>'
            f'<span class="module-count">{len(bucket)} {L["lesson_word"] if len(bucket) == 1 else L["lessons_word"]}</span>'
            f'</div>'
            f'{inner}'
            f'</section>'
        )

    return (
        f'{head}<body>'
        f'<a class="skip-link" href="#contenu">{L["skip"]}</a>'
        f'{header}'
        f'<main id="contenu">'
        f'<section class="page-hero"><div class="container">'
        f'<div class="breadcrumb">{L["breadcrumb"]}</div>'
        f'<span class="eyebrow">{html.escape(statut)}</span>'
        f'<h1>{md_inline(titre)}</h1>'
        f'{f"<p>{md_inline(sous_titre)}</p>" if sous_titre else ""}'
        f'{f"<p>{md_inline(description)}</p>" if description else ""}'
        f'</div></section>'
        f'<section class="section"><div class="container">'
        f'<h2>{html.escape(L["modules_title"])}</h2>'
        f'{progress_html}'
        f'{"".join(sections)}'
        f'<p style="margin-top:32px"><a class="text-link" href="../">{L["back"]}</a></p>'
        f'</div></section>'
        f'</main>{footer}</body></html>'
    )


# --- Main ------------------------------------------------------------------

def load_fiches() -> list[dict]:
    """Charge toutes les fiches *.yaml du dossier contenus/fiches.

    Une fiche est retenue si elle est un dict, qu'elle a un `id`, qu'elle
    est au statut `valide`, et qu'elle a des éditions FR ET EN.
    Le glob est ouvert à tous les motifs : lots futurs, piliers A/MF… inclus.
    """
    fiches = []
    seen_codes: set[str] = set()
    for fp in sorted(FICHES.glob("*.yaml")):
        try:
            with fp.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as exc:
            print(f"warning: fiche illisible {fp.name} : {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict):
            continue
        fid = data.get("id")
        if not fid:
            continue
        if data.get("validation", {}).get("statut") != "valide":
            continue
        ed = data.get("editions", {})
        if not ed.get("fr") or not ed.get("en"):
            continue
        # Les fiches « short » (TikTok/YouTube Shorts, 9:16) sont des extraits
        # dérivés d'une leçon. Elles ne produisent pas de page web dédiée :
        # elles existent comme média vertical rattaché à la leçon mère.
        fmt = str(data.get("format") or "").lower()
        if fmt == "short":
            continue
        code = module_code(fid)
        if code in seen_codes:
            print(f"warning: code {code} déjà vu (fiche en double : {fp.name})", file=sys.stderr)
            continue
        seen_codes.add(code)
        fiches.append({
            "data": data,
            "code": code,
            "module": module_of(code),
            "category": category_for(code),
            "ed_fr": ed["fr"],
            "ed_en": ed["en"],
        })
    return fiches


def load_parcours() -> list[dict]:
    fp = ROOT / "contenus" / "parcours.yaml"
    if not fp.exists():
        return []
    with fp.open(encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    parcours = raw.get("parcours", []) or []
    return sorted(parcours, key=lambda p: p.get("ordre", 999))


def _cleanup_orphans(valid_codes: set[str]) -> int:
    """Supprime les répertoires de leçon qui ne correspondent plus à une fiche
    valide (fiche supprimée, filtrée en `format: short`, renommée…).

    Retourne le nombre de répertoires retirés.
    """
    import shutil
    removed = 0
    for lesson_dir in (DOCS / "lecons").glob("*"):
        if lesson_dir.is_dir() and lesson_dir.name not in valid_codes:
            shutil.rmtree(lesson_dir)
            removed += 1
    for lesson_dir in (DOCS / "en" / "lessons").glob("*"):
        if lesson_dir.is_dir() and lesson_dir.name not in valid_codes:
            shutil.rmtree(lesson_dir)
            removed += 1
    return removed


# --- Pages de module -------------------------------------------------------
#
# Chaque module (M0, S1, S2, …) dispose de sa propre page, accessible depuis
# la page Programme et depuis chaque leçon du module. La page présente le
# module, liste ses leçons dans l'ordre, et pointe vers les parcours qui
# l'utilisent. C'est le chaînon manquant entre « Programme » (vue d'ensemble)
# et « Leçon » (détail d'une fiche) : il permet de parcourir un sujet
# complet sans passer par le programme global ni par la bibliothèque.


def _module_parcours(mod: str, parcours_list: list[dict]) -> list[dict]:
    return [p for p in (parcours_list or []) if mod in (p.get("modules") or [])]


def render_module_page(mod: str, lessons: list[dict], parcours_list: list[dict], lang: str) -> str:
    """Rend la page dédiée à un module donné."""
    meta = module_meta(mod, lang)
    is_fr = lang == "fr"
    base = "../../" if is_fr else "../../../"

    module_lessons = _module_lessons_sorted(mod, lessons)
    linked_parcours = _module_parcours(mod, parcours_list)

    L = {
        "fr": {
            "head_title": f"{mod} · {meta['titre']} · ACTU-BASICS",
            "head_desc": meta.get("sous_titre") or f"Le module {mod} du programme ACTU-BASICS.",
            "canon": f"https://johngab7.github.io/le-monde-en-chiffres/modules/{mod}/",
            "alt":   f"https://johngab7.github.io/le-monde-en-chiffres/en/modules/{mod}/",
            "og_locale": "fr_BE",
            "og_title": f"{mod} — {meta['titre']} · ACTU-BASICS",
            "og_desc": meta.get("sous_titre") or "",
            "skip": "Aller au contenu",
            "breadcrumb_home": "ACTU-BASICS",
            "breadcrumb_prog": "Programme",
            "breadcrumb_mod": "Module",
            "eyebrow": f"Module {mod}",
            "lessons_h": "Les leçons du module",
            "lessons_empty": "Les leçons de ce module seront ajoutées progressivement.",
            "parcours_h": "Parcours qui utilisent ce module",
            "nav_prev_mod": "Module précédent",
            "nav_next_mod": "Module suivant",
            "see_programme": "Voir tout le programme →",
        },
        "en": {
            "head_title": f"{mod} · {meta['titre']} · ACTU-BASICS",
            "head_desc": meta.get("sous_titre") or f"Module {mod} of the ACTU-BASICS programme.",
            "canon": f"https://johngab7.github.io/le-monde-en-chiffres/en/modules/{mod}/",
            "alt":   f"https://johngab7.github.io/le-monde-en-chiffres/modules/{mod}/",
            "og_locale": "en_US",
            "og_title": f"{mod} — {meta['titre']} · ACTU-BASICS",
            "og_desc": meta.get("sous_titre") or "",
            "skip": "Skip to content",
            "breadcrumb_home": "ACTU-BASICS",
            "breadcrumb_prog": "Programme",
            "breadcrumb_mod": "Module",
            "eyebrow": f"Module {mod}",
            "lessons_h": "Lessons in this module",
            "lessons_empty": "Lessons in this module will be added as they ship.",
            "parcours_h": "Learning paths that use this module",
            "nav_prev_mod": "Previous module",
            "nav_next_mod": "Next module",
            "see_programme": "See the full programme →",
        },
    }[lang]

    # Pour les liens précédent / suivant : on calcule l'ordre global.
    all_mods = sorted({m["module"] for m in lessons} | {mod}, key=module_sort_key)
    try:
        idx = all_mods.index(mod)
    except ValueError:
        idx = -1
    prev_mod = all_mods[idx - 1] if idx > 0 else None
    next_mod = all_mods[idx + 1] if 0 <= idx < len(all_mods) - 1 else None

    # Cartes de leçon dans l'ordre.
    lesson_cards = []
    for L_item in module_lessons:
        code = L_item["code"]
        ed = L_item["data"].get("editions", {}).get(lang, {})
        titre = ed.get("titre", code)
        legende = ed.get("legende", "")
        href = (f"{base}lecons/{code}/" if is_fr else f"{base}en/lessons/{code}/")
        lesson_cards.append(
            f'<a class="card lesson-card" href="{href}">'
            f'<span class="lesson-code">{code}</span>'
            f'<h3>{md_inline(titre)}</h3>'
            f'<p>{md_inline((legende or "").split(".")[0] + "." if legende else "")}</p>'
            f'<span class="text-link">{"Ouvrir →" if is_fr else "Open →"}</span>'
            f'</a>'
        )
    cards_html = "".join(lesson_cards) or (
        f'<p class="muted">{L["lessons_empty"]}</p>'
    )

    # Parcours liés.
    parcours_cards = []
    for p in linked_parcours:
        slug = p.get("slug", "")
        p_titre = (p.get("titre") or {}).get(lang) or slug
        p_desc = (p.get("sous_titre") or {}).get(lang) or ""
        href = (f"{base}parcours/{slug}/" if is_fr else f"{base}en/paths/{slug}/")
        parcours_cards.append(
            f'<a class="card path-card" href="{href}">'
            f'<h3>{html.escape(p_titre)}</h3>'
            f'<p>{html.escape(p_desc)}</p>'
            f'<span class="text-link">{"Voir le parcours →" if is_fr else "See path →"}</span>'
            f'</a>'
        )
    parcours_html = ""
    if parcours_cards:
        parcours_html = (
            f'<section class="section-tight"><div class="container">'
            f'<div class="section-head"><div>'
            f'<span class="eyebrow">{L["parcours_h"]}</span>'
            f'</div></div>'
            f'<div class="grid-{min(3, len(parcours_cards))}">{"".join(parcours_cards)}</div>'
            f'</div></section>'
        )

    # Navigation module précédent / suivant.
    nav_prev = ""
    nav_next = ""
    if prev_mod:
        href = f"{base}{'modules' if is_fr else 'en/modules'}/{prev_mod}/"
        p_meta = module_meta(prev_mod, lang)
        nav_prev = (
            f'<a class="module-nav-link module-nav-prev" href="{href}">'
            f'<span class="module-nav-label">← {L["nav_prev_mod"]}</span>'
            f'<span class="module-nav-title">{prev_mod} · {html.escape(p_meta["titre"])}</span>'
            f'</a>'
        )
    if next_mod:
        href = f"{base}{'modules' if is_fr else 'en/modules'}/{next_mod}/"
        n_meta = module_meta(next_mod, lang)
        nav_next = (
            f'<a class="module-nav-link module-nav-next" href="{href}">'
            f'<span class="module-nav-label">{L["nav_next_mod"]} →</span>'
            f'<span class="module-nav-title">{next_mod} · {html.escape(n_meta["titre"])}</span>'
            f'</a>'
        )
    module_nav = ""
    if nav_prev or nav_next:
        module_nav = (
            f'<section class="section-tight"><div class="container">'
            f'<nav class="module-nav" aria-label="Navigation des modules">'
            f'{nav_prev or "<span></span>"}{nav_next or "<span></span>"}'
            f'</nav></div></section>'
        )

    head = (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{html.escape(L["head_desc"])}">'
        f'<meta name="theme-color" content="#0f2130">'
        f'<link rel="canonical" href="{L["canon"]}">'
        f'<link rel="alternate" hreflang="fr" href="https://johngab7.github.io/le-monde-en-chiffres/modules/{mod}/">'
        f'<link rel="alternate" hreflang="en" href="https://johngab7.github.io/le-monde-en-chiffres/en/modules/{mod}/">'
        f'<link rel="alternate" hreflang="x-default" href="https://johngab7.github.io/le-monde-en-chiffres/modules/{mod}/">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="{L["og_locale"]}">'
        f'<meta property="og:title" content="{html.escape(L["og_title"])}">'
        f'<meta property="og:description" content="{html.escape(L["og_desc"])}">'
        f'<meta property="og:url" content="{L["canon"]}">'
        f'<meta name="twitter:card" content="summary">'
        f'<title>{html.escape(L["head_title"])}</title>'
        f'{_premium_head_assets(base)}'
        f'</head>'
    )

    header = (header_fr if is_fr else header_en)(
        depth=2 if is_fr else 3, current="programme"
    )
    footer = (footer_fr if is_fr else footer_en)(depth=2 if is_fr else 3)

    body = (
        f'<body>'
        f'<a class="skip-link" href="#contenu">{L["skip"]}</a>'
        f'{header}'
        f'<main id="contenu">'
        f'<section class="page-hero"><div class="container">'
        f'<div class="breadcrumb">'
        f'<a href="{base}{"index.html" if is_fr else "en/"}">{L["breadcrumb_home"]}</a> / '
        f'<a href="{base}{"programme" if is_fr else "en/programme"}/">{L["breadcrumb_prog"]}</a> / '
        f'{L["breadcrumb_mod"]} {mod}'
        f'</div>'
        f'<span class="eyebrow">{L["eyebrow"]}</span>'
        f'<h1>{html.escape(meta["titre"])}</h1>'
        f'<p>{html.escape(meta.get("sous_titre") or "")}</p>'
        f'<a class="text-link" href="{base}{"programme" if is_fr else "en/programme"}/">{L["see_programme"]}</a>'
        f'</div></section>'
        f'<section class="section"><div class="container">'
        f'<div class="section-head"><div>'
        f'<span class="eyebrow">{L["lessons_h"]}</span>'
        f'</div></div>'
        f'<div class="grid-3">{cards_html}</div>'
        f'</div></section>'
        f'{parcours_html}'
        f'{module_nav}'
        f'</main>{footer}</body></html>'
    )

    return head + body


# --- Page Programme --------------------------------------------------------
#
# Vue d'ensemble unique du programme ACTU-BASICS :
#   3 piliers (Fondations · Statistiques & Probabilités · Actuariat & Finance)
#   → 11 modules connus ou référencés
#   → les leçons disponibles de chaque module, et la mention « à venir » pour
#     les slots pédagogiques prévus mais non encore livrés.
#
# Le pilier n'est pas la catégorie d'une leçon : on regroupe ici par pilier
# pédagogique de haut niveau. Les modules suivants sont inclus même sans
# fiche : ils figurent au programme et montrent la trajectoire.

_PROGRAMME_PILLARS = [
    {
        "slug": "foundations",
        "modules": ["M0"],
        "fr": {
            "number": "I",
            "titre": "Fondations",
            "intro": "Les repères indispensables : lecture des chiffres, fractions, pourcentages, lecture d'un graphique.",
        },
        "en": {
            "number": "I",
            "titre": "Foundations",
            "intro": "The essentials: reading numbers, fractions, percentages, reading a chart.",
        },
    },
    {
        "slug": "stats-probas",
        "modules": ["S1", "S2", "S3", "S4"],
        "fr": {
            "number": "II",
            "titre": "Statistiques et probabilités",
            "intro": "Décrire les données, comparer, mesurer la dispersion, puis raisonner avec l'incertitude.",
        },
        "en": {
            "number": "II",
            "titre": "Statistics and probability",
            "intro": "Describe data, compare groups, measure spread, then reason under uncertainty.",
        },
    },
    {
        "slug": "actuariat-finance",
        "modules": ["A0", "A1", "A2", "A3", "MF1", "MF2"],
        "fr": {
            "number": "III",
            "titre": "Actuariat et mathématiques financières",
            "intro": "Du calcul actuariel au risque assurable, de l'actualisation aux produits financiers.",
        },
        "en": {
            "number": "III",
            "titre": "Actuarial science and financial mathematics",
            "intro": "Actuarial computation, insurable risk, discounting and financial products.",
        },
    },
]


def _lesson_title_for(code: str, lessons: list[dict], lang: str) -> str:
    for L in lessons:
        if L.get("code") == code:
            d = L.get("data", {})
            ed = d.get(f"edition_{lang}", {}) or d.get("edition_fr", {}) or {}
            t = ed.get("titre") or d.get("titre") or code
            return t if isinstance(t, str) else str(t)
    return code


def _module_lessons_sorted(mod: str, lessons: list[dict]) -> list[dict]:
    rows = [L for L in lessons if L.get("module") == mod]
    return sorted(rows, key=lambda L: L["code"])


def render_programme_page(parcours_list: list[dict], lessons: list[dict], lang: str) -> str:
    """Rend la page Programme : piliers → modules → leçons disponibles."""
    is_fr = lang == "fr"
    base = "../" if is_fr else "../../"
    header = (header_fr if is_fr else header_en)(
        depth=1 if is_fr else 2, current="programme"
    )
    footer = (footer_fr if is_fr else footer_en)(depth=1 if is_fr else 2)

    labels = {
        "fr": {
            "head_title": "Programme · ACTU-BASICS",
            "head_desc": "Le programme complet d'ACTU-BASICS : trois piliers, onze modules, quarante-cinq leçons.",
            "canon": "https://johngab7.github.io/le-monde-en-chiffres/programme/",
            "alt":   "https://johngab7.github.io/le-monde-en-chiffres/en/programme/",
            "og_locale": "fr_BE",
            "og_title": "Programme · ACTU-BASICS",
            "og_desc": "Le programme complet en un coup d'œil.",
            "skip": "Aller au contenu",
            "breadcrumb_home": "ACTU-BASICS",
            "breadcrumb_here": "Programme",
            "eyebrow": "Le programme en un coup d'œil",
            "h1": "Le programme.",
            "lead": "Trois piliers, onze modules, une trentaine de leçons livrées, le reste en préparation. Chaque ligne mène à ce qui est disponible ; les slots gris sont au programme et arriveront.",
            "lesson_label": "leçons",
            "status_available": "Disponible",
            "status_partial": "Partiel",
            "status_soon": "À venir",
            "lessons_soon": "Prochaines leçons",
            "see_module": "Voir le module →",
        },
        "en": {
            "head_title": "Programme · ACTU-BASICS",
            "head_desc": "The complete ACTU-BASICS programme: three pillars, eleven modules, forty-five lessons.",
            "canon": "https://johngab7.github.io/le-monde-en-chiffres/en/programme/",
            "alt":   "https://johngab7.github.io/le-monde-en-chiffres/programme/",
            "og_locale": "en_US",
            "og_title": "Programme · ACTU-BASICS",
            "og_desc": "The complete programme at a glance.",
            "skip": "Skip to content",
            "breadcrumb_home": "ACTU-BASICS",
            "breadcrumb_here": "Programme",
            "eyebrow": "The programme at a glance",
            "h1": "The programme.",
            "lead": "Three pillars, eleven modules, around thirty lessons shipped, more in the works. Each row links to what is available; greyed slots are on the roadmap.",
            "lesson_label": "lessons",
            "status_available": "Available",
            "status_partial": "Partial",
            "status_soon": "Coming",
            "lessons_soon": "Upcoming lessons",
            "see_module": "See module →",
        },
    }[lang]

    # Ensemble des modules effectivement couverts dans les parcours ou ayant
    # des leçons, pour détecter ceux en dehors des piliers connus.
    modules_with_lessons = {L["module"] for L in lessons}

    pillar_cards = []
    pillar_sections = []

    for pillar in _PROGRAMME_PILLARS:
        p = pillar[lang]
        modules = pillar["modules"]
        # carte d'introduction (pilier)
        pillar_cards.append(
            f'<article class="pillar">'
            f'<div class="pillar-number">{p["number"]}</div>'
            f'<h2>{html.escape(p["titre"])}</h2>'
            f'<p>{html.escape(p["intro"])}</p>'
            f'</article>'
        )

        rows = []
        for mod in modules:
            meta = module_meta(mod, lang)
            lesson_rows = _module_lessons_sorted(mod, lessons)
            total_slots = len(lesson_rows)  # on ne connaît pas plus ici
            if not lesson_rows:
                status = "soon"
                status_label = labels["status_soon"]
            elif total_slots >= 4:
                status = "available"
                status_label = f"{labels['status_available']} · {total_slots} {labels['lesson_label']}"
            else:
                status = "partial"
                status_label = f"{labels['status_partial']} · {total_slots} {labels['lesson_label']}"

            chips = []
            for L in lesson_rows:
                code = L["code"]
                href = (f"{base}lecons/{code}/" if is_fr else f"{base}en/lessons/{code}/")
                title = _lesson_title_for(code, lessons, lang)
                # ne pas tout afficher en gros : chip courte = code, titre en attribut
                chips.append(
                    f'<a href="{href}" title="{html.escape(title)}">{code}</a>'
                )
            if not lesson_rows:
                chips.append(
                    f'<span class="lesson-upcoming">{labels["lessons_soon"]}</span>'
                )
            chips_html = "".join(chips)

            mod_href = f'{base}{"modules" if is_fr else "en/modules"}/{mod}/'
            rows.append(
                f'<div class="module-row" data-module="{mod}">'
                f'<a class="module-code" href="{mod_href}">{mod}</a>'
                f'<a class="module-title" href="{mod_href}">{html.escape(meta["titre"])}'
                f'<small>{html.escape(meta.get("sous_titre") or "")}</small></a>'
                f'<div class="module-lessons">{chips_html}</div>'
                f'<div class="module-status {status}">{html.escape(status_label)}</div>'
                f'</div>'
            )

        pillar_sections.append(
            f'<section class="programme-pillar" id="pillar-{pillar["slug"]}">'
            f'<div class="programme-pillar-head">'
            f'<h2>{p["number"]}. {html.escape(p["titre"])}</h2>'
            f'<p>{html.escape(p["intro"])}</p>'
            f'</div>'
            f'<div class="programme-modules-list">'
            f'{"".join(rows)}'
            f'</div>'
            f'</section>'
        )

    # Modules présents dans les fiches mais hors piliers connus → section "autres"
    known_mods = {m for pillar in _PROGRAMME_PILLARS for m in pillar["modules"]}
    orphans = sorted(modules_with_lessons - known_mods, key=module_sort_key)
    if orphans:
        rows = []
        for mod in orphans:
            meta = module_meta(mod, lang)
            lesson_rows = _module_lessons_sorted(mod, lessons)
            chips = "".join(
                f'<a href="{base}{"lecons" if is_fr else "en/lessons"}/{L["code"]}/">{L["code"]}</a>'
                for L in lesson_rows
            )
            mod_href = f'{base}{"modules" if is_fr else "en/modules"}/{mod}/'
            rows.append(
                f'<div class="module-row" data-module="{mod}">'
                f'<a class="module-code" href="{mod_href}">{mod}</a>'
                f'<a class="module-title" href="{mod_href}">{html.escape(meta["titre"])}'
                f'<small>{html.escape(meta.get("sous_titre") or "")}</small></a>'
                f'<div class="module-lessons">{chips}</div>'
                f'<div class="module-status partial">{len(lesson_rows)} {labels["lesson_label"]}</div>'
                f'</div>'
            )
        if is_fr:
            other_title, other_intro = "Modules complémentaires", "D'autres modules déjà commencés, qui trouveront leur place dans un pilier au fil des parutions."
        else:
            other_title, other_intro = "Additional modules", "Other modules already in motion; they will slot into a pillar as content ships."
        pillar_sections.append(
            f'<section class="programme-pillar">'
            f'<div class="programme-pillar-head">'
            f'<h2>+. {html.escape(other_title)}</h2>'
            f'<p>{html.escape(other_intro)}</p>'
            f'</div>'
            f'<div class="programme-modules-list">{"".join(rows)}</div>'
            f'</section>'
        )

    head = (
        f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{html.escape(labels["head_desc"])}">'
        f'<meta name="theme-color" content="#0f2130">'
        f'<link rel="canonical" href="{labels["canon"]}">'
        f'<link rel="alternate" hreflang="fr" href="https://johngab7.github.io/le-monde-en-chiffres/programme/">'
        f'<link rel="alternate" hreflang="en" href="https://johngab7.github.io/le-monde-en-chiffres/en/programme/">'
        f'<link rel="alternate" hreflang="x-default" href="https://johngab7.github.io/le-monde-en-chiffres/programme/">'
        f'<meta property="og:type" content="website">'
        f'<meta property="og:locale" content="{labels["og_locale"]}">'
        f'<meta property="og:title" content="{html.escape(labels["og_title"])}">'
        f'<meta property="og:description" content="{html.escape(labels["og_desc"])}">'
        f'<meta property="og:url" content="{labels["canon"]}">'
        f'<meta name="twitter:card" content="summary">'
        f'<title>{html.escape(labels["head_title"])}</title>'
        f'{_premium_head_assets(base)}'
        f'</head>'
    )

    body = (
        f'<body>'
        f'<a class="skip-link" href="#contenu">{labels["skip"]}</a>'
        f'{header}'
        f'<main id="contenu">'
        f'<section class="programme-hero"><div class="container">'
        f'<div class="breadcrumb">'
        f'<a href="{base}{"index.html" if is_fr else "en/"}">{labels["breadcrumb_home"]}</a> / {labels["breadcrumb_here"]}'
        f'</div>'
        f'<span class="eyebrow">{labels["eyebrow"]}</span>'
        f'<h1>{labels["h1"]}</h1>'
        f'<p class="lead">{labels["lead"]}</p>'
        f'<div class="pillars">{"".join(pillar_cards)}</div>'
        f'</div></section>'
        f'<section class="section"><div class="container">'
        f'{"".join(pillar_sections)}'
        f'</div></section>'
        f'</main>{footer}</body></html>'
    )

    return head + body


# --- Page Design System (référence interne) ------------------------------
#
# Expose les tokens clés (couleurs, typographie, échelles d'espace) et une
# galerie des composants premium. Sert de vitrine ET de contrat : si la
# page rend mal, c'est que la token-sheet a dérivé.

def render_design_system_page() -> str:
    swatches = [
        ("Ink", "--ink", "Texte principal"),
        ("Paper", "--paper", "Fond général"),
        ("Surface", "--surface", "Cartes, panneaux"),
        ("Teal", "--teal", "Accent de marque"),
        ("Gold", "--gold", "Accent chaud"),
        ("Muted", "--muted", "Texte adouci"),
        ("Line", "--line", "Séparateurs"),
        ("Success", "--success", "États OK"),
        ("Warn", "--warn", "Alertes"),
    ]
    swatch_html = "".join(
        f'<div class="ds-swatch">'
        f'<div class="ds-swatch-sample" style="background:var({var});"></div>'
        f'<div class="ds-swatch-meta"><strong>{name}</strong>{var} · {note}</div>'
        f'</div>'
        for (name, var, note) in swatches
    )

    type_samples = [
        ("Display · 6.2rem", "--size-display", "Un chiffre dit l'essentiel."),
        ("H1 · 4rem",         "--size-h1",       "Les chiffres racontent."),
        ("H2 · 2.6rem",       "--size-h2",       "Lire sans se faire avoir."),
        ("H3 · 1.35rem",      "--size-h3",       "Une section de leçon."),
        ("Lead · 1.32rem",    "--size-lead",     "Un paragraphe d'ouverture, posé."),
        ("Body · 1.02rem",    "--size-body",     "Le texte courant d'une leçon."),
        ("Small · .88rem",    "--size-small",    "Mention secondaire."),
    ]
    type_html = "".join(
        f'<div class="ds-type-sample">'
        f'<small>{label} · {var}</small>'
        f'<div style="font-family:var(--font-serif);font-weight:400;font-size:var({var});letter-spacing:-.04em;line-height:1.1;">{html.escape(text)}</div>'
        f'</div>'
        for (label, var, text) in type_samples
    )

    tokens_table = (
        '<table class="ds-token-table"><thead><tr>'
        '<th>Token</th><th>Rôle</th></tr></thead><tbody>'
        '<tr><td>--radius-s/m/l/xl</td><td>Rayons : 10 / 18 / 24 / 36 px</td></tr>'
        '<tr><td>--space-1..10</td><td>Grille 4/8/12/16/24/32/48/64/96/128 px</td></tr>'
        '<tr><td>--shadow-s/m/l</td><td>Ombres éditoriales chaudes</td></tr>'
        '<tr><td>--dur-s/m/l + --ease</td><td>Durées animation + courbe .2,.8,.2,1</td></tr>'
        '<tr><td>--measure</td><td>Limite typographique : 70ch</td></tr>'
        '</tbody></table>'
    )

    head = (
        '<!doctype html><html lang="fr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="description" content="Référence du design system ACTU-BASICS : tokens, typographie, composants.">'
        '<meta name="theme-color" content="#0f2130">'
        '<meta name="robots" content="noindex,follow">'
        '<title>Design System · ACTU-BASICS</title>'
        f'{_premium_head_assets("../../")}'
        '</head>'
    )
    return (
        f'{head}<body>'
        f'<a class="skip-link" href="#contenu">Aller au contenu</a>'
        f'{header_fr(depth=2)}'
        f'<main id="contenu">'
        f'<section class="programme-hero"><div class="container">'
        f'<div class="breadcrumb"><a href="../../index.html">ACTU-BASICS</a> / Technique / Design system</div>'
        f'<span class="eyebrow">Référence interne</span>'
        f'<h1>Le design system.</h1>'
        f'<p class="lead">La source de vérité visuelle : couleurs, typographie, échelles. Tout le site se sert exclusivement de ces variables CSS ; aucun hexadécimal n\'est écrit à la main.</p>'
        f'</div></section>'
        f'<section class="section"><div class="container">'
        f'<div class="ds-section"><h2>Couleurs</h2><div class="ds-grid">{swatch_html}</div></div>'
        f'<div class="ds-section"><h2>Typographie</h2>{type_html}</div>'
        f'<div class="ds-section"><h2>Jetons structurels</h2>{tokens_table}</div>'
        f'<div class="ds-section"><h2>Composants</h2>'
        f'<div class="grid-3">'
        f'<article class="card"><div class="card-top"><span class="icon-tile">∑</span><span class="tag">Carte</span></div><h3>Une carte standard</h3><p>Fond surface, ombre douce, radius-l. Au survol, elle monte de 3 px.</p></article>'
        f'<article class="card"><div class="card-top"><span class="icon-tile">✓</span><span class="tag">Tag</span></div><h3>Un tag éditorial</h3><p>Pastille teal, bordure teintée ; sert à qualifier un module ou un niveau.</p></article>'
        f'<article class="card"><div class="card-top"><span class="icon-tile">▶</span><span class="tag">Action</span></div><h3>Bouton primary</h3><p><a class="button button-primary" href="#">Voir un exemple</a></p></article>'
        f'</div></div>'
        f'<div class="ds-section"><h2>Bloc À retenir</h2>'
        f'<aside class="lesson-takeaway"><strong>À retenir</strong><p>Chaque composant du site se résume en une seule intention : rendre un sens exact plus lisible.</p></aside>'
        f'</div>'
        f'</div></section>'
        f'</main>{footer_fr(depth=2)}</body></html>'
    )


def main() -> int:
    fiches = load_fiches()
    if not fiches:
        sys.exit("Aucune fiche valide trouvée dans contenus/fiches/")
    parcours_list = load_parcours()

    # Retire d'abord les pages leçons orphelines (fiches retirées, filtrées
    # ou renommées) pour éviter tout page orpheline servie sur le site.
    valid_codes = {L["code"] for L in fiches}
    orphans_removed = _cleanup_orphans(valid_codes)

    pages = 0
    for L in fiches:
        code = L["code"]
        fr_dir = DOCS / "lecons" / code
        en_dir = DOCS / "en" / "lessons" / code
        fr_dir.mkdir(parents=True, exist_ok=True)
        en_dir.mkdir(parents=True, exist_ok=True)
        (fr_dir / "index.html").write_text(
            render_lesson_page(L["data"], "fr", parcours_list), encoding="utf-8"
        )
        (en_dir / "index.html").write_text(
            render_lesson_page(L["data"], "en", parcours_list), encoding="utf-8"
        )
        pages += 2

    # Plus de fiche manuelle hardcodée : A0-01 est désormais fourni par un YAML.
    lessons_for_lib = sorted(fiches, key=lambda x: x["code"])

    (DOCS / "bibliotheque" / "index.html").write_text(
        render_library_page(lessons_for_lib, "fr"), encoding="utf-8"
    )
    (DOCS / "en" / "library" / "index.html").write_text(
        render_library_page(lessons_for_lib, "en"), encoding="utf-8"
    )

    # Pages parcours : index + une page par parcours.
    parcours_pages = 0
    if parcours_list:
        (DOCS / "parcours").mkdir(parents=True, exist_ok=True)
        (DOCS / "en" / "paths").mkdir(parents=True, exist_ok=True)
        (DOCS / "parcours" / "index.html").write_text(
            render_parcours_index(parcours_list, lessons_for_lib, "fr"), encoding="utf-8"
        )
        (DOCS / "en" / "paths" / "index.html").write_text(
            render_parcours_index(parcours_list, lessons_for_lib, "en"), encoding="utf-8"
        )
        parcours_pages += 2
        for p in parcours_list:
            slug = p.get("slug", "")
            if not slug:
                continue
            fr_dir = DOCS / "parcours" / slug
            en_dir = DOCS / "en" / "paths" / slug
            fr_dir.mkdir(parents=True, exist_ok=True)
            en_dir.mkdir(parents=True, exist_ok=True)
            (fr_dir / "index.html").write_text(
                render_parcours_detail(p, lessons_for_lib, "fr"), encoding="utf-8"
            )
            (en_dir / "index.html").write_text(
                render_parcours_detail(p, lessons_for_lib, "en"), encoding="utf-8"
            )
            parcours_pages += 2

    # Page Programme (vue d'ensemble unique du cursus) : FR + EN.
    (DOCS / "programme").mkdir(parents=True, exist_ok=True)
    (DOCS / "en" / "programme").mkdir(parents=True, exist_ok=True)
    (DOCS / "programme" / "index.html").write_text(
        render_programme_page(parcours_list, lessons_for_lib, "fr"), encoding="utf-8"
    )
    (DOCS / "en" / "programme" / "index.html").write_text(
        render_programme_page(parcours_list, lessons_for_lib, "en"), encoding="utf-8"
    )

    # Pages de module : une page par M0, S1, A1… en FR et EN.
    # On couvre tous les modules référencés par les piliers du programme ET
    # les modules qui ont au moins une leçon publiée (dont ceux hors piliers,
    # comme Q3, listés en « modules autonomes »).
    pillar_mods = {m for p in _PROGRAMME_PILLARS for m in p["modules"]}
    lesson_mods = {L["module"] for L in lessons_for_lib}
    all_modules = sorted(pillar_mods | lesson_mods, key=module_sort_key)
    module_pages = 0
    for mod in all_modules:
        fr_dir = DOCS / "modules" / mod
        en_dir = DOCS / "en" / "modules" / mod
        fr_dir.mkdir(parents=True, exist_ok=True)
        en_dir.mkdir(parents=True, exist_ok=True)
        (fr_dir / "index.html").write_text(
            render_module_page(mod, lessons_for_lib, parcours_list, "fr"),
            encoding="utf-8",
        )
        (en_dir / "index.html").write_text(
            render_module_page(mod, lessons_for_lib, parcours_list, "en"),
            encoding="utf-8",
        )
        module_pages += 2

    # Page de référence du design system (tokens + composants).
    (DOCS / "technique").mkdir(parents=True, exist_ok=True)
    (DOCS / "technique" / "design-system" / "index.html").parent.mkdir(exist_ok=True)
    (DOCS / "technique" / "design-system" / "index.html").write_text(
        render_design_system_page(), encoding="utf-8"
    )

    print(f"Fiches valides   : {len(fiches)}")
    print(f"Pages écrites    : {pages} (leçons FR + EN)")
    print(f"Orphelines ôtées : {orphans_removed} (répertoires sans fiche valide)")
    print(f"Bibliothèques    : FR + EN mises à jour ({len(lessons_for_lib)} leçons affichées)")
    print(f"Pages parcours   : {parcours_pages} (index + détails, FR + EN)")
    print(f"Programme        : FR + EN générée")
    print(f"Pages de module  : {module_pages} ({len(all_modules)} modules × FR + EN)")
    print(f"Design system    : page de référence générée")
    return 0


if __name__ == "__main__":
    sys.exit(main())
