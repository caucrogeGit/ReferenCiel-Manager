# Retour terrain 005 : `forge make:crud` génère du code cassé et non conforme aux portes qualité

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** ✅ Résolu dans forge-mvc f38d5159 (2026-07-08), vérifié sur le banc d'essai.

## Environnement

- `forge-mvc` **e3197866**, Python **3.12**, MariaDB.
- `forge make:crud AnneeScolaire` sur une entité valide (`entity:validate` OK).

## Contexte

Chaîne du ticket 07 : après `make:entity` + migration, on génère la couche MVC
avec `forge make:crud`.
Le code produit **ne s'importe même pas**, et échoue les
portes qualité que Forge prône (pyright strict, ruff).

## Constats

### F11 : Défaut bloquant : import d'un helper que Forge ne fournit jamais

Le contrôleur généré contient :

```python
from mvc.helpers.flash import render_flash_html
```

et le layout généré l'affiche (`layouts/app.html` : `{{ flash_html | safe }}`).
Or **`render_flash_html` n'est défini nulle part** : ni dans le cœur, ni généré
par `make:crud` (aucun `mvc/helpers/flash.py` créé), ni de template dans le CLI.
Le générateur code l'import **en dur** (`cli/entities/crud/controller_builder.py:782`)
sans produire le helper.

**Conséquence** : le contrôleur généré **plante à l'import** (`ModuleNotFoundError`) ;
le CRUD n'est pas exécutable en l'état.

**Contournement** : nous avons écrit `mvc/helpers/flash.py` (helper minimal sur
l'API flash du cœur, `core.security.session.get_flash` / `get_session_id`).

**Proposition** : soit `make:crud` **génère** `mvc/helpers/flash.py` (write-if-new),
soit `render_flash_html` est **fourni par le cœur** (`core.mvc` / `core.security`)
et importé de là.
Un générateur ne devrait pas émettre un import qu'il ne satisfait pas.

### F12 : Modèle généré non typé (pyright strict)

`<entite>_model.py` déclare des fonctions **sans annotations**
(`def find_..._paginated(q=None, sort=None, direction="asc", ...)`), et
`_ALLOWED_SORT.get(sort, _DEFAULT_SORT)` reçoit `None` (paramètre non typé) →

```
error: Impossible d'affecter l'argument « Unknown | None » au paramètre « key » de type « str »
```

**Proposition** : générer des signatures typées (`q: str | None = None`, retours
`list[dict[str, Any]]` / `int`) et gérer le `None` (`sort or ""`).

### F13 : Contrôleur généré : import inutile (ruff F401)

Le contrôleur importe `get_annee_scolaires` (liste simple) alors qu'il n'utilise
que `find_..._paginated` → `ruff F401 imported but unused`.

**Proposition** : n'importer que les fonctions réellement utilisées.

## Synthèse

Le scaffolding `make:crud` est précieux (vues index/table/pagination, formulaire),
mais il faut aujourd'hui **le réparer à la main** (helper manquant) et **le typer**
pour qu'il passe les portes que Forge s'impose.
Corriger à la source rendrait
`make:crud` utilisable *out of the box*.
Voir aussi [retour-004](retour-004-code-genere-non-conforme-portes-qualite.md)
(même nature côté `make:entity`).

## Référence

Contournements : `mvc/helpers/flash.py`, `mvc/models/annee_scolaire_model.py`
(typé).
Entité de test : `AnneeScolaire` (ticket 07).
