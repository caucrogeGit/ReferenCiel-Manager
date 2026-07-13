# Retour terrain 001 — Conformité du squelette `forge new` aux standards Forge

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** à remonter.

## Environnement

- `forge-mvc` **1.0.0rc2**, épinglé au commit `49c636ea91abe...` (voir
  `requirements.txt`).
- Profil projet **`standard`**, Python **3.12**, squelette généré par `forge new`.

## Contexte et méthode

RéférenCiel Manager a été monté au **même standard que Forge** : documentation
mkdocs, tests pytest, **typage Pyright strict**, ruff — sur un squelette
fraîchement généré. Ce faisant, plusieurs **écarts entre le squelette livré et les
standards que Forge s'impose** (charte, ADR-036 typage strict, ADR-041 tests) sont
apparus. Ce retour les consigne pour que `forge new` livre un squelette déjà
conforme.

## Constats

### F1 — Défaut (typage) : `optins/registry.py` livre `register_optins(router)` non typé

Le squelette génère :

```python
def register_optins(router) -> None:
    ...
```

Le paramètre `router` n'est **pas typé**. Or Forge impose le typage strict à son
cœur (ADR-036) et génère par ailleurs des contrôleurs **entièrement typés**
(`def index(request: Request) -> Response`). Le fichier `optins/registry.py` est
pourtant **éditable à la main** (ADR-061) et importé par `mvc/routes.py` : sa
signature non typée casse toute vérification stricte des consommateurs.

**Preuve** — sous `# pyright: strict` :

```text
optins/registry.py:32:21 - error: Le type de paramètre « router » est inconnu
optins/registry.py:32:21 - error: L'annotation de type est manquante (« router »)
```

**Correctif appliqué localement** :

```python
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.http.router import Router

def register_optins(router: "Router") -> None:
    ...
```

**Recommandation** — le squelette devrait livrer `register_optins(router: Router)`
(import sous `TYPE_CHECKING`, coût runtime nul), pour qu'un projet démarre
strict-clean. Sévérité : **moyenne** (bloque le strict dès `mvc/routes.py`).

### F2 — Suggestion (config typage) : aucun `[tool.pyright]` livré

Le squelette ne pose **aucun `pyproject.toml`** ni configuration Pyright. Un
projet ne peut donc pas vérifier le typage strict « out of the box », alors même
que le cœur de Forge est strict (ADR-036) et que `pyright` est une dépendance de
dev de Forge.

**Recommandation** — livrer un `pyproject.toml` minimal avec `[tool.pyright]`
(baseline + `include` du code applicatif) et marquer `# pyright: strict` les
fichiers éditables à la main du squelette (`optins/registry.py`, `mvc/routes.py`,
contrôleurs générés). Même un squelette « nu » (ADR-024) gagne à livrer la
**config d'enforcement** du standard, pas seulement à respecter le standard.

### F3 — Suggestion (config lint) : aucun `[tool.ruff]` livré

Pas de configuration ruff dans le squelette : chaque projet la réinvente (et
risque de diverger de Forge). Notre premier essai avec `select` élargi a d'ailleurs
fait remonter 28 « erreurs » sur du code généré **conforme** à la config réelle de
Forge — le problème venait de notre config, pas du squelette.

**Recommandation** — livrer `[tool.ruff]` aligné sur Forge (`select = ["E","F"]`,
`line-length = 120`, `ignore = ["E501","E741","E402"]`), pour une conformité lint
immédiate et cohérente.

### F4 — Suggestion (tests) : aucun socle de test livré

Le squelette ne livre ni `pytest.ini`, ni `tests/`, ni `requirements-dev.txt`
référençant `pytest` / `forge-mvc-testing`. La charte Forge prône pourtant « tester
avant d'élargir » ; `forge-mvc-testing` (ADR-041) fournit `FakeRequest` + un plugin
pytest et **s'installe proprement** épinglé au commit du cœur (vérifié).

**Recommandation** (respectant ADR-024, projet nu) — proposer un générateur
optionnel (`forge test:init` ?) ou un starter minimal : `pytest.ini`
(`--strict-markers`, marqueurs `meta`/`smoke`/`db`), un test smoke
(`forge project:check`), `requirements-dev.txt` avec `forge-mvc-testing`. But :
outiller la discipline de test dès J0 sans imposer de contenu.

### F5 — Suggestion (documentation) : aucun `mkdocs` livré

Le squelette ne livre pas de chaîne de documentation, alors que Forge se documente
avec mkdocs (Material) et que la validation projet mentionne `mkdocs build
--strict`.

**Recommandation** — un générateur optionnel (`forge docs:init` ?) posant
`mkdocs.yml` (Material, fr), `requirements-docs.txt` et un `docs/index.md`, pour
démarrer une doc au standard sans l'imposer.

### F7 — Suggestion (traçabilité) : intégrer les ADR nécessaires au squelette

Le squelette livre déjà `docs/adr/001-adopter-forge.md` (via `forge agents:init`).
Puisqu'il incarne des standards (typage strict, config qualité, tests, doc), il
devrait aussi livrer les **décisions qui les fondent** — soit des **ADR de
squelette** prêts à l'emploi (typage strict, stratégie de test, documentation,
config qualité), soit des **pointeurs explicites vers les ADR de Forge**
correspondants : ADR-024 (projet nu), ADR-036 (typage strict), ADR-041 (test
partagé), ADR-054/060 (backend), ADR-061 (registre opt-ins).

**But** — un projet démarre avec le *pourquoi* à côté du *quoi*, cohérent avec la
discipline ADR de Forge, au lieu que chaque projet réécrive ces ADR à la main.
C'est précisément ce que RéférenCiel Manager a dû faire (ADR-004 à 007) : une
partie de ces décisions est récurrente et gagnerait à être livrée avec le squelette.

### F6 — À vérifier : `forge opt-in:enable` préserve-t-il le typage manuel ?

`optins/registry.py` est géré par `forge opt-in:enable`/`disable` (marqueurs
`# >>>`) **et** éditable à la main. Question : l'activation d'un opt-in
**préserve-t-elle** notre annotation manuelle `router: Router` et le marqueur
`# pyright: strict` (charte : préserver le code utilisateur, principes 4/9) ? À
confirmer par un test lors de la première activation d'opt-in route.

## Points positifs (le standard déjà tenu)

- **Cœur typé strict** (ADR-036) et **contrôleurs générés typés**
  (`index(request: Request) -> Response`).
- **Conception BDD agnostique propre** (ADR-054/060) : squelette sans backend,
  message d'erreur explicite, choix laissé au projet.
- **`forge-mvc-testing`** installable et cohérent (version alignée sur le cœur).
- **`forge project:check`** vert sur le squelette (structure conforme).

## Synthèse

Un squelette **même minimal** (ADR-024) gagnerait à être **strict-clean par
construction** (F1) et à **livrer la configuration d'enforcement** du standard
(F2 pyright, F3 ruff), la partie test/doc restant optionnelle via des générateurs
(F4/F5). Bénéfice : chaque nouveau projet Forge hérite du niveau de qualité de
Forge sans avoir à le reconstruire — ce que RéférenCiel Manager vient de faire à la
main.
