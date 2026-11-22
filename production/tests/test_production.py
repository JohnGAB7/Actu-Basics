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
        # Le job qui rend les vidéos (apercu.yml en a plusieurs : tests, liste, rendus par fiche).
        etapes = next(j["steps"] for j in wf["jobs"].values()
                      if any("produire.py" in str(e.get("run", "")) for e in j.get("steps", [])))
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


PAYANT_AUTORISE = {"gratuit_uniquement": False}   # tests des intégrations payantes, sans appel réel


def test_fournisseurs_sans_cle():
    with pytest.raises(ErreurTTS, match="OPENAI_API_KEY"):
        creer_fournisseur("openai", PAYANT_AUTORISE, "fr").verifier()
    with pytest.raises(ErreurTTS, match="ELEVENLABS_API_KEY"):
        creer_fournisseur("elevenlabs", PAYANT_AUTORISE, "fr").verifier()
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
    f = creer_fournisseur(nom, {**PAYANT_AUTORISE, "voix": {"fr": {nom: config}}}, "fr")
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


# La charte par défaut est en version claire (ivoire) depuis le 22/11/2026 : les cas « fond sombre »
# utilisent une charte sombre explicite (ancienne palette bleu nuit).
SOMBRE = dict(couleurs__fond="#0B1526", couleurs__fond_bas="#14284A", couleurs__barre="#3E7CB1",
              couleurs__texte="#F5F3EE", couleurs__halo="#3E7CB1", couleurs__encre_accent="#0B1526")


def test_logo_choisi_selon_la_langue_et_le_fond():
    clair = dict(couleurs__fond="#F5F5F1", couleurs__fond_bas="#FFFFFF", couleurs__barre="#E8EEF5",
                 couleurs__texte="#06152B", logo__sur_fond_clair="clair")
    attendu = {("fr", "sombre"): "logo-dark.png", ("fr", "clair"): "logo-light.png",
               ("en", "sombre"): "logo-dark-en.png", ("en", "clair"): "logo-light-en.png"}
    for langue in ("fr", "en"):
        for fond, ch in (("sombre", _charte(**SOMBRE)), ("clair", _charte(**clair))):
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
    sombre = _charte(**SOMBRE)
    for fmt in ("video", "carrousel"):
        r, im, ed = _rendu_fin(sombre, fmt)
        pose = r.poses[(fmt, len(ed.scenes) - 1)]
        assert pose.variante == "sombre" and pose.luminance_fond < 0.5
        x0, y0, x1, y1 = pose.boite
        source = logo_mod._ouvrir(str(r.logos.chemins["sombre"]))
        assert abs((y1 - y0) / (x1 - x0) - source.height / source.width) < 0.01      # jamais déformé
        assert pose.recouvrement <= logo_mod.SEUIL_RECOUVREMENT                       # rien dans sa zone
        assert pose.largeur <= pose.largeur_native                                    # jamais agrandi
        rap = Rapport()
        controler_logo("fr", r, [(fmt, len(ed.scenes) - 1, "fin")], sombre, PLATEFORMES, rap)
        assert not rap.bloquants and not rap.avertissements, [str(c) for c in rap.constats]
    assert _empreintes() == avant                                                     # fichiers d'origine intacts


def test_logo_sur_fond_clair_selon_la_charte():
    """Par défaut (JG, 22/11/2026) : disque sombre sur fond clair ; `sur_fond_clair: clair` reste possible,
    et le contrôle qualité suit la charte dans les deux cas."""
    base = dict(couleurs__fond="#F5F5F1", couleurs__fond_bas="#FFFFFF", couleurs__barre="#E8EEF5",
                couleurs__texte="#06152B")
    for voulu in ("sombre", "clair"):
        ch = _charte(logo__sur_fond_clair=voulu, **base)
        r, _, ed = _rendu_fin(ch, "carrousel")
        pose = r.poses[("carrousel", len(ed.scenes) - 1)]
        assert pose.variante == voulu and pose.luminance_fond >= 0.5
        rap = Rapport()
        controler_logo("fr", r, [("carrousel", len(ed.scenes) - 1, "fin")], ch, PLATEFORMES, rap)
        assert not any("variante" in str(c) for c in rap.bloquants)


def test_variante_forcee_contraire_au_fond_bloque():
    ch = _charte(logo__variante="clair", **SOMBRE)
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


def test_scene_animation_et_note(tmp_path):
    fiche = charger_fiche(LANCEMENT)
    ed = fiche.editions["fr"]
    anim = next(s for s in ed.scenes if s.type == "animation" and s.extra["animation"].get("n") == 4)
    assert anim.extra["animation"]["modele"] == "paires" and len(anim.extra["etapes"]) == 5
    assert any(s.extra.get("note", "").startswith("Hypothèses") for s in ed.scenes)
    r = Rendu(fiche, "fr", CHARTE, "video", False)
    i = ed.scenes.index(anim)
    debut, fin = r.dessiner(anim, i, len(ed.scenes), 1.0), r.dessiner(anim, i, len(ed.scenes), 9.0)
    assert debut.tobytes() != fin.tobytes()                   # les paires se tracent
    brut = valider(brut_lancement())
    scene = next(s for s in brut["editions"]["fr"]["scenes"] if s["type"] == "animation")
    scene["animation"] = {"modele": "spirale", "n": 500}
    scene["note"] = "x" * 200
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics"))
    assert "modele" in str(exc.value) and "note" in str(exc.value)


def test_animation_selection_par_la_survie(tmp_path):
    """Modèle « selection » (Q2.04) : les absentes s'estompent, les survivantes descendent dans le cadre
    des données ; une légende par phase ; paramètres invalides refusés."""
    fiche = charger_fiche(RACINE / "contenus/fiches/2026-11-pilote-q2-04-biais-du-survivant.yaml")
    for langue in ("fr", "en"):
        ed = fiche.editions[langue]
        scenes = [s for s in ed.scenes if s.type == "animation" and s.extra["animation"]["modele"] == "selection"]
        assert {s.extra["animation"]["icone"] for s in scenes} == {"avion", "entreprise"}
        r = Rendu(fiche, langue, CHARTE, "video", False)
        for s in scenes:
            i = ed.scenes.index(s)
            plan = r._plan_animation(s)
            assert len(plan) == len(s.extra["etapes"])
            images = [r.dessiner(s, i, len(ed.scenes), p["debut"] + p["duree"] + 0.2).tobytes() for p in plan]
            assert len(set(images)) == len(images)          # chaque phase change l'image
    from lmec.animations import Animations
    assert Animations._disparues(8, 5) == {1, 4, 6} and len(Animations._disparues(8, 3)) == 5
    brut = valider(brut_lancement())
    scene = next(x for x in brut["editions"]["fr"]["scenes"] if x["type"] == "animation")
    scene["animation"] = {"modele": "selection", "icone": "bateau", "n": 8, "restants": 8}
    scene.pop("etapes", None)
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics"))
    assert "animation.icone" in str(exc.value) and "animation.restants" in str(exc.value)


def test_courbe_en_points_avec_plusieurs_seuils(tmp_path):
    """« style: points » pose des points sans les relier ; « seuils » trace plusieurs pointillés étiquetés
    (moyenne et médiane ensemble, S2.05). Valeurs invalides refusées."""
    fiche = charger_fiche(RACINE / "contenus/fiches/2026-11-pilote-s2-05-moyenne-ou-mediane.yaml")
    ed = fiche.editions["fr"]
    s = next(x for x in ed.scenes if x.type == "courbe")
    assert s.extra["courbe"]["style"] == "points" and len(s.extra["courbe"]["seuils"]) == 2
    i = ed.scenes.index(s)
    points = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None)
    s.extra["courbe"] = dict(s.extra["courbe"], style="ligne")
    ligne = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None)
    assert points.tobytes() != ligne.tobytes()
    brut = valider(brut_lancement())
    scene = next(x for x in brut["editions"]["fr"]["scenes"] if x["type"] == "courbe")
    scene["courbe"] = dict(scene["courbe"], style="camembert", seuils=[{"label": "sans valeur"}])
    with pytest.raises(FicheInvalide) as exc:
        charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics"))
    assert "courbe.style" in str(exc.value) and "courbe.seuils" in str(exc.value)


