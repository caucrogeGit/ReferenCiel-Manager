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
from optins.registry import register_optins

router = Router()

with router.group("", public=True) as public:
    public.add("GET", "/", HomeController.index, name="home-index")

# Bloc A — socle scolaire. Routes protégées (auth Forge, ticket 07).
register_annee_scolaire_routes(router)

# Routes des opt-ins « route » activés (ADR-061).
register_optins(router)
