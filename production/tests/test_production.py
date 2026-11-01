"""Tests rapides : python -m pytest production/tests -q"""
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "production"))

from lmec.fiche import FicheInvalide, charger_fiche  # noqa: E402
from lmec.formatage import formater_chiffre, formater_nombre, typographie  # noqa: E402

EXEMPLE = RACINE / "contenus/exemples/exemple-fictif.yaml"
SCRIPT = RACINE / "production/produire.py"


def test_formatage_nombres():
    assert formater_nombre(8200000, "en") == "8,200,000"
    assert formater_nombre(8200000, "fr") == "8 200 000"
    assert formater_nombre(3.5, "fr") == "3,5"
    assert formater_nombre(3.5, "en") == "3.5"
    assert formater_nombre(2, "fr", 1) == "2,0"
    ch = {"valeur": 12.5, "suffixe": {"fr": " %", "en": "%"}}
    assert formater_chiffre(ch, "fr") == "12,5 %"
    assert formater_chiffre(ch, "en") == "12.5%"


def test_typographie_francaise():
    assert typographie("Pourquoi ?", "fr") == "Pourquoi ?"
    assert typographie("Why ?", "en") == "Why ?"


def test_exemple_charge():
    fiche = charger_fiche(EXEMPLE)
    assert set(fiche.editions) == {"fr", "en"}
    assert not fiche.est_validee


def test_fiche_incomplete_refusee(tmp_path):
    brut = yaml.safe_load(EXEMPLE.read_text(encoding="utf-8"))
    del brut["sources"]
    del brut["editions"]["en"]
    f = tmp_path / "f.yaml"
    f.write_text(yaml.safe_dump(brut, allow_unicode=True), encoding="utf-8")
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(f)
    assert "sources" in str(exc.value) and "editions.en" in str(exc.value)


def test_fiche_non_validee_bloquee(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), str(EXEMPLE), "--sortie", str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 1
    assert not (tmp_path / "exemple-fictif").exists()


def test_production_carrousel(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), str(EXEMPLE), "--sortie", str(tmp_path),
                        "--brouillon-autorise", "--sans-video"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    for langue in ("fr", "en"):
        d = tmp_path / "exemple-fictif" / langue
        assert len(list((d / "carrousel").glob("*.png"))) == 6
        for nom in ("legende.txt", "sous-titres.srt", "metadonnees.json", "script-voix-off.txt"):
            assert (d / nom).stat().st_size > 0
