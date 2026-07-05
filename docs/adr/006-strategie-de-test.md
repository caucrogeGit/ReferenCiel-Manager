# ADR-006 — Stratégie et qualité de test (alignée Forge)

## Statut

Accepté (2026-07-05).

> Applique au projet le standard de test de Forge (ADR-005 : qualité niveau Forge).

## Date

2026-07-05

## Contexte

Le porteur exige la **même qualité de test** que le framework Forge. Forge teste
avec **pytest** : `--strict-markers`, une taxonomie de marqueurs (`meta`, `smoke`,
`db`), une infrastructure partagée (`forge-mvc-testing` : `FakeRequest` + plugin
pytest, ADR-041), et des tests d'intégration `db` qui exigent un backend réel.

RéférenCiel Manager est une **application** (pas le monorepo Forge) et n'a **pas
encore de backend BDD** (ADR-004 proposé) ni d'entité. Il faut donc un socle de
test opérationnel **dès maintenant**, extensible sans réécriture quand la base
arrivera.

## Décision

### Outillage (`requirements-dev.txt`)

`pytest`, `ruff`, `pyright`, `pip-audit`, `bandit`, et **`forge-mvc-testing`**
épinglé au **même commit git que `forge-mvc`** (compatibilité de version). C'est
de l'outillage de **développement** : jamais importé à l'exécution de l'app (le
runtime reste 100% Forge, ADR-003).

### Configuration (`pytest.ini`)

- `testpaths = tests`, `addopts = --strict-markers`.
- Marqueurs :
  - **`meta`** — cohérence projet (doc, ADR, nav mkdocs) ; pas un test métier.
  - **`smoke`** — fumée (structure Forge conforme, imports) sans backend BDD.
  - **`db`** — intégration nécessitant un backend BDD installé ; **sauté** tant
    qu'aucun backend n'est présent (repris dès l'ADR-004 appliqué).

### Organisation (`tests/`)

- `tests/meta/` — tests méta (ex. « toute page doc est dans la nav mkdocs »,
  numérotation ADR contiguë). Ils **dogfoodent la discipline** documentaire.
- `tests/` (racine) — tests de fumée (registre d'opt-ins, `forge project:check`).
- `tests/**/` par domaine métier au fil des tickets (avec `FakeRequest` pour les
  contrôleurs, une vraie MariaDB pour les tests `db`).

### Politique

- **`mkdocs build --strict`**, **`python -m pytest`**, **`ruff check .`**,
  **`forge project:check`** font partie de la validation **avant de livrer**.
- Un nouveau comportement métier **arrive avec ses tests** (charte Forge : tester
  avant d'élargir).
- Les tests `db` valident la persistance réelle (MariaDB) dès qu'elle existe ; ils
  exigent un serveur (sautés en local sans base, requis en CI via
  `FORGE_REQUIRE_DB=1`, modèle Forge) et ne sont pas simulés.

## Conséquences

- Suite verte dès le squelette (méta + smoke), sans base : la qualité est
  vérifiable immédiatement et le restera à chaque ticket.
- Le passage à la base (ticket 07) ajoute des tests `db` sans rien réécrire.
- La barre de test est explicite et exécutable (CI-ready).

## Alternatives écartées

- **Tester plus tard** (quand il y aura du métier) : rejeté — on perd le filet
  méta/smoke et la discipline dès le départ.
- **Réinventer un harnais maison** au lieu de `forge-mvc-testing` : rejeté —
  contraire au « 100% Forge » et au rôle de banc d'essai (ADR-003/005).

## Suite

- Épingler/installer `forge-mvc-testing` (dev) ; toute friction d'installation est
  **révélée** (rôle de banc d'essai) plutôt que contournée.
- Ajouter les tests `db` à l'arrivée du backend MariaDB (ADR-004 → ticket 07).
