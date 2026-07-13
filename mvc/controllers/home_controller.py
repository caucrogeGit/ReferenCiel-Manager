# pyright: strict
from core.auth.session import current_user, get_authenticated_user_id, logout_user
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController
from core.security.cookies import clear_session_cookie

from mvc.models.user_model import charger_utilisateur


class HomeController(BaseController):

    @staticmethod
    def index(request: Request) -> Response:
        # La racine est l'entrée de l'application. Étant publique, elle échappe
        # aux middlewares : on y résout le sujet réel via le loader natif
        # (existence + activité), pas le seul id de session. Sujet valide →
        # accueil ; anonyme → login ; session orpheline (id présent mais compte
        # disparu/inactif) → on la ferme (sinon /login reboucle vers /) puis login.
        if current_user(request, charger_utilisateur) is not None:
            return BaseController.render("home/index.html", request=request)
        response = BaseController.redirect("/login")
        if get_authenticated_user_id(request) is not None:
            logout_user(request)
            clear_session_cookie(response)
        return response

    @staticmethod
    def charte(request: Request) -> Response:
        # Page de référence de la charte graphique (thème « Accessible chaleureux »).
        # Les tokens s'éditent dans static/src/input.css ; cette page montre le résultat.
        return BaseController.render("pages/charte.html", request=request)
