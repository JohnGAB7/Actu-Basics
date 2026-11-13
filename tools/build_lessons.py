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
}
CATEGORY_LABELS_EN = {
    "fondations":    "Foundations",
    "statistiques":  "Statistics",
    "probabilites":  "Probability",
    "actuariat":     "Actuarial science",
    "finance":       "Financial mathematics",
}

# Ordre et libellés des modules (préfixe du code -> module).
MODULE_ORDER = ["M0", "S1", "S2", "S3", "S4", "A0"]

MODULE_META_FR = {
    "M0": {
        "titre": "Fondations",
        "sous_titre": "Rappels mathématiques pour démarrer en confiance.",
        "category": "fondations",
    },
    "S1": {
        "titre": "Statistiques · lire un chiffre",
        "sous_titre": "Vocabulaire, pourcentages, lecture des chiffres du quotidien.",
        "category": "statistiques",
    },
    "S2": {
        "titre": "Statistiques · indicateurs",
        "sous_titre": "Moyennes, médianes, taux et comparaisons entre groupes.",
        "category": "statistiques",
    },
    "S3": {
        "titre": "Statistiques · séries et dispersion",
        "sous_titre": "Écart-type, séries chronologiques et interprétation des graphiques.",
        "category": "statistiques",
    },
    "S4": {
        "titre": "Probabilités",
        "sous_titre": "Événements, indépendance, probabilités conditionnelles.",
        "category": "probabilites",
    },
    "A0": {
        "titre": "Actuariat · premiers pas",
        "sous_titre": "Métier d'actuaire, risque, prime pure.",
        "category": "actuariat",
    },
}

MODULE_META_EN = {
    "M0": {
        "titre": "Foundations",
        "sous_titre": "A math refresher to start with confidence.",
        "category": "fondations",
    },
    "S1": {
        "titre": "Statistics · reading numbers",
        "sous_titre": "Vocabulary, percentages, making sense of everyday numbers.",
        "category": "statistiques",
    },
    "S2": {
        "titre": "Statistics · indicators",
        "sous_titre": "Averages, medians, rates and group comparisons.",
        "category": "statistiques",
    },
    "S3": {
        "titre": "Statistics · series and spread",
        "sous_titre": "Standard deviation, time series and chart interpretation.",
        "category": "statistiques",
    },
    "S4": {
        "titre": "Probability",
        "sous_titre": "Events, independence, conditional probability.",
        "category": "probabilites",
    },
    "A0": {
        "titre": "Actuarial science · first steps",
        "sous_titre": "The actuary's role, risk, pure premium.",
        "category": "actuariat",
    },
}


def module_of(code: str) -> str:
    """M0-01 -> M0 ; S4-07 -> S4 ; A0-01 -> A0."""
    low = code.lower()
    if low.startswith("m0"):
        return "M0"
    if low.startswith("s1"):
        return "S1"
    if low.startswith("s2"):
        return "S2"
    if low.startswith("s3"):
        return "S3"
    if low.startswith("s4"):
        return "S4"
    if low.startswith("a"):
        return "A0"
    return "M0"


def module_code(fiche_id: str) -> str:
    """Extrait le code module d'un id fiche. 2026-11-n1-s2-04-xxx -> S2-04."""
    m = re.match(r"2026-\d+-n1-([a-z0-9]+-\d+)-", fiche_id)
    if m:
        return m.group(1).upper()
    m = re.match(r"2026-\d+-act-(a\d+-\d+)-", fiche_id)
    if m:
        return m.group(1).upper()
    return fiche_id.upper()


def category_for(code: str) -> str:
    low = code.lower()
    if low.startswith("m0"):
        return "fondations"
    if low.startswith("s1") or low.startswith("s2") or low.startswith("s3"):
        return "statistiques"
    if low.startswith("s4"):
        return "probabilites"
    if low.startswith("a"):
        return "actuariat"
    return "statistiques"


# --- Rendu Markdown léger -> HTML ------------------------------------------

def md_inline(text: str) -> str:
    """Rend l'emphase *...* en <em>, échappe le reste."""
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


# --- Rendu d'une scène ------------------------------------------------------

