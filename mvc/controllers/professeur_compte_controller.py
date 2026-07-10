# pyright: strict
"""Comptes professeurs (socle admin) : créer un compte et le lier à une fiche Professeur.

Écran réservé à l'admin (préfixe `/professeur` gardé par `socle.gerer`). Symétrique
de la gestion des comptes élèves. POST protégé par CSRF (défaut Forge).
"""
from __future__ import annotations

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id

from mvc.models.professeur_compte_model import (
    creer_compte_professeur,
    email_est_valide,
    email_existe,
    list_professeurs_avec_compte,
    professeurs_sans_compte,
)

_PASSWORD_MIN = 8


class ProfesseurCompteController:
    @staticmethod
    def index(request: Request) -> Response:
        """Liste des professeurs + formulaire (`GET /professeur/comptes`)."""
        return BaseController.render(
            "professeur_compte/index.html",
            context={
                "professeurs": list_professeurs_avec_compte(),
                "sans_compte": professeurs_sans_compte(),
                "erreurs": [],
                "email": "",
                "flash": get_flash(get_session_id(request)),
            },
            request=request,
        )

    @staticmethod
    def create(request: Request) -> Response:
        """Crée un compte et le lie à un professeur (`POST /professeur/comptes/create`)."""
        pro_id_raw = request.form("professeur_id", "")
        email = request.form("email", "").strip()
        password = request.form("password", "")

        erreurs: list[str] = []
        if not pro_id_raw.isdigit():
            erreurs.append("Sélectionnez un professeur.")
        if not email_est_valide(email):
            erreurs.append("Email invalide (format attendu : utilisateur@domaine.com).")
        elif email_existe(email):
            erreurs.append("Cet email est déjà utilisé par un compte.")
        if len(password) < _PASSWORD_MIN:
            erreurs.append(f"Le mot de passe doit faire au moins {_PASSWORD_MIN} caractères.")

        if erreurs:
            return BaseController.render(
                "professeur_compte/index.html",
                status=422,
                context={
                    "professeurs": list_professeurs_avec_compte(),
                    "sans_compte": professeurs_sans_compte(),
                    "erreurs": erreurs,
                    "email": email,
                },
                request=request,
            )

        creer_compte_professeur(int(pro_id_raw), email, password)
        return BaseController.redirect_with_flash(
            request, "/professeur/comptes", "Compte professeur créé et lié.", "success"
        )
