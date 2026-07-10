# pyright: strict
"""Couche RBAC applicative (couche fine maison).

Pont entre l'auth *moderne* de Forge (`core.auth.session`, qui ne stocke que
`user.id` en session) et l'opt-in `forge-mvc-rbac` (dont le resolveur natif lit
une session *dépréciée* — voir docs/banc-essai). Plutôt que de dépendre de ce
resolveur incompatible, cette couche fournit elle-même le maillon manquant : les
**rôles de l'utilisateur courant, lus en base**, puis délègue la décision au
**contrat** `mvc/security/rbac.json` via les fonctions du framework
(`load_rbac_contract`, `has_contract_permission`).

Trois usages :
- `can(request, permission)` : décision booléenne (nav, vues).
- garde de route `guarded(permission, handler)` : enveloppe un handler et
  renvoie 403 si la permission manque (protège l'URL, pas seulement le menu).
- `rbac_context` : fournisseur de contexte Jinja, injecte `can(...)` dans tous
  les rendus (enregistré une fois via `register_rbac_provider`).
"""
from typing import Any

from core.auth.session import get_authenticated_user_id
from core.database.db import fetch_all
from core.http.request import Request
from core.http.response import Response
from core.http.router import Handler, Router
from core.mvc.controller import register_jinja_context_provider
from forge_mvc_rbac.contract import (
    RbacContractResult,
    has_contract_permission,
    load_rbac_contract,
)

# Contrat chargé et validé une seule fois (lecture seule ; l'app redémarre pour
# recharger). Évite de relire/valider mvc/security/rbac.json à chaque rendu.
_contract_cache: RbacContractResult | None = None


def _contract() -> RbacContractResult:
    global _contract_cache
    if _contract_cache is None:
        _contract_cache = load_rbac_contract(".")
    return _contract_cache


def current_user_roles(request: Request) -> list[str]:
    """Rôles (slugs) de l'utilisateur courant, lus en base.

    Résout `user.id` depuis la session moderne, puis joint `user_roles`/`roles`.
    Renvoie `[]` pour un visiteur anonyme, ou si les tables RBAC sont absentes
    (tolérant : la couche ne casse pas une app sans base ni schéma RBAC).
    """
    user_id = get_authenticated_user_id(request)
    if user_id is None:
        return []
    try:
        rows = fetch_all(
            "SELECT r.slug FROM user_roles ur "
            "JOIN roles r ON r.id = ur.role_id "
            "WHERE ur.user_id = ?",
            (user_id,),
        )
    except Exception:
        return []
    return [str(row["slug"]) for row in rows]


def can(request: Request, permission: str) -> bool:
    """True si l'utilisateur courant possède `permission` selon le contrat."""
    return has_contract_permission(_contract(), current_user_roles(request), permission)


def require_permission(request: Request, permission: str) -> Response | None:
    """Garde de contrôleur : None si autorisé, `Response(403)` sinon.

    Usage :
        denied = require_permission(request, "socle.gerer")
        if denied is not None:
            return denied
    """
    if can(request, permission):
        return None
    return Response(403, body=f"Permission requise : {permission}".encode())


def guarded(permission: str, handler: Handler) -> Handler:
    """Enveloppe un handler de route d'une exigence de permission.

    Protège la **route** (l'URL tapée à la main), complément indispensable au
    masquage du menu qui n'est que du confort. Usage dans un fichier de routes :
        g.add("GET", "", guarded("socle.gerer", XController.index), name=...)
    """
    def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
        denied = require_permission(request, permission)
        if denied is not None:
            return denied
        return handler(request, *args, **kwargs)
    return wrapper


def guard_prefix(router: Router, prefix: str, permission: str) -> None:
    """Applique une garde de permission à toutes les routes sous `prefix`.

    Passe unique après enregistrement : enveloppe le handler de chaque route
    dont le chemin est `prefix` ou commence par `prefix/`. Protège la route
    (URL tapée à la main), sans éditer les fichiers de routes générés, et couvre
    d'office les routes futures du même préfixe.
    """
    for entry in router.iter_routes():
        if entry.pattern == prefix or entry.pattern.startswith(prefix + "/"):
            entry.handler = guarded(permission, entry.handler)


def rbac_context(request: Request) -> dict[str, Any]:
    """Fournisseur de contexte Jinja : injecte `can(...)` dans tous les rendus.

    Les rôles sont résolus une fois par rendu ; `can(perm)` côté template n'est
    plus qu'une vérification contractuelle (pas de requête par appel).
    """
    roles = current_user_roles(request)
    contract = _contract()

    def can_in_template(permission: str) -> bool:
        return has_contract_permission(contract, roles, permission)

    return {"can": can_in_template, "current_roles": roles}


def register_rbac_provider() -> None:
    """Enregistre `rbac_context` comme fournisseur de contexte Jinja (une fois)."""
    register_jinja_context_provider(rbac_context)
