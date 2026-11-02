"""Synthèse vocale : fournisseurs interchangeables.

Chaque fournisseur transforme UNE phrase en un fichier WAV. Le reste de la chaîne
(découpage, durées, sous-titres, montage) ne dépend pas du fournisseur.

Fournisseurs :
  kokoro      local, gratuit, hors ligne (paquet `kokoro-onnx` + modèle Kokoro-82M téléchargé) ;
              moteur prioritaire, Piper en secours (voir docs/voice-licenses.md)
  piper       local, gratuit, hors ligne (paquet `piper-tts` + modèle de voix téléchargé)
  openai      API OpenAI (clé OPENAI_API_KEY), payant à l'usage
  elevenlabs  API ElevenLabs (clé ELEVENLABS_API_KEY), abonnement
  manuel      fichiers enregistrés à la main (un par scène)
  test        bip de synthèse pour les tests automatiques ; JAMAIS publiable

Aucune clé n'est lue ailleurs que dans les variables d'environnement.

Garde-fou de gratuité : avec `gratuit_uniquement: true` dans tts.yaml (réglage par défaut), un
fournisseur payant est refusé dès sa création, et toute requête vers une API payante est bloquée
avant de partir. Seuls les fournisseurs locaux restent possibles.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
import urllib.error
import urllib.request
import wave
from pathlib import Path

RACINE_PRODUCTION = Path(__file__).resolve().parent.parent
DOSSIER_VOIX = Path(os.environ.get("LMEC_DOSSIER_VOIX", RACINE_PRODUCTION / "voix"))
DELAI_API_S = 60
# À incrémenter si le format des fichiers du cache change (invalide tout le cache).
VERSION_CACHE = 1


class ErreurTTS(Exception):
    """La narration n'a pas pu être produite (configuration, réseau, quota…)."""


def charger_env(chemin: Path) -> None:
    """Lit un fichier .env local (jamais versionné) sans écraser l'environnement existant."""
    if not chemin.exists():
        return
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            cle, val = ligne.split("=", 1)
            os.environ.setdefault(cle.strip(), val.strip().strip('"').strip("'"))


def duree_wav(chemin: Path) -> float:
    with wave.open(str(chemin), "rb") as w:
        return w.getnframes() / w.getframerate()


def _vers_wav(source: Path, destination: Path) -> None:
    """Convertit n'importe quel fichier audio en WAV mono 48 kHz (ffmpeg)."""
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(source), "-ac", "1", "-ar", "48000",
                        str(destination)], capture_output=True, text=True)
    if r.returncode != 0:
        raise ErreurTTS(f"Conversion audio impossible ({source.name}) : {r.stderr.strip()[:200]}")


class Fournisseur:
    nom = "?"
    publiable = True       # False : la vidéo ne peut pas sortir en mode final
    par_scene = False      # True : le fournisseur livre une scène entière (mode manuel)

    def __init__(self, config_langue: dict, langue: str):
        self.config = config_langue or {}
        self.langue = langue

    def signature(self) -> str:
        """Identifie la voix : sert de clé de cache (changer de voix = nouvelle synthèse).

        Contient le fournisseur, la langue, TOUTE la configuration de voix de tts.yaml
        (voix, modèle, consignes, vitesse, réglages…) et l'empreinte du modèle local s'il y en a un.
        """
        return json.dumps({"v": VERSION_CACHE, "f": self.nom, "c": self.config, "l": self.langue,
                           "m": self.empreinte_modele()}, sort_keys=True, default=str)

    def empreinte_modele(self) -> str:
        """Identifiant du modèle local (vide pour une API : le modèle est dans la config)."""
        return ""

    def synthetiser(self, texte: str, destination: Path) -> None:
        raise NotImplementedError

    def verifier(self) -> None:
        """Lève ErreurTTS si le fournisseur n'est pas utilisable (clé absente, modèle manquant…)."""


