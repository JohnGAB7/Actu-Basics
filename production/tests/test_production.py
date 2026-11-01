"""Tests : python -m pytest production/tests -q

Tous les tests tournent sans clé d'API ni modèle de voix (fournisseur « test »).
"""
import copy
import datetime as dt
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "production"))

from lmec.fiche import FicheInvalide, charger_fiche  # noqa: E402
from lmec.formatage import formater_chiffre, formater_nombre, typographie  # noqa: E402
from lmec.narration import durees_avec_voix, piste_complete, produire_voix, reperes_sous_titres  # noqa: E402
from lmec.qc import BLOQUANT, Rapport, controler_fiche, controler_plateformes, lire_unite, nombres  # noqa: E402
from lmec.rendu import mots_riches  # noqa: E402
from lmec.textes import decouper_sous_titres  # noqa: E402
from lmec.tts import Cache, ErreurTTS, Manuel, OpenAI, Piper, VoixTest, creer_fournisseur, duree_wav  # noqa: E402

EXEMPLE = RACINE / "contenus/exemples/exemple-fictif.yaml"
SCRIPT = RACINE / "production/produire.py"
FICHE_REELLE = RACINE / "contenus/fiches/2026-11-pic-population-mondiale.yaml"   # lue, jamais modifiée
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


CACHE_TESTS = tempfile.mkdtemp(prefix="lmec-cache-tests-")   # n'écrit jamais dans le .cache-tts du dépôt


def lancer(*args):
    env = dict(os.environ, LMEC_CACHE_TTS=CACHE_TESTS)
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, env=env)


def fiche_reelle():
    return yaml.safe_load(FICHE_REELLE.read_text(encoding="utf-8"))


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


# Structures mal formées et mauvais types : toujours une FicheInvalide lisible, jamais un plantage
@pytest.mark.parametrize("modif, attendu", [
    (lambda b: b.update(validation="valide"), "validation doit être un bloc"),
    (lambda b: b.update(chiffre_cle=[10.3]), "chiffre_cle doit être un bloc"),
    (lambda b: b["chiffre_cle"].update(valeur=True), "chiffre_cle.valeur doit être un nombre"),
    (lambda b: b["chiffre_cle"].update(decimales="1"), "decimales doit être un nombre entier"),
    (lambda b: b["chiffre_cle"].update(unite=["habitants"]), "chiffre_cle.unite doit être un texte"),
    (lambda b: b["chiffre_cle"].update(unite={"fr": "habitants", "es": "habitantes"}), "langue(s) inconnue(s)"),
    (lambda b: b.update(contexte="2025"), "contexte doit être un bloc"),
    (lambda b: b.update(sources={"nom": "x", "url": "https://x.org"}), "sources doit être une liste"),
    (lambda b: b.update(sources=["https://x.org"]), "sources[0] doit être un bloc"),
    (lambda b: b["donnees"].update(points={"a": 1}), "donnees.points doit être une liste"),
    (lambda b: b["donnees"]["points"].append(3.2), "donnees.points[4] doit être un bloc"),
    (lambda b: b["donnees"]["points"][0].pop("label"), "« label » manquant"),
    (lambda b: b["donnees"]["points"][0].update(mis_en_avant="oui"), "mis_en_avant doit valoir true ou false"),
    (lambda b: b.update(editions=["fr", "en"]), "editions doit être un bloc"),
    (lambda b: b["editions"].update(fr="texte"), "editions.fr doit être un bloc"),
    (lambda b: b["editions"]["fr"].update(scenes="accroche"), "editions.fr.scenes doit être une liste"),
    (lambda b: b["editions"]["fr"]["scenes"].insert(0, "accroche"), "scenes[0] doit être un bloc"),
    (lambda b: b["editions"]["fr"]["scenes"][0].update(texte=["a", "b"]), "texte doit être un texte"),
    (lambda b: b["editions"]["fr"]["scenes"][0].update(duree="3 s"), "duree doit être un nombre"),
    (lambda b: b["editions"]["fr"].update(hashtags="donnees"), "hashtags doit être une liste"),
    (lambda b: b["editions"]["fr"].update(hashtags=[{"a": 1}]), "n'est pas un mot-clé"),
    (lambda b: b["editions"]["fr"].update(narration="non"), "narration doit valoir true ou false"),
    (lambda b: b["editions"]["fr"].update(titre={"fr": "x"}), "titre doit être un texte"),
])
def test_types_incorrects_messages_explicites(tmp_path, modif, attendu):
    brut = brut_exemple()
    modif(brut)
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(ecrire(tmp_path, brut))
    assert attendu in str(exc.value), str(exc.value)


@pytest.mark.parametrize("contenu, attendu", [
    ("", "le fichier est vide"),
    ("- id: x\n- theme: y\n", "doit être un dictionnaire"),
    ("id: x\nvalidation:\n  statut: valide\n   date: 2026", "ligne 4"),
    ("id: \"x\ntheme: y\n", "YAML illisible"),
])
def test_yaml_mal_forme(tmp_path, contenu, attendu):
    f = tmp_path / "f.yaml"
    f.write_text(contenu, encoding="utf-8")
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(f)
    assert attendu in str(exc.value), str(exc.value)


def test_aucun_plantage_sur_des_valeurs_quelconques(tmp_path):
    """Remplace chaque champ de la fiche réelle par des valeurs de types variés :
    seules FicheInvalide (message lisible) ou un chargement réussi sont acceptables."""
    base = fiche_reelle()
    valeurs = [None, 0, -3, 1.5, True, "", "x", [], [1, "a"], {}, {"fr": None}, {"fr": [1]}, dt.date(2026, 1, 1),
               dt.datetime(2026, 1, 1, 12, 0), float("nan"), float("inf")]

    def chemins(o, p=()):
        if p:
            yield p
        enfants = o.items() if isinstance(o, dict) else enumerate(o) if isinstance(o, list) else []
        for k, v in enfants:
            yield from chemins(v, p + (k,))

    f = tmp_path / f"{base['id']}.yaml"
    for chemin in chemins(base):
        for v in valeurs:
            b = copy.deepcopy(base)
            o = b
            for k in chemin[:-1]:
                o = o[k]
            o[chemin[-1]] = copy.deepcopy(v)
            f.write_text(yaml.safe_dump(b, allow_unicode=True), encoding="utf-8")
            try:
                controler_fiche(charger_fiche(f), Rapport(), AUJOURD_HUI)
            except FicheInvalide:
                pass
            except Exception as exc:  # pragma: no cover - le test échoue avec le détail
                pytest.fail(f"{'.'.join(map(str, chemin))} = {v!r} : {type(exc).__name__} : {exc}")


