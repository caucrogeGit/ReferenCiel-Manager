#!/usr/bin/env bash
# Montee de niveau FRAMEWORK (ADR-009) : passe TOUS les paquets forge-mvc-*
# (coeur + entites + opt-ins actives + testing) au commit git cible et force la
# reinstallation. Le monorepo Forge doit rester a un sha UNIQUE : melanger les
# shas entre le coeur et les opt-ins est fragile (cf. retour-021 :
# forge-mvc-rbac oublie laissait le provider Jinja F55 a la traine).
#
# forge-mvc-entities (ADR-070) : moteur de donnees extrait du coeur — REQUIS ici
# (make:entity/relation/crud, sync, migrations, db:*). Les opt-ins actives sont
# declares dans optins/registry.py (ADR-061) ; garder la liste ci-dessous alignee.
#
# Usage : tools/forge-upgrade.sh <commit-git-forge>
# Appele par `make forge-upgrade COMMIT=<sha>` (qui enchaine `make check`).
#
# Piege resolu : un pin git a version inchangee (1.0.0rc2) n'est PAS re-fetche
# par pip -> d'ou le --force-reinstall --no-deps.
set -euo pipefail

COMMIT="${1:?usage: tools/forge-upgrade.sh <commit-git-forge>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="git+https://github.com/caucrogeGit/Forge.git"
PIP="$ROOT/.venv/bin/pip"

test -x "$PIP" || { echo "venv introuvable ($PIP) — lance d'abord: make setup" >&2; exit 2; }

# Paquets forge-mvc-* a monter, avec leur sous-dossier dans le monorepo.
# forge-mvc est a la RACINE (pas de subdirectory). L'ordre n'importe pas pour
# pip. Aligner cette liste sur optins/registry.py + requirements*.txt.
FORGE_PKGS=(
  "forge-mvc:"
  "forge-mvc-entities:packages/forge-mvc-entities"
  "forge-mvc-rbac:packages/forge-mvc-rbac"
  "forge-mvc-mfa:packages/forge-mvc-mfa"
  "forge-mvc-admin:packages/forge-mvc-admin"
  "forge-mvc-files:packages/forge-mvc-files"
  "forge-mvc-fixtures:packages/forge-mvc-fixtures"
  "forge-mvc-sessions-db:packages/forge-mvc-sessions-db"
  "forge-mvc-mariadb:packages/forge-mvc-mariadb"
  "forge-mvc-testing:packages/forge-mvc-testing"
)

echo "== 1. bump des pins vers ${COMMIT} =="
sed -i -E "s#(Forge\.git@)[0-9a-f]{7,40}#\1${COMMIT}#g" \
    "$ROOT/requirements.txt" "$ROOT/requirements-dev.txt"
grep -HoE "Forge\.git@[0-9a-f]+" "$ROOT/requirements.txt" "$ROOT/requirements-dev.txt"

echo "== 2. reinstallation forcee au commit cible (tous les paquets forge-mvc-*) =="
specs=()
for entry in "${FORGE_PKGS[@]}"; do
  pkg="${entry%%:*}"
  sub="${entry#*:}"
  if [ -n "$sub" ]; then
    specs+=("${pkg} @ ${REPO}@${COMMIT}#subdirectory=${sub}")
  else
    specs+=("${pkg} @ ${REPO}@${COMMIT}")
  fi
done
"$PIP" install --force-reinstall --no-deps "${specs[@]}"

echo "== 3. verification (tous les paquets doivent pointer le meme sha) =="
"$PIP" freeze | grep -iE "forge-mvc" | sort
echo "OK — enchaine avec 'make check'."