def render_scene(s: dict, lang: str) -> str:
    """Convertit une scène YAML en un fragment HTML."""
    if not isinstance(s, dict):
        return ""
    t = s.get("type", "")
    parts: list[str] = []

    texte = s.get("texte", "")
    voix = s.get("voix_off", "")
    etapes = s.get("etapes") or []
    formule = s.get("formule")
    etiquette = s.get("etiquette", "")
    reponse = s.get("reponse", "")
    note = s.get("note", "")
    prefixe = s.get("prefixe", "")
    suffixe = s.get("suffixe", "")
    valeur = s.get("valeur", "")

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
            # LaTeX brut en V1.1 ; KaTeX viendra dans une étape ultérieure.
            parts.append(f'<div class="formula"><code>{html.escape(str(raw))}</code></div>')
        return "".join(parts)

    if t == "courbe":
        if texte:
            parts.append(f"<h3>{md_inline(texte)}</h3>")
        if voix:
            parts.append(f"<p>{md_inline(voix)}</p>")
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
        parts.append(md_items(etapes))
        return "".join(parts)

    # fallback
    if texte:
        parts.append(f"<p><strong>{md_inline(texte)}</strong></p>")
    if voix:
        parts.append(f"<p>{md_inline(voix)}</p>")
    return "".join(parts)


# --- Templates HTML --------------------------------------------------------

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


# --- Page leçon ------------------------------------------------------------

