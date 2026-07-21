"""Fixture callable : chaîne pédagogique complète et cohérente (ADR-029/032).

Construit, sur un socle déjà chargé (classes, profs, élèves) et le référentiel
2tne-ciel importé :

- des **scénarios adossés au référentiel** ET un/des **scénarios hors référentiel**
  (ADR-027), chacun avec sa **séquence jumelle** (appairage ADR-029, via
  `creer_scenario`) ;
- des **liens profs↔classes** (`classe_professeur`) et **prof responsable↔séquence**
  (`professeur_sequence`) ;
- pour une séquence adossée au référentiel, des **séances** qui **observent** des
  compétences/critères (`seance_competence`/`seance_critere`, scopés par le scénario)
  avec leurs **indicateurs** (pour la suggestion de la feuille, ADR-032) ;
- des **progressions élève** à statuts variés (pour peupler la file « à évaluer »)
  et une **observation évaluée** pour Dupont Marie (le bilan s'appuie dessus).

On résout les Id au fil de l'eau (ADR-078). SQL visible et paramétré.
"""
from typing import Any

from forge_mvc_fixtures import Fixture
from core.database import db
from mvc.models.scenario_editeur_model import creer_scenario

_REFERENTIEL = "2tne-ciel"  # referentiel_niveau_classe.Identifiant (import 2tne-ciel)
_INDIC = ["Le mode opératoire est respecté.", "Le résultat obtenu est conforme à l'attendu."]


def _id(row: "dict[str, Any] | None", quoi: str) -> int:
    if row is None:
        raise RuntimeError(f"Fixture pedagogie : {quoi} introuvable (socle/référentiel non chargé ?).")
    return int(row["Id"])


