# pyright: strict
"""Routes de l'import de référentiel par upload admin (ticket 11, ADR-008).

Montées sous l'espace `/admin` (non public → session requise). Le rôle `admin`
(RBAC, opt-in `rbac`) est différé : pour l'instant « admin » = utilisateur authentifié.
"""
from core.http.router import Router
from mvc.controllers.referentiel_import_controller import ReferentielImportController


def register_referentiel_import_routes(router: Router) -> None:
    with router.group("/admin/referentiel") as g:
        g.add("GET", "/import", ReferentielImportController.form, name="referentiel_import-form")
        g.add("POST", "/import", ReferentielImportController.upload, name="referentiel_import-upload")
