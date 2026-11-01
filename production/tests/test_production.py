"""Tests : python -m pytest production/tests -q

Tous les tests tournent sans clé d'API ni modèle de voix (fournisseur « test »).
"""
import copy
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "production"))

from lmec.fiche import FicheInvalide, charger_fiche  # noqa: E402
from lmec.formatage import formater_chiffre, formater_nombre, typographie  # noqa: E402
from lmec.narration import durees_avec_voix, piste_complete, produire_voix, reperes_sous_titres  # noqa: E402
from lmec.qc import BLOQUANT, Rapport, controler_fiche, controler_plateformes, nombres  # noqa: E402
from lmec.rendu import mots_riches  # noqa: E402
from lmec.textes import decouper_sous_titres  # noqa: E402
from lmec.tts import Cache, ErreurTTS, Manuel, VoixTest, creer_fournisseur, duree_wav  # noqa: E402

EXEMPLE = RACINE / "contenus/exemples/exemple-fictif.yaml"
SCRIPT = RACINE / "production/produire.py"
AUJOURD_HUI = dt.date(2026, 11, 1)
CHARTE = yaml.safe_load((RACINE / "production/charte.yaml").read_text(encoding="utf-8"))
PLATEFORMES = yaml.safe_load((RACINE / "production/plateformes.yaml").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- utilitaires
def brut_exemple():
    return yaml.safe_load(EXEMPLE.read_text(encoding="utf-8"))


def valider(brut):
    brut["validation"] = {"statut": "valide", "valide_par": "JG", "date": "2026-11-01"}
    return brut


def ecrire(tmp_path, brut, nom="exemple-fictif"):
    f = tmp_path / f"{nom}.yaml"
    f.write_text(yaml.safe_dump(brut, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return f


def constats(tmp_path, brut):
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, brut)), r, AUJOURD_HUI)
    return [str(c) for c in r.bloquants], [str(c) for c in r.avertissements]


def lancer(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True)


# --------------------------------------------------------------------------- formatage
def test_formatage_nombres():
    assert formater_nombre(8200000, "en") == "8,200,000"
    assert formater_nombre(8200000, "fr") == "8 200 000"
    assert formater_nombre(3.5, "fr") == "3,5"
    assert formater_nombre(2, "fr", 1) == "2,0"
    ch = {"valeur": 12.5, "suffixe": {"fr": " %", "en": "%"}}
    assert formater_chiffre(ch, "fr") == "12,5 %"
    assert formater_chiffre(ch, "en") == "12.5%"


def test_typographie_et_mise_en_valeur():
    assert typographie("Pourquoi ?", "fr") == "Pourquoi ?"
    assert typographie("Why ?", "en") == "Why ?"
    mots = mots_riches("Dans *63 pays*, dont la Chine")
    assert mots[:4] == [("Dans", False, False), ("63", True, False), ("pays", True, False), (",", False, True)]


def test_lecture_des_nombres():
    assert nombres("de 3,3 à 2,3 et 8 200 habitants en 1990", "fr") == [3.3, 2.3, 8200.0, 1990.0]
    assert nombres("from 3.3 to 2.3 and 8,200 people in 1990", "en") == [3.3, 2.3, 8200.0, 1990.0]


def test_sous_titres_equilibres():
    m = decouper_sous_titres("Dans 63 pays, dont la Chine, l'Allemagne et le Japon, la population a déjà atteint son maximum.")
    assert len(m) == 2 and all(len(x) <= 84 for x in m) and min(len(x) for x in m) > 25


# --------------------------------------------------------------------------- chargement de la fiche
def test_exemple_charge():
    fiche = charger_fiche(EXEMPLE)
    assert set(fiche.editions) == {"fr", "en"} and not fiche.est_validee


@pytest.mark.parametrize("modif, attendu", [
    (lambda b: b.pop("sources"), "sources"),
    (lambda b: b["editions"].pop("en"), "editions.en"),
    (lambda b: b["sources"][0].update(url="https://"), "url"),
    (lambda b: b["validation"].update(statut="ok"), "statut"),
    (lambda b: b["chiffre_cle"].update(valeur="8,2"), "nombre"),
    (lambda b: b["editions"]["fr"]["scenes"][0].update(texte="  "), "texte vide"),
    (lambda b: b["editions"]["fr"]["scenes"].append({"type": "video"}), "inconnu"),
])
def test_fiche_inexploitable(tmp_path, modif, attendu):
    brut = brut_exemple()
    modif(brut)
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(ecrire(tmp_path, brut))
    assert attendu in str(exc.value)


# --------------------------------------------------------------------------- contrôles qualité
def test_fiche_valide_sans_bloquant(tmp_path):
    bloquants, _ = constats(tmp_path, valider(brut_exemple()))
    assert bloquants == []


