# Procédure — Monter le squelette Forge en place

Procédure **rejouable** pour récupérer les apports d'une nouvelle version de Forge
sans « tout reprendre » et sans casser le projet. Cadre : [ADR-010](../adr/010-montee-squelette-forge-en-place.md).

> Principe : **on ne déplace aucun dossier**. Le `.git` (historique + `origin`) et
> le `.venv` restent en place ; on apporte les fichiers neufs *dans* le projet.

## Deux niveaux à distinguer

| Niveau | Ce qui change | Action |
|---|---|---|
| **Framework** | paquet `forge-mvc` (pin git) | bump du pin + réinstallation forcée |
| **Squelette** | fichiers émis par `forge new` | rafraîchir les fichiers *squelette* selon le manifeste |

Le niveau *framework* est le cas fréquent et le plus simple ; le niveau *squelette*
est plus rare et demande le manifeste ci-dessous.

## Manifeste de propriété

Qui possède quoi — ce qui rend l'opération sûre.

### Squelette (écrasable depuis un `forge new` neuf)

`app.py`, `config.py`, `mvc/`, `optins/` (voir note `registry.py`), `schemas/`,
`static/` (parts squelette), `.vscode/`, `.github/`, `package.json`,
`package-lock.json`, `.npmrc`, `.nvmrc`, `.editorconfig`, `CHANGELOG.md`,
`docs/adr/000-template.md`, `docs/adr/001-adopter-forge.md`,
`tests/test_smoke_001.py`, `tests/conftest.py`.

### Projet (jamais touché)

`docs/` métier (`cadrage/`, `roadmap/`, `tickets/`, `specs/`, `banc-essai/`,
`procedures/`, `index.md`), `docs/adr/002-*.md` … et suivants, `sources/`,
`tests/meta/`, `tests/test_smoke.py`, `tests/README.md`, `conftest.py` (racine),
`Makefile`, `requirements-docs.txt`, `pytest.ini`, `.gitignore`, `env/`,
`storage/`, `cert.pem`, `key.pem`.

### Pin (bump du commit git)

`requirements.txt` (pin `forge-mvc`), `requirements-dev.txt` (pin
`forge-mvc-testing`, **même commit**).

### Fusion idempotente (ni écrasé, ni figé)

- `CLAUDE.md` / `AGENTS.md` : **briefing Forge neuf** + **notre bloc prioritaire**
  ré-injecté entre les marqueurs `<!-- PRIORITÉ REFERENCIEL-MANAGER -->` … `<!-- FIN … -->`.
- `pyproject.toml` : garder notre `[tool.pyright] include` (`mvc`, `optins`,
  `conftest.py`, `tests`) ; ruff déjà aligné.
- `mkdocs.yml` : notre nav curée + entrées ADR `index.md` et `000-template.md`.
- `docs/adr/index.md` : garder notre **journal** (002…), le gabarit `000` reste la trame.

> Note `optins/registry.py` : fichier squelette **mais** éditable à la main
> (ADR-061). Sa signature est déjà typée strict. La valeur `BACKEND` est posée par
> l'installation de l'opt-in, pas à la main.

## Procédure pas à pas

1. **Générer un squelette neuf à côté** à la version cible :
   `forge new` dans `../Test` (ou un dossier jetable). Noter le **commit
   `forge-mvc`** visé (dans son `requirements.txt`).
2. **Overlay des fichiers *squelette*** (liste ci-dessus) depuis `../Test` vers le
   projet. Ne jamais toucher aux fichiers *projet*.
3. **Bump du pin** au commit cible dans `requirements.txt` **et**
   `requirements-dev.txt` (`forge-mvc-testing`, même commit).
4. **Réinstaller au commit neuf** (le pin git à version identique n'est pas
   re-fetché par pip) :
   ```bash
   .venv/bin/pip install --force-reinstall --no-deps \
     "forge-mvc @ git+https://github.com/caucrogeGit/Forge.git@<COMMIT>" \
     "forge-mvc-testing @ git+https://github.com/caucrogeGit/Forge.git@<COMMIT>#subdirectory=packages/forge-mvc-testing"
   ```
   Puis `make setup` pour le reste.
5. **Fusions idempotentes** (section ci-dessus) : ré-injecter le bloc prioritaire,
   vérifier `pyproject`/`mkdocs`/journal ADR.
6. **Valider** : `make check` — les 5 portes doivent être vertes (pyright, ruff,
   pytest, mkdocs `--strict`, `forge project:check`).
7. **Commit + push** : commit descriptif, `git push origin main` en **fast-forward**
   (pas de force-push).
8. **Nettoyer** : le squelette `../Test` peut être supprimé.

## Outillage local (disponible)

Le manifeste ci-dessus est **exécutable** (`tools/skeleton-manifest.txt`), et deux
cibles Make couvrent les deux niveaux :

- **`make forge-upgrade COMMIT=<sha>`** — niveau *framework* : bump du pin dans
  `requirements.txt` + `requirements-dev.txt`, réinstallation forcée de
  `forge-mvc`/`forge-mvc-testing` au commit, puis `make check`. (script
  `tools/forge-upgrade.sh`)
- **`make skeleton-check REF=<squelette-neuf>`** — niveau *squelette* : liste les
  écarts sur les fichiers du manifeste vs une référence `forge new` neuve (revue,
  **aucun écrasement**). (script `tools/skeleton-check.sh`)

Un test méta (`tests/meta/test_skeleton_manifest.py`) vérifie que le manifeste ne
référence que des chemins réels. L'étape *overlay* (2) et les *fusions
idempotentes* (5) restent manuelles — c'est là que le jugement est nécessaire.

Le *bon* endroit à terme est le framework : voir
[retour-002](../banc-essai/retour-002-commande-skeleton-upgrade.md)
(`forge skeleton:upgrade`).
