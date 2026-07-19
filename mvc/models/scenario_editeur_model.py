# pyright: strict
"""Modèle de l'éditeur de scénario (ADR-019).

Lecture et écriture par section du scénario pédagogique (aligné cpro-education).
Phase 1 : section Titre (titre, co-intervention, co-auteurs). SQL visible et
paramétré. Les co-auteurs sont le many_to_many scenario <-> professeur
(pivot scenario_professeur).
"""
from typing import Any

from core.database.db import execute, fetch_all, fetch_one, insert
from core.database.transaction import transaction
from mvc.services.scenario_tunnel import slug

# INSERT d'une séquence minimale (ADR-029) : née appairée à un scénario, sans
# niveau (nullable, renseigné ensuite dans le tunnel) ni cadre.
_INSERT_SEQUENCE_JUMELLE = (
    "INSERT INTO sequence (Identifiant, Titre, Statut, ActiviteGlissante, OrdreImpose, "
    "niveau_classe_id, CreatedAt, UpdatedAt) VALUES (?, ?, 'brouillon', 0, 0, ?, NOW(), NOW())"
)
_INSERT_SCENARIO = (
    "INSERT INTO scenario (Titre, Intention, Statut, Version, CoIntervention, referentiel_id, "
    "CreatedAt, UpdatedAt) VALUES (?, '', 'brouillon', '0.1.0', 0, ?, NOW(), NOW())"
)
_LIER_PAIRE = "INSERT INTO scenario_sequence (scenario_id, sequence_id) VALUES (?, ?)"


def list_scenarios() -> list[dict[str, Any]]:
    """Tous les scénarios, les plus récemment modifiés d'abord."""
    return fetch_all(
        "SELECT s.Id, s.Titre, s.Statut, s.Version, s.CoIntervention, s.UpdatedAt, "
        "r.Identifiant AS referentiel_identifiant "
        "FROM scenario s LEFT JOIN referentiel_niveau_classe r ON r.Id = s.referentiel_id "
        "ORDER BY s.UpdatedAt DESC, s.Id DESC"
    )


def get_scenario(scenario_id: int) -> "dict[str, Any] | None":
    return fetch_one("SELECT * FROM scenario WHERE Id = ?", (scenario_id,))


def titre_existe(titre: str) -> bool:
    """Un scénario porte-t-il déjà ce titre ? (unicité du titre, ADR-019)."""
    return fetch_one("SELECT 1 AS x FROM scenario WHERE Titre = ? LIMIT 1", (titre,)) is not None


def titre_existe_autre(titre: str, sauf_id: int) -> bool:
    """Le titre est-il déjà pris par un AUTRE scénario ? (garde-fou au renommage)."""
    return fetch_one(
        "SELECT 1 AS x FROM scenario WHERE Titre = ? AND Id <> ? LIMIT 1", (titre, sauf_id)
    ) is not None


def creer_scenario(titre: str, referentiel_id: "int | None") -> int:
    """Crée un scénario. Le référentiel est **facultatif** (ADR-027 : matières non
    adossées à un référentiel, comme les enseignements généraux).

    Avec référentiel : point d'entrée dont formation, niveau et débouchés se
    déduisent. Sans référentiel (`None`) : la finalisation ne requiert que le
    contexte (voir `recalculer_statut`). Le reste se remplit par sections.

    ADR-029 : la paire naît ensemble. Le scénario ET sa séquence jumelle (titre
    partagé, niveau vide, identifiant dérivé) ET le lien sont écrits dans une
    seule transaction — tout ou rien.
    """
    with transaction() as tx:
        scenario_id = insert(_INSERT_SCENARIO, (titre, referentiel_id), tx=tx)
        sequence_id = insert(_INSERT_SEQUENCE_JUMELLE, (slug(titre), titre, None), tx=tx)
        execute(_LIER_PAIRE, (scenario_id, sequence_id), tx=tx)
    return scenario_id