@pytest.mark.parametrize("validation, attendu", [
    ({"statut": "valide", "valide_par": "JG", "date": ""}, "date de validation est absente"),
    ({"statut": "valide", "valide_par": "JG", "date": "01/11/2026"}, "illisible"),
    ({"statut": "valide", "valide_par": "JG", "date": "2027-01-01"}, "futur"),
    ({"statut": "valide", "valide_par": "", "date": "2026-11-01"}, "valide_par"),
    ({"statut": "brouillon", "valide_par": "", "date": ""}, "non validée"),
])
def test_validation(tmp_path, validation, attendu):
    brut = brut_exemple()
    brut["validation"] = validation
    bloquants, _ = constats(tmp_path, brut)
    assert any(attendu in b for b in bloquants), bloquants


def test_brouillon_date_incoherente(tmp_path):
    brut = brut_exemple()
    brut["validation"] = {"statut": "brouillon", "valide_par": "JG", "date": "2026-11-01"}
    _, avert = constats(tmp_path, brut)
    assert any("incohérent" in a for a in avert)


def test_scenes_obligatoires(tmp_path):
    brut = valider(brut_exemple())
    brut["editions"]["en"]["scenes"] = [s for s in brut["editions"]["en"]["scenes"] if s["type"] != "fin"]
    bloquants, _ = constats(tmp_path, brut)
    assert any("[en]" in b and "« fin »" in b for b in bloquants)


def test_incoherences_chiffres(tmp_path):
    brut = valider(brut_exemple())
    brut["donnees"]["points"][2]["valeur"] = 1.2       # mis en avant ≠ chiffre clé (1 234 567)
    brut["editions"]["fr"]["scenes"][3]["texte"] = "En 2025, 8.2 % de plus."  # format anglais + nombre absent en EN
    _, avert = constats(tmp_path, brut)
    texte = " | ".join(avert)
    assert "mis en avant" in texte
    assert "format anglais" in texte
    assert "seulement FR" in texte


def test_annee_hors_periode(tmp_path):
    brut = valider(brut_exemple())
    brut["donnees"]["points"][0]["label"] = {"fr": "1990", "en": "1990"}
    _, avert = constats(tmp_path, brut)
    assert any("hors de la période" in a for a in avert)


def test_asterisques(tmp_path):
    brut = valider(brut_exemple())
    brut["editions"]["fr"]["titre"] = "Un *titre*"
    brut["editions"]["en"]["scenes"][0]["texte"] = "A *broken highlight"
    bloquants, _ = constats(tmp_path, brut)
    assert any("titre ou la légende" in b for b in bloquants)
    assert any("non fermé" in b for b in bloquants)


def test_source_consultee_dans_le_futur(tmp_path):
    brut = valider(brut_exemple())
    brut["sources"][0]["date_consultation"] = "2027-05-01"
    bloquants, _ = constats(tmp_path, brut)
    assert any("futur" in b for b in bloquants)


def test_limites_par_plateforme():
    r = Rapport()
    controler_plateformes("fr", 200, "x" * 100, "titre", 3, CHARTE, PLATEFORMES, r)
    noms = " ".join(str(c) for c in r.bloquants)
    assert "Instagram Reels" in noms and "YouTube Shorts" in noms and "TikTok" not in noms
    r = Rapport()
    controler_plateformes("fr", 75, "x", "titre", 3, CHARTE, PLATEFORMES, r)
    assert not r.bloquants and any("conseillée" in str(c) for c in r.avertissements)


# --------------------------------------------------------------------------- voix
def test_narration_synchronisee(tmp_path):
    fiche = charger_fiche(EXEMPLE)
    ed = fiche.editions["fr"]
    cache = Cache(tmp_path / "cache")
    n = produire_voix(fiche, ed, VoixTest({}, "fr"), cache, tmp_path / "t", {})
    assert not n.publiable and n.synthese > 0
    durees, _ = durees_avec_voix([2.0] * len(ed.scenes), n, [None] * len(ed.scenes))
    assert all(d >= vs.duree_voix for d, vs in zip(durees, n.scenes))
    piste = piste_complete(n, durees, tmp_path / "t")
    assert abs(duree_wav(piste) - sum(durees)) < 0.05
    reperes = reperes_sous_titres(n, durees)
    assert reperes[0][0] == pytest.approx(0.35)
    assert all(a[1] <= b[0] + 1e-6 for a, b in zip(reperes, reperes[1:]))  # aucun chevauchement
    debut = 0.0
    for vs, d in zip(n.scenes, durees):  # chaque sous-titre reste dans sa scène
        assert debut + 0.35 + vs.phrases[-1].fin <= debut + d + 1e-6
        debut += d
    # deuxième passage : tout vient du cache, rien n'est re-synthétisé (donc rien n'est refacturé)
    n2 = produire_voix(fiche, ed, VoixTest({}, "fr"), cache, tmp_path / "t2", {})
    assert n2.synthese == 0


