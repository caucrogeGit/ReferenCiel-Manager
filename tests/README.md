# Tests — RéférenCiel Manager

Socle de test au standard Forge (voir `docs/adr/006-strategie-de-test.md`).

## Lancer

```bash
python -m pytest            # toute la suite
python -m pytest -m meta    # cohérence projet (doc, ADR, nav)
python -m pytest -m smoke   # fumée (structure Forge, imports) sans base
python -m pytest -m db      # intégration BDD (nécessite un backend installé)
```

## Marqueurs (`pytest.ini`, `--strict-markers`)

- **`meta`** — cohérence documentaire et discipline (pas de métier).
- **`smoke`** — le squelette Forge reste sain, sans backend BDD.
- **`db`** — nécessite un backend BDD installé ; **sauté** tant qu'aucun backend
  n'est présent (arrive avec l'ADR-004 → ticket 07).

## Organisation

- `tests/meta/` — tests méta (ex. toute page doc est dans la nav mkdocs).
- `tests/` — tests de fumée (registre d'opt-ins, `forge project:check`).
- Tests métier par domaine à venir (avec `FakeRequest` de `forge-mvc-testing`
  pour les contrôleurs, SQLite pour les tests `db`).

## Validation avant de livrer

```bash
python -m pytest
pyright              # typage strict, 0 erreur (ADR-007)
ruff check .
forge project:check
mkdocs build --strict
```
