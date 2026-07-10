"""Contrôleur d'authentification (généré par forge make:auth).

Flux de connexion sur le socle `users` (forge auth:init) : formulaire, POST de
login (avec défense anti-fixation de session), et logout. Le loader charge un
utilisateur par email pour `authenticate_user` (cœur).
"""
from core.auth.session import authenticate_user, is_authenticated, login_user, logout_user
from core.database.db import fetch_one
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController
from core.security.cookies import clear_session_cookie, set_session_cookie
from core.security.session import get_session, get_session_id, regenerate_session
from core.sessions.manager import get_session_store


def load_user_by_email(email: str):
    """Charge un utilisateur du socle `users` par email (loader d'authenticate_user)."""
    return fetch_one(
        "SELECT id, email, password_hash, is_active FROM users WHERE email = ?",
        (email,),
    )


class AuthController(BaseController):

    @staticmethod
    def login_form(request: Request) -> Response:
        # Un utilisateur déjà connecté n'a rien à faire sur le formulaire : on le
        # renvoie à l'accueil (évite la boucle avec la racine qui redirige ici).
        if is_authenticated(request):
            return BaseController.redirect("/")
        # Garantit une session (donc un csrf_token) même pour un visiteur anonyme.
        session_id = get_session_id(request)
        if not session_id or get_session(session_id) is None:
            session_id = get_session_store().create()
        session = get_session(session_id) or {}
        response = BaseController.render("app/auth/login.html", context={
            "csrf_token": session.get("csrf_token", ""),
            "erreur": "",
        })
        set_session_cookie(response, session_id)
        return response

    @staticmethod
    def login(request: Request) -> Response:
        session_id = get_session_id(request)
        session = get_session(session_id) if session_id else None
        if session_id is None or session is None:
            return BaseController.redirect("/login")

        email = request.form("email", "")
        password = request.form("password", "")
        user = authenticate_user(email, password, load_user_by_email)
        if user is not None:
            login_user(request, user)
            # Défense anti-fixation : nouvel identifiant de session + réémission du cookie.
            new_id = regenerate_session(session_id)
            response = BaseController.redirect("/")
            set_session_cookie(response, new_id)
            return response

        response = BaseController.render("app/auth/login.html", context={
            "csrf_token": session.get("csrf_token", ""),
            "erreur": "Identifiant ou mot de passe incorrect.",
        })
        set_session_cookie(response, session_id)
        return response

    @staticmethod
    def logout(request: Request) -> Response:
        logout_user(request)
        response = BaseController.redirect("/login")
        clear_session_cookie(response)
        return response
