# pyright: strict
"""Intégrité de session : ferme une session pointant vers un compte disparu.

`AuthMiddleware` (Forge) considère une requête authentifiée dès qu'un identifiant
utilisateur est présent en session, sans vérifier que ce compte existe encore.
Une session peut donc pointer vers un utilisateur supprimé — ou réattribué (ex.
après un rechargement de fixtures qui réassigne les `id`) : l'application
afficherait alors un état « connecté » fantôme (menu profil, pas de redirection)
au lieu de renvoyer au login.

`enforce_session_integrity` détecte ce cas, **ferme** la session (sinon la home
publique reboucle : `/` → `/login` → toujours « authentifié » → `/`) et renvoie
une redirection vers `/login`. Elle est utilisée à deux endroits :

- `SessionIntegrityMiddleware`, placé avant `AuthMiddleware` (`app.py`), couvre
  toutes les routes protégées (`route.public == False`) ;
- `HomeController.index`, car la racine `/` est publique et échappe aux middlewares.
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id, logout_user
from core.database.db import fetch_one
from core.http.request import Request
from core.http.response import Response
from core.security.cookies import clear_session_cookie


def enforce_session_integrity(
    request: Request, login_url: str = "/login"
) -> Response | None:
    """Ferme la session et redirige vers `login_url` si le compte n'existe plus.

    Retourne `None` si la session est absente ou valide (la requête suit son cours).
    """
    user_id = get_authenticated_user_id(request)
    if user_id is None:
        return None  # Pas de session utilisateur.
    if fetch_one("SELECT id FROM users WHERE id = ?", (user_id,)) is not None:
        return None  # Compte présent : session valide.
    # Session orpheline : le compte n'existe plus. On la ferme proprement.
    logout_user(request)
    response = Response(302, headers={"Location": login_url})
    clear_session_cookie(response)
    return response


class SessionIntegrityMiddleware:
    """Renvoie au login si la session pointe vers un utilisateur inexistant."""

    def __init__(self, login_url: str = "/login") -> None:
        self._login_url = login_url

    def check(self, request: Request) -> Response | None:
        return enforce_session_integrity(request, self._login_url)