def test_fiche_mal_formee_sans_trace_python(tmp_path):
    f = tmp_path / "f.yaml"
    f.write_text("id: f\neditions: [fr, en]\n", encoding="utf-8")
    res = lancer(f, "--verifier")
    assert res.returncode == 1
    assert "Traceback" not in res.stdout + res.stderr and "editions doit être un bloc" in res.stdout


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
    brut["donnees"]["points"][2]["valeur"] = 1.5       # 1,5 million mis en avant ≠ chiffre clé (1 234 567)
    brut["editions"]["fr"]["scenes"][3]["texte"] = "En 2025, 8.2 % de plus."  # format anglais + nombre absent en EN
    _, avert = constats(tmp_path, brut)
    texte = " | ".join(avert)
    assert "mis en avant" in texte
    assert "format anglais" in texte
    assert "seulement FR" in texte


# Cohérence chiffre clé / graphique / unités / périodes
def test_lecture_des_unites():
    assert lire_unite("milliards d'humains", "fr") == ("valeur", 1e9)
    assert lire_unite("billion people", "en") == ("valeur", 1e9)
    assert lire_unite("billions d'euros", "fr") == ("valeur", 1e12)   # faux ami
    assert lire_unite(" %", "fr") == ("pourcentage", 1.0)
    assert lire_unite("per 1,000 people", "en") == ("pour_mille", 1.0)
    assert lire_unite("habitants", "fr") == ("valeur", None)            # échelle inconnue, pas supposée


def test_fiche_reelle_coherente_sans_tout_affirmer(tmp_path):
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, fiche_reelle(), "2026-11-pic-population-mondiale")), r, AUJOURD_HUI)
    assert [str(c) for c in r.bloquants] == ["Fiche non validée (statut « brouillon ») : aucun rendu final possible"]
    # Ne dépend pas du contenu éditorial de la fiche (qui peut changer de graphique) :
    brut = fiche_reelle()
    mis_en_avant = [p["valeur"] for p in brut["donnees"]["points"] if p.get("mis_en_avant")]
    egal = mis_en_avant == [brut["chiffre_cle"]["valeur"]]
    assert ("Chiffre clé égal au point mis en avant du graphique" in r.ok) == egal
    # la machine ne prétend pas avoir vérifié la grandeur mesurée : c'est renvoyé à l'humain
    assert any("même grandeur" in a for a in r.a_verifier)


def test_unite_differente_fr_en_bloque(tmp_path):
    brut = valider(fiche_reelle())
    brut["chiffre_cle"]["unite"]["en"] = "million people at the peak"     # milliards ≠ million
    bloquants, _ = constats(tmp_path, brut)
    assert any("Unité du chiffre clé différente entre FR et EN" in b for b in bloquants)
    brut = valider(fiche_reelle())
    brut["chiffre_cle"]["unite"]["en"] = "trillion people at the peak"    # « billion » fr = trillion
    brut["chiffre_cle"]["unite"]["fr"] = "billions d'humains au maximum"
    bloquants, _ = constats(tmp_path, brut)
    assert not any("Unité du chiffre clé" in b for b in bloquants)


def test_unite_du_graphique_differente_fr_en_bloque(tmp_path):
    brut = valider(fiche_reelle())
    brut["donnees"]["unite"]["en"] = "World population, millions"
    bloquants, _ = constats(tmp_path, brut)
    assert any("Unité du graphique différente" in b for b in bloquants)


def test_echelles_differentes_chiffre_et_graphique(tmp_path):
    # même nombre, échelles différentes : 10,3 milliards ≠ 10,3 millions → alerte, pas de faux « cohérent »
    brut = valider(fiche_reelle())
    brut["donnees"]["unite"] = {"fr": "Population mondiale, en millions", "en": "World population, millions"}
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, brut, brut["id"])), r, AUJOURD_HUI)
    assert any("ne correspond pas au chiffre clé" in str(c) for c in r.avertissements)
    assert not any(o.startswith("Chiffre clé égal") for o in r.ok)
    # nombres différents mais même grandeur après conversion : accepté, et dit comme tel
    brut["donnees"]["points"][1]["valeur"] = 10300
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, brut, brut["id"])), r, AUJOURD_HUI)
    assert any("après conversion d'échelle" in o for o in r.ok)


def test_pourcentage_contre_valeur(tmp_path):
    brut = valider(fiche_reelle())
    brut["chiffre_cle"].update(valeur=10.3, suffixe={"fr": " %", "en": "%"},
                               unite={"fr": "de la population", "en": "of the population"})
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, brut, brut["id"])), r, AUJOURD_HUI)
    assert any("pas la même nature d'unité" in str(c) for c in r.avertissements)
    assert not any(o.startswith("Chiffre clé égal") for o in r.ok)


def test_pourcentage_hors_bornes(tmp_path):
    brut = valider(fiche_reelle())
    brut["chiffre_cle"].update(valeur=130, suffixe={"fr": " %", "en": "%"})
    _, avert = constats(tmp_path, brut)
    assert any("hors de 0–100" in a for a in avert)


def test_periode_differente_fr_en_bloque(tmp_path):
    brut = valider(fiche_reelle())
    brut["contexte"]["periode"]["en"] = "2024–2050 (projection)"
    bloquants, _ = constats(tmp_path, brut)
    assert any("Période différente entre FR" in b for b in bloquants)


