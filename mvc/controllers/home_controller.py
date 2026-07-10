# pyright: strict
from core.auth.session import is_authenticated
from core.http.request import Request
from core.http.response import Response
from core.mvc.controller.base_controller import BaseController


class HomeController(BaseController):

    @staticmethod
    def index(request: Request) -> Response:
        # La racine est l'entrée de l'application : un visiteur anonyme est
        # envoyé sur la page de connexion (la navigation par rôle n'apparaît
        # qu'une fois authentifié). Un utilisateur connecté voit l'accueil.
        if not is_authenticated(request):
            return BaseController.redirect("/login")
        return BaseController.render("home/index.html", request=request)

    @staticmethod
    def charte(request: Request) -> Response:
        # Page de référence de la charte graphique (thème « Accessible chaleureux »).
        # Les tokens s'éditent dans static/src/input.css ; cette page montre le résultat.
        return BaseController.render("pages/charte.html", request=request)