def test_duree_imposee_trop_courte_allongee(tmp_path):
    fiche = charger_fiche(EXEMPLE)
    ed = fiche.editions["en"]
    n = produire_voix(fiche, ed, VoixTest({}, "en"), Cache(tmp_path / "c"), tmp_path / "t", {})
    durees, notes = durees_avec_voix([1.0] * len(ed.scenes), n, [1.0] * len(ed.scenes))
    assert notes and all(d > 1.0 for d in durees)


def test_fournisseurs_sans_cle():
    with pytest.raises(ErreurTTS, match="OPENAI_API_KEY"):
        creer_fournisseur("openai", {}, "fr").verifier()
    with pytest.raises(ErreurTTS, match="ELEVENLABS_API_KEY"):
        creer_fournisseur("elevenlabs", {}, "fr").verifier()
    with pytest.raises(ErreurTTS, match="inconnu"):
        creer_fournisseur("robot", {}, "fr")


def test_voix_manuelle(tmp_path):
    fiche = charger_fiche(EXEMPLE)
    ed = fiche.editions["fr"]
    dossier = tmp_path / "enregistrements"
    dossier.mkdir()
    for i in range(1, len(ed.scenes) + 1):
        VoixTest({}, "fr").synthetiser("phrase enregistrée " * i, dossier / f"{i:02d}.wav")
    n = produire_voix(fiche, ed, Manuel({}, "fr", dossier), Cache(tmp_path / "c"), tmp_path / "t", {})
    assert len(n.scenes) == len(ed.scenes) and n.publiable
    (dossier / "03.wav").unlink()
    with pytest.raises(ErreurTTS, match="scène 3"):
        produire_voix(fiche, ed, Manuel({}, "fr", dossier), Cache(tmp_path / "c"), tmp_path / "t", {})


# --------------------------------------------------------------------------- ligne de commande
def test_final_refuse_un_brouillon(tmp_path):
    r = lancer(EXEMPLE, "--mode", "final", "--voix", "test", "--sortie", tmp_path)
    assert r.returncode == 1
    assert not (tmp_path / "exemple-fictif/fr").exists()
    assert "BLOQUÉ" in (tmp_path / "exemple-fictif/rapport-qc.md").read_text()


def test_final_refuse_la_voix_de_test(tmp_path):
    f = ecrire(tmp_path, valider(brut_exemple()))
    r = lancer(f, "--mode", "final", "--voix", "test", "--sans-video", "--sortie", tmp_path / "s")
    assert r.returncode == 1
    assert "réservée aux tests" in (tmp_path / "s/exemple-fictif/rapport-qc.md").read_text()


def test_final_refuse_une_narration_manquante(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    f = ecrire(tmp_path, valider(brut_exemple()))
    r = lancer(f, "--mode", "final", "--voix", "openai", "--sans-video", "--sortie", tmp_path / "s")
    assert r.returncode == 1
    assert "Narration impossible" in (tmp_path / "s/exemple-fictif/rapport-qc.md").read_text()


def test_apercu_sans_voix_jamais_presente_comme_pret(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    r = lancer(EXEMPLE, "--voix", "openai", "--sans-video", "--sortie", tmp_path)
    assert r.returncode == 0  # l'aperçu se produit quand même…
    rapport = (tmp_path / "exemple-fictif/rapport-qc.md").read_text()
    assert "BLOQUÉ" in rapport and "SANS VOIX" in rapport  # …mais il est explicitement non publiable


def test_final_reussi_sans_voix_par_choix_editorial(tmp_path):
    brut = valider(brut_exemple())
    for langue in ("fr", "en"):
        brut["editions"][langue]["narration"] = False
    f = ecrire(tmp_path, brut)
    r = lancer(f, "--mode", "final", "--sans-video", "--sortie", tmp_path / "s")
    assert r.returncode == 0, r.stdout + r.stderr
    d = tmp_path / "s/exemple-fictif"
    assert len(list((d / "fr/carrousel").glob("*.png"))) == 6
    meta = json.loads((d / "en/metadonnees.json").read_text())
    assert meta["mode"] == "final" and meta["validation"]["statut"] == "valide"
    assert (tmp_path / "s/resume.md").exists()


def test_video_avec_voix_de_test(tmp_path):
    r = lancer(EXEMPLE, "--voix", "test", "--langues", "fr", "--sortie", tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    d = tmp_path / "exemple-fictif/fr"
    sonde = json.loads(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration", "-of", "json", str(d / "video.mp4")],
        capture_output=True, text=True).stdout)
    durees = {s["codec_type"]: float(s["duration"]) for s in sonde["streams"]}
    assert abs(durees["video"] - durees["audio"]) < 0.15
    srt = (d / "sous-titres.srt").read_text()
    assert srt.startswith("1\n00:00:00,350")
    for f in ("planche-video.png", "apercu-mobile.png", "zones-tiktok.png"):
        assert (d / "inspection" / f).exists()