def test_periode_sans_annee_non_presentee_comme_verifiee(tmp_path):
    brut = valider(fiche_reelle())
    brut["contexte"]["periode"] = {"fr": "projection", "en": "projection"}
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, brut, brut["id"])), r, AUJOURD_HUI)
    assert any("aucune année" in str(c) for c in r.avertissements)
    assert any("période sans année" in a for a in r.a_verifier)
    assert not any("comprises dans la période" in o for o in r.ok)


def test_annee_du_chiffre_hors_periode(tmp_path):
    brut = valider(fiche_reelle())
    brut["editions"]["en"]["scenes"][1]["texte"] = "That's the UN's expected peak, around 2120."
    _, avert = constats(tmp_path, brut)
    assert any("[en]" in a and "2120" in a and "chiffre clé" in a for a in avert)


def test_annees_des_libelles_differentes_fr_en(tmp_path):
    brut = valider(fiche_reelle())
    brut["donnees"]["points"][0]["label"] = {"fr": "2024", "en": "2023"}
    bloquants, _ = constats(tmp_path, brut)
    assert any("années différentes entre FR" in b for b in bloquants)


def test_plusieurs_points_mis_en_avant_et_arrondi(tmp_path):
    brut = valider(fiche_reelle())
    brut["donnees"]["points"][0]["mis_en_avant"] = True
    brut["donnees"]["points"][-1]["valeur"] = 10.25
    _, avert = constats(tmp_path, brut)
    assert any("2 points mis en avant" in a for a in avert)
    assert any("arrondies" in a for a in avert)


def test_rapport_liste_ce_qui_n_est_pas_verifie(tmp_path):
    brut = valider(brut_exemple())
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, brut)), r, AUJOURD_HUI)
    from lmec.qc import ecrire_rapport
    texte_rapport = (ecrire_rapport(charger_fiche(ecrire(tmp_path, brut)), r, tmp_path / "r.md", "final"),
                     (tmp_path / "r.md").read_text(encoding="utf-8"))[1]
    assert "n'a **pas** pu vérifier" in texte_rapport and "même grandeur" in texte_rapport


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


@pytest.mark.parametrize("valeur", [
    dt.datetime(2026, 10, 15, 9, 30),          # YAML : 2026-10-15 09:30:00 → datetime
    "2026-10-15T09:30:00Z",
    "2026-10-15 09:30:00",
])
def test_date_de_consultation_horodatee(tmp_path, valeur):
    brut = valider(brut_exemple())
    brut["sources"][0]["date_consultation"] = valeur
    bloquants, avert = constats(tmp_path, brut)
    assert bloquants == [] and not any("consultation" in a for a in avert)


def test_dates_horodatees_dans_le_futur_et_validation(tmp_path):
    brut = valider(brut_exemple())
    brut["sources"][0]["date_consultation"] = dt.datetime(2027, 1, 2, 8, 0)
    brut["validation"]["date"] = dt.datetime(2026, 11, 1, 18, 45)     # même jour, heure ignorée
    bloquants, _ = constats(tmp_path, brut)
    assert any("futur" in b and "consultation" in b.lower() for b in bloquants), bloquants
    assert not any("validation" in b.lower() and "futur" in b for b in bloquants)
    # écrit tel quel en YAML (sans guillemets), comme le ferait un humain
    f = ecrire(tmp_path, valider(brut_exemple()))
    f.write_text(f.read_text(encoding="utf-8").replace("date_consultation: '2026-11-01'",
                                                       "date_consultation: 2026-10-15 09:30:00"), encoding="utf-8")
    assert isinstance(yaml.safe_load(f.read_text(encoding="utf-8"))["sources"][0]["date_consultation"], dt.datetime)
    r = Rapport()
    controler_fiche(charger_fiche(f), r, AUJOURD_HUI)
    assert not r.bloquants


def test_controle_avec_un_aujourd_hui_horodate(tmp_path):
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, valider(brut_exemple()))), r, dt.datetime(2026, 11, 1, 23, 59))
    assert not r.bloquants


@pytest.mark.parametrize("chemin, yaml_brut", [
    (("chiffre_cle", "valeur"), ".nan"),
    (("chiffre_cle", "valeur"), ".inf"),
    (("chiffre_cle", "valeur"), "-.inf"),
    (("donnees", "points", 0, "valeur"), ".nan"),
    (("donnees", "points", 1, "valeur"), ".Inf"),
])
def test_nan_et_infini_refuses(tmp_path, chemin, yaml_brut):
    brut = brut_exemple()
    o = brut
    for k in chemin[:-1]:
        o = o[k]
    o[chemin[-1]] = "@@VALEUR@@"
    f = ecrire(tmp_path, brut)
    f.write_text(f.read_text(encoding="utf-8").replace("'@@VALEUR@@'", yaml_brut), encoding="utf-8")
    lu = yaml.safe_load(f.read_text(encoding="utf-8"))
    for k in chemin:
        lu = lu[k]
    assert isinstance(lu, float) and not math.isfinite(lu)      # YAML a bien lu NaN / infini
    with pytest.raises(FicheInvalide, match="nombre fini"):
        charger_fiche(f)


def test_source_consultee_dans_le_futur(tmp_path):
    brut = valider(brut_exemple())
    brut["sources"][0]["date_consultation"] = "2027-05-01"
    bloquants, _ = constats(tmp_path, brut)
    assert any("futur" in b for b in bloquants)


def test_limites_par_plateforme():
    r = Rapport()
    controler_plateformes("fr", 200, "x" * 100, "titre", 3, CHARTE, PLATEFORMES, r)
    bloq = " ".join(str(c) for c in r.bloquants)
    avert = " ".join(str(c) for c in r.avertissements)
    assert "YouTube Shorts" in bloq                      # 3 min : limite officielle → bloquant
    assert "Instagram Reels" not in bloq and "Instagram Reels" in avert   # plafond interne → avertissement
    assert "TikTok" not in bloq
    r = Rapport()
    controler_plateformes("fr", 75, "x", "titre", 3, CHARTE, PLATEFORMES, r)
    assert not r.bloquants and any("conseillée" in str(c) for c in r.avertissements)


