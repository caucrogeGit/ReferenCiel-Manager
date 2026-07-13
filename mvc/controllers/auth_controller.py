"""Contrôleur d'authentification (généré par forge make:auth).

Flux de connexion sur le socle `users` (forge auth:init) : formulaire, POST de
login (avec défense anti-fixation de session), et logout. Le loader charge un
utilisateur par email pour `authenticate_user` (cœur).
"""
from core.auth import (
    AUTH_EVENT_MFA_CHALLENGE_FAILED,
    AUTH_EVENT_MFA_CHALLENGE_SUCCESS,
    AUTH_EVENT_MFA_REQUIRED,
    safe_log_auth_event,
)
from core.auth.session import (
    authenticate_user,
    is_authenticated,
    login_user,
    logout_user,
)
from core.auth.user import normalize_auth_user
from core.database.db import fetch_one
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController
from core.security.cookies import clear_session_cookie, set_session_cookie
from core.security.session import get_session, get_session_id, regenerate_session
from core.sessions.manager import get_session_store
from forge_mvc_mfa import (
    get_mfa_challenge_user_id,
    has_pending_mfa_challenge,
    start_mfa_challenge,
    verify_mfa_challenge,
)

from mvc.models.mfa_model import (
    get_active_totp_factors,
    get_unused_recovery_codes,
    has_active_totp,
    mark_recovery_used,
    touch_factor_last_used,
)


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
            # MFA (ADR-015) : si le compte a un facteur TOTP actif, exiger un
            # second facteur AVANT de connecter (challenge en session).
            if has_active_totp(user.id):
                start_mfa_challenge(request, user)
                safe_log_auth_event(AUTH_EVENT_MFA_REQUIRED, user_id=user.id)
                response = BaseController.redirect("/login/mfa")
                set_session_cookie(response, session_id)
                return response
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
    def mfa_form(request: Request) -> Response:
        """Formulaire du second facteur (`GET /login/mfa`)."""
        if is_authenticated(request):
            return BaseController.redirect("/")
        if not has_pending_mfa_challenge(request):
            return BaseController.redirect("/login")
        session_id = get_session_id(request)
        session = get_session(session_id) if session_id else None
        response = BaseController.render("app/auth/mfa.html", context={
            "csrf_token": (session or {}).get("csrf_token", ""),
            "erreur": "",
        })
        if session_id:
            set_session_cookie(response, session_id)
        return response

    @staticmethod
    def mfa_verify(request: Request) -> Response:
        """Vérifie le second facteur et connecte (`POST /login/mfa`)."""
        user_id = get_mfa_challenge_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        code = request.form("code", "").strip()
        factors = get_active_totp_factors(user_id)
        recovery = get_unused_recovery_codes(user_id)
        result = verify_mfa_challenge(request, code, factors, recovery)

        if result is None:
            safe_log_auth_event(AUTH_EVENT_MFA_CHALLENGE_FAILED, user_id=user_id)
            session_id = get_session_id(request)
            session = get_session(session_id) if session_id else None
            response = BaseController.render("app/auth/mfa.html", status=422, context={
                "csrf_token": (session or {}).get("csrf_token", ""),
                "erreur": "Code invalide. Réessayez.",
            })
            if session_id:
                set_session_cookie(response, session_id)
            return response

        # Succès : persister l'usage du facteur ou du code de secours consommé.
        if result.factor is not None and result.factor.id is not None:
            touch_factor_last_used(result.factor.id)
        if result.recovery_code is not None:
            mark_recovery_used(result.recovery_code.code_hash)

        row = fetch_one(
            "SELECT id, email, password_hash, is_active FROM users WHERE id = ?", (user_id,)
        )
        if row is None:
            return BaseController.redirect("/login")
        user = normalize_auth_user(row)
        session_id = get_session_id(request)
        login_user(request, user)
        safe_log_auth_event(AUTH_EVENT_MFA_CHALLENGE_SUCCESS, user_id=user_id)
        # Anti-fixation, comme le login simple.
        new_id = regenerate_session(session_id) if session_id else None
        response = BaseController.redirect("/")
        if new_id:
            set_session_cookie(response, new_id)
        return response

    @staticmethod
    def logout(request: Request) -> Response:
        logout_user(request)
        response = BaseController.redirect("/login")
        clear_session_cookie(response)
        return response
