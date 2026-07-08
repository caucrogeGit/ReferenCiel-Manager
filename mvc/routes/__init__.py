# pyright: strict
"""Racine de composition du routage applicatif (ADR-068).

Ce module ne fait que **brancher** les routes ; il ne les déclare pas lui-même.
Chaque contrôleur a son fichier `mvc/routes/<controleur>_routes.py` exposant
`register_<controleur>_routes(router)`. `forge make:crud` / `make:auth` génèrent
ces fichiers et affichent la ligne de branchement à ajouter ci-dessous.

Ainsi le routage reste lisible quel que soit le nombre de contrôleurs : un fichier
par contrôleur, cette racine se contentant de les brancher explicitement.
"""
from core.http.router import Router
from mvc.controllers.home_controller import HomeController
from mvc.routes.annee_scolaire_routes import register_annee_scolaire_routes
from mvc.routes.auth_routes import register_auth_routes
from mvc.routes.classe_routes import register_classe_routes
from mvc.routes.niveau_classe_routes import register_niveau_classe_routes
from optins.registry import register_optins

router = Router()

with router.group("", public=True) as public:
    public.add("GET", "/", HomeController.index, name="home-index")

# Routes appliquées pour : annee_scolaire_controller
register_annee_scolaire_routes(router)

# Routes appliquées pour : niveau_classe_controller
register_niveau_classe_routes(router)

# Routes appliquées pour : classe_controller
register_classe_routes(router)

# Routes appliquées pour : auth_controller
register_auth_routes(router)

# Routes des opt-ins activés (ADR-061).
register_optins(router)