def test_chaque_limite_de_plateforme_a_une_reference():
    limites = ("duree_max_s", "duree_conseillee_s", "legende_max", "titre_max", "hashtags_max",
               "hashtags_conseilles", "zone_ui", "images_max")
    for cle, p in PLATEFORMES["plateformes"].items():
        refs = p.get("references") or {}
        for champ in limites:
            if champ not in p:
                continue
            ref = refs.get(champ)
            assert ref, f"{cle}.{champ} sans référence"
            assert ref["statut"] in ("officiel", "non_confirme", "estimation"), f"{cle}.{champ}"
            assert dt.date.fromisoformat(str(ref["verifie_le"])) <= dt.date.today(), f"{cle}.{champ}"
            if ref["statut"] != "estimation":
                assert str(ref.get("source", "")).startswith("https://"), f"{cle}.{champ} : source manquante"


def test_plafond_non_confirme_jamais_bloquant():
    r = Rapport()
    controler_plateformes("fr", 700, "x" * 2300, "t" * 120, 70, CHARTE, PLATEFORMES, r)
    for c in r.bloquants:   # chaque bloquant repose sur une limite marquée « officiel »
        assert "plafond interne" not in str(c)
    tiktok = [str(c) for c in r.constats if "TikTok : durée" in str(c)]
    reels = [str(c) for c in r.constats if "Instagram Reels : durée" in str(c)]
    assert tiktok and reels
    assert all(c in map(str, r.avertissements) and "plafond interne de production" in c for c in tiktok + reels)
    assert any("TikTok : légende" in str(c) for c in r.bloquants)       # 2 200 : officiel (API)
    assert any("YouTube Shorts : titre" in str(c) for c in r.bloquants)
    assert any("⚠️ durée (plafond interne)" in l[3] for l in r.plateformes if l[1] == "TikTok")
    # cohérence avec plateformes.yaml : les durées TikTok et Reels sont bien « non_confirme »
    for cle in ("tiktok", "instagram_reels"):
        assert PLATEFORMES["plateformes"][cle]["references"]["duree_max_s"]["statut"] == "non_confirme"


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


def test_cle_du_cache_texte_et_configuration(tmp_path):
    cle = Cache.cle
    base = OpenAI({"modele": "gpt-4o-mini-tts", "voix": "nova", "vitesse": 1.0}, "fr")
    assert cle(base, "Bonjour.") == cle(OpenAI({"voix": "nova", "vitesse": 1.0, "modele": "gpt-4o-mini-tts"}, "fr"),
                                        "Bonjour.")                       # ordre des clés indifférent
    differents = [
        cle(base, "Bonjour !"),                                             # texte
        cle(OpenAI({"modele": "gpt-4o-mini-tts", "voix": "coral", "vitesse": 1.0}, "fr"), "Bonjour."),  # voix
        cle(OpenAI({"modele": "gpt-4o-mini-tts", "voix": "nova", "vitesse": 1.1}, "fr"), "Bonjour."),   # vitesse
        cle(OpenAI({"modele": "tts-1", "voix": "nova", "vitesse": 1.0}, "fr"), "Bonjour."),             # modèle
        cle(OpenAI({"modele": "gpt-4o-mini-tts", "voix": "nova", "vitesse": 1.0, "consignes": "calme"}, "fr"),
            "Bonjour."),                                                    # consignes
        cle(OpenAI({"modele": "gpt-4o-mini-tts", "voix": "nova", "vitesse": 1.0}, "en"), "Bonjour."),   # langue
        cle(VoixTest({"modele": "gpt-4o-mini-tts", "voix": "nova", "vitesse": 1.0}, "fr"), "Bonjour."),  # fournisseur
    ]
    assert len(set(differents + [cle(base, "Bonjour.")])) == len(differents) + 1


def test_cle_du_cache_suit_le_modele_piper(tmp_path, monkeypatch):
    import lmec.tts as tts
    monkeypatch.setattr(tts, "DOSSIER_VOIX", tmp_path)
    modele = tmp_path / "fr.onnx"
    modele.write_bytes(b"a" * 10)
    p = Piper({"modele": "fr.onnx", "locuteur": None}, "fr")
    avant = Cache.cle(p, "Bonjour.")
    modele.write_bytes(b"b" * 20)          # modèle remplacé sous le même nom
    assert Cache.cle(p, "Bonjour.") != avant


def test_cache_lexique_et_nettoyage(tmp_path):
    fiche = charger_fiche(EXEMPLE)
    ed = fiche.editions["fr"]
    cache = Cache(tmp_path / "cache")
    produire_voix(fiche, ed, VoixTest({}, "fr"), cache, tmp_path / "t", {})
    # une règle de prononciation change le texte envoyé : nouvelle synthèse pour la phrase concernée
    n = produire_voix(fiche, ed, VoixTest({}, "fr"), cache, tmp_path / "t2", {"fr": {"Exempleville": "Exemple-ville"}})
    assert 0 < n.synthese < n.synthese + n.depuis_cache
    fichiers = list((tmp_path / "cache").glob("*.wav"))
    assert fichiers and not list((tmp_path / "cache").glob("*.tmp"))
    os.utime(fichiers[0], (0, 0))           # inutilisé depuis 1970
    assert cache.nettoyer(jours=90) == 1 and not fichiers[0].exists()


def test_workflows_persistent_le_cache():
    for nom in ("apercu.yml", "validation-finale.yml"):
        wf = yaml.safe_load((RACINE / ".github/workflows" / nom).read_text(encoding="utf-8"))
        etapes = next(iter(wf["jobs"].values()))["steps"]
        restaure = [e for e in etapes if str(e.get("uses", "")).startswith("actions/cache/restore")]
        sauve = [e for e in etapes if str(e.get("uses", "")).startswith("actions/cache/save")]
        assert restaure and sauve, nom
        assert restaure[0]["with"]["path"] == sauve[0]["with"]["path"] == ".cache-tts"
        assert sauve[0].get("if") == "always()", nom     # même en cas de refus : la voix payée est gardée
        assert restaure[0]["with"]["restore-keys"].startswith("tts-")


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


