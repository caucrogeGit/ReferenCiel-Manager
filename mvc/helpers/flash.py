# pyright: strict
"""Rendu HTML du message flash courant.

Comble un manque du générateur `forge make:crud` : le contrôleur généré importe
`mvc.helpers.flash.render_flash_html` et le layout l'affiche
(`{{ flash_html | safe }}`), mais Forge ne fournit ni ne génère ce helper
(voir docs/banc-essai/retour-005). Implémentation minimale sur l'API flash du
cœur (`core.security.session`).
"""

from __future__ import annotations

from html import escape
from typing import Any

from core.http.request import Request
from core.security.session import get_flash, get_session_id


def render_flash_html(request: Request) -> str:
    """Retourne le HTML du message flash de la session, ou une chaîne vide."""
    flash: dict[str, Any] | None = get_flash(get_session_id(request))
    if not flash:
        return ""
    message = escape(str(flash.get("message", "")))
    if not message:
        return ""
    level = escape(str(flash.get("level", "success")))
    return f'<div class="flash flash-{level}" role="status">{message}</div>'