def lister_scenarios_sans_sequence() -> list[dict[str, Any]]:
    """Scénarios sans séquence appairée (orphelins à backfiller, ADR-029)."""
    return fetch_all(
        "SELECT s.Id, s.Titre FROM scenario s "
        "LEFT JOIN scenario_sequence ss ON ss.scenario_id = s.Id "
        "WHERE ss.Id IS NULL ORDER BY s.Id"
    )


def creer_sequence_jumelle(scenario_id: int, titre: str) -> int:
    """Crée et lie la séquence jumelle d'un scénario existant (backfill ADR-029)."""
    with transaction() as tx:
        sequence_id = insert(_INSERT_SEQUENCE_JUMELLE, (slug(titre), titre, None), tx=tx)
        execute(_LIER_PAIRE, (scenario_id, sequence_id), tx=tx)
    return sequence_id


def creer_sequence_et_scenario(identifiant: str, titre: str, niveau_classe_id: "int | None") -> int:
    """Séquence-first (ADR-029) : crée la séquence ET son scénario jumeau (hors
    référentiel) ET le lien, en une transaction. Retourne l'id de la séquence.

    L'appelant garantit l'unicité du titre du scénario (contrainte UNIQUE).
    """
    with transaction() as tx:
        sequence_id = insert(_INSERT_SEQUENCE_JUMELLE, (identifiant, titre, niveau_classe_id), tx=tx)
        scenario_id = insert(_INSERT_SCENARIO, (titre, None), tx=tx)
        execute(_LIER_PAIRE, (scenario_id, sequence_id), tx=tx)
    return sequence_id


def list_professeurs(exclure_user_id: "int | None" = None) -> list[dict[str, Any]]:
    """Professeurs sélectionnables comme co-auteurs.

    On exclut le professeur du compte courant (`exclure_user_id`) : l'auteur du
    scénario ne peut pas être son propre co-enseignant.
    """
    if exclure_user_id is not None:
        return fetch_all(
            "SELECT Id, Nom, Prenom FROM professeur "
            "WHERE UserId IS NULL OR UserId <> ? ORDER BY Nom, Prenom",
            (exclure_user_id,),
        )
    return fetch_all("SELECT Id, Nom, Prenom FROM professeur ORDER BY Nom, Prenom")


def get_co_auteur_ids(scenario_id: int) -> list[int]:
    rows = fetch_all(
        "SELECT professeur_id FROM scenario_professeur WHERE scenario_id = ?", (scenario_id,)
    )
    return [int(r["professeur_id"]) for r in rows]


def enregistrer_titre(
    scenario_id: int, titre: str, co_intervention: bool, co_auteur_ids: list[int]
) -> None:
    """Enregistre la section Titre : titre, co-intervention, et les co-auteurs (m2m)."""
    with transaction() as tx:
        execute(
            "UPDATE scenario SET Titre = ?, CoIntervention = ?, UpdatedAt = NOW() WHERE Id = ?",
            (titre, 1 if co_intervention else 0, scenario_id),
            tx=tx,
        )
        execute("DELETE FROM scenario_professeur WHERE scenario_id = ?", (scenario_id,), tx=tx)
        for pid in co_auteur_ids:
            execute(
                "INSERT INTO scenario_professeur (scenario_id, professeur_id) VALUES (?, ?)",
                (scenario_id, pid),
                tx=tx,
            )


def enregistrer_contexte(
    scenario_id: int,
    description_contexte: str,
    problematique: str,
    materiels_logiciels: str,
    liens_associes: str,
    espaces_formation: str,
) -> None:
    """Enregistre la section Contexte (5 champs cpro, ADR-019)."""
    execute(
        "UPDATE scenario SET DescriptionContexte = ?, Problematique = ?, "
        "MaterielsLogiciels = ?, LiensAssocies = ?, EspacesFormation = ?, UpdatedAt = NOW() "
        "WHERE Id = ?",
        (
            description_contexte,
            problematique,
            materiels_logiciels,
            liens_associes,
            espaces_formation,
            scenario_id,
        ),
    )


_CHAMPS_CONTEXTE = (
    "DescriptionContexte",
    "Problematique",
    "MaterielsLogiciels",
    "LiensAssocies",
    "EspacesFormation",
)


