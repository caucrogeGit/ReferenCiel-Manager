#!/usr/bin/env bash
# Montée de niveau SQUELETTE (ADR-009) : liste les écarts sur les fichiers
# appartenant au squelette, entre le projet et une référence neuve (`forge new`).
# Ne modifie RIEN — c'est un outil de revue, pas d'écrasement.
#
# Usage : tools/skeleton-check.sh <chemin-squelette-neuf>
# Appelé par `make skeleton-check REF=<chemin>`.
set -euo pipefail

REF="${1:?usage: tools/skeleton-check.sh <chemin-squelette-neuf>}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/tools/skeleton-manifest.txt"

test -d "$REF" || { echo "référence introuvable : $REF" >&2; exit 2; }
test -f "$MANIFEST" || { echo "manifeste introuvable : $MANIFEST" >&2; exit 2; }

echo "Écarts squelette (projet vs $REF) :"
drift=0
while IFS= read -r path; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    if [[ ! -e "$REF/$path" ]]; then
        echo "  ABSENT-RÉF  $path"; continue
    fi
    if ! diff -rq --exclude=__pycache__ --exclude='*.pyc' "$ROOT/$path" "$REF/$path" >/dev/null 2>&1; then
        echo "  ÉCART       $path"; drift=1
    fi
done < "$MANIFEST"

if [[ $drift -eq 0 ]]; then
    echo "→ Aucun écart : le squelette est à jour."
else
    echo "→ Revoir les écarts ci-dessus, puis overlay manuel selon la procédure"
    echo "  (docs/procedures/montee-squelette-forge.md). Rappel : optins/registry.py"
    echo "  diffère normalement (édité à la main)."
fi
