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
from mvc.routes.admin_routes import register_admin
from mvc.routes.activite_routes import register_activite_routes
from mvc.routes.affectation_parcours_routes import register_affectation_parcours_routes
from mvc.routes.affectation_professeur_classe_routes import (
    register_affectation_professeur_classe_routes,
)
from mvc.routes.annee_scolaire_routes import register_annee_scolaire_routes
from mvc.routes.auth_routes import register_auth_routes
from mvc.routes.classe_routes import register_classe_routes
from mvc.routes.eleve_compte_routes import register_eleve_compte_routes
from mvc.routes.eleve_routes import register_eleve_routes
from mvc.routes.evaluation_activite_routes import register_evaluation_activite_routes
from mvc.routes.evaluation_critere_routes import register_evaluation_critere_routes
from mvc.routes.groupe_routes import register_groupe_routes
from mvc.routes.inscription_eleve_routes import register_inscription_eleve_routes
from mvc.routes.mon_parcours_routes import register_mon_parcours_routes
from mvc.routes.niveau_classe_routes import register_niveau_classe_routes
from mvc.routes.palier_routes import register_palier_routes
from mvc.routes.parcours_routes import register_parcours_routes
from mvc.routes.checklist_routes import register_checklist_routes
from mvc.routes.choix_qcm_routes import register_choix_qcm_routes
from mvc.routes.depot_eleve_routes import register_depot_eleve_routes
from mvc.routes.item_checklist_routes import register_item_checklist_routes
from mvc.routes.item_coche_routes import register_item_coche_routes
from mvc.routes.professeur_routes import register_professeur_routes
from mvc.routes.progression_eleve_routes import register_progression_eleve_routes
from mvc.routes.progression_palier_routes import register_progression_palier_routes
from mvc.routes.qcm_routes import register_qcm_routes
from mvc.routes.question_qcm_routes import register_question_qcm_routes
from mvc.routes.section_checklist_routes import register_section_checklist_routes
from mvc.routes.reponse_qcm_routes import register_reponse_qcm_routes
from mvc.routes.tentative_qcm_routes import register_tentative_qcm_routes
from mvc.routes.referentiel_import_routes import register_referentiel_import_routes
from mvc.routes.scenario_routes import register_scenario_routes
from mvc.routes.starter_welcome_routes import register_starter_welcome_routes
from mvc.routes.suivi_routes import register_suivi_routes
from mvc.routes.version_parcours_routes import register_version_parcours_routes
from mvc.routes.version_starter_routes import register_version_starter_routes
from mvc.services.rbac import guard_prefix, register_rbac_provider
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

# Comptes élèves (socle admin) : créer + lier un compte à une fiche Eleve.
# Monté avant le CRUD /eleve pour que /eleve/comptes matche en priorité.
register_eleve_compte_routes(router)

# Routes appliquées pour : eleve_controller
register_eleve_routes(router)

# Routes appliquées pour : professeur_controller
register_professeur_routes(router)

# Routes appliquées pour : inscription_eleve_controller
register_inscription_eleve_routes(router)

# Routes appliquées pour : scenario_controller (chaîne Scenario, ticket 13)
register_scenario_routes(router)

# Routes StarterWelcome + VersionStarter (phase ⑦, ticket 14)
register_starter_welcome_routes(router)
register_version_starter_routes(router)

# Routes Parcours + VersionParcours + Palier (phase ⑧, tickets 15-16)
register_parcours_routes(router)
register_version_parcours_routes(router)
register_palier_routes(router)

# Bloc B — AffectationParcours (ticket 17)
register_affectation_parcours_routes(router)

# Bloc B — ProgressionEleve + ProgressionPalier (ticket 18)
register_progression_eleve_routes(router)
register_progression_palier_routes(router)

# Bloc B — Définition QCM : QCM + QuestionQCM + ChoixQCM (ticket 19, sous-lot 1)
register_qcm_routes(router)
register_question_qcm_routes(router)
register_choix_qcm_routes(router)