def recalculer_statut(scenario_id: int) -> None:
    """Recalcule et persiste le statut du scénario d'après les données saisies (ADR-019).

    Le statut est stocké en base (pas de calcul à la lecture) mais tenu à jour à
    chaque écriture qui peut le faire changer, donc jamais falsifiable.
      - avec référentiel : « finalise » = contexte complet ET au moins une activité
        ET au moins un critère (la compétence est impliquée par le critère) ;
      - **sans référentiel** (ADR-027, matière non adossée) : « finalise » = contexte
        complet seul (pas de compétences/critères à exiger) ;
      - « brouillon » : sinon.
    Un scénario « utilise » (utilisé par des élèves) est verrouillé : on n'y touche pas.
    """
    row = fetch_one(
        "SELECT Statut, referentiel_id, " + ", ".join(_CHAMPS_CONTEXTE) + " FROM scenario WHERE Id = ?",
        (scenario_id,),
    )
    if row is None or row["Statut"] == "utilise":
        return
    contexte_complet = all(row[champ] for champ in _CHAMPS_CONTEXTE)
    if row["referentiel_id"] is None:
        # Hors référentiel : le contexte complet suffit à finaliser.
        statut = "finalise" if contexte_complet else "brouillon"
    else:
        n_act = fetch_one(
            "SELECT COUNT(*) AS n FROM scenario_activite WHERE scenario_id = ?", (scenario_id,)
        )
        n_crit = fetch_one(
            "SELECT COUNT(*) AS n FROM scenario_critere WHERE scenario_id = ?", (scenario_id,)
        )
        a_activite = bool(n_act and int(n_act["n"]) > 0)
        a_critere = bool(n_crit and int(n_crit["n"]) > 0)
        statut = "finalise" if (contexte_complet and a_activite and a_critere) else "brouillon"
    execute(
        "UPDATE scenario SET Statut = ?, UpdatedAt = NOW() WHERE Id = ?",
        (statut, scenario_id),
    )


def enregistrer_referentiel(scenario_id: int, referentiel_id: int) -> None:
    """Rattache le scénario à un référentiel (section Liaison, ADR-019)."""
    execute(
        "UPDATE scenario SET referentiel_id = ?, UpdatedAt = NOW() WHERE Id = ?",
        (referentiel_id, scenario_id),
    )


def get_activite_ids(scenario_id: int) -> list[int]:
    rows = fetch_all(
        "SELECT activite_professionnelle_id FROM scenario_activite WHERE scenario_id = ?",
        (scenario_id,),
    )
    return [int(r["activite_professionnelle_id"]) for r in rows]


def get_critere_ids(scenario_id: int) -> list[int]:
    rows = fetch_all(
        "SELECT critere_observable_id FROM scenario_critere WHERE scenario_id = ?", (scenario_id,)
    )
    return [int(r["critere_observable_id"]) for r in rows]


def enregistrer_liaison(
    scenario_id: int, activite_ids: list[int], critere_ids: list[int]
) -> None:
    """Enregistre la liaison au référentiel : activités et critères cochés (m2m)."""
    with transaction() as tx:
        execute("DELETE FROM scenario_activite WHERE scenario_id = ?", (scenario_id,), tx=tx)
        for aid in activite_ids:
            execute(
                "INSERT INTO scenario_activite (scenario_id, activite_professionnelle_id) VALUES (?, ?)",
                (scenario_id, aid),
                tx=tx,
            )
        execute("DELETE FROM scenario_critere WHERE scenario_id = ?", (scenario_id,), tx=tx)
        for cid in critere_ids:
            execute(
                "INSERT INTO scenario_critere (scenario_id, critere_observable_id) VALUES (?, ?)",
                (scenario_id, cid),
                tx=tx,
            )


# Cochage unitaire (tunnel maître-détail) : écriture CIBLÉE d'un seul lien, et non
# une réécriture de la liste entière. Deux cases cochées/décochées « en même temps »
# (HTMX émet des requêtes concurrentes) touchent alors des lignes distinctes et ne
# s'écrasent plus l'une l'autre. `INSERT IGNORE` s'appuie sur la contrainte unique
# du pivot (scenario_id, fk) pour rester idempotent sans lecture préalable fiable.

