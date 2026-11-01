# Contrôles qualité avant publication

Deux niveaux : ce que la machine vérifie à chaque rendu (rapport `sortie/<id>/rapport-qc.md`) et ce qu'un humain doit regarder (≈ 3 minutes). Un ❌ bloque la publication, un ⚠️ demande un coup d'œil.

## 1. Contrôles automatiques (`produire.py`)

| Domaine | Contrôle | Gravité |
|---|---|---|
| Éditorial | Fiche validée (`statut: valide` + `valide_par`) | ❌ |
| Éditorial | Au moins une source avec une URL `http(s)` | ❌ |
| Éditorial | Période, périmètre et définition renseignés | ❌ |
| Éditorial | Scène `source` présente dans chaque langue | ❌ |
| Éditorial | Date de consultation des sources | ⚠️ |
| Linguistique | Éditions FR **et** EN présentes et complètes | ❌ |
| Linguistique | Aucun marqueur « TODO », « à compléter », « XXX » | ❌ |
| Linguistique | Nombres au format de la langue (8,2 / 8.2 ; 1 234 / 1,234) | automatique |
| Linguistique | Espaces insécables avant `; : ! ? %` en français | automatique |
| Linguistique | Nombre de scènes identique FR/EN | ⚠️ (une adaptation peut le justifier) |
| Visuel | Texte qui ne tient pas dans sa zone après réduction | ⚠️ |
| Visuel | Contenu dans les zones de sécurité (hors interface TikTok/Reels) | automatique (charte) |
| Production | Vidéo 1080×1920, H.264, piste audio présente | ❌ |
| Production | Durée entre 8 et 60 s | ⚠️ |
| Production | Fichier audio de voix off introuvable | ❌ |
| Production | Titre ≤ 100 caractères, légende ≤ 2 200 caractères, ≤ 30 hashtags | ❌ |
| Production | 3 à 5 hashtags conseillés | ⚠️ |
| Audio | Absence de voix off signalée | ⚠️ (information) |

## 2. Contrôles humains (checklist du rapport)

**Visuel**
- [ ] Planche `apercu-carrousel.png` FR et EN : aucun texte coupé, chevauchant ou illisible.
- [ ] Le chiffre affiché est identique à la fiche validée (valeur, unité, période).
- [ ] Rien d'important sous l'interface des applications (bas et droite de l'écran).
- [ ] La miniature donne envie et reste lisible en petit.

**Audio**
- [ ] Vidéo regardée en entier une fois, son activé.
- [ ] Voix off : prononciation des chiffres, des sigles et des noms propres ; volume homogène.
- [ ] Musique ajoutée (si utilisée) issue de la bibliothèque libre de la plateforme, sous la voix.

**Linguistique**
- [ ] Sous-titres synchronisés, sans faute.
- [ ] Légende : source et période présentes, ton adapté à chaque langue (adaptation, pas traduction littérale).

**Production / publication**
- [ ] Bon compte (FR ou EN) et bonne plateforme.
- [ ] Mention « contenu généré par IA » activée si une voix synthétique réaliste est utilisée.
- [ ] Date et heure de programmation conformes au calendrier.
- [ ] Après publication : fiche déplacée dans `contenus/publie/`.

## 3. En cas de problème

- Erreur de fond : ne pas corriger soi-même le chiffre dans la fiche ; renvoyer à la direction éditoriale.
- Texte trop long : raccourcir le texte de la scène (décision éditoriale si le sens change).
- Problème de rendu : relancer en local ; sinon, mode manuel (voir [guide-quotidien.md](guide-quotidien.md)).
