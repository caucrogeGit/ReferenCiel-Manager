# Raccourcis de développement — RéférenCiel Manager.
# Prêt au développement en UNE commande : `make setup`.
# Toutes les commandes passent par le venv du projet (.venv) : pas besoin de l'activer.

VENV := .venv/bin

.PHONY: help setup check type lint test docs docs-serve run

help:
	@echo "make setup       — installe toutes les dépendances (prêt au dev)"
	@echo "make check       — les 5 portes de qualité (type, lint, test, docs, project:check)"
	@echo "make type        — typage strict (pyright)"
	@echo "make lint        — style (ruff, aligné Forge)"
	@echo "make test        — tests (pytest)"
	@echo "make docs        — build documentation (mkdocs --strict)"
	@echo "make docs-serve  — documentation en local (mkdocs serve)"
	@echo "make run         — lance l'application (forge run)"

setup:
	$(VENV)/pip install -r requirements-dev.txt

check: type lint test docs
	$(VENV)/forge project:check

type:
	$(VENV)/pyright

lint:
	$(VENV)/ruff check .

test:
	$(VENV)/python -m pytest

docs:
	$(VENV)/mkdocs build --strict

docs-serve:
	$(VENV)/mkdocs serve

run:
	$(VENV)/forge run
