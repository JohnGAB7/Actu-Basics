#!/usr/bin/env python3
"""Fiche de contenu -> vidéos verticales avec voix, carrousels, sous-titres, légendes, rapport (FR + EN).

Deux modes :
  apercu (défaut)  accepte les fiches en brouillon ; tout rendu qui a une erreur bloquante
                   porte le filigrane « BROUILLON · NON VALIDÉ ». Jamais publiable tel quel.
  final            refuse toute fiche non validée ou avec une erreur bloquante (voix comprise) ;
                   seul ce mode produit des fichiers prêts à publier.

Exemples :
    python production/produire.py contenus/fiches/ma-fiche.yaml
    python production/produire.py contenus/fiches/ma-fiche.yaml --mode final
    python production/produire.py ma-fiche.yaml --voix openai      # change de fournisseur de voix
    python production/produire.py ma-fiche.yaml --verifier         # contrôle la fiche, ne produit rien
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import time
import traceback
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lmec.carrousel import planche_apercu, produire_carrousel  # noqa: E402
from lmec.fiche import LANGUES, FicheInvalide, charger_fiche  # noqa: E402
from lmec.inspection import inspection_logo, produire_inspection  # noqa: E402
from lmec.narration import AMORCE_S, durees_avec_voix, piste_complete, produire_voix, reperes_sous_titres  # noqa: E402
from lmec.pedagogie import controler_duree_format  # noqa: E402
from lmec.son import habiller  # noqa: E402
from lmec.qc import (Rapport, controler_fiche, controler_lisibilite, controler_logo, controler_longueurs, controler_marque,  # noqa: E402
                     controler_plateformes, controler_video, ecrire_rapport)
from lmec.rendu import Rendu  # noqa: E402
from lmec.textes import ecrire_metadonnees, ecrire_script_voix, ecrire_srt, legende_complete  # noqa: E402
from lmec.tts import Cache, ErreurTTS, charger_env, creer_avec_secours  # noqa: E402
from lmec.video import durees_visuelles, produire_video, sonder_video  # noqa: E402

RACINE = Path(__file__).resolve().parent
DEPOT = RACINE.parent
# Phrases déjà synthétisées (non versionné ; persisté entre exécutions GitHub par actions/cache).
DOSSIER_CACHE = Path(os.environ.get("LMEC_CACHE_TTS", DEPOT / ".cache-tts"))


def _yaml(chemin: Path) -> dict:
    return yaml.safe_load(chemin.read_text(encoding="utf-8"))


def _afficher(rapport: Rapport) -> None:
    for c in rapport.bloquants:
        print(f"  ❌ {c}")
    for c in rapport.avertissements:
        print(f"  ⚠️  {c}")


def produire(chemin: Path, args, charte: dict, plateformes: dict, config_tts: dict, resume: list[str]) -> bool:
    print(f"\n=== {chemin}  (mode {args.mode})")
    try:
        fiche = charger_fiche(chemin)
    except FicheInvalide as exc:
        print(f"❌ Fiche inexploitable :\n{exc}")
        resume += [f"### ❌ `{chemin}` — fiche inexploitable", "", "```", str(exc), "```", ""]
        return False

    rapport = Rapport()
    controler_fiche(fiche, rapport)
    controler_marque(charte, rapport)
    if args.verifier:
        _afficher(rapport)
        print("✅ Aucune erreur bloquante" if not rapport.bloquants else
              f"❌ {len(rapport.bloquants)} erreur(s) bloquante(s)")
        return not rapport.bloquants

    racine_sortie = Path(args.sortie) / fiche.id
    if args.mode == "final" and rapport.bloquants:
        racine_sortie.mkdir(parents=True, exist_ok=True)
        etat = ecrire_rapport(fiche, rapport, racine_sortie / "rapport-qc.md", args.mode)
        _afficher(rapport)
        print("❌ Mode final : production refusée.")
        resume += _resume(fiche, rapport, etat, [], args.mode)
        return False

    nom_voix = args.voix or os.environ.get("LMEC_TTS") or config_tts.get("fournisseur", "piper")
    cache = Cache(DOSSIER_CACHE)
    lexique = config_tts.get("prononciation") or {}
    durees_langues: dict[str, list[float]] = {}
    lignes_resume: list[list[str]] = []

    for langue in args.langues:
        t0 = time.time()
        edition = fiche.editions[langue]
        dossier = racine_sortie / langue
        if dossier.exists():
            shutil.rmtree(dossier)
        dossier.mkdir(parents=True)
        travail = dossier / "_travail"

        format_v = fiche.format_image          # « video » (vertical) ou « lecon » (16:9)
        rendu_v = Rendu(fiche, langue, charte, format_v, True)
        durees = durees_visuelles(edition, rendu_v)
        explicites = [s.duree for s in edition.scenes]

        # ---- Voix off
        narration, piste, voix_info = None, None, {"fournisseur": None}
        if not edition.narration:
            rapport.production.append(f"- {langue.upper()} : sans voix (choix éditorial)")
        else:
            dossier_manuel = None
            if nom_voix == "manuel":
                dossier_manuel = ((chemin.parent / edition.audio) if edition.audio
                                  else DEPOT / "audio" / fiche.id / langue).resolve()
            try:
                fournisseur, bascule = creer_avec_secours(nom_voix, config_tts, langue, dossier_manuel)
                if bascule:
                    rapport.avertir(bascule, langue)
                narration = produire_voix(fiche, edition, fournisseur, cache, travail, lexique)
                durees, notes = durees_avec_voix(durees, narration, explicites)
                for n in notes:
                    rapport.avertir(n, langue)
                caler_sur_la_voix(rendu_v, edition, narration, durees)
                piste = piste_complete(narration, durees, travail)
                son = charte.get("son") or {}
                if fiche.habillage_sonore and son.get("actif", True):
                    fin = next((i for i, s in enumerate(edition.scenes) if s.type == "fin"), None)
                    piste = habiller(piste, durees, son, travail / "narration-habillee.wav", fin,
                                     rendu_v.reperes_sonores(edition.scenes, durees))
                    rapport.ok.append(f"[{langue}] Habillage sonore ajouté (signature, nappe et repères, prototype)")
                voix_info = {"fournisseur": narration.fournisseur, "publiable": narration.publiable,
                             "config": fournisseur.config}
                rapport.ok.append(f"[{langue}] Narration produite ({narration.fournisseur}) : "
                                  f"{narration.synthese} phrase(s) synthétisée(s), "
                                  f"{narration.depuis_cache} reprise(s) du cache, "
                                  f"{narration.caracteres} caractères facturables")
                if not narration.publiable:
                    rapport.bloquant(f"Voix « {narration.fournisseur} » réservée aux tests : non publiable", langue)
            except ErreurTTS as exc:
                rapport.bloquant(f"Narration impossible ({nom_voix}) : {exc}. La vidéo d'aperçu est SANS VOIX "
                                 "et ne doit pas être publiée. Secours : --voix manuel (voir guide).", langue)
                narration = None

        # ---- Contrôles dépendant des durées
        legende = legende_complete(fiche, edition)
        if fiche.pedagogique:
            controler_duree_format(fiche, langue, sum(durees), rapport)
        if format_v == "video" and fiche.format == "short":
            controler_plateformes(langue, sum(durees), legende, edition.titre, len(edition.hashtags),
                                  charte, plateformes, rapport)
        durees_langues[langue] = durees

        final_bloque = args.mode == "final" and rapport.bloquants
        if final_bloque:
            print(f"  ❌ {langue} : erreurs bloquantes, rien n'est produit en mode final")
            continue
        filigrane = bool(rapport.bloquants)

        # ---- Carrousel, textes
        rendu_c = None
        if fiche.format == "short":   # les vidéos pédagogiques longues n'ont pas de carrousel
            rendu_c = Rendu(fiche, langue, charte, "carrousel", filigrane)
            images = produire_carrousel(rendu_c, edition, dossier / "carrousel")
            planche_apercu(images, dossier / "apercu-carrousel.png")
            for a in rendu_c.alertes:
                rapport.avertir(a, langue)
            controler_logo(langue, rendu_c, [("carrousel", i, s.type) for i, s in enumerate(edition.scenes)
                                             if rendu_c.logo_prevu(s)], charte, plateformes, rapport)
        reperes = reperes_sous_titres(narration, durees) if narration else None
        ecrire_srt(fiche, edition, durees, dossier / "sous-titres.srt", reperes)
        ecrire_script_voix(fiche, edition, durees, dossier / "script-voix-off.txt", lexique)
        ecrire_metadonnees(fiche, edition, durees, dossier, voix_info, args.mode)

        # ---- Vidéo + inspection
        if not args.sans_video:
            rendu_v.brouillon = filigrane
            produire_video(rendu_v, edition, durees, piste, dossier / "video.mp4")
            if piste:
                shutil.copyfile(piste, dossier / "narration.wav")
            rendu_v.dessiner(edition.scenes[0], 0, len(edition.scenes), couverture=True).convert("RGB").save(
                dossier / "miniature.jpg", quality=90)
            for a in rendu_v.alertes:
                rapport.avertir(a, langue)
            attendus = [("video", i, s.type) for i, s in enumerate(edition.scenes) if rendu_v.logo_prevu(s)]
            if rendu_v.logo_prevu(edition.scenes[0], couverture=True):
                attendus.append(("couverture", 0, edition.scenes[0].type))
            controler_logo(langue, rendu_v, attendus, charte, plateformes, rapport)
            controler_video(langue, sonder_video(dossier / "video.mp4"), charte["formats"][format_v], rapport)
            controler_lisibilite(langue, rendu_v.tailles, rapport)
            if not args.sans_inspection:
                produire_inspection(dossier / "video.mp4", edition.scenes, durees,
                                    [rendu_v.duree_animation(s) for s in edition.scenes],
                                    plateformes if format_v == "video" else {"cibles": []}, dossier / "inspection")
                rendus = [r for r in (rendu_v, rendu_c) if r]
                for r in rendus:   # images d'inspection sans filigrane
                    r.brouillon = False
                inspection_logo(rendus, edition.scenes, dossier / "inspection")
                for r in rendus:
                    r.brouillon = filigrane
        shutil.rmtree(travail, ignore_errors=True)
        voix_txt = voix_info["fournisseur"] or "aucune"
        lignes_resume.append([langue.upper(), f"{sum(durees):.1f} s", voix_txt, str(len(edition.scenes)),
                              "oui" if filigrane else "non", f"{time.time() - t0:.0f} s"])
        rapport.production.append(f"- {langue.upper()} : {len(edition.scenes)} scènes, {sum(durees):.1f} s, "
                                  f"voix {voix_txt}, filigrane {'oui' if filigrane else 'non'}, "
                                  f"rendu en {time.time() - t0:.0f} s")
        print(f"  {langue}: {dossier}")

    controler_longueurs(durees_langues, fiche, rapport)
    racine_sortie.mkdir(parents=True, exist_ok=True)
    etat = ecrire_rapport(fiche, rapport, racine_sortie / "rapport-qc.md", args.mode)
    _afficher(rapport)
    print(f"{etat}\nRapport : {racine_sortie / 'rapport-qc.md'}")
    resume += _resume(fiche, rapport, etat, lignes_resume, args.mode)
    return args.mode == "apercu" or not rapport.bloquants


def caler_sur_la_voix(rendu: Rendu, edition, narration, durees: list[float]) -> None:
    """Étapes et compte à rebours calés sur la voix ; temps de réflexion ajouté après chaque exercice."""
    for i, (scene, vs) in enumerate(zip(edition.scenes, narration.scenes)):
        # Début de chaque PHRASE (la synthèse découpe aussi sur « : » et « ; », pas les étapes).
        rendu.reperes[id(scene)] = [AMORCE_S + ph.debut for k, ph in enumerate(vs.phrases)
                            if k == 0 or vs.phrases[k - 1].texte.rstrip()[-1:] in ".!?…"]
        rendu.fins_voix[id(scene)] = AMORCE_S + vs.duree_voix + 0.2
        if scene.type == "exercice" and not scene.duree:
            besoin = rendu.fins_voix[id(scene)] + scene.extra.get("pause", 3) + 0.8
            durees[i] = round(max(durees[i], besoin), 3)


def _resume(fiche, rapport, etat, lignes, mode) -> list[str]:
    r = [f"### {fiche.id}", "", f"**{etat}**", ""]
    if lignes:
        r += ["| Langue | Durée | Voix | Scènes | Filigrane | Rendu |", "|---|---|---|---|---|---|"]
        r += [f"| {' | '.join(l)} |" for l in lignes] + [""]
    if rapport.bloquants:
        r += [f"**Erreurs bloquantes ({len(rapport.bloquants)})**", ""] + [f"- ❌ {c}" for c in rapport.bloquants] + [""]
    if rapport.avertissements:
        r += [f"<details><summary>Avertissements ({len(rapport.avertissements)})</summary>", ""]
        r += [f"- ⚠️ {c}" for c in rapport.avertissements] + ["", "</details>", ""]
    if rapport.plateformes:
        r += ["| Langue | Plateforme | Durée | État |", "|---|---|---|---|"]
        r += [f"| {' | '.join(l)} |" for l in rapport.plateformes] + [""]
    r += ["La vérification factuelle (chiffres vs sources) reste humaine : voir `rapport-qc.md`, section 1.", ""]
    return r


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("fiches", nargs="+", type=Path)
    parseur.add_argument("--mode", choices=("apercu", "final"), default="apercu")
    parseur.add_argument("--voix", help="fournisseur de voix : kokoro (défaut) | piper | openai | elevenlabs | manuel | test")
    parseur.add_argument("--sortie", default="sortie", help="dossier de sortie (défaut : sortie/)")
    parseur.add_argument("--langues", nargs="+", choices=LANGUES, default=list(LANGUES))
    parseur.add_argument("--sans-video", action="store_true", help="carrousels et textes seulement")
    parseur.add_argument("--sans-inspection", action="store_true", help="ne pas générer les images d'inspection")
    parseur.add_argument("--verifier", action="store_true", help="contrôler la fiche sans rien produire")
    parseur.add_argument("--brouillon-autorise", action="store_true", help=argparse.SUPPRESS)  # ancien nom d'« apercu »
    parseur.add_argument("--charte", type=Path, default=RACINE / "charte.yaml")
    args = parseur.parse_args()
    if args.mode == "final" and set(args.langues) != set(LANGUES):
        parseur.error("le mode final produit toujours FR et EN")
    charger_env(DEPOT / ".env")
    charte, plateformes, config_tts = _yaml(args.charte), _yaml(RACINE / "plateformes.yaml"), _yaml(RACINE / "tts.yaml")
    resume = [f"## Production — mode {args.mode}", ""]
    resultats = []
    for f in args.fiches:
        try:
            resultats.append(produire(f, args, charte, plateformes, config_tts, resume))
        except Exception as exc:  # anomalie non prévue : rapportée lisiblement, les autres fiches continuent
            traceback.print_exc()
            print(f"❌ Erreur inattendue sur {f} : {type(exc).__name__} : {exc}")
            resume += [f"### ❌ `{f}` — erreur inattendue du programme", "",
                       f"`{type(exc).__name__} : {exc}`", "",
                       "Ce n'est probablement pas une erreur de la fiche : transmettre ce message à la "
                       "direction technique.", ""]
            resultats.append(False)
    Cache(DOSSIER_CACHE).nettoyer()
    Path(args.sortie).mkdir(parents=True, exist_ok=True)
    (Path(args.sortie) / "resume.md").write_text("\n".join(resume), encoding="utf-8")
    return 0 if all(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
