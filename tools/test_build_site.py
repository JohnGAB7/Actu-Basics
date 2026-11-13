#!/usr/bin/env python3
"""Tests automatiques du générateur de site ACTU-BASICS.

Usage:   python3 tools/test_build_site.py
Objectif: détecter rapidement les régressions avant un merge.

Couvre:
- unit tests sur les helpers (module_of, module_code, pick_lang, URL whitelist,
  module_sort_key)
- validation des modules référencés par parcours.yaml : chacun doit être
  reconnu par les fonctions et attribué à une catégorie
- génération complète + contrôle d'intégrité:
  * tout fiche produit exactement ses deux pages (FR + EN)
  * chaque code apparaît exactement une fois dans les bibliothèques FR + EN
  * chaque lien de bibliothèque pointe vers une page existante, sans lien orphelin
  * slugs et modules des parcours sont valides et non ambigus
  * tout parcours produit index + détail FR + EN
  * tout fichier lie bien hreflang fr et en
  * aucune page ne contient de dict Python brut `{'fr': ...}`
  * aucune page ne charge un iframe pour une URL hors whitelist
  * tout code module de fiche appartient bien à l'un des parcours OU n'y
    appartient à aucun (on refuse les modules hors radar, mais pas un
    module qui serait orphelin du parcours)

Fin avec sys.exit(0) si tout passe, sinon sys.exit(1) et imprime les erreurs.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

# pylint: disable=wrong-import-position
import build_lessons as B  # type: ignore


class Failures:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, name: str, msg: str) -> None:
        self.items.append(f"[{name}] {msg}")

    def ok(self) -> bool:
        return not self.items


F = Failures()


# -------------------- unit tests ------------------------------------------

def test_module_code() -> None:
    cases = {
        "2026-11-n1-s2-04-xxx": "S2-04",
        "2026-11-act-a0-01-the-actuarial-profession": "A0-01",
        "2026-11-act-x-a0-01a-votre-premier-calcul": "A0-01",  # a-suffix dropped
        "2026-11-n1-m0-01-fractions-ratios": "M0-01",
        "2026-11-n1-s4-07-probabilite-conditionnelle": "S4-07",
    }
    for fid, want in cases.items():
        got = B.module_code(fid)
        if got != want:
            F.add("module_code", f"{fid!r} -> {got!r}, attendu {want!r}")


def test_module_of_and_sort() -> None:
    cases = {
        "M0-01": "M0",
        "S4-07": "S4",
        "A0-01": "A0",
        "MF2-03": "MF2",
        "F1-12": "F1",
    }
    for code, want in cases.items():
        got = B.module_of(code)
        if got != want:
            F.add("module_of", f"{code!r} -> {got!r}, attendu {want!r}")
    ordered = sorted(["S5", "A1", "M0", "S1", "S10", "MF1", "A0"], key=B.module_sort_key)
    expected = ["M0", "S1", "S5", "S10", "A0", "A1", "MF1"]
    if ordered != expected:
        F.add("module_sort_key", f"ordre inattendu : {ordered}")


def test_category_for() -> None:
    cases = {
        "M0-01": "fondations",
        "S1-02": "statistiques",
        "S3-05": "statistiques",
        "S4-01": "probabilites",
        "S9-01": "probabilites",
        "A0-01": "actuariat",
        "A3-01": "actuariat",
        "MF2-01": "finance",
    }
    for code, want in cases.items():
        got = B.category_for(code)
        if got != want:
            F.add("category_for", f"{code!r} -> {got!r}, attendu {want!r}")


def test_pick_lang() -> None:
    if B.pick_lang({"fr": " %", "en": "%"}, "fr") != " %":
        F.add("pick_lang", "dict FR non résolu")
    if B.pick_lang({"fr": " %", "en": "%"}, "en") != "%":
        F.add("pick_lang", "dict EN non résolu")
    if B.pick_lang("brut", "fr") != "brut":
        F.add("pick_lang", "scalaire altéré")
    if B.pick_lang(None, "fr", "x") != "x":
        F.add("pick_lang", "default non appliqué")
    if B.pick_lang({"fr": "a"}, "en") != "a":
        F.add("pick_lang", "repli autre langue manquant")


def test_url_whitelist_youtube() -> None:
    good = [
        ("https://youtu.be/dQw4w9WgXcQ", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "https://www.youtube.com/embed/dQw4w9WgXcQ"),
    ]
    for url, want in good:
        got = B._youtube_embed_url(url)
        if got != want:
            F.add("youtube_whitelist", f"{url!r} -> {got!r}, attendu {want!r}")
    bad = [
        "http://youtu.be/dQw4w9WgXcQ",       # http
        "https://evil.example/watch?v=X",    # autre domaine
        "https://www.youtube.com/watch?v=<script>",  # id invalide
        "https://www.youtube.com/watch?v=",  # id vide
        "https://example.com/youtube.com/watch?v=X",  # confusion de domaine
        "",
        None,
    ]
    for url in bad:
        got = B._youtube_embed_url(url) if url else None
        if got is not None:
            F.add("youtube_whitelist", f"URL interdite acceptée : {url!r} -> {got!r}")


def test_url_whitelist_tiktok() -> None:
    if not B._tiktok_safe_url("https://www.tiktok.com/@a/video/1"):
        F.add("tiktok_whitelist", "URL valide rejetée")
    if B._tiktok_safe_url("http://www.tiktok.com/@a/video/1"):
        F.add("tiktok_whitelist", "http accepté à tort")
    if B._tiktok_safe_url("https://example.com/@a/video/1"):
        F.add("tiktok_whitelist", "autre domaine accepté")


def test_parcours_lesson_relations() -> None:
    parcours = B.load_parcours()
    fiches = B.load_fiches()
    code_to_mod = {f["code"]: f["module"] for f in fiches}
    modules_in_parcours = {m for p in parcours for m in (p.get("modules") or [])}

    # Les modules référencés par parcours doivent être reconnaissables.
    for mod in modules_in_parcours:
        meta = B.module_meta(mod, "fr")
        if not meta.get("titre"):
            F.add("parcours_modules", f"module {mod!r} sans libellé")
        if not B.category_for(f"{mod}-00"):
            F.add("parcours_modules", f"module {mod!r} sans catégorie")

    # Multi-parcours (données réelles) : si deux parcours partagent un module,
    # une leçon de ce module doit remonter plusieurs parcours.
    overlap_mods = set()
    for i, p1 in enumerate(parcours):
        for p2 in parcours[i + 1:]:
            overlap_mods.update(set(p1.get("modules", [])) & set(p2.get("modules", [])))
    for code, mod in code_to_mod.items():
        if mod in overlap_mods:
            found = B.parcours_for_lesson(code, parcours)
            if len(found) < 2:
                F.add("parcours_multi", f"{code} dans un module partagé "
                                        f"mais rattaché à {len(found)} parcours")


def test_parcours_multi_synthetic() -> None:
    """Exerce le cas multi-parcours sur données synthétiques, indépendamment
    de l'état de contenus/parcours.yaml : garantit que la logique continue
    de fonctionner si deux parcours se partageaient un module."""
    fake = [
        {"slug": "tronc-commun", "modules": ["M0", "S1"], "titre": {"fr": "TC", "en": "TC"}},
        {"slug": "statistiques-decouverte", "modules": ["S1", "S2", "S3"],
         "titre": {"fr": "Stats D", "en": "Stats D"}},
        {"slug": "parcours-court", "modules": ["S1"], "titre": {"fr": "Court", "en": "Short"}},
    ]
    # Une leçon S1 doit être rattachée aux 3 parcours.
    matching = B.parcours_for_lesson("S1-04", fake)
    if len(matching) != 3:
        F.add("parcours_multi_synth", f"S1-04 attendu dans 3 parcours, trouvé {len(matching)}")
    # Une leçon M0 : 1 parcours seulement (tronc-commun).
    matching_m0 = B.parcours_for_lesson("M0-01", fake)
    if len(matching_m0) != 1 or matching_m0[0]["slug"] != "tronc-commun":
        F.add("parcours_multi_synth", f"M0-01 devrait être dans tronc-commun uniquement, trouvé "
                                      f"{[p['slug'] for p in matching_m0]}")
    # Une leçon d'un module non référencé : 0 parcours.
    matching_x = B.parcours_for_lesson("X9-01", fake)
    if matching_x:
        F.add("parcours_multi_synth", f"X9-01 devrait être orphelin, trouvé {matching_x}")


def test_category_unknown_module_is_autre() -> None:
    """Un module dont la lettre n'est pas dans la taxonomie connue est
    classé en 'autre', jamais silencieusement en 'statistiques'."""
    for code in ("Z1-01", "XY42-01", "Q2-04"):
        got = B.category_for(code)
        if got != "autre":
            F.add("category_unknown", f"{code!r} -> {got!r}, attendu 'autre'")
    # Les familles explicitement reconnues conservent leur catégorie.
    for code, expected in (("M0-01", "fondations"), ("S1-01", "statistiques"),
                           ("S4-01", "probabilites"), ("A0-01", "actuariat"),
                           ("MF1-01", "finance"), ("F1-01", "finance")):
        got = B.category_for(code)
        if got != expected:
            F.add("category_known", f"{code!r} -> {got!r}, attendu {expected!r}")


def test_short_fiches_not_generated() -> None:
    """Un code qui n'est représenté QUE par des fiches `format: short` ne doit
    produire aucune page. Un code qui a à la fois une fiche long-form (valide)
    et une variante short est autorisé à avoir une page générée par le long-form.
    """
    import yaml as _y
    by_code_formats: dict[str, list[str]] = {}
    for fp in sorted((ROOT / "contenus" / "fiches").glob("*.yaml")):
        try:
            with fp.open(encoding="utf-8") as f:
                data = _y.safe_load(f) or {}
        except Exception:
            continue
        fid = data.get("id") or ""
        if not fid:
            continue
        if data.get("validation", {}).get("statut") != "valide":
            continue
        fmt = str(data.get("format") or "").lower()
        code = B.module_code(fid)
        by_code_formats.setdefault(code, []).append(fmt)
    for code, fmts in by_code_formats.items():
        only_short = all(f == "short" for f in fmts) and len(fmts) > 0
        if not only_short:
            continue
        for lang_dir in ("lecons", "en/lessons"):
            path = ROOT / "docs" / lang_dir / code / "index.html"
            if path.exists():
                F.add("short_filter", f"page générée pour un code 100 % short : {path.relative_to(ROOT)}")


def test_parcours_schema() -> None:
    """Les parcours doivent avoir des slugs uniques et des modules syntaxiquement valides."""
    parcours = B.load_parcours()
    seen_slugs: set[str] = set()
    slug_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    module_re = re.compile(r"^[A-Z]+[0-9]+$")
    for p in parcours:
        slug = str(p.get("slug") or "")
        if not slug_re.fullmatch(slug):
            F.add("parcours_schema", f"slug invalide : {slug!r}")
        if slug in seen_slugs:
            F.add("parcours_schema", f"slug dupliqué : {slug!r}")
        seen_slugs.add(slug)
        titles = p.get("titre") or {}
        if not titles.get("fr") or not titles.get("en"):
            F.add("parcours_schema", f"{slug}: titre FR/EN manquant")
        modules = p.get("modules") or []
        if len(modules) != len(set(modules)):
            F.add("parcours_schema", f"{slug}: module déclaré plusieurs fois")
        for mod in modules:
            if not isinstance(mod, str) or not module_re.fullmatch(mod):
                F.add("parcours_schema", f"{slug}: code module invalide {mod!r}")


def test_library_links_integrity() -> None:
    """Chaque fiche publiée apparaît exactement une fois dans chaque catalogue,
    et chaque URL locale de leçon pointe vers un fichier HTML réellement généré."""
    fiches = B.load_fiches()
    expected = {f["code"] for f in fiches}
    cases = (
        (ROOT / "docs" / "bibliotheque" / "index.html",
         re.compile(r'href="([^"]*/lecons/([A-Z0-9-]+)/?)"'),
         ROOT / "docs" / "lecons"),
        (ROOT / "docs" / "en" / "library" / "index.html",
         re.compile(r'href="([^"]*/lessons/([A-Z0-9-]+)/?)"'),
         ROOT / "docs" / "en" / "lessons"),
    )
    for library, pattern, lesson_root in cases:
        if not library.exists():
            F.add("library_links", f"catalogue manquant : {library.relative_to(ROOT)}")
            continue
        text = library.read_text(encoding="utf-8")
        module_count = len({fiche["module"] for fiche in fiches})
        expected_overview = (
            f"{module_count} portes d&#x27;entrée" if "bibliotheque" in str(library)
            else f"{module_count} entry points"
        )
        if expected_overview not in text:
            F.add("library_overview", f"compteur de modules absent ou incorrect dans {library.relative_to(ROOT)}")
        found = [m.group(2) for m in pattern.finditer(text)]
        found_set = set(found)
        if len(found) != len(found_set):
            F.add("library_links", f"liens dupliqués dans {library.relative_to(ROOT)}")
        missing = sorted(expected - found_set)
        extra = sorted(found_set - expected)
        if missing:
            F.add("library_links", f"fiches absentes de {library.relative_to(ROOT)} : {missing}")
        if extra:
            F.add("library_links", f"liens sans fiche dans {library.relative_to(ROOT)} : {extra}")
        for code in found_set:
            target = lesson_root / code / "index.html"
            if not target.is_file():
                F.add("library_links", f"lien cassé {code} dans {library.relative_to(ROOT)}")


def test_relative_links_resolve() -> None:
    """Résolution stricte de chaque href RELATIF sur chaque page générée :
    le fichier cible doit exister sur disque.

    Ce test aurait attrapé la régression où les cartes de leçons des pages
    parcours pointaient vers ``../lecons/<CODE>/`` au lieu de
    ``../../lecons/<CODE>/`` — ce qui donnait un lien vers
    ``/parcours/lecons/<CODE>/`` au lieu de ``/lecons/<CODE>/``.
    """
    docs = ROOT / "docs"
    href_re = re.compile(r'href="([^"#]+)(#[^"]*)?"')
    # Toutes les pages générées à ausculter.
    targets: list[Path] = []
    targets.extend(docs.rglob("lecons/**/index.html"))
    targets.extend(docs.rglob("en/lessons/**/index.html"))
    targets.extend(docs.glob("parcours/**/index.html"))
    targets.extend(docs.glob("en/paths/**/index.html"))
    targets.extend([docs / "bibliotheque" / "index.html", docs / "en" / "library" / "index.html"])

    for page in targets:
        if not page.exists():
            continue
        text = page.read_text(encoding="utf-8")
        for m in href_re.finditer(text):
            href = m.group(1).strip()
            # On ne teste que les URLs locales relatives.
            if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:")):
                continue
            # URL absolue site (/foo/) : résoudre depuis docs/
            if href.startswith("/"):
                target_base = docs
                rel = href.lstrip("/")
            else:
                target_base = page.parent
                rel = href
            # Résoudre comme un chemin : si ça finit par /, cherche index.html.
            resolved = (target_base / rel).resolve()
            if resolved.is_dir() or rel.endswith("/"):
                resolved = resolved / "index.html"
            # Rester dans l'arbre docs/ pour éviter les faux positifs en dehors.
            try:
                resolved.relative_to(docs.resolve())
            except ValueError:
                # Lien hors de docs/ : ignoré ici.
                continue
            if not resolved.is_file():
                F.add(
                    "relative_links",
                    f"lien cassé {href!r} dans {page.relative_to(docs)} -> "
                    f"{resolved.relative_to(docs.resolve())}",
                )


# -------------------- integration tests -----------------------------------

def test_generation_integrity() -> None:
    """Appelle main() (via B.main) puis vérifie le résultat sur disque."""
    rc = B.main()
    if rc != 0:
        F.add("generate", f"rc = {rc}")
        return

    fiches = B.load_fiches()
    parcours = B.load_parcours()
    docs = ROOT / "docs"

    # Pages leçon FR + EN pour chaque fiche.
    for f in fiches:
        for path in (docs / "lecons" / f["code"] / "index.html",
                     docs / "en" / "lessons" / f["code"] / "index.html"):
            if not path.exists():
                F.add("gen_pages", f"manquante : {path.relative_to(docs)}")

    # Bibliothèque FR + EN.
    lib_fr = (docs / "bibliotheque" / "index.html")
    lib_en = (docs / "en" / "library" / "index.html")
    if not lib_fr.exists():
        F.add("gen_lib", "bibliotheque FR manquante")
    if not lib_en.exists():
        F.add("gen_lib", "bibliotheque EN manquante")

    # Chaque fiche doit être liée exactement une fois et chaque lien doit être valide.
    test_library_links_integrity()

    # Pages parcours.
    for p in parcours:
        slug = p.get("slug", "")
        for path in (docs / "parcours" / slug / "index.html",
                     docs / "en" / "paths" / slug / "index.html"):
            if not path.exists():
                F.add("gen_parcours", f"manquante : {path.relative_to(docs)}")

    # Pas de dict Python brut qui fuite dans les pages produites.
    leaked_dict = re.compile(r"\{'(?:fr|en)'\s*:")
    for path in list(docs.rglob("lecons/**/index.html")) + list(docs.rglob("en/lessons/**/index.html")):
        txt = path.read_text(encoding="utf-8")
        if leaked_dict.search(txt):
            F.add("gen_no_dict_leak", f"dict FR/EN brut dans {path.relative_to(docs)}")

    # Chaque page HTML lie bien hreflang fr + en.
    for path in list(docs.rglob("lecons/**/index.html")) + list(docs.rglob("en/lessons/**/index.html")):
        txt = path.read_text(encoding="utf-8")
        if 'hreflang="fr"' not in txt or 'hreflang="en"' not in txt:
            F.add("gen_hreflang", f"hreflang manquant dans {path.relative_to(docs)}")

    # Pas d'iframe youtube avec URL hors whitelist.
    iframe_re = re.compile(r'<iframe[^>]+src="([^"]+)"')
    for path in list(docs.rglob("lecons/**/index.html")) + list(docs.rglob("en/lessons/**/index.html")):
        for m in iframe_re.finditer(path.read_text(encoding="utf-8")):
            src = m.group(1)
            if not src.startswith("https://www.youtube.com/embed/"):
                F.add("gen_iframe_safety", f"iframe hors whitelist dans {path.name}: {src}")


def test_premium_foundations() -> None:
    """Chaque page générée charge les assets premium (tokens, Fraunces,
    premium.css, print.css, theme init). La page Programme existe en FR+EN
    et mentionne les trois piliers. Le mode sombre est accessible par un
    bouton `[data-theme-toggle]` dans chaque <header>."""
    name = "test_premium_foundations"

    # 1) Les assets premium sont partout, y compris les accueils manuels
    #    (régression constatée : le bouton de thème manquait sur /index.html).
    sample_pages = [
        ROOT / "docs" / "index.html",
        ROOT / "docs" / "en" / "index.html",
        ROOT / "docs" / "a-propos" / "index.html",
        ROOT / "docs" / "en" / "about" / "index.html",
        ROOT / "docs" / "lecons" / "M0-03" / "index.html",
        ROOT / "docs" / "en" / "lessons" / "M0-03" / "index.html",
        ROOT / "docs" / "bibliotheque" / "index.html",
        ROOT / "docs" / "en" / "library" / "index.html",
        ROOT / "docs" / "parcours" / "index.html",
        ROOT / "docs" / "en" / "paths" / "index.html",
        ROOT / "docs" / "programme" / "index.html",
        ROOT / "docs" / "en" / "programme" / "index.html",
    ]
    required = ["tokens.css", "premium.css", "print.css", "Source+Serif+4", "data-theme-toggle", "ab-theme"]
    for pg in sample_pages:
        if not pg.exists():
            F.add(name, f"page absente : {pg.relative_to(ROOT)}")
            continue
        txt = pg.read_text(encoding="utf-8")
        for token in required:
            if token not in txt:
                F.add(name, f"{pg.relative_to(ROOT)} : {token} manquant")

    # 2) La page Programme contient bien les trois piliers.
    fr = (ROOT / "docs" / "programme" / "index.html").read_text(encoding="utf-8")
    en = (ROOT / "docs" / "en" / "programme" / "index.html").read_text(encoding="utf-8")
    for piece in ("I.", "II.", "III.", "Fondations", "Statistiques", "Actuariat"):
        if piece not in fr:
            F.add(name, f"programme FR : {piece!r} manquant")
    for piece in ("I.", "II.", "III.", "Foundations", "Statistics", "Actuarial"):
        if piece not in en:
            F.add(name, f"programme EN : {piece!r} manquant")

    # 3) La page Programme lie bien les leçons disponibles de chaque module.
    #    Au moins M0-01 doit y figurer en tant que lien.
    if 'href="../lecons/M0-01/"' not in fr:
        F.add(name, "programme FR : lien ../lecons/M0-01/ manquant")
    if 'href="../../en/lessons/M0-01/"' not in en:
        F.add(name, "programme EN : lien ../../en/lessons/M0-01/ manquant")

    # 4) La page design system existe.
    ds = ROOT / "docs" / "technique" / "design-system" / "index.html"
    if not ds.exists():
        F.add(name, "page design system manquante")

    # 5) Les pages de module existent (FR + EN) pour M0 et S1, chargent les
    #    assets premium, et depuis Programme le code du module est cliquable.
    for mod in ("M0", "S1", "A1"):
        fr_mod = ROOT / "docs" / "modules" / mod / "index.html"
        en_mod = ROOT / "docs" / "en" / "modules" / mod / "index.html"
        for p in (fr_mod, en_mod):
            if not p.exists():
                F.add(name, f"module {mod} : {p.relative_to(ROOT)} manquante")
                continue
            t = p.read_text(encoding="utf-8")
            for token in ("tokens.css", "premium.css", "data-theme-toggle"):
                if token not in t:
                    F.add(name, f"{p.relative_to(ROOT)} : {token} manquant")
    # Depuis Programme FR, le lien vers /modules/M0/ doit être présent.
    if 'href="../modules/M0/"' not in fr:
        F.add(name, "programme FR : lien ../modules/M0/ manquant")
    if 'href="../../en/modules/M0/"' not in en:
        F.add(name, "programme EN : lien ../../en/modules/M0/ manquant")

    # 6) Contacts par langue : FR porte actubasics.officiel, EN porte
    #    actubasics.official, et chaque langue n'inclut que le sien.
    fr_home = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    en_home = (ROOT / "docs" / "en" / "index.html").read_text(encoding="utf-8")
    if "actubasics.officiel@gmail.com" not in fr_home:
        F.add(name, "accueil FR : actubasics.officiel@gmail.com manquant")
    if "actubasics.official@gmail.com" not in en_home:
        F.add(name, "accueil EN : actubasics.official@gmail.com manquant")
    if "actubasics.official@gmail.com" in fr_home:
        F.add(name, "accueil FR : contact EN visible par erreur")
    if "actubasics.officiel@gmail.com" in en_home:
        F.add(name, "accueil EN : contact FR visible par erreur")


def test_courbe_svg_rendering() -> None:
    """Chaque style de courbe produit un <svg> accessible avec aria-label.

    Vérifie aussi qu'aucune scène `type: courbe` d'une fiche valide n'est
    rendue comme placeholder `[Graphique associé à cette étape]` : si la
    scène est présente mais sans bloc `courbe:`, c'est un défaut de contenu
    (le générateur doit le rendre, pas afficher un placeholder).
    """
    name = "test_courbe_svg_rendering"

    # 1) Chaque style renvoie un <svg> avec aria-label
    styles = {
        "points": {"style": "points", "points": [[0, 1], [1, 2], [2, 3]], "axe_x": "x", "axe_y": "y"},
        "ligne": {"style": "ligne", "points": [[0, 1], [1, 2], [2, 3]]},
        "barres": {"style": "barres", "points": [[0, 10], [1, 20]], "etiquettes": ["A", "B"], "valeurs": True},
        "histogramme": {"style": "histogramme", "points": [[0, 3], [10, 7], [20, 6]], "largeur_classe": 10},
        "boites": {"style": "boites", "boites": [{"etiquette": "x", "valeurs": [1, 2, 3, 4, 5]}]},
        "expression": {"expression": "1000 * 1.05**t", "variable": "t", "de": 0, "a": 10, "y_max": 2000},
    }
    for st, courbe in styles.items():
        svg = B.render_courbe_svg(courbe, "fr", aria_label=f"test {st}")
        if "<svg" not in svg:
            F.add(name, f"style {st} : <svg> manquant")
        if 'aria-label="test ' not in svg:
            F.add(name, f"style {st} : aria-label manquant")
        if 'role="img"' not in svg:
            F.add(name, f"style {st} : role=img manquant")

    # 1b) Double axe : la seconde série structurée doit être visible sur
    # son propre domaine Y, avec graduations et titre d'axe à droite.
    dual = B.render_courbe_svg({
        "style": "ligne",
        "points": [[2020, 100], [2021, 110], [2022, 120], [2023, 130], [2024, 140]],
        "y_min": 100, "y_max": 140, "axe_y": "Vélos (milliers)",
        "serie_2": {
            "points": [[2020, 20], [2021, 26], [2022, 32], [2023, 38], [2024, 44]],
            "y_min": 16, "y_max": 48, "axe_y": "Trottinettes (milliers)",
        },
    }, "fr", aria_label="Double échelle")
    for token in ("courbe-line-alt", "courbe-axis-right", "Trottinettes (milliers)", ">20<", ">40<"):
        if token not in dual:
            F.add(name, f"double axe : élément manquant {token!r}")

    # 1c) L'animation de surface doit devenir une illustration SVG, pas
    # uniquement une liste d'étapes textuelles.
    surface = B.render_scene({
        "type": "animation",
        "animation": {"modele": "surface"},
        "etapes": ["Valeur ×1", "Valeur ×2"],
    }, "fr")
    if "surface-svg" not in surface or "Aire ×4" not in surface or "Aire ×2" not in surface:
        F.add(name, "illustration de surface absente ou incomplète")

    # 1d) Les pages publiées FR et EN de S1-09 doivent contenir les deux
    # graphiques à double axe et la comparaison de surfaces.
    for rel in ("docs/lecons/S1-09/index.html", "docs/en/lessons/S1-09/index.html"):
        page = ROOT / rel
        if page.exists():
            txt = page.read_text(encoding="utf-8")
            if txt.count("courbe-axis-right") < 2:
                F.add(name, f"{rel}: les deux axes droits ne sont pas rendus")
            if "surface-svg" not in txt:
                F.add(name, f"{rel}: illustration de surface absente")

    # 2) Aucune page leçon ne doit afficher le placeholder `[Graphique associé...]`
    #    pour une scène courbe qui porte bien un bloc `courbe:` dans la fiche.
    import glob, yaml
    def walk(obj):
        if isinstance(obj, dict):
            yield obj
            for v in obj.values():
                yield from walk(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from walk(v)

    for fp in glob.glob(str(ROOT / "contenus" / "fiches" / "*.yaml")):
        try:
            d = yaml.safe_load(open(fp))
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        if (d.get("validation", {}) or {}).get("statut") != "valide":
            continue
        if d.get("format") == "short":
            continue
        code = (d.get("fiche") or d.get("id") or "").upper().replace(".", "-")
        if not code:
            continue
        page_fr = ROOT / "docs" / "lecons" / code / "index.html"
        if not page_fr.exists():
            continue
        txt = page_fr.read_text(encoding="utf-8")
        # compter les scènes courbe avec un bloc `courbe:`
        n_courbes_with_data = sum(
            1 for scn in walk(d)
            if isinstance(scn, dict) and scn.get("type") == "courbe" and scn.get("courbe")
        )
        if n_courbes_with_data > 0:
            # aucun placeholder admis
            if "[Graphique associé à cette étape]" in txt:
                F.add(name, f"{code}/index.html : placeholder affiché malgré {n_courbes_with_data} courbe(s) avec données")
            # au moins un svg attendu
            if txt.count("courbe-svg") < n_courbes_with_data:
                F.add(name, f"{code}/index.html : {n_courbes_with_data} courbe(s) attendue(s), {txt.count('courbe-svg')} <svg> trouvé(s)")


# -------------------- runner ----------------------------------------------

def main() -> int:
    tests = [
        test_module_code,
        test_module_of_and_sort,
        test_category_for,
        test_category_unknown_module_is_autre,
        test_parcours_schema,
        test_pick_lang,
        test_url_whitelist_youtube,
        test_url_whitelist_tiktok,
        test_parcours_lesson_relations,
        test_parcours_multi_synthetic,
        test_generation_integrity,
        test_library_links_integrity,
        test_relative_links_resolve,
        test_short_fiches_not_generated,
        test_courbe_svg_rendering,
        test_premium_foundations,
    ]
    for t in tests:
        try:
            t()
        except Exception as exc:  # pragma: no cover
            F.add(t.__name__, f"exception : {exc!r}")

    if F.ok():
        print(f"✅ {len(tests)} groupes de tests passent.")
        return 0
    print(f"❌ {len(F.items)} échec(s) :", file=sys.stderr)
    for item in F.items:
        print("  -", item, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
