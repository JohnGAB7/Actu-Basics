#!/usr/bin/env python3
"""Fiche de contenu validée -> vidéos verticales, carrousels, sous-titres, légendes (FR + EN).

Exemples :
    python production/produire.py contenus/fiches/ma-fiche.yaml
    python production/produire.py contenus/fiches/*.yaml --brouillon-autorise
    python production/produire.py ma-fiche.yaml --verifier        # contrôle de la fiche seulement
    python production/produire.py ma-fiche.yaml --sans-video      # carrousels uniquement
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lmec.carrousel import planche_apercu, produire_carrousel  # noqa: E402
from lmec.fiche import LANGUES, FicheInvalide, charger_fiche  # noqa: E402
from lmec.qc import Rapport, controler_fiche, controler_legende, controler_video, ecrire_rapport  # noqa: E402
from lmec.rendu import Rendu  # noqa: E402
from lmec.textes import ecrire_metadonnees, ecrire_script_voix, ecrire_srt  # noqa: E402
from lmec.video import calculer_durees, produire_video, sonder_video  # noqa: E402

RACINE = Path(__file__).resolve().parent


def produire(chemin: Path, args, charte: dict) -> bool:
    print(f"\n=== {chemin}")
    try:
        fiche = charger_fiche(chemin)
    except FicheInvalide as exc:
        print(f"❌ Fiche invalide :\n{exc}")
        return False

    rapport = Rapport()
    controler_fiche(fiche, rapport, args.brouillon_autorise)
    if args.verifier:
        for e in rapport.erreurs:
            print(f"❌ {e}")
        for a in rapport.alertes:
            print(f"⚠️  {a}")
        if not rapport.erreurs:
            print("✅ Fiche conforme")
        return not rapport.erreurs
    if not fiche.est_validee and not args.brouillon_autorise:
        print("❌ Fiche non validée. Rien n'est produit (utiliser --brouillon-autorise pour un aperçu).")
        return False

    brouillon = not fiche.est_validee
    racine_sortie = Path(args.sortie) / fiche.id
    extras: list[str] = []
    for langue in args.langues:
        edition = fiche.editions[langue]
        dossier = racine_sortie / langue
        dossier.mkdir(parents=True, exist_ok=True)
        t0 = time.time()

        audio = None
        if edition.audio:
            audio = (chemin.parent / edition.audio).resolve()
            if not audio.exists():
                rapport.erreurs.append(f"[{langue}] Fichier audio introuvable : {edition.audio}")
                audio = None
        durees = calculer_durees(edition, audio)

        # Carrousel
        rendu_c = Rendu(fiche, langue, charte, "carrousel", brouillon)
        images = produire_carrousel(rendu_c, edition, dossier / "carrousel")
        planche_apercu(images, dossier / "apercu-carrousel.png")
        rapport.alertes += rendu_c.alertes

        # Textes
        ecrire_srt(fiche, edition, durees, dossier / "sous-titres.srt")
        ecrire_script_voix(fiche, edition, durees, dossier / "script-voix-off.txt")
        meta = ecrire_metadonnees(fiche, edition, durees, dossier)
        controler_legende(langue, meta["legende"], rapport)

        # Vidéo
        if not args.sans_video:
            rendu_v = Rendu(fiche, langue, charte, "video", brouillon)
            produire_video(rendu_v, edition, durees, audio, dossier / "video.mp4")
            rendu_v.dessiner(edition.scenes[0], 0, len(edition.scenes)).save(dossier / "miniature.jpg",
                                                                               quality=90)
            rapport.alertes += rendu_v.alertes
            controler_video(langue, sonder_video(dossier / "video.mp4"), charte["formats"]["video"],
                            audio is not None, rapport)
        extras.append(f"- {langue.upper()} : {len(edition.scenes)} scènes, {sum(durees):.1f} s, "
                      f"produit en {time.time() - t0:.0f} s")
        print(f"  {langue}: {dossier}")

    ecrire_rapport(fiche, rapport, racine_sortie / "rapport-qc.md", ["## Production", ""] + extras + [""])
    etat = "❌" if rapport.erreurs else ("⚠️ " if rapport.alertes else "✅")
    print(f"{etat} Rapport : {racine_sortie / 'rapport-qc.md'} "
          f"({len(rapport.erreurs)} erreur(s), {len(rapport.alertes)} alerte(s))")
    return not rapport.erreurs


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("fiches", nargs="+", type=Path)
    parseur.add_argument("--sortie", default="sortie", help="dossier de sortie (défaut : sortie/)")
    parseur.add_argument("--langues", nargs="+", choices=LANGUES, default=list(LANGUES))
    parseur.add_argument("--sans-video", action="store_true", help="ne produire que carrousels et textes")
    parseur.add_argument("--verifier", action="store_true", help="contrôler la fiche sans rien produire")
    parseur.add_argument("--brouillon-autorise", action="store_true",
                         help="produire un aperçu filigrané « BROUILLON » d'une fiche non validée")
    parseur.add_argument("--charte", type=Path, default=RACINE / "charte.yaml")
    args = parseur.parse_args()
    charte = yaml.safe_load(args.charte.read_text(encoding="utf-8"))
    resultats = [produire(f, args, charte) for f in args.fiches]
    return 0 if all(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
