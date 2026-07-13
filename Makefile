# Raccourcis de développement — RéférenCiel Manager.
# Prêt au développement en UNE commande : `make setup`.
# Toutes les commandes passent par le venv du projet (.venv) : pas besoin de l'activer.

VENV := .venv/bin

.PHONY: help setup check type lint test docs docs-serve run stop restart forge-upgrade skeleton-check

help:
	@echo "make setup                      — installe toutes les dépendances (prêt au dev)"
	@echo "make check                      — les 5 portes de qualité (type, lint, test, docs, project:check)"
	@echo "make type                       — typage strict (pyright)"
	@echo "make lint                       — style (ruff, aligné Forge)"
	@echo "make test                       — tests (pytest)"
	@echo "make docs                       — build documentation (mkdocs --strict)"
	@echo "make docs-serve                 — documentation en local (mkdocs serve)"
	@echo "make run                        — lance l'application (forge run)"
	@echo "make stop                       — arrête les 'forge run' de ce projet (libère le port)"
	@echo "make restart                    — arrête puis relance proprement (évite le port occupé)"
	@echo "make forge-upgrade COMMIT=<sha> — monte forge-mvc au commit cible + check (ADR-009)"
	@echo "make skeleton-check REF=<dir>   — liste les écarts squelette vs un forge new neuf (ADR-009)"

setup:
	$(VENV)/pip install -r requirements-dev.txt

check: type lint test docs
	$(VENV)/forge project:check
	$(VENV)/forge entity:validate

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

# Arrêt propre : tue les 'forge run' de CE projet (évite les orphelins qui
# gardent le port occupé). Restreint à $(CURDIR) pour ne pas toucher un autre
# projet Forge lancé en parallèle.
stop:
	@pkill -f "$(CURDIR).*forge run" && echo "forge run arrêté." || echo "aucun forge run à arrêter."

# Redémarrage propre : arrête l'ancien serveur, laisse le port se libérer, relance.
restart: stop
	@sleep 1
	$(VENV)/forge run

# --- Montée de squelette Forge (ADR-009) ---

forge-upgrade:
	@test -n "$(COMMIT)" || { echo "usage: make forge-upgrade COMMIT=<commit-git-forge>"; exit 2; }
	bash tools/forge-upgrade.sh $(COMMIT)
	$(MAKE) check

skeleton-check:
	@test -n "$(REF)" || { echo "usage: make skeleton-check REF=<chemin-squelette-neuf>"; exit 2; }
	bash tools/skeleton-check.sh $(REF)