@pytest.mark.parametrize("modele", ["foule", "paires", "doublon", "calendrier", "complement"])
def test_chaque_modele_d_animation_se_construit_phase_par_phase(modele):
    fiche = charger_fiche(LANCEMENT)
    for langue in ("fr", "en"):
        ed = fiche.editions[langue]
        scenes = [s for s in ed.scenes if s.type == "animation" and s.extra["animation"]["modele"] == modele]
        assert scenes, modele
        r = Rendu(fiche, langue, CHARTE, "video", False)
        for s in scenes:
            i = ed.scenes.index(s)
            plan = r._plan_animation(s)
            assert not s.extra.get("etapes") or len(s.extra["etapes"]) == len(plan)   # une légende par phase
            fin = r.duree_animation(s)
            images = [r.dessiner(s, i, len(ed.scenes), t).tobytes() for t in (0.0, fin / 2, fin)]
            assert len(set(images)) == 3, f"{modele} : l'image doit évoluer pendant l'animation"
        assert not r.alertes


def test_animation_calee_sur_les_phrases_de_la_voix():
    fiche = charger_fiche(LANCEMENT)
    ed = fiche.editions["fr"]
    s = next(s for s in ed.scenes if s.type == "animation" and s.extra["animation"].get("n") == 4)
    r = Rendu(fiche, "fr", CHARTE, "video", False)
    r.reperes[id(s)] = [0.35, 2.0, 4.0, 8.0, 12.0, 15.0]    # intro + une phrase par phase
    assert [p["debut"] for p in r._plan_animation(s)] == [2.0, 4.0, 8.0, 12.0, 15.0]
    assert r.duree_animation(s) == pytest.approx(15.0 + 0.8 + 0.8)


def test_legendes_et_phases_d_animation_doivent_correspondre(tmp_path):
    brut = valider(brut_lancement())
    scene = next(s for s in brut["editions"]["fr"]["scenes"]
                 if s["type"] == "animation" and s["animation"].get("n") == 4)
    scene["etapes"] = scene["etapes"][:3]
    with pytest.raises(FicheInvalide, match="une légende par phase"):
        charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics"))


def test_correction_etapes_puis_reponse_sur_la_derniere_phrase():
    fiche = charger_fiche(LANCEMENT)
    ed = fiche.editions["fr"]
    s = next(s for s in ed.scenes if s.type == "correction" and len(s.extra.get("etapes", [])) == 2)
    r = Rendu(fiche, "fr", CHARTE, "video", False)
    r.reperes[id(s)] = [0.35, 4.0, 8.0]
    assert r._debuts_etapes(s, 2) == [0.35, 4.0] and r._debut_reponse(s) == 8.0


def test_courbe_avec_quatre_reperes_et_seuil():
    fiche = charger_fiche(LANCEMENT)
    ed = fiche.editions["fr"]
    s = next(s for s in ed.scenes if s.type == "courbe" and s.extra["courbe"].get("seuil"))
    assert [rep["x"] for rep in s.extra["courbe"]["reperes"]] == [23, 40, 41, 50]
    for fmt in ("video", "lecon"):
        r = Rendu(fiche, "fr", CHARTE, fmt, False)
        r.dessiner(s, ed.scenes.index(s), len(ed.scenes))
        assert not r.alertes


def test_application_cryptographie_verifiee():
    """L'application concrète (collisions d'empreintes) est recalculée comme le reste, et prudente."""
    assert pedagogie.evaluer("1 - exp(-(5e9) ** 2 / (2 * 2 ** 64))") == pytest.approx(0.49, abs=0.01)
    fiche = charger_fiche(LANCEMENT)
    for langue in ("fr", "en"):
        textes = " ".join(s.voix_off for s in fiche.editions[langue].scenes).lower()
        assert "collision" in textes
        assert "sécuris" not in textes and "secure" not in textes and "fraud" not in textes


def test_reperes_sonores_et_signature():
    from lmec import son
    fiche = charger_fiche(LANCEMENT)
    ed = fiche.editions["fr"]
    r = Rendu(fiche, "fr", CHARTE, "video", True)
    durees = [r.duree_animation(s) + 2 for s in ed.scenes]
    reperes = r.reperes_sonores(ed.scenes, durees)
    pauses = sum(int(s.extra.get("pause", 3)) for s in ed.scenes if s.type == "exercice")
    assert sum(1 for _, n in reperes if n == "tic") == pauses                # un tic par seconde de réflexion
    assert sum(1 for _, n in reperes if n == "revele") == sum(1 for s in ed.scenes if s.type == "chiffre") \
        + sum(1 for s in ed.scenes if s.type == "correction" and s.extra.get("reponse"))
    assert all(0 <= t < sum(durees) for t, _ in reperes)
    sig = son.signature()
    assert abs(sig).max() == pytest.approx(1.0) and (sig == son.signature()).all()   # identique à chaque rendu
    assert abs(sig[-100:]).max() < 0.01                                       # extinction douce


def test_pauses_de_narration_selon_la_ponctuation():
    from lmec.narration import pause_apres
    assert pause_apres("Une question ?") > pause_apres("Une phrase.") > pause_apres("Une énumération :")


# --------------------------------------------------------------------------- gratuité et Kokoro
from lmec import tts as tts_mod  # noqa: E402


@pytest.mark.parametrize("nom", ["openai", "elevenlabs"])
def test_service_payant_refuse_par_defaut(nom, monkeypatch):
    """Gratuité imposée (tts.yaml) : un fournisseur payant est refusé, et aucune requête ne part."""
    config = yaml.safe_load((RACINE / "production/tts.yaml").read_text(encoding="utf-8"))
    assert config["gratuit_uniquement"] is True and config["fournisseur"] == "kokoro"
    with pytest.raises(tts_mod.ServicePayantRefuse, match="gratuit_uniquement"):
        creer_fournisseur(nom, config, "fr")
    with pytest.raises(tts_mod.ServicePayantRefuse):
        creer_fournisseur(nom, {}, "fr")                     # sans réglage : gratuité par défaut
    import urllib.request
    appels = []
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: appels.append(a))
    with pytest.raises(tts_mod.ServicePayantRefuse):
        tts_mod._requete("https://api.openai.com/v1/audio/speech", {}, {})
    assert not appels                                         # bloqué avant le réseau


def test_qc_bloque_un_service_payant(tmp_path):
    r = lancer(EXEMPLE, "--voix", "elevenlabs", "--sans-video", "--sortie", tmp_path)
    rapport = (tmp_path / "exemple-fictif/rapport-qc.md").read_text()
    assert "BLOQUÉ" in rapport and "gratuit_uniquement" in rapport


def test_kokoro_absent_bascule_sur_le_secours(tmp_path, monkeypatch):
    monkeypatch.setattr(tts_mod, "DOSSIER_VOIX", tmp_path)            # aucun modèle Kokoro ici
    config = {"secours": {"kokoro": "test"}, "voix": {"fr": {"kokoro": {"voix": "ff_siwis"}}}}
    f, note = tts_mod.creer_avec_secours("kokoro", config, "fr")
    assert f.nom == "test" and "secours" in note
    with pytest.raises(ErreurTTS):
        tts_mod.creer_avec_secours("kokoro", {"voix": {"fr": {"kokoro": {"voix": "ff_siwis"}}}}, "fr")


def _kokoro_disponible():
    try:
        import kokoro_onnx  # noqa: F401
    except ImportError:
        return False
    return (tts_mod.DOSSIER_VOIX / "kokoro-v1.0.onnx").exists() and (tts_mod.DOSSIER_VOIX / "voices-v1.0.bin").exists()