class PedagogieFixture(Fixture):
    tables = (
        "scenario", "scenario_sequence", "scenario_competence", "scenario_critere",
        "sequence", "seance", "seance_competence", "seance_critere", "indicateur_reussite",
        "classe_professeur", "professeur_sequence",
        "progression_sequence", "progression_seance",
        "evaluation_activite", "evaluation_critere",
    )
    depends_on = (
        "niveau_classe", "classe", "eleve", "professeur",
        "competence", "critere_observable", "referentiel_niveau_classe",
    )

    def load(self) -> None:
        ref = _id(db.fetch_one("SELECT Id FROM referentiel_niveau_classe WHERE Identifiant = ?", (_REFERENTIEL,)),
                  "référentiel 2tne-ciel")
        prof = {nom: _id(db.fetch_one("SELECT Id FROM professeur WHERE Nom = ?", (nom,)), f"prof {nom}")
                for nom in ("Bernard", "Moreau", "Petit")}
        classe = {code: _id(db.fetch_one("SELECT Id FROM classe WHERE Code = ?", (code,)), f"classe {code}")
                  for code in ("2TNE-A", "2TNE-B", "2TNE-C")}

        # --- Affectations profs ↔ classes (avec recouvrement réaliste). ---
        for pid, cid in [
            (prof["Bernard"], classe["2TNE-A"]), (prof["Bernard"], classe["2TNE-B"]),
            (prof["Moreau"], classe["2TNE-B"]), (prof["Moreau"], classe["2TNE-C"]),
            (prof["Petit"], classe["2TNE-A"]), (prof["Petit"], classe["2TNE-C"]),
        ]:
            db.execute("INSERT INTO classe_professeur (classe_id, professeur_id) VALUES (?, ?)", (cid, pid))

        # --- Scénarios + séquences jumelles (ADR-029). ---
        def paire(titre: str, referentiel_id: "int | None") -> tuple[int, int]:
            sid = creer_scenario(titre, referentiel_id)
            seq = _id(db.fetch_one("SELECT sequence_id AS Id FROM scenario_sequence WHERE scenario_id = ?", (sid,)),
                      "séquence jumelle")
            return sid, seq

        eth = paire("Installer une liaison Ethernet", ref)
        _cli = paire("Configurer un poste client Windows", ref)
        _com = paire("Mettre en service un commutateur", ref)
        _cr = paire("Co-intervention — Rédiger un compte rendu d'intervention", None)
        _pse = paire("PSE — Prévention des risques électriques", None)

        # Séquence support des progressions : on la publie (les autres restent en brouillon).
        db.execute("UPDATE sequence SET Statut = 'publie' WHERE Id = ?", (eth[1],))

        # Prof responsable de chaque séquence.
        for pid, seq in [
            (prof["Bernard"], eth[1]), (prof["Bernard"], _cli[1]), (prof["Moreau"], _com[1]),
            (prof["Petit"], _cr[1]), (prof["Petit"], _pse[1]),
        ]:
            db.execute("INSERT INTO professeur_sequence (professeur_id, sequence_id) VALUES (?, ?)", (pid, seq))

        # --- Séquence Ethernet : 2 compétences observées, séances + critères + indicateurs. ---
        comps = db.fetch_all(
            "SELECT cp.Id AS id, cp.Intitule AS intitule FROM competence cp "
            "WHERE cp.Code IN ('C01', 'C04') ORDER BY cp.Code"
        )
        seances_eth: list[tuple[int, list[int]]] = []  # (seance_id, [critere_id…])
        for i, comp in enumerate(comps, start=1):
            comp_id = int(comp["id"])
            criteres = [int(r["Id"]) for r in db.fetch_all(
                "SELECT Id FROM critere_observable WHERE competence_id = ? ORDER BY Code LIMIT 3", (comp_id,))]
            # Liaison du scénario (source des critères observables de la séance, ADR-032).
            db.execute("INSERT INTO scenario_competence (scenario_id, competence_id) VALUES (?, ?)", (eth[0], comp_id))
            for cr in criteres:
                db.execute("INSERT INTO scenario_critere (scenario_id, critere_observable_id) VALUES (?, ?)", (eth[0], cr))
                nb = db.fetch_one("SELECT COUNT(*) AS n FROM indicateur_reussite WHERE critere_id = ?", (cr,))
                if nb is not None and int(nb["n"]) == 0:
                    for k, lib in enumerate(_INDIC, start=1):
                        db.execute("INSERT INTO indicateur_reussite (Code, Libelle, critere_id, CreatedAt, UpdatedAt) "
                                   "VALUES (?, ?, ?, NOW(), NOW())", (f"I{k}", lib, cr))
            seance = db.insert(
                "INSERT INTO seance (Ordre, Titre, sequence_id, CreatedAt, UpdatedAt) VALUES (?, ?, ?, NOW(), NOW())",
                (i, f"Séance {i} — {comp['intitule'][:40]}", eth[1]))
            db.execute("INSERT INTO seance_competence (seance_id, competence_id, Role, CreatedAt, UpdatedAt) "
                       "VALUES (?, ?, 'evaluee', NOW(), NOW())", (seance, comp_id))
            for cr in criteres:
                db.execute("INSERT INTO seance_critere (seance_id, critere_observable_id, CreatedAt, UpdatedAt) "
                           "VALUES (?, ?, NOW(), NOW())", (seance, cr))
            seances_eth.append((seance, criteres))

        # Une séance d'introduction pour chaque autre séquence (repère visuel dans les tunnels).
        for titre, (_sid, seq) in [("Configurer un poste client Windows", _cli),
                                   ("Mettre en service un commutateur", _com),
                                   ("Co-intervention — Rédiger un compte rendu d'intervention", _cr),
                                   ("PSE — Prévention des risques électriques", _pse)]:
            db.execute("INSERT INTO seance (Ordre, Titre, sequence_id, CreatedAt, UpdatedAt) "
                       "VALUES (1, ?, ?, NOW(), NOW())", (f"Séance 1 — {titre[:40]}", seq))

        # --- Progressions de la classe 2TNE-A sur la séquence Ethernet (statuts variés). ---
        eleves_a = db.fetch_all(
            "SELECT Id, Identifiant FROM eleve WHERE classe_id = ? ORDER BY Nom", (classe["2TNE-A"],))
        statuts = [
            ["en_attente_validation", "en_cours"],   # 1er élève
            ["en_cours", "a_reprendre"],              # 2e
            ["validee", "non_commencee"],             # 3e
        ]
        pp_par_eleve: dict[str, list[int]] = {}
        for idx, el in enumerate(eleves_a):
            psq = db.insert(
                "INSERT INTO progression_sequence (Statut, DateDebut, eleve_id, sequence_id, CreatedAt, UpdatedAt) "
                "VALUES ('en_cours', CURDATE(), ?, ?, NOW(), NOW())", (el["Id"], eth[1]))
            pps: list[int] = []
            for (seance, _crits), statut in zip(seances_eth, statuts[idx % len(statuts)]):
                pps.append(db.insert(
                    "INSERT INTO progression_seance (Statut, progression_sequence_id, seance_id, CreatedAt, UpdatedAt) "
                    "VALUES (?, ?, ?, NOW(), NOW())", (statut, psq, seance)))
            pp_par_eleve[el["Identifiant"]] = pps

        # --- Observation évaluée de Dupont Marie sur la séance 1 (le bilan s'en sert). ---
        pp_dupont = pp_par_eleve["dupont-marie"][0]
        _seance1, crits1 = seances_eth[0]
        ea = db.insert(
            "INSERT INTO evaluation_activite (DateEvaluation, Appreciation, progression_seance_id, professeur_id, CreatedAt, UpdatedAt) "
            "VALUES (NOW(), 'Bon travail, gestes maîtrisés.', ?, ?, NOW(), NOW())", (pp_dupont, prof["Bernard"]))
        for cr, niv in zip(crits1, ["NIVEAU_3", "NIVEAU_4", "NIVEAU_3"]):
            db.execute("INSERT INTO evaluation_critere (Niveau, evaluation_activite_id, critere_id, CreatedAt, UpdatedAt) "
                       "VALUES (?, ?, ?, NOW(), NOW())", (niv, ea, cr))