def render_lesson_page(data: dict, lang: str) -> str:
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

    lesson_section = (
        f'<section class="section"><div class="container lesson-layout">'
        f'<article class="lesson-content">'
        f'{obj_block}{pre_block}'
        f'{scene_html}'
        f'{hyp_block}'
        f'</article>'
        f'<aside class="lesson-aside">'
        f'<span class="tag">{L["tag_available"]}</span>'
        f'<h3>{L["at_a_glance"]}</h3>'
        f'<p><strong>Code</strong><br>{code}</p>'
        f'<a class="button button-dark" href="{L["lib_href"]}">{L["lib_back"]}</a>'
        f'<a class="button button-outline" href="{L["other_lang_href"]}">{L["other_lang_label"]}</a>'
        f'</aside></div></section>'
    )

    return (
        f'{head}<body>'
        f'<a class="skip-link" href="#contenu">{L["skip"]}</a>'
        f'{header}'
        f'<main id="contenu">{page_hero}{lesson_section}</main>'
        f'{footer}</body></html>'
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


def build_lesson_card(L: dict, lang: str) -> str:
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
    path = f"../lecons/{code}/" if lang == "fr" else f"../lessons/{code}/"
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

    badges = (
        f'<span class="badge badge-level">{html.escape(niveau)}</span>'
        f'<span class="badge badge-prereq">{html.escape(prereq_label)}</span>'
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
    """Regroupe par module avec en-têtes et compte."""
    by_mod: dict[str, list[dict]] = {m: [] for m in MODULE_ORDER}
    for L in lessons:
        by_mod.setdefault(L["module"], []).append(L)

    meta = MODULE_META_FR if lang == "fr" else MODULE_META_EN
    lessons_word = ("leçon", "leçons") if lang == "fr" else ("lesson", "lessons")
    module_word = "Module" if lang == "fr" else "Module"

    out = []
    for mod in MODULE_ORDER:
        bucket = by_mod.get(mod) or []
        if not bucket:
            continue
        bucket = sorted(bucket, key=lambda x: x["code"])
        m = meta.get(mod, {"titre": mod, "sous_titre": "", "category": "statistiques"})
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


def build_parcours_overview(lessons: list[dict], lang: str) -> str:
    by_mod: dict[str, int] = {}
    for L in lessons:
        by_mod[L["module"]] = by_mod.get(L["module"], 0) + 1

    meta = MODULE_META_FR if lang == "fr" else MODULE_META_EN
    title_fr = "Parcours"
    title_en = "Learning path"
    jump_label_fr = "Aller au module"
    jump_label_en = "Jump to module"

    items = []
    for i, mod in enumerate([m for m in MODULE_ORDER if by_mod.get(m)], start=1):
        count = by_mod[mod]
        m = meta.get(mod, {"titre": mod})
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
    overview_sub = (
        "Un fil pédagogique : chaque module prépare le suivant."
        if lang == "fr"
        else "A learning thread: each module leads into the next."
    )
    return (
        f'<section class="parcours-overview" aria-label="{html.escape(overview_title)}">'
        f'<div class="parcours-head">'
        f'<span class="eyebrow">{html.escape(overview_title)}</span>'
        f'<p class="muted">{html.escape(overview_sub)}</p>'
        f'</div>'
        f'<div class="parcours-steps">{"".join(items)}</div>'
        f'</section>'
    )


def render_library_page(lessons: list[dict], lang: str) -> str:
    cards_html = build_library_cards(lessons, lang)
    cats_in_use = sorted({L["category"] for L in lessons})
    cat_labels = CATEGORY_LABELS_FR if lang == "fr" else CATEGORY_LABELS_EN
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
        f'<div class="catalog-tools">'
        f'<label class="skip-link" for="search-{lang}">{search_label}</label>'
        f'<input id="search-{lang}" class="search-input" type="search" placeholder="{html.escape(search_placeholder)}" data-search>'
        f'<label class="skip-link" for="filter-{lang}">{filter_label}</label>'
        f'<select id="filter-{lang}" class="filter-select" data-filter>{"".join(options)}</select>'
        f'</div>'
        f'<div class="grid-3">{cards_html}</div>'
        f'<p class="empty-state" data-empty role="status" aria-live="polite" hidden>{empty_msg}</p>'
        f'</div></section>'
        f'</main>{footer}</body></html>'
    )


# --- Main ------------------------------------------------------------------

def load_fiches() -> list[dict]:
    fiches = []
    for fp in sorted(FICHES.glob("2026-11-n1-*.yaml")):
        with fp.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            continue
        if data.get("validation", {}).get("statut") != "valide":
            continue
        if not data.get("editions", {}).get("fr") or not data.get("editions", {}).get("en"):
            continue
        code = module_code(data["id"])
        fiches.append({
            "data": data,
            "code": code,
            "category": category_for(code),
            "ed_fr": data["editions"]["fr"],
            "ed_en": data["editions"]["en"],
        })
    return fiches


def main() -> int:
    fiches = load_fiches()
    if not fiches:
        sys.exit("Aucune fiche n1-* valide trouvée dans contenus/fiches/")
    pages = 0
    for L in fiches:
        code = L["code"]
        fr_dir = DOCS / "lecons" / code
        en_dir = DOCS / "en" / "lessons" / code
        fr_dir.mkdir(parents=True, exist_ok=True)
        en_dir.mkdir(parents=True, exist_ok=True)
        (fr_dir / "index.html").write_text(render_lesson_page(L["data"], "fr"), encoding="utf-8")
        (en_dir / "index.html").write_text(render_lesson_page(L["data"], "en"), encoding="utf-8")
        pages += 2

    # A0.01 reste manuelle ; on l'ajoute en entrée de bibliothèque uniquement.
    a0_entry = {
        "code": "A0-01",
        "category": "actuariat",
        "manual": True,
        "ed_fr": {
            "titre": "Actuaires : le métier et un premier calcul",
            "legende": "Le rôle de l'actuaire, le contrat d'assurance et le calcul d'une prime pure.",
            "hashtags": ["prime pure", "assurance", "risque", "probabilité", "métier"],
        },
        "ed_en": {
            "titre": "Actuaries: the profession and a first calculation",
            "legende": "The role of actuaries, insurance contracts and the calculation of a pure premium.",
            "hashtags": ["pure premium", "insurance", "risk", "probability", "profession"],
        },
    }
    lessons_for_lib = [a0_entry] + sorted(fiches, key=lambda x: x["code"])

    (DOCS / "bibliotheque" / "index.html").write_text(
        render_library_page(lessons_for_lib, "fr"), encoding="utf-8"
    )
    (DOCS / "en" / "library" / "index.html").write_text(
        render_library_page(lessons_for_lib, "en"), encoding="utf-8"
    )

    print(f"Fiches valides   : {len(fiches)}")
    print(f"Pages écrites    : {pages} (leçons FR + EN)")
    print(f"Bibliothèques    : FR + EN mises à jour ({len(lessons_for_lib)} leçons affichées)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
