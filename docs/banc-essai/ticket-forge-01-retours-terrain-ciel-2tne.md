# Ticket Forge : Retours terrain (banc d'essai RéférenCiel Manager)

**Pour :** l'agent Claude Code travaillant sur le framework Forge (`caucrogeGit/Forge`).
**De :** projet RéférenCiel Manager, application-banc d'essai (ADR-006).
**Objet :** défauts et frictions rencontrés en construisant une **tranche verticale
réelle** (entité → migration → CRUD → auth) sur Forge.
Chaque point est **fondé sur
une preuve reproductible** (fichier:ligne, commande, sortie) avec un **correctif
proposé**.

> ## ✅ Résolu : forge-mvc `f38d5159` (2026-07-08)
>
> **Les 9 items ont été corrigés** côté framework et **vérifiés sur le banc d'essai**
> (montée du projet sur `f38d5159`, `make check` vert).
> Les correctifs sont taggés
> dans le code Forge avec les IDs de ce ticket :
>
> | Item | Correctif (Forge) | Vérif |
> |---|---|---|
> | FORGE-1 | `crud/controller_builder.py` : flash via `get_flash`/`redirect_with_flash` (plus d'import cassé) | ✅ |
> | FORGE-2 | `db:init` affiche `CREATE TABLE forge_migrations` | ✅ |
> | FORGE-3 | `entities/db_apply.py:76` : applique `mvc/models/sql/*.sql` | ✅ |
> | FORGE-4 | `security/auth.py:287` : ponts opt-in émis seulement si l'opt-in installé | ✅ |
> | FORGE-5 | `security/make_auth.py` : `forge make:auth` (login) | ✅ |
> | FORGE-6 | `make_entity.py:584` : `from_dict` sans `reportArgumentType` | ✅ |
> | FORGE-7 | `make_entity.py:673` : pas de F401 dans `__init__.py` | ✅ |
> | FORGE-8 | `crud/model_builder.py` : signatures de modèle typées | ✅ |
> | FORGE-9 | `commands/skeleton_upgrade.py` : `forge skeleton:upgrade` | ✅ |
>
> Bonus : évolution `mvc/routes.py` → package `mvc/routes/` (ADR-068).
> Le détail
> ci-dessous est conservé pour la trace ; les statuts des retours 001-007 sont passés
> à « Résolu ».

## Environnement

- `forge-mvc` épinglé au commit **`e3197866fcf780c6d5d10cd317e3f4f671668749`**.
- `forge-mvc-mariadb` au commit **`ff41d83909d26311a737ea0d549ca2052049bc63`**.
- MariaDB, Python **3.12**, profil `standard`.
- Portes qualité du projet (alignées Forge) : `pyright` strict par fichier, `ruff`
  (`select = ["E","F"]`), `pytest`, `mkdocs --strict`, `forge project:check`.
- Opt-ins `rbac` / `mfa` **non installés** (différés volontairement).

## Scénario reproductible

```
forge make:entity AnneeScolaire        # contrat + modèle
forge sync:entity AnneeScolaire        # SQL + _base.py
forge migration:make ... --from-entity # migration
forge migration:apply                  # -> table
forge make:crud AnneeScolaire          # CRUD
forge auth:init ; forge auth:user:create
```

---

## P1 : Bloquant (la chaîne ne fonctionne pas *out of the box*)

### FORGE-1 · `make:crud` génère un import vers un helper que Forge ne fournit jamais

- **Symptôme** : le contrôleur généré **plante à l'import** (`ModuleNotFoundError:
  mvc.helpers.flash`). Le CRUD n'est pas exécutable.
- **Preuve** : `cli/entities/crud/controller_builder.py:782` émet en dur
  `from mvc.helpers.flash import render_flash_html` ; l'appel `render_flash_html(request)`
  est injecté dans les contextes (l.200, 372, 727) et le layout l'affiche
  (`{{ flash_html | safe }}`). Or **`render_flash_html` n'est défini nulle part**
  (ni cœur, ni généré, aucun template). Aucun `mvc/helpers/flash.py` n'est créé.
- **Correctif proposé** : soit `make:crud` **génère** `mvc/helpers/flash.py`
  (write-if-new), soit `render_flash_html` est **fourni par le cœur**
  (`core.mvc` / `core.security`) et importé de là. Un générateur ne doit pas émettre
  un import qu'il ne satisfait pas.
- Détail : `retour-005`.

### FORGE-2 · Le registre `forge_migrations` n'est jamais créé sur le chemin de provisioning manuel

- **Symptôme** : `migration:status` / `migration:apply` échouent :
  `[ERREUR] Lecture de forge_migrations impossible. Lancez d'abord : forge db:init`,
  alors que `db:init` **a été lancé**.
- **Preuve** : `forge db:init` en **mode affiche** (défaut) imprime `CREATE DATABASE`
  + 2 comptes, **sans** `forge_migrations`. La table n'est créée qu'en **`--run`**
  (`cli/entities/db_init.py`, `_create_forge_migrations_table`, ~l.244/367). Or
  `--run` exige des droits **serveur** pour `DB_ADMIN`, ce que contredit le compte
  admin *scellé à la base* que `db:init` recommande lui-même. La DDL existe pourtant
  (`dialect.forge_migrations_ddl` / `db_init.FORGE_MIGRATIONS_TABLE_SQL`, l.28).
- **Correctif proposé** : (a) **inclure** `CREATE TABLE forge_migrations` dans le SQL
  **affiché** (il ne requiert que `CREATE` sur `DB_NAME`) ; **ou** (b) auto-amorcer le
  registre au premier `migration:apply` ; **et** (c) corriger le message (distinguer
  « base non provisionnée » de « registre absent »).
- Détail : `retour-003`.

### FORGE-3 · `db:apply` ignore `mvc/models/sql/` ; `auth:init` recommande une commande sans effet

- **Symptôme** : après `forge auth:init`, la commande recommandée `forge db:apply`
  **ne crée aucune table auth**.
- **Preuve** : `cli/entities/db_apply.py` : `collect_sql_files` (l.68-76) n'itère que
  `mvc/entities/*/` + `relations.sql` ; `main` utilise `entities_root = mvc/entities`
  (l.109). Le répertoire `mvc/models/sql/` (où `auth:init` écrit) est **jamais scanné**.
- **Correctif proposé** : que `db:apply` applique aussi `mvc/models/sql/*.sql`, ou
  fournir une commande dédiée (`forge auth:apply` ?), ou corriger le message de
  `auth:init`.
- Détail : `retour-006` (F14).

### FORGE-4 · `auth:init` génère le pont RBAC/MFA même sans les opt-ins → socle inapplicable en une fois

- **Symptôme** : appliquer le socle **complet** d'`auth:init` échoue (FK vers table
  absente).
