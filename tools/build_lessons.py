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
        ys = [p[1] for p in pts]
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
        f'<svg class="courbe-svg" viewBox="0 0 {W} {H}" '
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
        f'<link rel="stylesheet" href="{base}assets/css/main.css">'
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
        f'<link rel="stylesheet" href="{base}assets/css/main.css">'
        f'{_katex_head()}'
        f'</head>'
    )


def header_fr(depth: int, current: str = "") -> str:
    b = "../" * depth
    def cls(name): return ' aria-current="page"' if current == name else " "
    return (
        f'<header class="site-header"><div class="nav-wrap">'
        f'<a class="brand" href="{b}index.html" aria-label="ACTU-BASICS">'
        f'<img src="{b}assets/img/logo-light.png" alt="ACTU-BASICS" '
        f'onerror="this.style.display=\'none\';this.insertAdjacentHTML(\'afterend\',\'<span class=&quot;brand-fallback&quot;>ACTU-BASICS</span>\')">'
        f'</a>'
        f'<nav id="site-navigation" class="nav-links" aria-label="Navigation principale">'
        f'<a href="{b}parcours/"{cls("parcours")}>Parcours</a>'
        f'<a href="{b}bibliotheque/"{cls("bibliotheque")}>Bibliothèque</a>'
        f'<a href="{b}a-propos/"{cls("apropos")}>À propos</a>'
        f'</nav>'
        f'<div class="nav-actions">'
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
        f'<img src="{b}assets/img/logo-light-en.png" alt="ACTU-BASICS" '
        f'onerror="this.style.display=\'none\';this.insertAdjacentHTML(\'afterend\',\'<span class=&quot;brand-fallback&quot;>ACTU-BASICS</span>\')">'
        f'</a>'
        f'<nav id="site-navigation" class="nav-links" aria-label="Main navigation">'
        f'<a href="{b}en/paths/"{cls("paths")}>Learning paths</a>'
        f'<a href="{b}en/library/"{cls("library")}>Library</a>'
        f'<a href="{b}en/about/"{cls("about")}>About</a>'
        f'</nav>'
        f'<div class="nav-actions">'
        f'<a class="lang" href="{b}index.html" lang="fr" aria-label="Passer en français">FR</a>'
        f'<button class="menu-toggle" type="button" aria-controls="site-navigation" aria-expanded="false" aria-label="Open menu">☰</button>'
        f'</div></div></header>'
    )


def footer_fr(depth: int) -> str:
    b = "../" * depth
    return (
        f'<footer class="footer"><div class="footer-inner">'
        f'<div><h3>ACTU-BASICS</h3>'
        f'<p>Éveiller par les chiffres. Comprendre les méthodes derrière les résultats.</p>'
        f'<p>Un projet éducatif indépendant consacré aux statistiques, aux probabilités et à l\'actuariat.</p></div>'
        f'<div><h3>Explorer</h3><div class="footer-links">'
        f'<a href="{b}parcours/">Parcours</a>'
        f'<a href="{b}bibliotheque/">Bibliothèque</a>'
        f'<a href="{b}a-propos/">À propos</a>'
        f'</div></div>'
        f'<div><h3>Retrouver les vidéos</h3><div class="footer-links">'
        f'<a href="https://www.youtube.com/channel/UC3MrzU4G6UnSfDsYSci9BuQ" target="_blank" rel="noopener">YouTube · Français ↗</a>'
        f'<a href="https://www.youtube.com/channel/UC9AkR6xNGl9S9XHuFnbFCGg" target="_blank" rel="noopener">YouTube · English ↗</a>'
        f'<a href="https://www.tiktok.com/@actu_basics_fr" target="_blank" rel="noopener">TikTok · Français ↗</a>'
        f'<a href="https://www.tiktok.com/@actu_basics" target="_blank" rel="noopener">TikTok · English ↗</a>'
        f'<a href="https://github.com/JohnGAB7/le-monde-en-chiffres" target="_blank" rel="noopener">GitHub ↗</a>'
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
        f'<a href="{b}en/paths/">Learning paths</a>'
        f'<a href="{b}en/library/">Library</a>'
        f'<a href="{b}en/about/">About</a>'
        f'</div></div>'
        f'<div><h3>Watch the videos</h3><div class="footer-links">'
        f'<a href="https://www.youtube.com/channel/UC3MrzU4G6UnSfDsYSci9BuQ" target="_blank" rel="noopener">YouTube · Français ↗</a>'
        f'<a href="https://www.youtube.com/channel/UC9AkR6xNGl9S9XHuFnbFCGg" target="_blank" rel="noopener">YouTube · English ↗</a>'
        f'<a href="https://www.tiktok.com/@actu_basics_fr" target="_blank" rel="noopener">TikTok · Français ↗</a>'
        f'<a href="https://www.tiktok.com/@actu_basics" target="_blank" rel="noopener">TikTok · English ↗</a>'
        f'<a href="https://github.com/JohnGAB7/le-monde-en-chiffres" target="_blank" rel="noopener">GitHub ↗</a>'
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

    lesson_section = (
        f'<section class="section"><div class="container lesson-layout">'
        f'<article class="lesson-content">'
        f'{video_block}'
        f'{obj_block}{pre_block}'
        f'{scene_html}'
        f'{hyp_block}'
        f'</article>'
        f'<aside class="lesson-aside">'
        f'<span class="tag">{L["tag_available"]}</span>'
        f'<h3>{L["at_a_glance"]}</h3>'
        f'<p><strong>Code</strong><br>{code}</p>'
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
            '<link rel="stylesheet" href="../assets/css/main.css"></head>'
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
            '<link rel="stylesheet" href="../../assets/css/main.css"></head>'
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
            "css": "../assets/css/main.css",
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
            "css": "../../assets/css/main.css",
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
        f'<link rel="stylesheet" href="{L["css"]}"></head>'
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
            "css": "../../assets/css/main.css",
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
            "css": "../../../assets/css/main.css",
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
        f'<link rel="stylesheet" href="{L["css"]}"></head>'
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

    print(f"Fiches valides   : {len(fiches)}")
    print(f"Pages écrites    : {pages} (leçons FR + EN)")
    print(f"Orphelines ôtées : {orphans_removed} (répertoires sans fiche valide)")
    print(f"Bibliothèques    : FR + EN mises à jour ({len(lessons_for_lib)} leçons affichées)")
    print(f"Pages parcours   : {parcours_pages} (index + détails, FR + EN)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