class _Reponse:
    def __init__(self, donnees):
        self.donnees = donnees

    def read(self):
        return self.donnees

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _wav_bref(chemin):
    VoixTest({}, "fr").synthetiser("Bonjour.", chemin)
    return chemin.read_bytes()


@pytest.mark.parametrize("nom, cle, config", [
    ("openai", "OPENAI_API_KEY", {"modele": "gpt-4o-mini-tts", "voix": "nova", "consignes": "calme", "vitesse": 1.05}),
    ("elevenlabs", "ELEVENLABS_API_KEY", {"voice_id": "abc123", "modele": "eleven_multilingual_v2"}),
])
def test_api_simulee_sans_appel_reel(tmp_path, monkeypatch, nom, cle, config):
    """Simulation des réponses de l'API (AUCUN appel réseau) : vérifie la requête envoyée et la
    gestion des erreurs. Ne prouve PAS que l'intégration fonctionne avec le vrai service."""
    import io
    import urllib.error
    import urllib.request
    monkeypatch.setenv(cle, "cle-factice")
    f = creer_fournisseur(nom, {"voix": {"fr": {nom: config}}}, "fr")
    envoyes = []
    audio = _wav_bref(tmp_path / "ref.wav")

    def repondre(req, timeout):
        envoyes.append(req)
        return _Reponse(audio)
    monkeypatch.setattr(urllib.request, "urlopen", repondre)
    f.synthetiser("Bonjour.", tmp_path / "ok.wav")
    assert duree_wav(tmp_path / "ok.wav") > 0
    corps = json.loads(envoyes[0].data)
    assert "cle-factice" not in envoyes[0].data.decode()          # la clé ne va que dans l'en-tête
    assert ("Bonjour." in (corps.get("input"), corps.get("text")))
    if nom == "openai":
        assert corps["voice"] == "nova" and corps["instructions"] == "calme" and corps["speed"] == 1.05
    else:
        assert "abc123" in envoyes[0].full_url and corps["model_id"] == "eleven_multilingual_v2"

    erreurs = [
        (urllib.error.HTTPError("u", 401, "Unauthorized", {}, io.BytesIO(b"invalid key")), "401"),
        (urllib.error.HTTPError("u", 429, "Too Many", {}, io.BytesIO(b"quota")), "429"),
        (urllib.error.URLError("hors ligne"), "Réseau indisponible"),
    ]
    for exc, attendu in erreurs:
        def lever(req, timeout, exc=exc):
            raise exc
        monkeypatch.setattr(urllib.request, "urlopen", lever)
        with pytest.raises(ErreurTTS, match=attendu):
            f.synthetiser("Bonjour.", tmp_path / "x.wav")
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: _Reponse(b"<html>erreur</html>"))
    with pytest.raises(ErreurTTS, match="Conversion audio impossible"):
        f.synthetiser("Bonjour.", tmp_path / "y.wav")


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
    for f in ("planche-video.png", "apercu-mobile.png", "zones-tiktok.png", "logo-mobile.png"):
        assert (d / "inspection" / f).exists()
    rapport = (tmp_path / "exemple-fictif/rapport-qc.md").read_text(encoding="utf-8")
    assert "Logo sombre (vidéo, scène 6 (fin))" in rapport and "Logo sombre (couverture" in rapport



# --------------------------------------------------------------------------- logo ACTU-BASICS
import hashlib  # noqa: E402

from lmec import logo as logo_mod  # noqa: E402
from lmec.qc import controler_logo, controler_marque  # noqa: E402
from lmec.rendu import Rendu  # noqa: E402

DOSSIER_LOGOS = RACINE / "assets/brand/actu-basics"


def _charte(**modifs):
    ch = copy.deepcopy(CHARTE)
    for chemin, valeur in modifs.items():
        o = ch
        cles = chemin.split("__")
        for k in cles[:-1]:
            o = o.setdefault(k, {})
        o[cles[-1]] = valeur
    return ch


def _empreintes():
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in DOSSIER_LOGOS.glob("logo-*")}


def _rendu_fin(charte, fmt="video", langue="fr"):
    fiche = charger_fiche(EXEMPLE)
    ed = fiche.editions[langue]
    r = Rendu(fiche, langue, charte, fmt, False)
    n = len(ed.scenes)
    im = r.dessiner(ed.scenes[-1], n - 1, n)
    return r, im, ed


def test_fichiers_logo_officiels_presents():
    from PIL import Image
    noms = set()
    for langue in ("fr", "en"):
        fichiers = logo_mod.fichiers_langue(CHARTE["logo"], langue)
        assert set(fichiers) == {"clair", "sombre"}
        for variante, candidats in fichiers.items():
            trouves = [c for c in candidats if (DOSSIER_LOGOS / c).is_file()]
            assert trouves, f"logo {langue} {variante} absent de {DOSSIER_LOGOS}"
            noms.add(trouves[0])
            im = Image.open(DOSSIER_LOGOS / trouves[0])
            assert im.mode == "RGBA" and im.width >= 400    # fond transparent autour du disque
    assert len(noms) == 4                                   # un fichier distinct par langue et par fond


def test_logo_choisi_selon_la_langue_et_le_fond():
    clair = dict(couleurs__fond="#F5F5F1", couleurs__fond_bas="#FFFFFF", couleurs__barre="#E8EEF5",
                 couleurs__texte="#06152B")
    attendu = {("fr", "sombre"): "logo-dark.png", ("fr", "clair"): "logo-light.png",
               ("en", "sombre"): "logo-dark-en.png", ("en", "clair"): "logo-light-en.png"}
    for langue in ("fr", "en"):
        for fond, ch in (("sombre", CHARTE), ("clair", _charte(**clair))):
            r, _, ed = _rendu_fin(ch, "carrousel", langue)
            pose = r.poses[("carrousel", len(ed.scenes) - 1)]
            assert pose.variante == fond
            assert r.logos.chemins[pose.variante].name == attendu[(langue, fond)]
            rap = Rapport()
            controler_logo(langue, r, [("carrousel", len(ed.scenes) - 1, "fin")], ch, PLATEFORMES, rap)
            assert not rap.bloquants, [str(c) for c in rap.bloquants]
    # logo d'une autre langue : bloquant
    r, _, ed = _rendu_fin(CHARTE, "video", "fr")
    rap = Rapport()
    controler_logo("en", r, [("video", len(ed.scenes) - 1, "fin")], CHARTE, PLATEFORMES, rap)
    assert any("Logo de la langue « fr »" in str(c) for c in rap.bloquants)