- **Preuve** : `mvc/models/sql/user_roles.sql` contient
  `FOREIGN KEY (role_id) REFERENCES roles(id)` : `roles` appartient à l'opt-in
  **rbac** (non installé). `auth:status`/`auth:doctor` confirment `forge_mvc_rbac` et
  `forge_mvc_mfa` non importables, mais leurs SQL sont quand même générés.
- **Correctif proposé** : n'émettre `user_roles.sql` / `auth_mfa_*.sql` que si les
  opt-ins correspondants sont présents (ou séparer clairement « socle de base » et
  « ponts opt-in »), pour que le socle de base soit applicable d'un bloc.
- Détail : `retour-006` (F15).

### FORGE-5 · Aucune page de login fournie ni scaffoldée, alors que le cœur redirige vers `/login`

- **Symptôme** : après `auth:init` + routes protégées (défaut de `make:crud`),
  **aucune route protégée n'est atteignable** : le cœur redirige (302) vers `/login`,
  mais **rien ne sert `/login`** → 404. Impossible de se connecter.
- **Preuve** : `core/security/decorators.py:34` et `:72` →
  `Response(302, headers={"Location": "/login"})` ; `core/security/middleware.py:28` →
  `AuthMiddleware(login_url="/login")`. Le cœur fournit le **backend**
  (`core.auth.session.login_user`, `AuthUser`, OK dans `auth:doctor`) mais **ni
  route, ni contrôleur, ni vue** de login, et **aucune commande** ne les scaffolde
  (`auth:*` gère les comptes, pas l'UI ; pas de `make:auth`).
- **Correctif proposé** : scaffolder optionnel `forge make:auth` (contrôleur + route
  `/login` GET/POST câblée sur `login_user` + vue + `/logout`, write-if-new, style de
  l'app). À défaut, **documenter** le câblage attendu et rendre cohérente la
  redirection `/login` codée en dur avec `AuthMiddleware(login_url=...)`.
- Détail : `retour-007`.

---

## P2 : Qualité (le code généré ne passe pas les portes que Forge prône)

> Forge impose le typage strict (ADR-036) et lint ruff à son cœur, mais **son propre
> code généré** ne les passe pas.
> Un projet tenu au même standard doit contourner
> (exclusions pyright, per-file-ignores ruff), voir `pyproject.toml` du projet.

### FORGE-6 · `make:entity` : `_base.py` `from_dict` non strict-clean

- **Preuve** : `<entite>_base.py` : `from_dict(cls, data: dict)` : `data.get("active")`
  vaut `Unknown | None`, passé au paramètre `active: bool` →
  `reportArgumentType`. Latent pour tout champ non optionnel.
- **Correctif** : typer `data: dict[str, object]` (ou `TypedDict`) et coercer/caster
  les valeurs vers le type du champ. Détail : `retour-004` (F10a).

### FORGE-7 · Générateurs : `__init__.py` de ré-export → ruff F401

- **Preuve** : `<entite>/__init__.py` : `from .x import X` sans re-export explicite →
  `F401 imported but unused`.
- **Correctif** : `from .x import X as X` (ou `__all__`). Détail : `retour-004` (F10b).

### FORGE-8 · `make:crud` : modèle généré non typé + import inutile

- **Preuve** : `<entite>_model.py` a des signatures **sans annotations**
  (`def find_..._paginated(q=None, sort=None, ...)`) et `_ALLOWED_SORT.get(sort, ...)`
  reçoit `None`. Le contrôleur généré importe `get_<entities>` **non utilisé**
  (ruff F401).
- **Correctif** : signatures typées (`q: str | None = None`, retours
  `list[dict[str, Any]]` / `int`), gestion du `None` (`sort or ""`), et n'importer que
  les fonctions utilisées. Détail : `retour-005` (F12/F13).

---

## P3 : Cycle de vie / DX (suggestions)

### FORGE-9 · Pas de commande de montée de squelette d'un projet existant

- `forge new` crée, mais rien ne **met à jour** le squelette d'un projet existant
  quand Forge évolue. Piège vérifié : un pin git à version inchangée (`1.0.0rc2`)
  n'est **pas re-fetché** par pip (il faut `--force-reinstall`). Proposition :
  `forge skeleton:upgrade` s'appuyant sur *write-if-new* + un mode `--check`.
  Détail : `retour-002`.

### Résolu : pour information

- `retour-001` (squelette non strict-clean / sans config qualité *by construction*) :
  **largement corrigé** dans le squelette récent (le projet l'a vérifié). Merci.

---

## Note transversale

Le fil rouge P1-P2 : **les générateurs Forge produisent du code que Forge lui-même
ne passe pas** (import cassé, typage, lint) ; **les chemins base de données**
(`db:init` manuel, `db:apply`, socle `auth:init`) ont des angles morts ; et le
**flux d'authentification** est incomplet (le cœur redirige vers `/login` sans que
rien ne fournisse cette page).
Corriger à la source rendrait la chaîne
`make:entity → migration → make:crud → auth → login` **fonctionnelle et conforme
d'emblée**.

## Références (retours détaillés, avec preuves et contournements)

- `retour-003` : `forge_migrations` & provisioning manuel.
- `retour-004` : code généré vs portes qualité (`make:entity`).
- `retour-005` : `make:crud` cassé & non conforme.
- `retour-006` : `db:apply` & socle auth.
- `retour-007` : aucune page de login scaffoldée.
- `retour-002` : commande `skeleton:upgrade`.
- `retour-001` : conformité du squelette (résolu).
