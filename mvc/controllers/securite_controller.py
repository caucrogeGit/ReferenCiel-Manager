# pyright: strict
"""Espace « Sécurité » — MFA en self-service (ADR-014).

L'utilisateur **connecté** active/désactive sa MFA TOTP et gère ses codes de secours.
Enrôlement : `create_totp_factor` (secret chiffré, facteur `pending`) → l'utilisateur
scanne/saisit → `confirm_totp_factor` active le facteur et génère 10 codes de secours
(affichés une seule fois). Route protégée par la seule auth Forge (pas de permission de
domaine : chacun gère SA propre MFA). L'auteur est le compte connecté.

Faute de bibliothèque QR dans l'environnement (et CSP strict), on affiche le **secret**
et l'**URI `otpauth://`** pour saisie/collage manuel dans l'application d'authentification.
"""
from __future__ import annotations

from core.auth.session import get_authenticated_user_id
from core.database.db import fetch_one
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id
from forge_mvc_mfa import (
    MfaSecretInvalidKey,
    MfaSecretKeyMissing,
    MfaSecretKeyPlaceholder,
    confirm_totp_factor,
    create_recovery_codes,
    create_totp_factor,
    decrypt_totp_secret,
    has_recent_mfa_revalidation,
    totp_provisioning_uri,
    validate_mfa_secret_key_config,
    verify_mfa_revalidation,
)

from mvc.models.mfa_model import (
    activate_factor,
    count_unused_recovery,
    desactiver_mfa,
    get_active_totp_factors,
    get_pending_totp_factor,
    get_unused_recovery_codes,
    has_active_totp,
    insert_factor,
    remplacer_recovery_codes,
)

_ISSUER = "ReferenCiel-Manager"


def _account_name(user_id: int) -> str:
    row = fetch_one("SELECT email FROM users WHERE id = ?", (user_id,))
    return str(row["email"]) if row is not None else str(user_id)


def _cle_configuree() -> bool:
    try:
        validate_mfa_secret_key_config()
    except (MfaSecretKeyMissing, MfaSecretKeyPlaceholder, MfaSecretInvalidKey):
        return False
    return True


class SecuriteController:
    @staticmethod
    def index(request: Request) -> Response:
        """État MFA du compte connecté (`GET /securite`)."""
        user_id = get_authenticated_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        actif = has_active_totp(user_id)
        return BaseController.render(
            "app/securite/index.html",
            context={
                "mfa_active": actif,
                "codes_restants": count_unused_recovery(user_id) if actif else 0,
                "cle_configuree": _cle_configuree(),
                "flash": get_flash(get_session_id(request)),
            },
            request=request,
        )

    @staticmethod
    def activer(request: Request) -> Response:
        """Démarre (ou reprend) l'enrôlement TOTP (`GET /securite/activer`)."""
        user_id = get_authenticated_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        if has_active_totp(user_id):
            return BaseController.redirect("/securite")
        if not _cle_configuree():
            return BaseController.redirect_with_flash(
                request, "/securite",
                "La clé de chiffrement MFA (FORGE_MFA_SECRET_KEY) n'est pas configurée.",
                "error",
            )
        account = _account_name(user_id)
        pending = get_pending_totp_factor(user_id)
        if pending is None:
            setup = create_totp_factor(user_id, issuer_name=_ISSUER, account_name=account)
            insert_factor(setup.factor)
            secret, uri = setup.secret, setup.provisioning_uri
        else:
            # Reprise : on reconstruit secret + URI depuis le facteur en attente
            # (secret déchiffré à la volée, jamais stocké en clair).
            secret = decrypt_totp_secret(pending.totp_secret)
            uri = totp_provisioning_uri(secret, account_name=account, issuer_name=_ISSUER)
        return BaseController.render(
            "app/securite/activer.html",
            context={"secret": secret, "uri": uri, "erreur": ""},
            request=request,
        )

    @staticmethod
    def confirmer(request: Request) -> Response:
        """Confirme le code TOTP et active la MFA (`POST /securite/confirmer`)."""
        user_id = get_authenticated_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        code = request.form("code", "").strip()
        pending = get_pending_totp_factor(user_id)
        if pending is None or pending.id is None:
            return BaseController.redirect_with_flash(
                request, "/securite/activer", "Enrôlement expiré, recommencez.", "error"
            )
        if confirm_totp_factor(pending, code) is None:
            return BaseController.redirect_with_flash(
                request, "/securite/activer", "Code incorrect. Réessayez.", "error"
            )
        activate_factor(pending.id)
        setup = create_recovery_codes(user_id)
        remplacer_recovery_codes(user_id, list(setup.code_records))
        return BaseController.render(
            "app/securite/codes.html",
            context={"codes": list(setup.raw_codes), "apres_activation": True},
            request=request,
        )

    @staticmethod
    def regenerer_codes(request: Request) -> Response:
        """Régénère les codes de secours (`POST /securite/codes/regenerer`)."""
        user_id = get_authenticated_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        if not has_active_totp(user_id):
            return BaseController.redirect("/securite")
        setup = create_recovery_codes(user_id)
        remplacer_recovery_codes(user_id, list(setup.code_records))
        return BaseController.render(
            "app/securite/codes.html",
            context={"codes": list(setup.raw_codes), "apres_activation": False},
            request=request,
        )

    @staticmethod
    def desactiver_confirm(request: Request) -> Response:
        """Page de confirmation de désactivation (`GET /securite/desactiver`).

        Action sensible : si la MFA est active et qu'aucune revalidation récente
        n'existe, on exige un code (TOTP ou code de secours) — step-up (ADR-014).
        """
        user_id = get_authenticated_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        if not has_active_totp(user_id):
            return BaseController.redirect("/securite")
        # Step-up : un code n'est demandé que s'il n'y a pas de revalidation récente.
        besoin_code = not has_recent_mfa_revalidation(request, user_id)
        return BaseController.render(
            "app/securite/desactiver.html",
            context={"besoin_code": besoin_code, "erreur": ""},
            request=request,
        )

    @staticmethod
    def desactiver(request: Request) -> Response:
        """Désactive la MFA du compte, après re-preuve du 2e facteur (`POST /securite/desactiver`)."""
        user_id = get_authenticated_user_id(request)
        if user_id is None:
            return BaseController.redirect("/login")
        if has_active_totp(user_id) and not has_recent_mfa_revalidation(request, user_id):
            # Step-up (revalidation de l'opt-in, F42 corrigé) : re-prouver le 2e facteur.
            code = request.form("code", "").strip()
            factors = get_active_totp_factors(user_id)
            recovery = get_unused_recovery_codes(user_id)
            if verify_mfa_revalidation(request, user_id, code, factors, recovery) is None:
                return BaseController.render(
                    "app/securite/desactiver.html",
                    status=422,
                    context={"besoin_code": True, "erreur": "Code invalide. Réessayez."},
                    request=request,
                )
        desactiver_mfa(user_id)
        return BaseController.redirect_with_flash(
            request, "/securite", "MFA désactivée.", "success"
        )
