# Ticket Forge 02 — Bugs runtime de la tranche verticale (login + CRUD)

**Pour :** l'agent Claude Code travaillant sur le framework Forge (`caucrogeGit/Forge`).
**De :** projet RéférenCiel Manager, application-banc d'essai (ADR-006).
**Objet :** deux défauts **bloquants** du code généré, découverts en **exécutant
réellement** la tranche verticale (login → liste protégée → données MariaDB) après
les correctifs du ticket 01.

## Environnement

- `forge-mvc` **`f38d5159294ab246b1fd77a2615b4c96a3b64db1`**, `forge-mvc-mariadb`.
- MariaDB, Python **3.12**, profil `standard`.
- Reproduction : `make:entity` → `migration:*` → `make:crud` → `auth:init` →
  `make:auth` → brancher les routes → `forge run` → se connecter → afficher la liste.

## Point important — les portes statiques ne suffisent pas

`make check` (pyright strict, ruff, pytest, `mkdocs --strict`, `project:check`) est
**vert**, et pourtant l'application **plante à l'usage**. Ces bugs ne sont visibles
qu'en **exécutant** le parcours. Ils échappent à `make:crud`/`make:auth` parce que
personne ne lance le flux complet avec un vrai backend.

---

## P1 — Bloquant

### FORGE-10 · Login impossible avec MariaDB : `is_active` (int) refusé par `normalize_auth_user` (bool strict)

- **Symptôme** : login toujours refusé (« Identifiant ou mot de passe incorrect »),
  même avec le bon mot de passe (`verify_password(...) == True` vérifié isolément).
- **Preuve** :
  - Loader généré par `make:auth` : `SELECT ... is_active FROM users` renvoie la
    ligne **brute** ; MariaDB renvoie `BOOLEAN`/`tinyint(1)` comme **int** `0/1`.
  - `core/auth/user.py:39` : `if not isinstance(is_active, bool): raise InvalidAuthUserError`.
  - → `authenticate_user` → `normalize_auth_user` lève → capturé → renvoie `None` →
    échec **avant** la vérification du mot de passe.
  - Repro : `normalize_auth_user({..., "is_active": 1})` échoue ; `True` passe.
- **Correctif proposé** (le plus robuste en premier) :
  1. `normalize_auth_user` : `is_active = bool(is_active)` (accepte 0/1) — corrige
     **tous** les backends d'un coup ;
  2. ou le backend `forge-mvc-mariadb` mappe `tinyint(1)`/`BOOLEAN` → `bool` ;
  3. ou le loader généré par `make:auth` caste `is_active` en `bool`.
- Détail : `retour-008` (F17).

### FORGE-11 · `make:crud` inclut `components/button.html` (inexistant) → 500 au rendu

- **Symptôme** : `500` au rendu de la liste ;
  `jinja2.exceptions.TemplateNotFound: components/button.html`.
- **Preuve** :
  - Vues générées : `{% include "components/button.html" %}`
    (`cli/entities/crud/views_builder.py:101, 444, 541, 787, 790`).
  - Le bouton existe comme **macro** dans `components/ui.html`
    (`{% macro button(label, variant="primary", href=none, type="button", extra="") %}`) ;
    `forge new` ne livre **pas** de fichier `components/button.html`
    (il livre `components/{data,forms,interactive,ui}.html`).
- **Correctif proposé** :
  1. `make:crud` utilise la macro : `{% from "components/ui.html" import button %}`
     puis `{{ button(label, variant=..., href=...) }}` ;
  2. ou `forge new` livre `components/button.html` déléguant à la macro.
- Détail : `retour-008` (F18).

---

## Contournements appliqués côté projet (pour référence)

- `mvc/controllers/auth_controller.py` : `load_user_by_email` caste `is_active` en `bool`.
- `mvc/views/components/button.html` : créé, délègue à `components/ui.html::button`.

Une fois corrigés à la source, `make:auth` + `make:crud` produiraient une tranche
verticale **fonctionnelle du premier coup** sur MariaDB.

## Référence

`retour-008`. Preuves : `core/auth/user.py:39`, `cli/entities/crud/views_builder.py`,
`components/ui.html`. Flux : ticket 07 (commit `f29002c`).
