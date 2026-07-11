# pyright: strict
"""Comptes élèves (socle admin) : créer un compte et le lier à une fiche Eleve.

Écran réservé à l'admin (préfixe `/eleve` gardé par `socle.gerer`). Le formulaire
crée en une action un compte `users`, lui pose le rôle `eleve` et le rattache à un
élève sans compte. Validation avant écriture ; POST protégé par CSRF (défaut Forge).
"""
from __future__ import annotations

from core.http.request import Request
from core.http.response import Response
from core.mvc.controller import BaseController
from core.security.session import get_flash, get_session_id

from mvc.models.eleve_compte_model import (
    creer_compte_eleve,
    eleves_sans_compte,
    email_est_valide,
    email_existe,
    list_eleves_avec_compte,
)
from mvc.services.password_policy import valider_mot_de_passe


class EleveCompteController:
    @staticmethod
    def index(request: Request) -> Response:
        """Liste des élèves avec l'état de leur compte + formulaire (`GET /eleve/comptes`)."""
        return BaseController.render(
            "app/eleve_compte/index.html",
            context={
                "eleves": list_eleves_avec_compte(),
                "sans_compte": eleves_sans_compte(),
                "erreurs": [],
                "email": "",
                "flash": get_flash(get_session_id(request)),
            },
            request=request,
        )

    @staticmethod
    def create(request: Request) -> Response:
        """Crée un compte et le lie à un élève (`POST /eleve/comptes/create`)."""
        eleve_id_raw = request.form("eleve_id", "")
        email = request.form("email", "").strip()
        password = request.form("password", "")

        erreurs: list[str] = []
        if not eleve_id_raw.isdigit():
            erreurs.append("Sélectionnez un élève.")
        if not email_est_valide(email):
            erreurs.append("Email invalide (format attendu : utilisateur@domaine.com).")
        elif email_existe(email):
            erreurs.append("Cet email est déjà utilisé par un compte.")
        message_mdp = valider_mot_de_passe(password)
        if message_mdp is not None:
            erreurs.append(message_mdp)

        if erreurs:
            return BaseController.render(
                "app/eleve_compte/index.html",
                status=422,
                context={
                    "eleves": list_eleves_avec_compte(),
                    "sans_compte": eleves_sans_compte(),
                    "erreurs": erreurs,
                    "email": email,
                },
                request=request,
            )

        creer_compte_eleve(int(eleve_id_raw), email, password)
        return BaseController.redirect_with_flash(
            request, "/eleve/comptes", "Compte élève créé et lié.", "success"
        )
