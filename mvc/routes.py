# pyright: strict
from core.http.router import Router
from mvc.controllers.home_controller import HomeController
from mvc.controllers.annee_scolaire_controller import AnneeScolaireController
from optins.registry import register_optins

router = Router()

with router.group("", public=True) as public:
    public.add("GET", "/", HomeController.index, name="home-index")

# Bloc A — socle scolaire. Routes PROTÉGÉES par défaut (auth Forge, ticket 07).
with router.group("/annee_scolaire") as g:
    g.add("GET",  "",                     AnneeScolaireController.index,               name="annee_scolaire-index")
    g.add("GET",  "/new",                 AnneeScolaireController.new,                 name="annee_scolaire-new")
    g.add("POST", "/create",              AnneeScolaireController.create,              name="annee_scolaire-create")
    g.add("GET",  "/show/{id}",           AnneeScolaireController.show,                name="annee_scolaire-show")
    g.add("GET",  "/edit/{id}",           AnneeScolaireController.edit,                name="annee_scolaire-edit")
    g.add("POST", "/update/{id}",         AnneeScolaireController.update,              name="annee_scolaire-update")
    g.add("POST", "/destroy/{id}",        AnneeScolaireController.destroy,             name="annee_scolaire-destroy")
    g.add("POST", "/bulk-delete",         AnneeScolaireController.bulk_delete,         name="annee_scolaire-bulk_delete")
    g.add("POST", "/bulk-delete-confirm", AnneeScolaireController.bulk_delete_confirm, name="annee_scolaire-bulk_delete_confirm")
    g.add("GET",  "/export-csv",          AnneeScolaireController.export_csv,          name="annee_scolaire-export_csv")

# Branche les routes des opt-ins « route » activés (ADR-061).
register_optins(router)
