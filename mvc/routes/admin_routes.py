# pyright: strict
"""Back-office admin (forge-mvc-admin) — parcourir les référentiels importés (ticket 11).

On expose **`ReferentielNiveauClasse`** pour consulter les référentiels importés et gérer
leur **statut** (`brouillon`/`publie`/`archive`). Les entités-enfants (pôles, activités,
compétences…) ne sont **pas** exposées : elles sont pilotées par l'import (ADR-010) et ne
se modifient pas à la main. La suppression d'un référentiel est de toute façon bloquée par
les clés étrangères `RESTRICT` (garde-fou naturel).

`forge-mvc-admin` ne propose pas de ressource en lecture seule : le CRUD complet est monté,
mais l'édition utile ici est le **statut**, et le reste est protégé par les FK.

**Contrainte (retour-014, F29)** : `forge-mvc-admin` exige des noms de champ **snake_case**,
alors que `forge-mvc-entities` génère des colonnes **PascalCase** (`Identifiant`, `ImporteLe`…).
MariaDB étant insensible à la casse, les colonnes **mono-mot** (`identifiant`, `version`,
`statut`) passent ; mais **`ImporteLe` (multi-mots) est inutilisable** ici (pas de colonne
`importe_le`) — d'où son absence de la liste. La création via l'admin échoue aussi (les
colonnes NOT NULL `identifiant`/FK ne sont pas dans `form_fields`) : c'est **voulu**, les
référentiels entrent par l'import, pas à la main.

Slug `referentiels` (pluriel) volontaire : évite toute collision avec la route d'upload
`/admin/referentiel/import` (singulier), montée avant celle-ci.
"""
from core.http.router import Router
from forge_mvc_admin import AdminResource, register_admin_routes, registry


def register_admin(router: Router) -> None:
    registry.register(
        AdminResource(
            entity="ReferentielNiveauClasse",
            slug="referentiels",
            label="Référentiel",
            plural_label="Référentiels",
            list_fields=("identifiant", "version", "statut"),
            form_fields=("version", "statut"),
            table="referentiel_niveau_classe",
            order_by="identifiant",
            pk="id",
        )
    )
    register_admin_routes(router)
