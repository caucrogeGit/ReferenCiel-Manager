#!/usr/bin/env bash
# Montée de niveau FRAMEWORK (ADR-009) : passe forge-mvc / forge-mvc-testing au
# commit git cible et force la réinstallation.
#
# Usage : tools/forge-upgrade.sh <commit-git-forge>
# Appelé par `make forge-upgrade COMMIT=<sha>` (qui enchaîne `make check`).
#
# Piège résolu : un pin git à version inchangée (1.0.0rc2) n'est PAS re-fetché
# par pip → d'où le --force-reinstall --no-deps.
set -euo pipefail

COMMIT="${1:?usage: tools/forge-upgrade.sh <commit-git-forge>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="git+https://github.com/caucrogeGit/Forge.git"
PIP="$ROOT/.venv/bin/pip"

test -x "$PIP" || { echo "venv introuvable ($PIP) — lance d'abord: make setup" >&2; exit 2; }

echo "== 1. bump des pins vers ${COMMIT} =="
sed -i -E "s#(Forge\.git@)[0-9a-f]{7,40}#\1${COMMIT}#g" \
    "$ROOT/requirements.txt" "$ROOT/requirements-dev.txt"
grep -HoE "Forge\.git@[0-9a-f]+" "$ROOT/requirements.txt" "$ROOT/requirements-dev.txt"

echo "== 2. réinstallation forcée au commit cible =="
"$PIP" install --force-reinstall --no-deps \
    "forge-mvc @ ${REPO}@${COMMIT}" \
    "forge-mvc-testing @ ${REPO}@${COMMIT}#subdirectory=packages/forge-mvc-testing"

echo "== 3. vérification =="
"$PIP" freeze | grep -iE "forge-mvc(-testing)? @"
echo "OK — enchaîne avec 'make check'."
