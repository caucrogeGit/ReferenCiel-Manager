# pyright: strict
"""Détection d'une requête HTMX (fragment attendu, pas la page complète)."""
from __future__ import annotations

from core.http.request import Request


def est_htmx(request: Request) -> bool:
    """Vrai si la requête vient de HTMX (en-tête HX-Request)."""
    return request.header("HX-Request") is not None