def test_logo_anglais_absent_bloque(tmp_path):
    import shutil
    for f in DOSSIER_LOGOS.glob("logo-*.png"):
        if "-en" not in f.name:
            shutil.copy(f, tmp_path / f.name)
    rap = Rapport()
    controler_marque(_charte(logo__dossier=str(tmp_path)), rap)
    assert any("[en]" in str(c) and "introuvable" in str(c) for c in rap.bloquants)
    assert not any("[fr]" in str(c) for c in rap.bloquants)


def test_logo_unique_toutes_langues_accepte():
    """Ancien format (fichiers.<variante>) : le même logo pour toutes les langues."""
    ch = _charte(logo__fichiers={"clair": ["logo-light.png"], "sombre": ["logo-dark.png"]})
    assert logo_mod.charger_logos(ch["logo"], "en").chemins["sombre"].name == "logo-dark.png"


def test_logo_lisible_sur_mobile():
    for langue in ("fr", "en"):
        for fmt in ("video", "carrousel"):
            r, _, ed = _rendu_fin(CHARTE, fmt, langue)
            rap = Rapport()
            controler_logo(langue, r, [(fmt, len(ed.scenes) - 1, "fin")], CHARTE, PLATEFORMES, rap)
            assert not any("peu lisible" in str(c) for c in rap.avertissements), (langue, fmt)
    ch = _charte(logo__video={"scenes": ["fin"], "largeur_px": 280, "largeur_min_px": 200, "slogan": False})
    r, _, ed = _rendu_fin(ch, "video", "en")
    rap = Rapport()
    controler_logo("en", r, [("video", len(ed.scenes) - 1, "fin")], ch, PLATEFORMES, rap)
    assert any("Slogan du logo peu lisible" in str(c) for c in rap.avertissements)


def test_logo_discret_en_video_sans_slogan_ajoute():
    for langue in ("fr", "en"):
        r, im, ed = _rendu_fin(CHARTE, "video", langue)
        pose = r.poses[("video", len(ed.scenes) - 1)]
        assert pose.largeur <= 420                                          # discret (440 px avant)
        assert pose.largeur * 390 / 1080 >= logo_mod.LARGEUR_MOBILE_MIN       # mais lisible sur téléphone
        sans = _charte(logo__video__slogan=True)
        r2, im2, _ = _rendu_fin(sans, "video", langue)
        assert im.tobytes() != im2.tobytes()          # le slogan écrit sous le logo est bien désactivé


def test_slogans_et_marque_officiels():
    assert CHARTE["slogan"] == {"fr": "Éveiller par les chiffres.", "en": "Enlightening through numbers."}
    assert CHARTE["slogan"] == logo_mod.SLOGANS_OFFICIELS
    assert CHARTE["marque"] == {"fr": "ACTU-BASICS", "en": "ACTU-BASICS"}
    r = Rapport()
    controler_marque(_charte(slogan={"fr": "Éveiller par les chiffres", "en": "Enlightening through numbers."}), r)
    assert any("Slogan FR" in str(c) for c in r.bloquants)


def test_logo_sur_fond_sombre_proportions_et_original_intact():
    avant = _empreintes()
    for fmt in ("video", "carrousel"):
        r, im, ed = _rendu_fin(CHARTE, fmt)
        pose = r.poses[(fmt, len(ed.scenes) - 1)]
        assert pose.variante == "sombre" and pose.luminance_fond < 0.5
        x0, y0, x1, y1 = pose.boite
        source = logo_mod._ouvrir(str(r.logos.chemins["sombre"]))
        assert abs((y1 - y0) / (x1 - x0) - source.height / source.width) < 0.01      # jamais déformé
        assert pose.recouvrement <= logo_mod.SEUIL_RECOUVREMENT                       # rien dans sa zone
        assert pose.largeur <= pose.largeur_native                                    # jamais agrandi
        rap = Rapport()
        controler_logo("fr", r, [(fmt, len(ed.scenes) - 1, "fin")], CHARTE, PLATEFORMES, rap)
        assert not rap.bloquants and not rap.avertissements, [str(c) for c in rap.constats]
    assert _empreintes() == avant                                                     # fichiers d'origine intacts


def test_logo_clair_sur_fond_clair():
    ch = _charte(couleurs__fond="#F5F5F1", couleurs__fond_bas="#FFFFFF", couleurs__barre="#E8EEF5",
                 couleurs__texte="#06152B")
    r, _, ed = _rendu_fin(ch, "carrousel")
    pose = r.poses[("carrousel", len(ed.scenes) - 1)]
    assert pose.variante == "clair" and pose.luminance_fond >= 0.5


def test_variante_forcee_contraire_au_fond_bloque():
    ch = _charte(logo__variante="clair")
    r, _, ed = _rendu_fin(ch)
    rap = Rapport()
    controler_logo("fr", r, [("video", len(ed.scenes) - 1, "fin")], ch, PLATEFORMES, rap)
    assert any("variante sombre" in str(c) for c in rap.bloquants)