class Piper(Fournisseur):
    nom = "piper"

    def _modele(self) -> Path:
        nom = self.config.get("modele")
        if not nom:
            raise ErreurTTS(f"tts.yaml : voix.{self.langue}.piper.modele manquant")
        chemin = Path(nom) if Path(nom).is_absolute() else DOSSIER_VOIX / nom
        if not chemin.exists():
            raise ErreurTTS(f"Modèle Piper introuvable : {chemin}. Lancez : python production/telecharger_voix.py")
        return chemin

    def empreinte_modele(self) -> str:
        # Nom + taille du fichier .onnx : un modèle remplacé sous le même nom invalide le cache.
        try:
            chemin = self._modele()
        except ErreurTTS:
            return "absent"
        return f"{chemin.name}:{chemin.stat().st_size}"

    def verifier(self) -> None:
        try:
            import piper  # noqa: F401
        except ImportError as exc:
            raise ErreurTTS("Paquet « piper-tts » absent : pip install -r production/requirements-voix.txt") from exc
        self._modele()

    def synthetiser(self, texte: str, destination: Path) -> None:
        from piper import PiperVoice, SynthesisConfig
        voix = _charger_piper(str(self._modele()))
        cfg = SynthesisConfig(speaker_id=self.config.get("locuteur"),
                              length_scale=self.config.get("lenteur", 1.0),
                              noise_scale=self.config.get("variation", 0.667),
                              noise_w_scale=self.config.get("variation_rythme", 0.8))
        brut = destination.with_suffix(".piper.wav")
        with wave.open(str(brut), "wb") as w:
            voix.synthesize_wav(texte, w, syn_config=cfg)
        _vers_wav(brut, destination)
        brut.unlink(missing_ok=True)


_CACHE_PIPER: dict = {}


def _charger_piper(chemin: str):
    import logging
    # Piper signale chaque phonème absent du modèle (voyelles nasales des anciennes voix FR) :
    # limite connue, documentée dans docs/technique/voix-off.md ; inutile d'inonder la console.
    logging.getLogger("piper").setLevel(logging.ERROR)
    if chemin not in _CACHE_PIPER:
        from piper import PiperVoice
        _CACHE_PIPER[chemin] = PiperVoice.load(chemin)
    return _CACHE_PIPER[chemin]


FOURNISSEURS_PAYANTS = ("openai", "elevenlabs")
# Activé par creer_fournisseur quand tts.yaml impose la gratuité : dernier verrou avant le réseau.
_GRATUIT_UNIQUEMENT = {"actif": False}


class ServicePayantRefuse(ErreurTTS):
    """Tentative d'utiliser un service payant alors que la gratuité est imposée."""


def _requete(url: str, entetes: dict, corps: dict) -> bytes:
    if _GRATUIT_UNIQUEMENT["actif"]:
        raise ServicePayantRefuse(f"Appel refusé vers {url.split('/')[2]} : service payant, interdit par "
                                  "« gratuit_uniquement: true » (tts.yaml)")
    req = urllib.request.Request(url, data=json.dumps(corps).encode(), headers=entetes, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=DELAI_API_S) as rep:
            return rep.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise ErreurTTS(f"{url.split('/')[2]} a répondu {exc.code} : {detail}") from exc
    except urllib.error.URLError as exc:
        raise ErreurTTS(f"Réseau indisponible pour {url.split('/')[2]} : {exc.reason}") from exc


