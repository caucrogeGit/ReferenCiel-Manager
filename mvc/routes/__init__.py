# pyright: strict
"""Racine de composition du routage applicatif (ADR-068).

Ce module ne fait que **brancher** les routes ; il ne les déclare pas lui-même.
Chaque contrôleur a son fichier `mvc/routes/<controleur>_routes.py` exposant
`register_<controleur>_routes(router)`. `forge make:crud` / `make:auth` génèrent
ces fichiers et affichent la ligne de branchement à ajouter ci-dessous.

Ainsi le routage reste lisible quel que soit le nombre de contrôleurs : un fichier
par contrôleur, cette racine se contentant de les brancher explicitement.
"""
from typing import Any

from core.http.request import Request
from core.http.router import Router
from core.mvc.controller.registry import register_jinja_context_provider
from mvc.controllers.home_controller import HomeController
from mvc.routes.admin_routes import register_admin
from mvc.routes.activite_routes import register_activite_routes
from mvc.routes.bilan_eleve_routes import register_bilan_eleve_routes
from mvc.routes.annee_scolaire_routes import register_annee_scolaire_routes
from mvc.routes.auth_routes import register_auth_routes
from mvc.routes.classe_routes import register_classe_routes
from mvc.routes.eleve_compte_routes import register_eleve_compte_routes
from mvc.routes.eleve_routes import register_eleve_routes
from mvc.routes.evaluation_activite_routes import register_evaluation_activite_routes
from mvc.routes.evaluation_critere_routes import register_evaluation_critere_routes
from mvc.routes.evaluation_prof_routes import register_evaluation_prof_routes
from mvc.routes.groupe_routes import register_groupe_routes
from mvc.routes.mes_classes_routes import register_mes_classes_routes
from mvc.routes.mon_parcours_routes import register_mon_parcours_routes
from mvc.routes.niveau_classe_routes import register_niveau_classe_routes
# CRUD des entités du référentiel (admin) — ADR-017
from mvc.routes.formation_routes import register_formation_routes
from mvc.routes.pole_activite_routes import register_pole_activite_routes
from mvc.routes.activite_professionnelle_routes import register_activite_professionnelle_routes
from mvc.routes.competence_routes import register_competence_routes
from mvc.routes.critere_observable_routes import register_critere_observable_routes
from mvc.routes.famille_competence_routes import register_famille_competence_routes
# Atelier référentiel (ADR-018) : vue cohérente d'un référentiel.
from mvc.routes.referentiel_atelier_routes import register_referentiel_atelier_routes
# Éditeur de scénario (ADR-019) : conception sur mesure alignée cpro-education.
from mvc.routes.scenario_editeur_routes import register_scenario_editeur_routes
from mvc.routes.password_reset_routes import register_password_reset_routes
from mvc.routes.seance_routes import register_seance_routes
from mvc.routes.parcours_routes import register_parcours_routes
from mvc.routes.checklist_routes import register_checklist_routes
from mvc.routes.choix_qcm_routes import register_choix_qcm_routes
from mvc.routes.depot_eleve_routes import register_depot_eleve_routes
from mvc.routes.item_checklist_routes import register_item_checklist_routes
from mvc.routes.item_coche_routes import register_item_coche_routes
from mvc.routes.professeur_compte_routes import register_professeur_compte_routes
from mvc.routes.professeur_routes import register_professeur_routes
from mvc.routes.progression_parcours_routes import register_progression_parcours_routes
from mvc.routes.progression_seance_routes import register_progression_seance_routes
from mvc.routes.qcm_routes import register_qcm_routes
from mvc.routes.question_qcm_routes import register_question_qcm_routes
from mvc.routes.section_checklist_routes import register_section_checklist_routes
from mvc.routes.reponse_qcm_routes import register_reponse_qcm_routes
from mvc.routes.tentative_qcm_routes import register_tentative_qcm_routes
from mvc.routes.referentiel_import_routes import register_referentiel_import_routes
from mvc.routes.scenario_routes import register_scenario_routes
from mvc.routes.securite_routes import register_securite_routes
from mvc.routes.compte_routes import register_compte_routes
from mvc.routes.suivi_routes import register_suivi_routes
from forge_mvc_rbac import make_contract_jinja_context
from optins.registry import register_optins

from mvc.models.user_model import charger_utilisateur

router = Router()

with router.group("", public=True) as public:
    public.add("GET", "/", HomeController.index, name="home-index")

# Routes appliquées pour : annee_scolaire_controller
register_annee_scolaire_routes(router)

# Routes appliquées pour : niveau_classe_controller
register_niveau_classe_routes(router)
# CRUD des entités du référentiel (admin)
register_formation_routes(router)
register_pole_activite_routes(router)
register_activite_professionnelle_routes(router)
register_competence_routes(router)
register_critere_observable_routes(router)
register_famille_competence_routes(router)

# Atelier référentiel (ADR-018) : interface principale de gestion d'un référentiel.
register_referentiel_atelier_routes(router)

# Éditeur de scénario (ADR-019) : conception sur mesure alignée cpro-education.
register_scenario_editeur_routes(router)

# Routes appliquées pour : classe_controller
register_classe_routes(router)

# Comptes élèves (socle admin) : créer + lier un compte à une fiche Eleve.
# Monté avant le CRUD /eleve pour que /eleve/comptes matche en priorité.
register_eleve_compte_routes(router)

# Routes appliquées pour : eleve_controller
register_eleve_routes(router)

# Comptes professeurs (socle admin) : créer + lier un compte à une fiche Professeur.
# Monté avant le CRUD /professeur pour que /professeur/comptes matche en priorité.
register_professeur_compte_routes(router)

# Routes appliquées pour : professeur_controller
register_professeur_routes(router)