@pytest.mark.parametrize("position", logo_mod.POSITIONS)
def test_positions_configurables_sans_recouvrement(position):
    """Couverture : le logo est ancré dans la zone de sécurité et le texte lui laisse la place."""
    ch = _charte(logo__couverture={"actif": True, "position": position, "largeur_px": 240, "marge_px": 20})
    fiche = charger_fiche(FICHE_REELLE)
    ed = fiche.editions["fr"]
    r = Rendu(fiche, "fr", ch, "video", False)
    r.dessiner(ed.scenes[0], 0, len(ed.scenes), couverture=True)
    pose = r.poses[("couverture", 0)]
    g, h, d, b = r.zone
    x0, y0, x1, y1 = pose.boite
    assert g + 20 <= x0 and x1 <= d - 20 and h + 20 <= y0 and y1 <= b - 20
    if position != "centre":   # au centre, le logo ne peut que gêner l'accroche : contrôle qualité
        assert pose.recouvrement <= logo_mod.SEUIL_RECOUVREMENT, position
    else:
        rap = Rapport()
        controler_logo("fr", r, [("couverture", 0, "accroche")], ch, PLATEFORMES, rap)
        assert any("touche un texte" in str(c) for c in rap.bloquants)


def test_taille_et_marge_configurables():
    ch = _charte(logo__video={"scenes": ["fin"], "largeur_px": 360, "largeur_min_px": 200, "slogan": False})
    r, _, ed = _rendu_fin(ch)
    pose = r.poses[("video", len(ed.scenes) - 1)]
    assert pose.largeur == 360


def test_logo_agrandi_et_petit_sur_mobile_signales(tmp_path):
    # Copie réduite (dossier temporaire de test, jamais dans le dépôt) pour simuler un fichier trop petit.
    from PIL import Image
    for f in DOSSIER_LOGOS.glob("logo-*.png"):
        Image.open(f).resize((300, 300)).save(tmp_path / f.name)
    ch = _charte(logo__dossier=str(tmp_path),
                 logo__video={"scenes": ["fin"], "largeur_px": 440, "largeur_min_px": 400})
    r, _, ed = _rendu_fin(ch)
    rap = Rapport()
    controler_logo("fr", r, [("video", len(ed.scenes) - 1, "fin")], ch, PLATEFORMES, rap)
    assert any("agrandi au-delà de sa résolution" in str(c) for c in rap.avertissements)
    ch = _charte(logo__couverture={"actif": True, "position": "haut_droite", "largeur_px": 150, "marge_px": 0})
    fiche = charger_fiche(EXEMPLE)
    r = Rendu(fiche, "fr", ch, "video", False)
    r.dessiner(fiche.editions["fr"].scenes[0], 0, 6, couverture=True)
    rap = Rapport()
    controler_logo("fr", r, [("couverture", 0, "accroche")], ch, PLATEFORMES, rap)
    assert any("petit sur téléphone" in str(c) for c in rap.avertissements)


def test_logo_absent_jamais_remplace(tmp_path):
    ch = _charte(logo__dossier="assets/brand/inexistant")
    rap = Rapport()
    controler_marque(ch, rap)
    assert any("Logo officiel introuvable" in str(c) and "Aucun logo de substitution" in str(c) for c in rap.bloquants)
    r, im, ed = _rendu_fin(ch)
    assert r.poses == {}                                  # rien n'est dessiné à la place du logo
    # rendu final refusé avant toute production
    f = ecrire(tmp_path, valider(brut_exemple()))
    charte = tmp_path / "charte.yaml"
    charte.write_text(yaml.safe_dump(ch, allow_unicode=True), encoding="utf-8")
    res = lancer(f, "--mode", "final", "--voix", "test", "--sans-video", "--charte", charte, "--sortie", tmp_path / "s")
    assert res.returncode == 1 and "Logo officiel introuvable" in res.stdout
    assert not (tmp_path / "s/exemple-fictif/fr").exists()


def test_logo_desactivable():
    ch = _charte(logo__actif=False)
    r, _, _ = _rendu_fin(ch)
    assert r.poses == {}
    rap = Rapport()
    controler_marque(ch, rap)
    assert any("Logo désactivé" in str(c) for c in rap.avertissements)


def test_logo_absent_alors_que_prevu_bloque():
    r, _, ed = _rendu_fin(CHARTE)
    r.poses.clear()
    rap = Rapport()
    controler_logo("fr", r, [("video", len(ed.scenes) - 1, "fin")], CHARTE, PLATEFORMES, rap)
    assert any("Logo absent" in str(c) for c in rap.bloquants)


def test_ancienne_signature_signalee(tmp_path):
    _, avert = constats(tmp_path, valider(fiche_reelle()))
    assert not any("ancienne signature" in a for a in avert)          # fiche corrigée
    brut = valider(fiche_reelle())
    brut["editions"]["fr"]["scenes"][-1]["texte"] = "Abonnez-vous pour comprendre le monde, un chiffre à la fois."
    _, avert = constats(tmp_path, brut)
    assert any("ancienne signature" in a and "Éveiller par les chiffres." in a for a in avert)


def test_aucune_ancienne_signature_dans_les_contenus():
    for f in list((RACINE / "contenus").rglob("*.yaml")):
        texte = f.read_text(encoding="utf-8").lower()
        for ancienne in logo_mod.ANCIENNES_SIGNATURES[2:]:
            assert ancienne not in texte, f"{f.name} : « {ancienne} »"


# --------------------------------------------------------------------------- fiches pédagogiques
from lmec import pedagogie  # noqa: E402
from lmec.formules import formule_valide  # noqa: E402

LANCEMENT = RACINE / "contenus/fiches/2026-11-lancement-actu-basics.yaml"


def brut_lancement():
    return yaml.safe_load(LANCEMENT.read_text(encoding="utf-8"))


