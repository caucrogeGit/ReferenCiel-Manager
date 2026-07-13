# Retour terrain 008 : Deux bugs runtime du code généré (login MariaDB + composant bouton)

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** ⚠️ Partiellement résolu : F17 (is_active) corrigé dans forge-mvc 809d224f (normalize_auth_user accepte un int 0/1) ; F18 (button.html manquant) toujours en attente.

## Environnement

- `forge-mvc` **f38d5159**, `forge-mvc-mariadb`, MariaDB, Python **3.12**.
- Tranche verticale ticket 07 : `make:entity` → migration → `make:crud` →
  `auth:init` → `make:auth` → `forge run`.

## Contexte : ce que seul un parcours réel révèle

**`make check` est vert** (pyright strict, ruff, pytest, mkdocs, `project:check`),
et pourtant l'application **ne fonctionne pas** : le login échoue toujours, puis la
liste renvoie 500.
Ces deux bugs sont **invisibles aux portes statiques** : seul un
**parcours end-to-end** (se connecter, afficher une liste) les fait apparaître.

## Constats

### F17 : Défaut bloquant : login impossible avec MariaDB (`is_active` int vs bool)

- **Symptôme** : « Identifiant ou mot de passe incorrect » **quel que soit** le mot
  de passe, même après reset et `verify_password(...) == True` vérifié à la main.
- **Preuve** :
  - Le loader généré par `make:auth` renvoie la ligne brute :
    `load_user_by_email` → `SELECT id, email, password_hash, is_active FROM users`.
  - MariaDB renvoie `is_active` (colonne `BOOLEAN` = `tinyint(1)`) comme **entier**
    `0/1`, pas `True/False`.
  - `core/auth/user.py:39` : `if not isinstance(is_active, bool): raise InvalidAuthUserError`.
  - Donc `authenticate_user` → `normalize_auth_user` lève `InvalidAuthUserError` →
    capturée → renvoie `None` → login refusé **avant** la vérification du mot de passe.
  - Reproduit : `normalize_auth_user({... "is_active": 1})` → **ÉCHEC** ;
    `... "is_active": True` → OK.
- **Correctif proposé** (au choix, côté framework) :
  1. `normalize_auth_user` accepte les entiers 0/1 (`is_active = bool(is_active)`),
     le plus robuste, tous backends ;
  2. **ou** le loader généré par `make:auth` caste `is_active` en `bool` ;
  3. **ou** le backend `forge-mvc-mariadb` mappe `tinyint(1)`/`BOOLEAN` → `bool`.
- **Contournement** : cast dans `load_user_by_email` (`row["is_active"] = bool(...)`).

### F18 : Défaut bloquant : `make:crud` inclut un `components/button.html` inexistant → 500

- **Symptôme** : `500 Internal Server Error` au rendu de la liste ;
  `jinja2.exceptions.TemplateNotFound: components/button.html`.
- **Preuve** :
  - Les vues générées font `{% include "components/button.html" %}`
    (`cli/entities/crud/views_builder.py:101, 444, 541, 787, 790`).
  - Or Forge fournit le bouton comme **macro** dans `components/ui.html`
    (`{% macro button(label, variant="primary", href=none, type="button", extra="") %}`),
    **pas** comme fichier `components/button.html`, absent du squelette
    (`forge new` livre `components/{data,forms,interactive,ui}.html`).
- **Correctif proposé** :
  1. `make:crud` utilise la macro existante :
     `{% from "components/ui.html" import button %}` puis `{{ button(label, variant=..., href=...) }}` ;
  2. **ou** `forge new` livre `components/button.html` qui délègue à la macro.
- **Contournement** : `mvc/views/components/button.html` créé, délègue à
  `components/ui.html::button`.

## Synthèse

Deux défauts **bloquants** dans du code fraîchement généré (`make:auth` neuf,
`make:crud`), **non détectables** par les portes statiques.
Ils confirment la valeur
d'un banc d'essai qui **exécute réellement** le parcours.
Corrigés à la source,
`make:auth` + `make:crud` produiraient une tranche verticale **qui tourne du premier
coup** sur MariaDB.

## Référence

Contournements : `mvc/controllers/auth_controller.py` (`load_user_by_email`),
`mvc/views/components/button.html`.
Preuves : `core/auth/user.py:39`,
`cli/entities/crud/views_builder.py`.
Flux : ticket 07 (commit `f29002c`).
