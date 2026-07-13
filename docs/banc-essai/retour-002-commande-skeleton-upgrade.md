# Retour terrain 002 : Un chemin outillé pour mettre à jour le squelette d'un projet existant

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** ✅ Résolu dans forge-mvc f38d5159 (2026-07-08), vérifié sur le banc d'essai.

## Environnement

- `forge-mvc` **1.0.0rc2**, projet monté sur le squelette récent (commit
  `e3197866…`).
- Profil projet **`standard`**, Python **3.12**.

## Contexte et méthode

Le dépôt public de Forge bouge souvent.
Une application-banc d'essai doit **suivre
cette évolution régulièrement**.
Or `forge new` sait **créer** un projet, mais il
n'existe **aucun chemin outillé pour mettre à jour le squelette d'un projet
existant**.
Chaque application doit donc réinventer une procédure manuelle, et
c'est risqué : notre première tentative, par déplacement de dossier, a **cassé le
`.venv`** (chemins absolus non déplaçables) et imposé un **force-push**.

Nous avons formalisé une procédure sûre côté application
([ADR-010](../adr/010-montee-squelette-forge-en-place.md) + manifeste de propriété),
mais elle **devrait vivre dans Forge**.

## Constat

### F8 : Suggestion (cycle de vie) : pas de commande de montée de squelette

Deux niveaux évoluent indépendamment et n'ont pas le même outillage :

1. **Le framework** (`forge-mvc`, pin git) : mise à jour = bump du pin +
   réinstallation. **Piège vérifié** : un pin git à **version inchangée**
   (`1.0.0rc2`) n'est **pas re-fetché** par pip → il faut forcer
   `pip install --force-reinstall --no-deps`.
   Un projet naïf croit avoir mis à
   jour Forge alors qu'il tourne encore sur l'ancien commit.
2. **Le squelette** (`app.py`, `mvc/`, `optins/registry.py`, CI, gabarit ADR…) :
   mise à jour = rafraîchir les fichiers **appartenant au squelette** sans toucher
   au code utilisateur.
   Rien n'aide à distinguer les deux.

### Ce que Forge a déjà pour bâtir dessus

- La discipline **write-if-new** : les générateurs savent nativement **quels
  fichiers appartiennent au squelette** vs à l'utilisateur, exactement le
  « manifeste de propriété » qu'un projet doit sinon reconstruire à la main.
- `forge agents:init --check` : compare déjà `CLAUDE.md`/`AGENTS.md` à la référence.
  Le même esprit peut couvrir tout le squelette.

## Proposition

Une commande **`forge skeleton:upgrade`** (nom à décider) qui :

- **rafraîchit les fichiers appartenant au squelette** (en s'appuyant sur
  write-if-new) et **affiche un diff** pour tout ce qui est utilisateur, sans
  jamais l'écraser silencieusement ;
- **met à jour le pin** `forge-mvc` (et `forge-mvc-testing`) et **force la
  réinstallation** au bon commit (résout le piège pip ci-dessus) ;
- **ne touche ni au `.venv` ni au `.git`** du projet ;
- offre un mode **`--check`** (dry-run) listant les écarts squelette/pin, dans
  l'esprit de `forge agents:init --check`.

**Bénéfice** : chaque application Forge suit l'évolution du framework par une
commande officielle, sûre et rejouable, au lieu d'une procédure maison fragile.
C'est le pendant naturel de `forge new` pour la **maintenance**.

## Référence

Manifeste de propriété et procédure rejouable qui ont servi de base à cette
proposition : [docs/procedures/montee-squelette-forge.md](../procedures/montee-squelette-forge.md).