def constats_pedago(tmp_path, brut):
    r = Rapport()
    controler_fiche(charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics")), r, AUJOURD_HUI)
    return r


def test_fiche_de_lancement_chargee_et_calculs_justes(tmp_path):
    fiche = charger_fiche(LANCEMENT)
    assert fiche.pedagogique and fiche.format == "educational" and fiche.format_image == "video"
    assert fiche.famille == "presentation" and fiche.habillage_sonore
    r = constats_pedago(tmp_path, valider(brut_lancement()))
    assert not r.bloquants, [str(c) for c in r.bloquants]
    recalcules = [o for o in r.ok if "recalculé" in o]
    assert len(recalcules) >= 2 * 9                           # chaque nombre annoncé est recalculé
    assert any("Chaque exercice a sa correction" in o for o in r.ok)


def test_calcul_faux_bloque(tmp_path):
    brut = valider(brut_lancement())
    scene = next(s for s in brut["editions"]["fr"]["scenes"] if s["type"] == "chiffre")
    scene["verifier"][0]["attendu"] = 60.7                    # faute de frappe dans le résultat
    r = constats_pedago(tmp_path, brut)
    assert any("annoncé 60.7, recalculé 50.7" in str(c) for c in r.bloquants)


def test_exercice_sans_correction_bloque(tmp_path):
    brut = valider(brut_lancement())
    brut["editions"]["en"]["scenes"] = [s for s in brut["editions"]["en"]["scenes"] if s["type"] != "correction"]
    r = constats_pedago(tmp_path, brut)
    assert any("exercice(s) sans correction" in str(c) for c in r.bloquants)


def test_scenes_pedagogiques_refusees_dans_une_fiche_actualite(tmp_path):
    brut = valider(brut_exemple())
    brut["editions"]["fr"]["scenes"].insert(1, {"type": "formule", "texte": "x", "formule": "a=b", "voix_off": "a"})
    with pytest.raises(FicheInvalide, match="réservé aux fiches pédagogiques"):
        charger_fiche(ecrire(tmp_path, brut))


def test_fiche_pedagogique_incomplete(tmp_path):
    brut = valider(brut_lancement())
    del brut["pedagogie"]["objectifs"]
    scene = next(s for s in brut["editions"]["fr"]["scenes"] if s["type"] == "formule")
    del scene["voix_off"]
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics"))
    assert "pedagogie.objectifs" in str(exc.value) and "voix_off" in str(exc.value)


def test_formule_illisible_bloque(tmp_path):
    assert formule_valide(r"\frac{1}{2}") is None
    assert formule_valide(r"\frac{1") is not None
    brut = valider(brut_lancement())
    scene = next(s for s in brut["editions"]["fr"]["scenes"] if s["type"] == "formule")
    scene["formule"] = [r"\frac{365"]
    r = constats_pedago(tmp_path, brut)
    assert any("formule illisible" in str(c) for c in r.bloquants)


@pytest.mark.parametrize("expression", ['__import__("os")', "().__class__", 'open("x")', "10**10**10",
                                        "range(10**9)", "comb(10**9, 3)", "lambda: 1", '"a" * 10**8',
                                        "factorial(10**6)", "x"])
def test_evaluateur_refuse_le_dangereux(expression):
    with pytest.raises(pedagogie.CalculInvalide):
        pedagogie.evaluer(expression)


def test_evaluateur_et_courbe():
    assert pedagogie.evaluer("comb(23, 2)") == 253
    assert abs(pedagogie.evaluer("1 - prod((365 - k) / 365 for k in range(23))") - 0.5073) < 1e-4
    assert pedagogie.tolerance_par_defaut(0.507) == pytest.approx(0.0005)
    assert pedagogie.tolerance_par_defaut(253) == pytest.approx(0.5)
    pts = pedagogie.points_courbe({"variable": "n", "de": 1, "a": 70, "expression": "n * 2"})
    assert len(pts) == 70 and pts[-1] == (70, 140)


@pytest.mark.parametrize("fmt", ["video", "lecon"])
def test_rendu_des_scenes_pedagogiques(fmt):
    fiche = charger_fiche(LANCEMENT)
    for langue in ("fr", "en"):
        ed = fiche.editions[langue]
        r = Rendu(fiche, langue, CHARTE, fmt, False)
        for i, s in enumerate(ed.scenes):
            im = r.dessiner(s, i, len(ed.scenes))
            assert im.size == ((1080, 1920) if fmt == "video" else (1920, 1080))
            for t in (0.0, 0.7, r.duree_animation(s)):              # animations sans erreur
                r.dessiner(s, i, len(ed.scenes), t)
        assert not r.alertes, r.alertes
        assert ("video" if fmt == "video" else "lecon", len(ed.scenes) - 1) in r.poses   # logo de fin


def test_etapes_calees_sur_la_voix():
    fiche = charger_fiche(LANCEMENT)
    ed = fiche.editions["fr"]
    i = next(k for k, s in enumerate(ed.scenes) if s.type == "etapes")
    r = Rendu(fiche, "fr", CHARTE, "video", False)
    r.reperes[id(ed.scenes[i])] = [0.35, 2.0, 3.5, 6.0]     # intro + une phrase par étape
    assert r.duree_animation(ed.scenes[i]) == pytest.approx(6.5)   # indépendant de l'ordre de dessin
    assert r._debuts_etapes(ed.scenes[i], 3) == [2.0, 3.5, 6.0]
    vide = r.dessiner(ed.scenes[i], i, len(ed.scenes), 1.0)
    pleine = r.dessiner(ed.scenes[i], i, len(ed.scenes), 7.0)
    assert vide.tobytes() != pleine.tobytes()


def test_habillage_sonore(tmp_path):
    import wave
    from lmec import son
    voix = tmp_path / "voix.wav"
    son._ecrire(voix, np_sinus(2.0))
    sortie = son.habiller(voix, [1.0, 2.0], CHARTE["son"], tmp_path / "mix.wav", index_fin=1)
    with wave.open(str(sortie)) as w:
        assert w.getframerate() == 48000 and abs(w.getnframes() / 48000 - 3.0) < 0.01
    m = son._lire(sortie)
    assert m.max() <= 10 ** (-1 / 20) + 1e-3                  # crête ≤ -1 dBFS
    assert abs(m[int(1.5 * 48000):int(2.0 * 48000)]).max() > 0.05   # signature présente sur la fin


def np_sinus(duree):
    import numpy as np
    t = np.arange(int(duree * 48000)) / 48000
    return 0.3 * np.sin(2 * np.pi * 220 * t)


def test_fiche_actualite_inchangee():
    fiche = charger_fiche(FICHE_REELLE)
    assert fiche.type_fiche == "actualite" and fiche.format == "short" and not fiche.habillage_sonore