@pytest.mark.skipif(not _kokoro_disponible(), reason="Kokoro non installé ou modèle non téléchargé")
@pytest.mark.parametrize("langue, voix, texte", [
    ("fr", "ff_siwis", "Cinquante virgule sept pour cent, avec vingt-trois personnes."),
    ("en", "af_heart", "Fifty point seven percent, with twenty-three people."),
])
def test_kokoro_local_sans_reseau(tmp_path, monkeypatch, langue, voix, texte):
    """Kokoro synthétise sans aucun accès réseau (toute connexion est interdite pendant le test)."""
    import socket

    def interdit(*a, **k):
        raise AssertionError("connexion réseau tentée pendant la synthèse")
    monkeypatch.setattr(socket.socket, "connect", interdit)
    config = yaml.safe_load((RACINE / "production/tts.yaml").read_text(encoding="utf-8"))
    f, note = tts_mod.creer_avec_secours("kokoro", config, langue)
    assert f.nom == "kokoro" and note is None and f.config["voix"] == voix
    f.synthetiser(texte, tmp_path / "k.wav")
    import wave
    with wave.open(str(tmp_path / "k.wav")) as w:
        assert w.getframerate() == 48000 and w.getnchannels() == 1
    assert 2.0 < duree_wav(tmp_path / "k.wav") < 8.0


# --- Lecture des nombres et symboles par la voix (Kokoro et Piper passent par espeak-ng) ---

@pytest.mark.parametrize("langue,ecrit,dit", [
    ("fr", "50,7 %", "50 virgule 7 pour cent"),
    ("fr", "P₀ ≈ 0,493.", "P zéro environ 0 virgule 493."),
    ("fr", "1 − P₀", "1 moins P zéro"),
    ("fr", "365/365 × 364/365", "365 sur 365 fois 364 sur 365"),
    ("fr", "2⁶⁴ ≈ 18 400", "2 puissance 64 environ 18400"),
    ("fr", "23 × 22 ÷ 2 = 253", "23 fois 22 divisé par 2 égale 253"),
    ("fr", "41 - 40 = 1", "41 moins 40 égale 1"),
    ("fr", "Le 29 février 2028, 1,2,3.", "Le 29 février 2028, 1,2,3."),
    ("en", "50.7%", "50 point seven percent"),
    ("en", "P₀ ≈ 0.493.", "P zero about 0 point four nine three."),
    ("en", "18,400,000 pairs", "18400000 pairs"),
    ("en", "2⁶⁴ and 1 − P₀", "2 to the power of 64 and 1 minus P zero"),
    ("en", "365/365 × 364/365", "365 over 365 times 364 over 365"),
    ("en", "On 29 February 2028, the SHA-256 hash.", "On 29 February 2028, the SHA-256 hash."),
])
def test_lecture_des_nombres_et_symboles(langue, ecrit, dit):
    from lmec.lecture import normaliser_lecture
    assert normaliser_lecture(ecrit, langue) == dit


def test_lecture_appliquee_apres_le_lexique_et_pas_aux_sous_titres():
    from lmec.narration import preparer_pour_voix
    lex = {"fr": {"ONU": "Onu"}}
    assert preparer_pour_voix("L'ONU : 50,7 %.", "fr", lex) == "L'Onu : 50 virgule 7 pour cent."


def test_kokoro_prononce_les_nombres_normalises():
    """Vérifie la phonétisation réelle (espeak-ng via Kokoro) quand le modèle est installé."""
    from lmec.narration import preparer_pour_voix
    from lmec.tts import DOSSIER_VOIX
    kokoro_onnx = pytest.importorskip("kokoro_onnx")
    modele, voix = DOSSIER_VOIX / "kokoro-v1.0.onnx", DOSSIER_VOIX / "voices-v1.0.bin"
    if not (modele.exists() and voix.exists()):
        pytest.skip("modèle Kokoro absent")
    k = kokoro_onnx.Kokoro(str(modele), str(voix))
    fr = k.tokenizer.phonemize(preparer_pour_voix("50,7 % et 1 − P₀", "fr", {}), "fr-fr")
    assert "viʁɡˈyl" in fr and "mwˈɛ̃" in fr and "mˈaɪnəs" not in fr
    en = k.tokenizer.phonemize(preparer_pour_voix("0.493 ≈ 2⁶⁴", "en", {}), "en-us")
    assert "pˈɔɪnt" in en and "pˈaʊɚ" in en and "hˈʌndɹɪd nˈaɪnti" not in en


def test_enveloppe_de_voix_rapide_et_identique_a_la_convolution():
    """Une vidéo de 8 minutes ne doit pas bloquer l'habillage sonore (ancienne convolution O(n·k))."""
    import time
    import numpy as np
    from lmec import son
    x = np.random.default_rng(1).standard_normal(48000 * 3)
    k = int(0.25 * 48000)
    ref = np.convolve(np.abs(x), np.ones(k) / k, mode="same")
    assert np.allclose(son._enveloppe(x), np.clip(ref / np.percentile(ref, 95), 0, 1), atol=1e-9)
    debut = time.time()
    son._enveloppe(np.zeros(48000 * 480))
    assert time.time() - debut < 15


def test_sous_titres_sur_deux_lignes_lisibles_sur_mobile():
    from lmec.textes import deux_lignes
    t = deux_lignes("Et si les chiffres changeaient votre façon de voir le monde ?")
    assert t.count("\n") == 1 and all(len(l) <= 42 for l in t.split("\n"))
    assert not t.split("\n")[1].startswith("?")
    assert deux_lignes("Commençons par un défi.") == "Commençons par un défi."


def test_pas_de_coupure_au_milieu_d_une_expression():
    from lmec.rendu import mots_riches
    def mots(t):
        return [w.replace("\u00a0", " ") for w, _, _ in mots_riches(t)]
    assert "n(n − 1) ÷ 2" in mots("Compter les paires : *n(n − 1) ÷ 2*")   # formule sur une ligne
    assert "780 ÷ 365 > 2," in mots("40 personnes : 780 ÷ 365 > 2, impossible")
    assert mots("Multiplier, puis 1 − P₀")[-1] == "− P₀"
    assert len(mots_riches("(voir le rapport de rendu complet)")) == 6   # parenthèse longue : coupable


def test_un_nombre_ne_se_coupe_pas():
    from lmec.rendu import mots_riches
    def mots(t):
        return [w.replace("\u00a0", " ") for w, _, _ in mots_riches(t)]
    m = mots("Ils gagnent de *1 600 €* à 2 800 € par mois, puis 200 000 €")
    assert "1 600 €" in m and "2 800 €" in m and "200 000 €" in m
    assert mots("Sept salaires : 1 500, 1 600")[-2:] == ["1 500,", "1 600"]   # liste : coupable entre deux nombres
    assert mots("les 3 enfants") == ["les", "3", "enfants"]
    assert "5 min" in mots("Court intervalle : 5 min sur 20") and "1 point" in mots("écart de 1 point")
    assert "2,1 millions" in mots("La commune de Paris : 2,1 millions") and "20 °C" in mots("à 20 °C")


def test_prononciation_de_la_marque_dans_la_voix_seulement():
    import yaml
    from lmec.narration import preparer_pour_voix
    lex = yaml.safe_load(open(RACINE / "production/tts.yaml", encoding="utf-8"))["prononciation"]
    assert "ACTU-BASICS" not in preparer_pour_voix("Bienvenue sur ACTU-BASICS.", "fr", lex)
    assert "ACTU-BASICS" in preparer_pour_voix("Welcome to ACTU-BASICS.", "en", lex)   # bien lu en anglais


def test_barre_sous_le_grand_numero_de_chapitre_ne_le_coupe_pas():
    """La barre d'accent doit passer sous le bas réel du chiffre, avec un espace net."""
    import numpy as np
    fiche = charger_fiche(LANCEMENT)
    for langue in ("fr", "en"):
        r = Rendu(fiche, langue, CHARTE, "video", False)
        ed = fiche.editions[langue]
        for i, s in enumerate(ed.scenes):
            if s.type != "titre" or not s.extra.get("numero"):
                continue
            px = np.array(r.dessiner(s, i, len(ed.scenes)).convert("RGB")).astype(int)
            accent = np.array(r.c["accent"][:3])
            g = r.zone[0]
            colonne = np.abs(px[:, g + 20:g + 30] - accent).sum(axis=2).min(axis=1) < 40
            lignes = np.flatnonzero(colonne)
            blocs = np.split(lignes, np.flatnonzero(np.diff(lignes) > 1) + 1)
            numero, barre = blocs[-2], blocs[-1]     # le chiffre, puis la barre en dessous
            assert barre[0] - numero[-1] >= 20, (langue, i, numero[-1], barre[0])


