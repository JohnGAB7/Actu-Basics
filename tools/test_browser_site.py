#!/usr/bin/env python3
"""Recette navigateur ACTU-BASICS : Chromium, Firefox et WebKit.

Démarre le site statique localement et vérifie les pages FR/EN, l'absence
de débordement horizontal, les images, la recherche, le menu mobile et
la navigation clavier. Produit des captures desktop/mobile dans browser-artifacts/.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ARTIFACTS = ROOT / "browser-artifacts"
BASE = "http://127.0.0.1:8765"
PAGES = [
    ("/", "home-fr"),
    ("/bibliotheque/", "library-fr"),
    ("/parcours/", "paths-fr"),
    ("/lecons/S1-05/", "lesson-fr"),
    ("/en/", "home-en"),
    ("/en/library/", "library-en"),
    ("/en/paths/", "paths-en"),
    ("/en/lessons/S1-05/", "lesson-en"),
]


def wait_for_server(process: subprocess.Popen) -> None:
    for _ in range(80):
        if process.poll() is not None:
            raise RuntimeError("Le serveur HTTP s'est arrêté prématurément.")
        try:
            urllib.request.urlopen(BASE, timeout=1).close()
            return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    raise RuntimeError("Le serveur HTTP local n'a pas démarré.")


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_page(browser, browser_name: str, path: str, slug: str, width: int, height: int) -> None:
    page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
    page_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    response = page.goto(BASE + path, wait_until="networkidle")
    check(response is not None and response.status == 200,
          f"{browser_name} {path}: statut HTTP {response.status if response else 'absent'}")
    page.locator("main h1").wait_for(state="visible")
    metrics = page.evaluate("""() => ({
      viewport: document.documentElement.clientWidth,
      document: document.documentElement.scrollWidth,
      body: document.body.scrollWidth,
      title: document.title,
      images: [...document.images].map(i => ({src:i.getAttribute('src'), ok:i.complete && i.naturalWidth > 0}))
    })""")
    check(metrics["document"] <= metrics["viewport"] + 1 and metrics["body"] <= metrics["viewport"] + 1,
          f"{browser_name} {path} à {width}px: débordement horizontal {metrics}")
    broken = [img for img in metrics["images"] if not img["ok"]]
    check(not broken, f"{browser_name} {path}: images non chargées {broken}")
    check(not page_errors, f"{browser_name} {path}: erreurs JavaScript {page_errors}")
    mode = "mobile" if width < 600 else "desktop"
    ARTIFACTS.mkdir(exist_ok=True)
    page.screenshot(path=str(ARTIFACTS / f"{browser_name}-{slug}-{mode}.png"), full_page=True)
    page.close()


def check_keyboard_and_mobile_menu(browser, browser_name: str, home_path: str, lang: str) -> None:
    page = browser.new_page(viewport={"width": 390, "height": 844})
    page.goto(BASE + home_path, wait_until="networkidle")

    # Le premier arrêt clavier doit être le lien d'évitement.
    page.keyboard.press("Tab")
    active = page.evaluate("""() => ({
      className: document.activeElement.className,
      visible: !!(document.activeElement.getClientRects().length),
      outlineWidth: getComputedStyle(document.activeElement).outlineWidth
    })""")
    check("skip-link" in str(active["className"]) and active["visible"],
          f"{browser_name} {lang}: le lien d'évitement n'est pas le premier arrêt clavier ({active})")
    check(active["outlineWidth"] == "3px",
          f"{browser_name} {lang}: indicateur de focus clavier absent ou trop discret ({active})")
    page.keyboard.press("Enter")
    check(page.url.endswith("#contenu"), f"{browser_name} {lang}: le lien d'évitement ne mène pas au contenu")

    toggle = page.locator(".menu-toggle")
    nav = page.locator("#site-navigation")
    check(toggle.is_visible(), f"{browser_name} {lang}: bouton de menu mobile absent")
    check(not nav.is_visible(), f"{browser_name} {lang}: menu mobile visible avant ouverture")
    toggle.click()
    check(nav.is_visible() and toggle.get_attribute("aria-expanded") == "true",
          f"{browser_name} {lang}: ouverture du menu mobile incorrecte")
    page.keyboard.press("Escape")
    check(not nav.is_visible() and toggle.get_attribute("aria-expanded") == "false",
          f"{browser_name} {lang}: Échap ne ferme pas le menu")
    check(page.evaluate("document.activeElement === document.querySelector('.menu-toggle')"),
          f"{browser_name} {lang}: le focus ne revient pas au bouton après Échap")

    toggle.click()
    nav.locator("a").first.click()
    check(not nav.is_visible(), f"{browser_name} {lang}: le menu reste ouvert après navigation")
    check("/parcours/" in page.url if lang == "fr" else "/en/paths/" in page.url,
          f"{browser_name} {lang}: le premier lien du menu mène à une mauvaise destination ({page.url})")
    page.close()


def check_library_search(browser, browser_name: str, path: str, lang: str) -> None:
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(BASE + path, wait_until="networkidle")
    search = page.locator("[data-search]")
    check(search.count() == 1, f"{browser_name} {lang}: champ de recherche absent")
    search.fill("S1-05")
    card = page.locator('[data-lesson]').filter(has_text="S1-05")
    check(card.count() == 1 and card.is_visible(),
          f"{browser_name} {lang}: la recherche ne retrouve pas S1-05")
    search.fill("")
    page.locator("[data-filter]").select_option("probabilites")
    check(not card.is_visible() and page.locator('[data-lesson]').filter(has_text="S4-01").is_visible(),
          f"{browser_name} {lang}: le filtre par domaine ne fonctionne pas")
    search.fill("terme-qui-ne-correspond-a-aucune-lecon-xyz")
    empty = page.locator("[data-empty]")
    check(empty.count() == 1 and empty.is_visible(),
          f"{browser_name} {lang}: l'état vide n'est pas affiché")
    page.close()


def main() -> int:
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8765", "--bind", "127.0.0.1"],
        cwd=DOCS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    failures: list[str] = []
    try:
        wait_for_server(server)
        with sync_playwright() as p:
            for browser_name in ("chromium", "firefox", "webkit"):
                browser = getattr(p, browser_name).launch()
                try:
                    for path, slug in PAGES:
                        for width, height in ((1440, 1000), (390, 844)):
                            try:
                                check_page(browser, browser_name, path, slug, width, height)
                            except Exception as exc:
                                failures.append(str(exc))
                    for home, lang in (("/", "fr"), ("/en/", "en")):
                        try:
                            check_keyboard_and_mobile_menu(browser, browser_name, home, lang)
                        except Exception as exc:
                            failures.append(str(exc))
                    for library, lang in (("/bibliotheque/", "fr"), ("/en/library/", "en")):
                        try:
                            check_library_search(browser, browser_name, library, lang)
                        except Exception as exc:
                            failures.append(str(exc))
                finally:
                    browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()

    if failures:
        print(f"ÉCHEC : {len(failures)} contrôle(s) navigateur")
        for failure in failures:
            print(" - " + failure)
        return 1
    print("SUCCÈS : 3 moteurs, 8 pages FR/EN, desktop/mobile, navigation clavier, menu mobile et recherche.")
    print(f"Captures enregistrées dans {ARTIFACTS.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