class Kokoro(Fournisseur):
    """Kokoro-82M (ONNX), exécuté en local sur le processeur. Aucun appel réseau à la synthèse."""
    nom = "kokoro"
    TAUX = 24000

    def _fichiers(self) -> tuple[Path, Path]:
        modele = DOSSIER_VOIX / self.config.get("modele", "kokoro-v1.0.onnx")
        voix = DOSSIER_VOIX / self.config.get("fichier_voix", "voices-v1.0.bin")
        for f in (modele, voix):
            if not f.exists():
                raise ErreurTTS(f"Fichier Kokoro introuvable : {f}. Lancez : python production/telecharger_voix.py")
        return modele, voix

    def empreinte_modele(self) -> str:
        try:
            modele, voix = self._fichiers()
        except ErreurTTS:
            return "absent"
        return f"{modele.name}:{modele.stat().st_size}|{voix.name}:{voix.stat().st_size}"

    def verifier(self) -> None:
        try:
            import kokoro_onnx  # noqa: F401
        except ImportError as exc:
            raise ErreurTTS("Paquet « kokoro-onnx » absent : pip install -r production/requirements-voix.txt") from exc
        self._fichiers()
        if not self.config.get("voix"):
            raise ErreurTTS(f"tts.yaml : voix.{self.langue}.kokoro.voix manquant (ex. ff_siwis, af_heart)")
        if self.config["voix"] not in _charger_kokoro(*map(str, self._fichiers())).get_voices():
            raise ErreurTTS(f"Voix Kokoro « {self.config['voix']} » absente du fichier de voix")

    def synthetiser(self, texte: str, destination: Path) -> None:
        import numpy as np
        moteur = _charger_kokoro(*map(str, self._fichiers()))
        echantillons, taux = moteur.create(texte, voice=self.config["voix"], speed=self.config.get("vitesse", 1.0),
                                           lang=self.config.get("langue", "fr-fr" if self.langue == "fr" else "en-us"))
        brut = destination.with_suffix(".kokoro.wav")
        with wave.open(str(brut), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(taux)
            w.writeframes((np.clip(echantillons, -1, 1) * 32767).astype(np.int16).tobytes())
        _vers_wav(brut, destination)
        brut.unlink(missing_ok=True)


_CACHE_KOKORO: dict = {}


def _charger_kokoro(modele: str, voix: str):
    import logging
    logging.getLogger("kokoro_onnx").setLevel(logging.ERROR)
    if (modele, voix) not in _CACHE_KOKORO:
        from kokoro_onnx import Kokoro as MoteurKokoro
        _CACHE_KOKORO[(modele, voix)] = MoteurKokoro(modele, voix)
    return _CACHE_KOKORO[(modele, voix)]


class OpenAI(Fournisseur):
    nom = "openai"
    URL = "https://api.openai.com/v1/audio/speech"

    def verifier(self) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise ErreurTTS("Variable OPENAI_API_KEY absente (fichier .env local ou secret GitHub)")

    def synthetiser(self, texte: str, destination: Path) -> None:
        self.verifier()
        corps = {"model": self.config.get("modele", "gpt-4o-mini-tts"), "voice": self.config.get("voix", "alloy"),
                 "input": texte, "response_format": "wav"}
        if self.config.get("consignes") and not corps["model"].startswith("tts-1"):
            corps["instructions"] = self.config["consignes"]
        if self.config.get("vitesse"):
            corps["speed"] = self.config["vitesse"]
        audio = _requete(self.URL, {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                                    "Content-Type": "application/json"}, corps)
        brut = destination.with_suffix(".api.wav")
        brut.write_bytes(audio)
        _vers_wav(brut, destination)
        brut.unlink(missing_ok=True)


class ElevenLabs(Fournisseur):
    nom = "elevenlabs"

    def verifier(self) -> None:
        if not os.environ.get("ELEVENLABS_API_KEY"):
            raise ErreurTTS("Variable ELEVENLABS_API_KEY absente (fichier .env local ou secret GitHub)")
        if not self.config.get("voice_id"):
            raise ErreurTTS(f"tts.yaml : voix.{self.langue}.elevenlabs.voice_id manquant")

    def synthetiser(self, texte: str, destination: Path) -> None:
        self.verifier()
        url = (f"https://api.elevenlabs.io/v1/text-to-speech/{self.config['voice_id']}"
               "?output_format=mp3_44100_128")
        corps = {"text": texte, "model_id": self.config.get("modele", "eleven_multilingual_v2")}
        if self.config.get("forcer_langue"):  # pris en charge par certains modèles seulement
            corps["language_code"] = self.langue
        if self.config.get("reglages"):
            corps["voice_settings"] = self.config["reglages"]
        audio = _requete(url, {"xi-api-key": os.environ["ELEVENLABS_API_KEY"],
                               "Content-Type": "application/json", "Accept": "audio/mpeg"}, corps)
        brut = destination.with_suffix(".mp3")
        brut.write_bytes(audio)
        _vers_wav(brut, destination)
        brut.unlink(missing_ok=True)


class Manuel(Fournisseur):
    """Enregistrements faits à la main : <dossier>/<NN>.(wav|mp3|m4a), un fichier par scène."""
    nom = "manuel"
    par_scene = True

    def __init__(self, config_langue, langue, dossier: Path | None = None):
        super().__init__(config_langue, langue)
        self.dossier = dossier

    def verifier(self) -> None:
        if not self.dossier or not self.dossier.is_dir():
            raise ErreurTTS(f"Dossier d'enregistrements introuvable : {self.dossier}")

    def fichier_scene(self, numero: int) -> Path:
        for ext in ("wav", "mp3", "m4a", "aac", "ogg"):
            f = self.dossier / f"{numero:02d}.{ext}"
            if f.exists():
                return f
        raise ErreurTTS(f"Enregistrement manquant pour la scène {numero} : {self.dossier}/{numero:02d}.mp3")

    def synthetiser_scene(self, numero: int, destination: Path) -> None:
        _vers_wav(self.fichier_scene(numero), destination)


class VoixTest(Fournisseur):
    """Son de test (bip doux) d'une durée réaliste : permet de tester la chaîne sans voix ni clé."""
    nom = "test"
    publiable = False

    def synthetiser(self, texte: str, destination: Path) -> None:
        duree = max(0.6, len(texte) / 15.0)
        taux = 48000
        with wave.open(str(destination), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(taux)
            images = bytearray()
            for i in range(int(duree * taux)):
                enveloppe = min(1.0, i / 2000, (duree * taux - i) / 2000)
                images += struct.pack("<h", int(3000 * enveloppe * math.sin(2 * math.pi * 220 * i / taux)))
            w.writeframes(bytes(images))


FOURNISSEURS = {c.nom: c for c in (Kokoro, Piper, OpenAI, ElevenLabs, Manuel, VoixTest)}


def creer_fournisseur(nom: str, config_tts: dict, langue: str, dossier_manuel: Path | None = None) -> Fournisseur:
    if nom not in FOURNISSEURS:
        raise ErreurTTS(f"Fournisseur TTS inconnu « {nom} » ({', '.join(FOURNISSEURS)})")
    _GRATUIT_UNIQUEMENT["actif"] = bool(config_tts.get("gratuit_uniquement", True))
    if _GRATUIT_UNIQUEMENT["actif"] and nom in FOURNISSEURS_PAYANTS:
        raise ServicePayantRefuse(f"Fournisseur « {nom} » payant refusé : tts.yaml impose « gratuit_uniquement: true ». "
                                  "Le passer à false est une décision de dépense, réservée à JG.")
    cfg = ((config_tts.get("voix") or {}).get(langue) or {}).get(nom, {})
    if nom == "manuel":
        return Manuel(cfg, langue, dossier_manuel)
    return FOURNISSEURS[nom](cfg, langue)


def creer_avec_secours(nom: str, config_tts: dict, langue: str,
                       dossier_manuel: Path | None = None) -> tuple[Fournisseur, str | None]:
    """Crée le fournisseur et vérifie qu'il est utilisable ; sinon, bascule sur le fournisseur de
    secours de tts.yaml (« secours: {kokoro: piper} »). Retourne (fournisseur, note de bascule)."""
    principal = creer_fournisseur(nom, config_tts, langue, dossier_manuel)
    try:
        principal.verifier()
        return principal, None
    except ServicePayantRefuse:
        raise
    except ErreurTTS as exc:
        secours = (config_tts.get("secours") or {}).get(nom)
        if not secours:
            raise
        remplacant = creer_fournisseur(secours, config_tts, langue, dossier_manuel)
        remplacant.verifier()
        return remplacant, f"Voix « {nom} » indisponible ({exc}) : secours « {secours} » utilisé"


class Cache:
    """Évite de payer deux fois la même phrase.

    Clé = SHA-256 de (version du cache, fournisseur, langue, configuration complète de la voix,
    empreinte du modèle local, texte exact envoyé à la synthèse, lexique de prononciation compris).
    Changer un mot, une voix, une consigne ou une vitesse donne une nouvelle clé : jamais de
    réutilisation d'un audio qui ne correspond pas. Le fournisseur « manuel » n'est pas mis en cache.
    """

    def __init__(self, dossier: Path):
        self.dossier = dossier
        dossier.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def cle(fournisseur: Fournisseur, texte: str) -> str:
        return hashlib.sha256((fournisseur.signature() + "\n" + texte).encode()).hexdigest()[:32]

    def obtenir(self, fournisseur: Fournisseur, texte: str, destination: Path) -> bool:
        """Copie l'audio en cache vers `destination` (True) ou le synthétise et le range (False)."""
        fichier = self.dossier / f"{self.cle(fournisseur, texte)}.wav"
        if fichier.exists() and fichier.stat().st_size > 44:
            shutil.copyfile(fichier, destination)
            os.utime(fichier)  # « dernière utilisation », pour le nettoyage
            return True
        fournisseur.synthetiser(texte, destination)
        temporaire = fichier.with_suffix(".tmp")
        shutil.copyfile(destination, temporaire)
        temporaire.replace(fichier)  # écriture atomique : pas de fichier à moitié écrit en cache
        return False

    def nettoyer(self, jours: int = 90) -> int:
        """Supprime les audios inutilisés depuis `jours` jours (le cache ne grossit pas sans fin)."""
        import time
        limite = time.time() - jours * 86400
        supprimes = 0
        for f in self.dossier.glob("*"):
            if f.stat().st_mtime < limite:  # chaque utilisation remet la date à jour
                f.unlink(missing_ok=True)
                supprimes += 1
        return supprimes