def test_soulignement_du_chiffre_cle_sous_la_virgule():
    """« 50,7 % » : la virgule descend sous la ligne de base ; le soulignement doit passer dessous."""
    import numpy as np
    fiche = charger_fiche(LANCEMENT)
    for langue in ("fr", "en"):
        for fmt in ("video", "lecon"):
            r = Rendu(fiche, langue, CHARTE, fmt, False)
            ed = fiche.editions[langue]
            i, s = next((i, s) for i, s in enumerate(ed.scenes) if s.type == "chiffre")
            px = np.array(r.dessiner(s, i, len(ed.scenes)).convert("RGB")).astype(int)
            accent = np.abs(px - np.array(r.c["accent"][:3])).sum(axis=2) < 40
            blanc = np.abs(px - np.array(r.c["texte"][:3])).sum(axis=2) < 40
            lignes_barre = [y for y in range(px.shape[0]) if blanc[y].sum() > px.shape[1] * 0.3]
            assert lignes_barre, (langue, fmt)
            haut_barre = lignes_barre[0]
            bas_chiffre = max(y for y in range(haut_barre) if accent[y].sum() > 3)
            assert haut_barre - bas_chiffre >= 10, (langue, fmt, bas_chiffre, haut_barre)


def _faux_pt(tableau):
    """Fabrique un fichier au format torch.save (zip + pickle) sans torch, pour tester le lecteur."""
    import io, pickle, types, zipfile
    import numpy as np
    torch = types.ModuleType("torch"); utils = types.ModuleType("torch._utils")

    class FloatStorage:  # noqa: N801
        pass
    FloatStorage.__module__, FloatStorage.__qualname__ = "torch", "FloatStorage"
    torch.FloatStorage = FloatStorage

    def _rebuild_tensor_v2(*a):
        pass
    _rebuild_tensor_v2.__module__, _rebuild_tensor_v2.__qualname__ = "torch._utils", "_rebuild_tensor_v2"
    utils._rebuild_tensor_v2 = _rebuild_tensor_v2
    sys.modules["torch"], sys.modules["torch._utils"] = torch, utils
    try:
        class Tenseur:
            def __reduce__(self):
                pas = tuple(s // 4 for s in tableau.strides)
                return (_rebuild_tensor_v2, ("STOCK", 0, tableau.shape, pas, False, {}))

        class P(pickle.Pickler):
            def persistent_id(self, obj):
                return ("storage", FloatStorage, "0", "cpu", tableau.size) if obj == "STOCK" else None
        flux = io.BytesIO(); P(flux, protocol=2).dump(Tenseur())
    finally:
        del sys.modules["torch"], sys.modules["torch._utils"]
    sortie = io.BytesIO()
    with zipfile.ZipFile(sortie, "w") as z:
        z.writestr("archive/data.pkl", flux.getvalue())
        z.writestr("archive/data/0", np.ascontiguousarray(tableau, dtype=np.float32).tobytes())
    return sortie.getvalue()


def test_lecture_des_voix_officielles_sans_torch():
    import numpy as np
    from verifier_provenance_voix import lire_tenseur_pt
    t = np.random.default_rng(3).standard_normal((510, 1, 256)).astype(np.float32)
    assert np.array_equal(lire_tenseur_pt(_faux_pt(t)), t)


def test_lecture_pt_refuse_les_objets_inattendus():
    import io, pickle, zipfile
    from verifier_provenance_voix import lire_tenseur_pt
    flux = io.BytesIO(); pickle.dump(__import__("os").getcwd, flux)    # un appel de fonction arbitraire
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as a:
        a.writestr("archive/data.pkl", flux.getvalue())
    with pytest.raises(pickle.UnpicklingError):
        lire_tenseur_pt(z.getvalue())


def test_lecture_pth_officiel_sans_torch():
    import numpy as np
    from comparer_poids_onnx import lire_pth
    t = np.arange(12, dtype=np.float32).reshape(3, 4)
    assert np.array_equal(lire_pth(_faux_pt(t)), t)


def test_comparaison_des_poids_onnx():
    """Transposition, portes réordonnées et poids normalisés sont reconnus ; une valeur changée ne l'est pas."""
    import numpy as np
    from comparer_poids_onnx import comparer
    rng = np.random.default_rng(0)
    a, b = rng.standard_normal((8, 5), dtype=np.float32), rng.standard_normal((16, 3), dtype=np.float32)
    g, v = rng.random((4, 1, 1), dtype=np.float32) + 0.5, rng.standard_normal((4, 2, 3), dtype=np.float32)
    w = (g * v / np.sqrt((v.astype(np.float64) ** 2).reshape(4, -1).sum(1)).reshape(4, 1, 1)).astype(np.float32)
    c = rng.standard_normal(50, dtype=np.float32)
    c_modifie = c.copy(); c_modifie[:10] += 1.0
    officiels = {"lin.weight": a, "lstm.weight_ih": b, "conv.weight_g": g, "conv.weight_v": v, "autre": c}
    onnx_t = {"x": a.T.copy(), "y": np.concatenate([b[8:], b[:8]]), "z": w, "k": c_modifie,
              "forme": np.array([1, 2], dtype=np.int64)}
    res = comparer(officiels, onnx_t)
    assert set(res["exacts"]) == {"lin.weight", "lstm.weight_ih"}
    assert len(res["normalises"]) == 1
    taille, part = res["restants"]["autre"]
    assert taille == 50 and abs(part - 0.8) < 1e-9


def _occurrences_barres(fiche, langue, fmt, instants=(None, 0.3, 0.6, 1.2, 1.8, 3.0)):
    """Rend chaque scène à plusieurs instants en enregistrant chaque texte (boîte réelle des glyphes)
    et chaque barre fine (rectangle ≤ 20 px de haut). Retourne, pour chaque barre posée sous un grand
    texte (≥ 150 px), l'écart vertical entre le bas réel du glyphe et le haut de la barre."""
    from PIL import ImageDraw
    from lmec import rendu as module_rendu
    journal = []

    class Enregistreur(ImageDraw.ImageDraw):
        def text(self, xy, txt, *a, **k):
            f = k.get("font")
            if f is not None and str(txt).strip():
                journal[-1][0].append((str(txt), f.size, self.textbbox(xy, txt, font=f)))
            return super().text(xy, txt, *a, **k)

        def rectangle(self, box, *a, **k):
            if box[3] - box[1] <= 20 and box[2] - box[0] >= 1:
                journal[-1][1].append(tuple(box))
            return super().rectangle(box, *a, **k)

    origine = module_rendu.ImageDraw.Draw
    resultats = []
    try:
        module_rendu.ImageDraw.Draw = lambda im, mode=None: Enregistreur(im, mode)
        r = Rendu(fiche, langue, CHARTE, fmt, False)
        scenes = fiche.editions[langue].scenes
        for i, s in enumerate(scenes):
            for t in instants:
                journal.append(([], []))
                r.dessiner(s, i, len(scenes), t=t)
                textes, barres = journal[-1]
                for barre in barres:
                    for txt, taille, (x0, y0, x1, y1) in textes:
                        chevauche = x0 < barre[2] and barre[0] < x1
                        if taille >= 150 and chevauche and y0 < barre[1]:
                            resultats.append((i, s.type, t, txt, barre[1] - y1, (min(x0, barre[0]), y0, max(x1, barre[2]), barre[3])))
    finally:
        module_rendu.ImageDraw.Draw = origine
    return resultats


@pytest.mark.parametrize("chemin", sorted((RACINE / "contenus/fiches").glob("*.yaml")), ids=lambda p: p.stem)
def test_barre_sous_chaque_grand_chiffre_toutes_occurrences(chemin):
    """Composant commun : sous TOUT grand chiffre (numéro de chapitre, chiffre clé, quelle que soit la
    scène), la barre reste sous le glyphe entier avec une marge nette, à chaque instant de l'animation,
    en français et en anglais, en vertical comme en 16:9."""
    fiche = charger_fiche(chemin)
    vus = 0
    for langue in fiche.editions:
        for fmt in ("video", "lecon", "carrousel"):
            for i, type_, t, txt, ecart, _ in _occurrences_barres(fiche, langue, fmt):
                vus += 1
                assert ecart >= 10, (chemin.name, langue, fmt, f"scène {i + 1} {type_}", t, txt, ecart)
    # Depuis le 22/11/2026, les fiches pédagogiques n'ont plus de grands numéros de chapitre (titre soft :
    # surtitre « Chapitre N » et points de progression) : seule la capsule d'actualité en garde.
    if not fiche.pedagogique:
        assert vus, "aucune barre sous un grand chiffre trouvée : le test ne vérifie plus rien"


def test_inventaire_signale_une_video_manquante(tmp_path):
    """L'inventaire de l'artefact échoue si une langue rendue n'a pas sa vidéo."""
    sys.path.insert(0, str(RACINE / "production"))
    import inventaire
    for langue in ("fr", "en"):
        d = tmp_path / "fiche" / langue
        d.mkdir(parents=True)
        for nom in inventaire.ATTENDUS:
            (d / nom).write_text("{}" if nom.endswith(".json") else "x", encoding="utf-8")
    (tmp_path / "fiche/en/video.mp4").unlink()
    texte, erreurs = inventaire.inventorier(tmp_path)
    assert "fiche/en/video.mp4 manquant" in erreurs
    assert "| `fr/video.mp4` |" in texte and "## Contrôle" in texte


# ---------------------------------------------------------------- déclinaison 16:9 (YouTube)

PILOTE_S108 = RACINE / "contenus/fiches/2026-11-pilote-s1-08-pourcentages-et-points.yaml"


def test_horizontal_ignore_un_short(tmp_path):
    r = lancer(EXEMPLE, "--horizontal", "--voix", "test", "--sans-video", "--sortie", tmp_path)
    assert r.returncode == 0
    assert "pas de déclinaison 16:9" in r.stdout
    assert not (tmp_path / "exemple-fictif-16x9").exists()


def test_horizontal_decline_une_lecon_verticale_en_16_9(tmp_path):
    assert charger_fiche(PILOTE_S108).format_image == "video"
    r = lancer(PILOTE_S108, "--horizontal", "--voix", "test", "--sans-video", "--langues", "fr", "--sortie", tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    meta = json.loads((tmp_path / "2026-11-pilote-s1-08-pourcentages-et-points-16x9/fr/metadonnees.json").read_text())
    assert meta["image"] == "lecon" and meta["format"] == "educational"
    assert not (tmp_path / "2026-11-pilote-s1-08-pourcentages-et-points").exists()


def test_logo_de_fin_controle_en_16_9_sans_interface_d_application():
    r, _, ed = _rendu_fin(CHARTE, fmt="lecon")
    n = len(ed.scenes)
    assert ("lecon", n - 1) in r.poses
    rap = Rapport()
    controler_logo("fr", r, [("lecon", n - 1, "fin")], CHARTE, PLATEFORMES, rap)
    assert not rap.bloquants
    assert not [a for a in rap.avertissements if "interface" in str(a)]


def test_courbe_titre_d_axe_vertical_et_guide_horizontal():
    """« axe_y » écrit l'unité sur l'axe vertical ; « guide_y » d'un repère trace le pointillé vers cet axe
    (M0.03, relecture du 2026-11-07 : lire les deux coordonnées d'un point sur le graphique lui-même)."""
    fiche = charger_fiche(RACINE / "contenus/fiches/2026-11-n1-m0-03-lire-un-graphique-et-un-repere.yaml")
    for langue in ("fr", "en"):
        ed = fiche.editions[langue]
        s = next(x for x in ed.scenes if x.type == "courbe")
        c = s.extra["courbe"]
        assert c["axe_y"] and c["reperes"][0]["guide_y"] is True
        i = ed.scenes.index(s)
        complet = Rendu(fiche, langue, CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
        s.extra["courbe"] = dict(c, axe_y=None)
        sans_titre = Rendu(fiche, langue, CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
        s.extra["courbe"] = dict(c, reperes=[dict(c["reperes"][0], guide_y=False)])
        sans_guide = Rendu(fiche, langue, CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
        s.extra["courbe"] = c
        assert len({complet, sans_titre, sans_guide}) == 3


def test_courbe_annees_sans_separateur_de_milliers():
    """Abscisses en années (S1.07 : 2019 à 2023) : « 2019 », jamais « 2 019 ». L'image change si l'on
    remplace les années par des nombres ordinaires du même ordre."""
    fiche = charger_fiche(RACINE / "contenus/fiches/2026-11-n1-s1-07-donnees-manquantes-erreurs-definitions.yaml")
    ed = fiche.editions["fr"]
    s = next(x for x in ed.scenes if x.type == "courbe")
    i = ed.scenes.index(s)
    c = s.extra["courbe"]
    annees = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
    s.extra["courbe"] = dict(c, _points=[(x + 0.5, y) for x, y in c["_points"]])
    autres = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
    s.extra["courbe"] = c
    assert annees != autres


def test_courbe_barres_et_histogramme():
    """S2.01 à S2.03 : « style: barres » (catégories étiquetées, barres séparées) et « style: histogramme »
    (classes contiguës, éventuellement inégales : la dernière a la largeur « largeur_classe »)."""
    fiche = charger_fiche(RACINE / "contenus/fiches/2026-11-n1-s2-02-diagrammes-en-barres-et-histogrammes.yaml")
    ed = fiche.editions["fr"]
    courbes = [s for s in ed.scenes if s.type == "courbe"]
    assert [s.extra["courbe"]["style"] for s in courbes][:2] == ["barres", "histogramme"]
    images = []
    for s in courbes[:3]:
        i = ed.scenes.index(s)
        images.append(Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes())
    # Les mêmes points en ligne ne donnent pas la même image : le style est bien pris en compte.
    s = courbes[1]
    c = s.extra["courbe"]
    s.extra["courbe"] = dict(c, style="ligne")
    ligne = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, ed.scenes.index(s), len(ed.scenes), None).tobytes()
    s.extra["courbe"] = c
    assert len(set(images + [ligne])) == 4
    # Une étiquette par barre, sinon la fiche est refusée.
    brute = yaml.safe_load((RACINE / "contenus/fiches/2026-11-n1-s2-02-diagrammes-en-barres-et-histogrammes.yaml")
                           .read_text(encoding="utf-8"))
    sc = next(x for x in brute["editions"]["fr"]["scenes"] if x["type"] == "courbe")
    sc["courbe"]["etiquettes"] = sc["courbe"]["etiquettes"][:2]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "f.yaml"
        p.write_text(yaml.safe_dump(brute, allow_unicode=True), encoding="utf-8")
        with pytest.raises(FicheInvalide, match="étiquette par barre"):
            charger_fiche(p)


def test_etiquettes_valeurs_des_barres():
    """« etiquettes_valeurs » : le texte au-dessus de chaque barre est écrit tel quel dans la fiche (« 0,70 € »),
    au lieu de la valeur formatée par le moteur ; une par barre, sinon la fiche est refusée."""
    chemin = RACINE / "contenus/fiches/2026-11-act-a2-01-pooling-and-the-pure-premium.yaml"
    fiche = charger_fiche(chemin)
    ed = fiche.editions["fr"]
    s = next(x for x in ed.scenes if x.type == "courbe")
    c = s.extra["courbe"]
    assert c["etiquettes_valeurs"] == ["70 €", "7 €", "0,70 €"]
    i = ed.scenes.index(s)
    avec = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
    s.extra["courbe"] = {k: v for k, v in c.items() if k != "etiquettes_valeurs"}
    sans = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
    s.extra["courbe"] = c
    assert avec != sans
    brute = yaml.safe_load(chemin.read_text(encoding="utf-8"))
    sc = next(x for x in brute["editions"]["fr"]["scenes"] if x["type"] == "courbe")
    sc["courbe"]["etiquettes_valeurs"] = ["70 €", "7 €"]
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "f.yaml"
        p.write_text(yaml.safe_dump(brute, allow_unicode=True), encoding="utf-8")
        with pytest.raises(FicheInvalide, match="un texte par barre"):
            charger_fiche(p)


def test_double_echelle_surface_et_grille():
    """S1.09 : « serie_2 » trace une seconde courbe sur un axe de droite ; modèle « surface » (carrés de
    côté 1 et 2). S1.10 : modèle « grille », répartition au hasard reproductible (graine fixe)."""
    from lmec.animations import repartition_grille
    fiche = charger_fiche(RACINE / "contenus/fiches/2026-11-n1-s1-09-lire-et-critiquer-un-graphique.yaml")
    ed = fiche.editions["fr"]
    s = next(x for x in ed.scenes if x.type == "courbe" and x.extra["courbe"].get("serie_2"))
    i = ed.scenes.index(s)
    c = s.extra["courbe"]
    avec = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
    s.extra["courbe"] = {k: v for k, v in c.items() if k != "serie_2"}
    sans = Rendu(fiche, "fr", CHARTE, "video", False).dessiner(s, i, len(ed.scenes), None).tobytes()
    s.extra["courbe"] = c
    assert avec != sans
    surf = next(x for x in ed.scenes if x.type == "animation")
    assert surf.extra["animation"]["modele"] == "surface"
    Rendu(fiche, "fr", CHARTE, "video", False).dessiner(surf, ed.scenes.index(surf), len(ed.scenes), None)
    comptes = repartition_grille(240, 500, 3)
    assert sum(comptes) == 500 and comptes == repartition_grille(240, 500, 3)
    assert (comptes.count(1), comptes.count(0)) == (61, 27)   # chiffres annoncés dans S1.10
    f10 = charger_fiche(RACINE / "contenus/fiches/2026-11-n1-s1-10-donnees-ethique-et-vie-privee.yaml")
    for langue in ("fr", "en"):
        e10 = f10.editions[langue]
        g = next(x for x in e10.scenes if x.type == "animation")
        assert g.extra["animation"]["modele"] == "grille"
        Rendu(f10, langue, CHARTE, "video", False).dessiner(g, e10.scenes.index(g), len(e10.scenes), None)


def test_serie_2_et_graine_validees(tmp_path):
    """Relecture du 2026-11-08 : la seconde série partage les abscisses de la première et a des bornes
    valides ; une graine 0 explicite n'est pas remplacée par 1."""
    from lmec.pedagogie import valider_scene
    base = {"texte": "x", "voix_off": "x.", "courbe": {"points": [[1, 1], [2, 2]], "y_min": 0, "y_max": 3}}
    erreurs = []
    valider_scene("courbe", dict(base, courbe=dict(base["courbe"], serie_2={"points": [[1, 5], [3, 6]]})), "s", erreurs)
    assert any("mêmes abscisses" in e for e in erreurs)
    erreurs = []
    valider_scene("courbe", dict(base, courbe=dict(base["courbe"], serie_2={"points": [[1, 5], [2, 6]], "y_min": 9,
                                                                             "y_max": 4})), "s", erreurs)
    assert any("y_min doit être inférieur" in e for e in erreurs)
    erreurs = []
    extra = valider_scene("animation", {"texte": "x", "voix_off": "x.", "animation": {
        "modele": "grille", "n": 10, "personnes": 5, "graine": 0}}, "s", erreurs)
    assert not erreurs and extra["animation"]["graine"] == 0


def test_legende_sans_periode_sans_parentheses_vides():
    from lmec.textes import legende_complete
    fiche = charger_fiche(EXEMPLE)
    for langue in ("fr", "en"):
        edition = fiche.editions[langue]
        fiche.periode = ""
        assert "()" not in legende_complete(fiche, edition)
        fiche.periode = "2024"
        assert "(2024)" in legende_complete(fiche, edition)


def test_boites_a_moustaches_et_nuage(tmp_path):
    """Boîtes à moustaches (S2.06, S3.01) et nuage de points cadré, avec points mis en avant (S3.04)."""
    from lmec.pedagogie import valider_scene

    def valider(scene, ctx):
        err = []
        return valider_scene(scene["type"], scene, ctx, err), err
    bon = {"type": "courbe", "texte": "Boîtes", "voix_off": "Deux boîtes.",
           "courbe": {"style": "boites", "boites": [
               {"etiquette": "Lundi", "valeurs": [0, 2, 4, 7, 12], "atypiques": [25]},
               {"etiquette": "Mardi", "valeurs": [0, 1, 3, 5, 9]}]}}
    extra, err = valider(bon, "s")
    assert not err and extra["courbe"]["_points"] == [(0.0, 25.0), (1.0, 9.0)]
    assert extra["courbe"]["etiquettes"] == ["Lundi", "Mardi"]
    mauvais = copy.deepcopy(bon)
    mauvais["courbe"]["boites"][0]["valeurs"] = [0, 5, 4, 7, 12]
    assert any("boites" in e for e in valider(mauvais, "s")[1])
    nuage = {"type": "courbe", "texte": "Nuage", "voix_off": "Un nuage.",
             "courbe": {"style": "points", "points": [[5, 3], [2, 1], [9, 8]], "x_min": 0, "x_max": 10,
                        "mis_en_avant": [2]}}
    assert not valider(nuage, "s")[1]
    nuage["courbe"]["x_min"] = "zéro"
    assert any("x_min" in e for e in valider(nuage, "s")[1])


# --------------------------------------------------------------------------- fiche en une seule langue
def _brut_anglais_seul():
    """Fiche de lancement réduite à l'anglais : parcours Actuariat, EN d'abord (demande de JG, 2026-11-11)."""
    brut = valider(brut_lancement())
    brut["langues"] = ["en"]
    del brut["editions"]["fr"]
    brut["pedagogie"]["objectifs"].pop("fr")
    return brut


def test_fiche_anglais_seul_acceptee(tmp_path):
    fiche = charger_fiche(ecrire(tmp_path, _brut_anglais_seul(), "2026-11-lancement-actu-basics"))
    assert fiche.langues == ("en",) and set(fiche.editions) == {"en"}
    r = constats_pedago(tmp_path, _brut_anglais_seul())
    assert not r.bloquants, [str(c) for c in r.bloquants]
    assert any("une seule langue" in o for o in r.ok)
    assert not any("FR et EN" in str(a) or "entre FR et EN" in str(a) for a in r.avertissements)


def test_fiche_bilingue_par_defaut(tmp_path):
    assert charger_fiche(LANCEMENT).langues == ("fr", "en")


@pytest.mark.parametrize("modif, attendu", [
    (lambda b: b.update(langues=["de"]), "langues doit être une liste"),
    (lambda b: b.update(langues=[]), "langues doit être une liste"),
    (lambda b: b["editions"].update(fr={"titre": "x"}), "editions.fr : langue absente"),
    (lambda b: b.update(langues=["fr", "en"]), "editions.fr : édition manquante"),
])
def test_langues_mal_renseignees(tmp_path, modif, attendu):
    brut = _brut_anglais_seul()
    modif(brut)
    with pytest.raises(FicheInvalide, match=attendu):
        charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics"))


def test_objectifs_exiges_seulement_pour_les_langues_de_la_fiche(tmp_path):
    brut = _brut_anglais_seul()
    brut["pedagogie"]["objectifs"].pop("en")
    with pytest.raises(FicheInvalide, match="« en » d'objectifs"):
        charger_fiche(ecrire(tmp_path, brut, "2026-11-lancement-actu-basics"))


def test_produire_anglais_seul_refuse_le_francais(tmp_path):
    f = ecrire(tmp_path, _brut_anglais_seul(), "2026-11-lancement-actu-basics")
    ok = lancer(f, "--verifier")
    assert ok.returncode == 0, ok.stdout + ok.stderr
    fr = lancer(f, "--verifier", "--langues", "fr")
    assert fr.returncode != 0 and "absente(s) de la fiche : FR" in fr.stdout


# --------------------------------------------------------------------------- chapitres YouTube
def test_chapitres_youtube():
    from lmec.fiche import Edition, Scene
    from lmec.textes import chapitres
    sc = [Scene(type="accroche", texte="x", voix_off="", duree=None, extra={})]
    for n in (1, 2, 3):
        sc.append(Scene(type="titre", texte=f"Part *{n}*", voix_off="", duree=None, extra={"numero": str(n)}))
        sc.append(Scene(type="texte", texte="y", voix_off="", duree=None, extra={}))
    ed = Edition(langue="en", titre="t", legende="l", hashtags=[], scenes=sc)
    durees = [20, 3, 40, 3, 60, 3, 3600]
    assert chapitres(ed, durees) == [("0:00", "Intro"), ("0:20", "1. Part 1"), ("1:03", "2. Part 2"),
                                     ("2:06", "3. Part 3")]
    assert chapitres(ed, [20, 3, 2, 3, 60, 3, 30]) == []            # un chapitre de moins de 10 s
    assert chapitres(Edition(langue="en", titre="t", legende="l", hashtags=[], scenes=sc[:3]), [20, 3, 40]) == []


# --------------------------------------------------------------------------- parcours du spectateur et logo mobile
def _lecon(scenes_fr, scenes_en=None):
    """Fiche d'exemple passée en épisode long, avec les scènes données (type, texte, voix_off)."""
    brut = valider(brut_exemple())
    brut["format"] = "youtube_lesson"
    for langue, scenes in (("fr", scenes_fr), ("en", scenes_en or scenes_fr)):
        ed = brut["editions"][langue]
        base = {s["type"]: s for s in ed["scenes"]}
        ed["scenes"] = [dict(base.get(t, {}), type=t, texte=x, voix_off=v) for t, x, v in scenes]
    return brut


ACCROCHE = ("accroche", "Pourquoi attend-on plus longtemps ?", "")
FIN = ("fin", "ACTU-BASICS", "")
CLOTURE_FR = ("cloture", "Abonnez-vous, likez, partagez", "La suite : l'épisode suivant porte sur la variance.")
CLOTURE_EN = ("cloture", "Subscribe, like, share", "Up next: the next episode is about variance.")


def test_episode_long_sans_accueil_ni_cloture_bloque(tmp_path):
    bloq, _ = constats(tmp_path, _lecon([ACCROCHE, ("texte", "Un texte", ""), FIN]))
    assert any("accueil" in b for b in bloq)
    assert any("cloture" in b for b in bloq)


def test_episode_long_complet_accepte(tmp_path):
    fr = [ACCROCHE, ("accueil", "Bonjour, et merci d'être là", ""), ("texte", "Un texte", ""), CLOTURE_FR, FIN]
    en = [ACCROCHE, ("accueil", "Hi, and thanks for being here", ""), ("texte", "A text", ""), CLOTURE_EN, FIN]
    bloq, _ = constats(tmp_path, _lecon(fr, en))
    assert not [b for b in bloq if "accueil" in b.lower() or "clôture" in b.lower() or "cloture" in b]


def test_cloture_incomplete_nomme_ce_qui_manque(tmp_path):
    fr = [ACCROCHE, ("accueil", "Bonjour", ""), ("cloture", "Abonnez-vous", ""), FIN]
    bloq, _ = constats(tmp_path, _lecon(fr))
    msg = next(b for b in bloq if "Clôture incomplète" in b)
    assert "suite" in msg and "like" in msg and "partage" in msg and "abonnement" not in msg


def test_accueil_en_premiere_scene_signale(tmp_path):
    fr = [("accueil", "Bonjour, et merci d'être là", ""), ACCROCHE, CLOTURE_FR, FIN]
    _, avert = constats(tmp_path, _lecon(fr, [("accueil", "Hi, thanks", ""), ACCROCHE, CLOTURE_EN, FIN]))
    assert any("commence par l'accueil" in a for a in avert)


def test_short_renvoie_vers_l_episode_complet(tmp_path):
    brut = valider(brut_exemple())
    _, avert = constats(tmp_path, brut)
    assert any("épisode complet" in a for a in avert)
    brut["editions"]["fr"]["scenes"][-1]["texte"] = "L'épisode complet est sur la chaîne YouTube ACTU-BASICS."
    brut["editions"]["en"]["scenes"][-1]["texte"] = "The full episode is on the ACTU-BASICS YouTube channel."
    bloq, avert = constats(tmp_path, brut)
    assert not any("épisode complet" in a for a in avert + bloq)


def test_plus_de_nom_de_marque_fixe_en_video_et_logo_mobile():
    from PIL import ImageChops
    fiche = charger_fiche(EXEMPLE)
    ed = fiche.editions["fr"]
    for fmt in ("video", "lecon"):
        sans = Rendu(fiche, "fr", _charte(logo__mobile__actif=False), fmt, False)
        avec = Rendu(fiche, "fr", CHARTE, fmt, False)
        scene = ed.scenes[0]
        im = sans.dessiner(scene, 0, len(ed.scenes))
        g, h, dr, _ = sans.zone
        # Bandeau du haut vide : ni nom « ACTU-BASICS » ni logo quand le logo mobile est coupé.
        assert ImageChops.difference(im.crop((g, h, dr, h + 120)), sans._fond.crop((g, h, dr, h + 120))).getbbox() is None
        assert avec.mobile_prevu(scene) and not avec.mobile_prevu(ed.scenes[-1])   # jamais sur la fin
        x0, y0 = avec.mobile_position(0)
        x1, _ = avec.mobile_position(avec.conf_mobile()["periode_s"] / 2)
        lg, hl, p = avec._mobile_taille()
        assert x1 > x0 and g <= x0 - p and x1 + lg + p <= dr and y0 >= h   # il bouge, dans la zone
        avec.mesurer_mobile(scene, 0, len(ed.scenes))
        pose = avec.poses[("mobile", 0)]
        assert pose.recouvrement <= logo_mod.SEUIL_RECOUVREMENT   # aucun texte sous le logo
        assert pose.largeur == lg and pose.boite[3] - pose.boite[1] == hl   # proportions conservées


def test_carrousel_garde_le_nom_de_marque():
    from PIL import ImageChops
    fiche = charger_fiche(EXEMPLE)
    ed = fiche.editions["fr"]
    r = Rendu(fiche, "fr", CHARTE, "carrousel", False)
    im = r.dessiner(ed.scenes[1], 1, len(ed.scenes))
    g, h, dr, _ = r.zone
    assert ImageChops.difference(im.crop((g, h, g + 300, h + 40)), r._fond.crop((g, h, g + 300, h + 40))).getbbox()
    assert not r.mobile_prevu(ed.scenes[1])


# ---------------------------------------------------------------- revue ChatGPT de la PR #50

def test_empreinte_modele_depend_du_contenu_pas_de_la_taille(tmp_path):
    """Deux modèles différents de même nom et même taille ne partagent pas le cache audio (issue #53)."""
    from lmec.tts import empreinte_fichier
    a, b = tmp_path / "a" / "voix.onnx", tmp_path / "b" / "voix.onnx"
    a.parent.mkdir(); b.parent.mkdir()
    a.write_bytes(b"\x00" * 1000); b.write_bytes(b"\x00" * 999 + b"\x01")
    assert a.stat().st_size == b.stat().st_size
    assert empreinte_fichier(a) != empreinte_fichier(b)
    assert empreinte_fichier(a) == empreinte_fichier(a).strip() and empreinte_fichier(a).startswith("sha256-")
    piper_a = Piper({"modele": str(a)}, "fr")
    piper_b = Piper({"modele": str(b)}, "fr")
    assert piper_a.signature() != piper_b.signature()


def test_laboratoire_trajets_ep_s2a():
    """Les nombres annoncés dans contenus/conception/EP-S2A.yaml sortent du module de calcul (issue #55)."""
    from lmec import laboratoires as lab
    t = [4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44]
    assert lab.moyenne(t) == 21.25 and lab.mediane(t) == 20
    assert [c.effectif for c in lab.classes_regulieres(t, 10)] == [3, 7, 6, 3, 1]
    assert [c.effectif for c in lab.classes_regulieres(t, 20)] == [10, 9, 1]
    cinq = lab.classes_regulieres(t, 5)
    assert [c.effectif for c in cinq] == [1, 2, 3, 4, 2, 4, 1, 2, 1]
    assert cinq[-1].fin == 45 and max(t) < cinq[-1].fin          # la dernière classe dépasse le maximum
    # Borne gauche incluse, droite exclue : 15 va dans [15 ; 20[, 20 dans [20 ; 30[.
    assert lab.classes_regulieres([15], 5)[-1].debut == 15
    assert lab.classes_regulieres([0, 20], 10)[-1] == lab.Classe(20, 30, 1)
    demenage = lab.remplacer(t, t.index(44), 120)
    assert len(demenage) == 20 and lab.moyenne(demenage) == pytest.approx(25.05) and lab.mediane(demenage) == 20


def test_laboratoire_classes_inegales_et_normalisations():
    from lmec import laboratoires as lab
    ages = lab.classes_depuis_effectifs([0, 20, 30, 60], [8, 12, 20])
    assert [round(c.densite_effectif(), 2) for c in ages] == [0.4, 1.2, 0.67]
    assert ages[1].densite_effectif() * ages[1].largeur == 12                 # aire = effectif
    assert lab.aire_totale(ages, "effectif") == pytest.approx(40)             # aire totale = N
    assert lab.aire_totale(ages, "frequence") == pytest.approx(1)             # densité de fréquence
    with pytest.raises(ValueError):
        lab.classes_inegales([5, 60], [0, 20, 30, 60])                         # 60 hors de [0 ; 60[


def test_laboratoire_curseur_recalcule_la_mediane_apres_tri():
    from lmec import laboratoires as lab
    cafe = [1600, 1800, 1900, 2000, 2200, 2300, 2500, 2700, 2800, 2300]
    etats = lab.balayage(cafe, 9, [2300, 2800, 50000, 200000])
    assert [e["mediane"] for e in etats] == [2250] * 4                        # dès 2 300 € : 2 250 €
    assert etats[0]["moyenne"] == 2210 and etats[-1]["moyenne"] == 21980
    assert etats[-1]["serie_triee"][-1] == 200000
    bas = lab.balayage(cafe, 9, [1000, 2250])
    assert [e["mediane"] for e in bas] == [2100, 2225]                       # sous 2 300 € la médiane bouge
    assert lab.part_sous([5, 8, 12, 15, 15, 18, 22, 25, 30, 90], 24) == 0.7


def test_manifeste_de_rendu(tmp_path, monkeypatch):
    """Commit, empreintes et autorisation consignés (issue #51)."""
    sys.path.insert(0, str(RACINE / "production"))
    import manifeste
    fiche = tmp_path / "fiche.yaml"
    fiche.write_text("id: x\n", encoding="utf-8")
    sortie = tmp_path / "sortie"
    (sortie / "x" / "fr").mkdir(parents=True)
    (sortie / "x" / "fr" / "rapport-qc.md").write_text("ok", encoding="utf-8")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    monkeypatch.setenv("GITHUB_ACTOR", "relecteur")
    monkeypatch.delenv("GITHUB_TRIGGERING_ACTOR", raising=False)   # défini sur le runner GitHub
    monkeypatch.setenv("ENVIRONNEMENT_GITHUB", "production")
    assert manifeste.main([str(fiche), "--sortie", str(sortie), "--voix", "kokoro"]) == 0
    m = json.loads((sortie / "manifeste.json").read_text(encoding="utf-8"))
    assert m["commit"] == "abc123" and m["autorisation"]["environnement"] == "production"
    assert m["autorisation"]["lance_par"] == "relecteur"
    assert m["fiche"]["sha256"] == manifeste.sha256(fiche) and len(m["moteur_sha256"]) == 64
    assert list(m["rapports_qc_sha256"]) == ["x/fr/rapport-qc.md"]


def test_decor_ondes_bougent_sans_toucher_au_contenu():
    from PIL import Image, ImageChops, ImageDraw
    from lmec.decor import Decor
    fond = Image.new("RGB", (640, 360), (254, 248, 236))
    image = fond.copy()
    ImageDraw.Draw(image).rectangle((100, 250, 300, 330), fill=(16, 38, 56))   # contenu dans la bande des ondes
    couleurs = {"barre": (22, 133, 213), "accent": (217, 106, 0)}
    d = Decor(fond, couleurs, CHARTE["decor"], bandeau_px=60)
    a, b = d.appliquer(image, 0.0), d.appliquer(image, 3.0)
    assert ImageChops.difference(a, b).getbbox()                        # le décor bouge
    assert a.crop((100, 250, 300, 330)) == image.crop((100, 250, 300, 330))   # contenu intact
    assert a.crop((0, 0, 640, 60)) == image.crop((0, 0, 640, 60))       # bandeau du logo libre
    libre = d.masque_libre(image)
    assert d.appliquer(image, 3.0, libre) == b                          # masque réutilisable (images fixes)


def test_animations_pastilles_et_curseur_valides_et_dessinees():
    from lmec.pedagogie import _valider_animation
    trajets = [4, 7, 9, 11, 12, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 29, 32, 35, 38, 44]
    for anim in ({"modele": "pastilles", "valeurs": trajets, "largeur_classe": 10, "unite": "minutes"},
                 {"modele": "curseur", "valeurs": trajets, "indice": 19, "vers": 120, "axe_max": 55,
                  "decimales": 2}):
        erreurs, extra = [], {}
        _valider_animation({"animation": anim}, "s", erreurs, extra)
        assert not erreurs and extra["animation"]["modele"] == anim["modele"]
    erreurs = []
    _valider_animation({"animation": {"modele": "pastilles", "valeurs": trajets, "largeur_classe": 1}},
                       "s", erreurs, {})
    assert any("16 classes" in e for e in erreurs)
    erreurs = []
    _valider_animation({"animation": {"modele": "curseur", "valeurs": trajets}}, "s", erreurs, {})
    assert any("vers" in e for e in erreurs)


def test_animations_equilibre_elimination_densite_validees():
    from lmec.pedagogie import _valider_animation
    bons = ({"modele": "equilibre", "valeurs": [5, 10, 15, 30], "unite": "€"},
            {"modele": "elimination", "valeurs": [1600, 1800, 1900, 2000, 2200], "ajout": 200000, "unite": "€"},
            {"modele": "densite", "bornes": [0, 10, 20, 50], "effectifs": [3, 7, 10], "unite": "minutes"})
    for anim in bons:
        erreurs, extra = [], {}
        _valider_animation({"animation": anim}, "s", erreurs, extra)
        assert not erreurs and extra["animation"]["modele"] == anim["modele"], erreurs
    erreurs, extra = [], {}
    _valider_animation({"animation": {"modele": "elimination", "valeurs": [1, 2, 3]}}, "s", erreurs, extra)
    assert not erreurs and extra["animation"]["phases"] == ["rangement", "elimination", "milieu"]
    for faux, motif in (({"modele": "equilibre", "valeurs": list(range(9))}, "2 à 8"),
                        ({"modele": "elimination", "valeurs": [1, 2, 3], "phases": ["ajout"]}, "ajout"),
                        ({"modele": "densite", "bornes": [0, 10, 5], "effectifs": [1, 2]}, "croissantes"),
                        ({"modele": "densite", "bornes": [0, 10, 20], "effectifs": [1]}, "par classe")):
        erreurs = []
        _valider_animation({"animation": faux}, "s", erreurs, {})
        assert any(motif in e for e in erreurs), (faux, erreurs)


def test_episode_s2a_animations_dessinees_a_chaque_phase():
    """Les trois nouvelles animations de l'épisode se dessinent à tout instant, en FR et en EN, en 16:9
    comme en vertical (une barre de hauteur nulle au départ faisait échouer le rendu)."""
    fiche = charger_fiche(RACINE / "contenus/fiches/2026-12-ep-s2a-resumer-des-donnees.yaml")
    for langue, fmt in [(l, f) for l in ("fr", "en") for f in ("lecon", "video")]:
        r = Rendu(fiche, langue, CHARTE, fmt, False)
        scenes = fiche.editions[langue].scenes
        vus = set()
        for i, s in enumerate(scenes):
            m = (s.extra.get("animation") or {}).get("modele")
            if m not in ("equilibre", "elimination", "densite"):
                continue
            vus.add(m)
            for p in r._plan_animation(s):
                for t in (0.0, p["debut"], p["debut"] + 0.02, p["debut"] + p["duree"] / 2,
                          p["debut"] + p["duree"] + 0.2):
                    r.dessiner(s, i, len(scenes), t)
            r.dessiner(s, i, len(scenes), None)
        assert vus == {"equilibre", "elimination", "densite"}