# Routes appliquées pour : scenario_controller (chaîne Scenario, ticket 13)
register_scenario_routes(router)

# Routes StarterWelcome + VersionStarter (phase ⑦, ticket 14)

# Routes Parcours + VersionParcours + Seance (phase ⑧, tickets 15-16)
register_parcours_routes(router)
register_seance_routes(router)

# Bloc B — AffectationParcours (ticket 17)

# Bloc B — ProgressionParcours + ProgressionSeance (ticket 18)
register_progression_parcours_routes(router)
register_progression_seance_routes(router)

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

# Bloc B — Bilan élève (ticket 21) : synthèse arrêtée des évaluations
register_bilan_eleve_routes(router)

# Bloc B — Suivi professeur (ticket 20) : tableau de bord lecture seule
register_suivi_routes(router)

# Espace professeur — « Mes classes » (lecture seule, socle scolaire filtré par compte)
register_mes_classes_routes(router)

# Espace élève — « Mon parcours » (lecture seule, rôle eleve)
register_mon_parcours_routes(router)

# Évaluation professeur — détail progression, validation séance, checklist prof
register_evaluation_prof_routes(router)


# Routes appliquées pour : groupe_controller
register_groupe_routes(router)

# Import de référentiel par upload admin (ticket 11, ADR-009)
register_referentiel_import_routes(router)

# Back-office admin (forge-mvc-admin) : parcourir les référentiels importés.
# Monté après l'import pour que /admin/referentiel/import matche avant /admin/{slug}/{id}.
register_admin(router)

# Routes appliquées pour : auth_controller
register_auth_routes(router)

# Réinitialisation de mot de passe (ADR-014 T1) : routes publiques, CSRF actif
register_password_reset_routes(router)

# Espace Sécurité — MFA self-service (ADR-015) : auth requise, self-service
register_securite_routes(router)

# Espace Compte — profil / préférences / aide (menu profil) : auth requise
register_compte_routes(router)

# Routes des opt-ins activés (ADR-061).
register_optins(router)

# RBAC — provider Jinja du modèle contrat natif (ADR-016), rendu LOADER-AWARE
# (F55 / ADR-080). `can(...)` s'adosse au contrat `mvc/security/rbac.json` ; mais
# `is_authenticated` / `current_user` reflètent désormais le SUJET RÉEL via le
# loader (existence + activité) : une session orpheline est vue NON authentifiée
# dans les templates (plus de menu profil fantôme), cohérent avec l'AuthMiddleware.
# Enregistré après l'import de l'opt-in pour écraser le provider « table » auto-
# inscrit (fusion : dernier gagnant). Rôles résolus par le natif (get_request_roles).
def _provider_rbac_contrat(request: Request) -> "dict[str, Any]":
    return make_contract_jinja_context(request, user_loader=charger_utilisateur)


register_jinja_context_provider(_provider_rbac_contrat)

# Gardes de route par domaine (permission du contrat `mvc/security/rbac.json`).
# Masquer le menu n'est que du confort ; ces gardes protègent l'URL tapée à la main.
# Cette table préfixe -> permission est appliquée par `PrefixPermissionMiddleware`
# (câblé dans `app.py`) : elle couvre chaque route sous le préfixe, y compris les
# routes futures. Le préfixe le plus spécifique gagne. Un professeur ne gère pas le
# socle même en tapant l'URL.
RBAC_PREFIX_RULES: dict[str, str] = {
    # Socle scolaire + référentiel + back-office admin : socle.gerer (admin).
    "/annee_scolaire": "socle.gerer",
    "/niveau_classe": "socle.gerer",
    "/classe": "socle.gerer",
    "/eleve": "socle.gerer",
    "/professeur": "socle.gerer",
    "/groupe": "socle.gerer",
    "/admin": "socle.gerer",
    # Atelier référentiel (ADR-018) : interface principale, referentiel.gerer.
    "/referentiel": "referentiel.gerer",
    # Entités du référentiel (CRUD admin) : referentiel.gerer (admin).
    "/formation": "referentiel.gerer",
    "/pole_activite": "referentiel.gerer",
    "/activite_professionnelle": "referentiel.gerer",
    "/competence": "referentiel.gerer",
    "/critere_observable": "referentiel.gerer",
    "/famille_competence": "referentiel.gerer",
    # Conception pédagogique : conception.gerer (admin + professeur).
    # Éditeur de scénario sur mesure (ADR-019), avant le CRUD plat /scenario.
    "/conception": "conception.gerer",
    "/scenario": "conception.gerer",
    "/parcours": "conception.gerer",
    "/seance": "conception.gerer",
    # Exécution (travail, évaluation) : execution.gerer (admin + professeur).
    "/progression_parcours": "execution.gerer",
    "/progression_seance": "execution.gerer",
    "/qcm": "execution.gerer",
    "/question_qcm": "execution.gerer",
    "/choix_qcm": "execution.gerer",
    "/tentative_qcm": "execution.gerer",
    "/reponse_qcm": "execution.gerer",
    "/checklist": "execution.gerer",
    "/section_checklist": "execution.gerer",
    "/item_checklist": "execution.gerer",
    "/item_coche": "execution.gerer",
    "/activite": "execution.gerer",
    "/depot_eleve": "execution.gerer",
    "/evaluation_activite": "execution.gerer",
    "/evaluation_critere": "execution.gerer",
    "/bilan": "execution.gerer",
    "/evaluation": "execution.gerer",
    # Suivi (lecture seule) : suivi.voir (admin + professeur).
    "/suivi": "suivi.voir",
    "/mes-classes": "suivi.voir",
    # Espace élève : espace_eleve.voir (rôle eleve). Données filtrées par compte.
    "/mon-parcours": "espace_eleve.voir",
}