def lier_activite(scenario_id: int, activite_id: int) -> None:
    """Coche une activité pour un scénario (idempotent via l'unicité du pivot)."""
    execute(
        "INSERT IGNORE INTO scenario_activite (scenario_id, activite_professionnelle_id) "
        "VALUES (?, ?)",
        (scenario_id, activite_id),
    )


def delier_activite(scenario_id: int, activite_id: int) -> None:
    """Décoche une activité (suppression du seul lien concerné)."""
    execute(
        "DELETE FROM scenario_activite WHERE scenario_id = ? AND activite_professionnelle_id = ?",
        (scenario_id, activite_id),
    )


def lier_critere(scenario_id: int, critere_id: int) -> None:
    """Coche un critère pour un scénario (idempotent via l'unicité du pivot)."""
    execute(
        "INSERT IGNORE INTO scenario_critere (scenario_id, critere_observable_id) VALUES (?, ?)",
        (scenario_id, critere_id),
    )


def delier_critere(scenario_id: int, critere_id: int) -> None:
    """Décoche un critère (suppression du seul lien concerné)."""
    execute(
        "DELETE FROM scenario_critere WHERE scenario_id = ? AND critere_observable_id = ?",
        (scenario_id, critere_id),
    )


def elaguer_criteres_hors_activites(scenario_id: int) -> None:
    """Retire les critères dont la compétence n'est plus mobilisée par les activités
    cochées du scénario (invariant : on n'évalue qu'une compétence valide).

    Appelé après chaque bascule d'activité : décocher une activité peut invalider
    une compétence dont des critères étaient sélectionnés — ces critères deviennent
    « fantômes » (compétence grisée, inaccessible) et sont donc élagués. Un seul
    DELETE atomique ; sous-requête vide (aucune activité) => tous les critères
    partent (competence_id est NOT NULL, pas de piège NULL sur NOT IN)."""
    execute(
        "DELETE sc FROM scenario_critere sc "
        "JOIN critere_observable c ON c.Id = sc.critere_observable_id "
        "WHERE sc.scenario_id = ? AND c.competence_id NOT IN ("
        "SELECT ac.competence_id FROM activite_competence ac "
        "JOIN scenario_activite sa ON sa.activite_professionnelle_id = ac.activite_professionnelle_id "
        "WHERE sa.scenario_id = ?)",
        (scenario_id, scenario_id),
    )


def list_ressources(scenario_id: int) -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT Id, NomOriginal, CheminMedia, MimeType, Taille, CreatedAt "
        "FROM scenario_ressource WHERE scenario_id = ? ORDER BY CreatedAt DESC, Id DESC",
        (scenario_id,),
    )


def ajouter_ressource(
    scenario_id: int, nom_original: str, chemin_media: str, mime_type: "str | None", taille: int
) -> None:
    execute(
        "INSERT INTO scenario_ressource "
        "(scenario_id, NomOriginal, CheminMedia, MimeType, Taille, CreatedAt) "
        "VALUES (?, ?, ?, ?, ?, NOW())",
        (scenario_id, nom_original, chemin_media, mime_type, taille),
    )


def get_ressource(ressource_id: int, scenario_id: int) -> "dict[str, Any] | None":
    return fetch_one(
        "SELECT Id, scenario_id, CheminMedia FROM scenario_ressource WHERE Id = ? AND scenario_id = ?",
        (ressource_id, scenario_id),
    )


def supprimer_ressource(ressource_id: int) -> None:
    execute("DELETE FROM scenario_ressource WHERE Id = ?", (ressource_id,))


def supprimer_scenario(scenario_id: int) -> None:
    """Supprime un scénario. Ses pivots (activités, critères, ressources,
    co-auteurs, séquences) partent en CASCADE (FK ON DELETE CASCADE)."""
    execute("DELETE FROM scenario WHERE Id = ?", (scenario_id,))