# Bloc B — Exécution QCM : TentativeQCM + ReponseQCM (ticket 19, sous-lot 2)
register_tentative_qcm_routes(router)
register_reponse_qcm_routes(router)

# Bloc B — Checklist : définition (Checklist/Section/Item) + exécution (ItemCoche) (ticket 19, sous-lot 3)
register_checklist_routes(router)
register_section_checklist_routes(router)
register_item_checklist_routes(router)
register_item_coche_routes(router)

# Bloc B — Activité + DépôtEleve (ticket 19, sous-lot 4 — fin ticket 19)
register_activite_routes(router)
register_depot_eleve_routes(router)

# Bloc B — Évaluation par critères (ticket 21)
register_evaluation_activite_routes(router)
register_evaluation_critere_routes(router)

# Bloc B — Suivi professeur (ticket 20) : tableau de bord lecture seule
register_suivi_routes(router)

# Espace élève — « Mon parcours » (lecture seule, rôle eleve)
register_mon_parcours_routes(router)

# Routes appliquées pour : affectation_professeur_classe_controller
register_affectation_professeur_classe_routes(router)

# Routes appliquées pour : groupe_controller
register_groupe_routes(router)

# Import de référentiel par upload admin (ticket 11, ADR-008)
register_referentiel_import_routes(router)

# Back-office admin (forge-mvc-admin) : parcourir les référentiels importés.
# Monté après l'import pour que /admin/referentiel/import matche avant /admin/{slug}/{id}.
register_admin(router)

# Routes appliquées pour : auth_controller
register_auth_routes(router)

# Routes des opt-ins activés (ADR-061).
register_optins(router)

# RBAC applicatif (couche fine maison) : injecte `can(...)` dans tous les rendus
# Jinja. Les rôles sont lus en base depuis la session moderne, le resolveur natif
# de l'opt-in lisant une session dépréciée (voir docs/banc-essai).
register_rbac_provider()

# Gardes de route par domaine (permission du contrat mvc/security/rbac.json).
# Masquer le menu n'est que du confort ; ces gardes protègent l'URL tapée à la
# main. Une passe post-enregistrement (guard_prefix) enveloppe chaque handler du
# préfixe, ce qui couvre aussi les routes futures du même domaine.
#
# Socle scolaire + référentiel + back-office admin : réservés à `socle.gerer`
# (l'admin). C'est la vraie frontière de privilège : un professeur ne doit pas
# gérer le socle même en tapant l'URL.
for _prefix in (
    "/annee_scolaire", "/niveau_classe", "/classe", "/eleve", "/professeur",
    "/inscription_eleve", "/affectation_professeur_classe", "/groupe", "/admin",
):
    guard_prefix(router, _prefix, "socle.gerer")

# Conception pédagogique : `conception.gerer` (admin + professeur).
for _prefix in (
    "/scenario", "/starter_welcome", "/version_starter",
    "/parcours", "/version_parcours", "/palier",
):
    guard_prefix(router, _prefix, "conception.gerer")

# Exécution (travail, évaluation) : `execution.gerer` (admin + professeur).
for _prefix in (
    "/affectation_parcours", "/progression_eleve", "/progression_palier",
    "/qcm", "/question_qcm", "/choix_qcm", "/tentative_qcm", "/reponse_qcm",
    "/checklist", "/section_checklist", "/item_checklist", "/item_coche",
    "/activite", "/depot_eleve", "/evaluation_activite", "/evaluation_critere",
):
    guard_prefix(router, _prefix, "execution.gerer")

# Suivi (lecture seule) : `suivi.voir` (admin + professeur).
guard_prefix(router, "/suivi", "suivi.voir")

# Espace élève : `espace_eleve.voir` (rôle eleve). Données filtrées par compte.
guard_prefix(router, "/mon-parcours", "espace_eleve.voir")
