# pyright: strict
"""Complétude des étapes du tunnel séquence (logique pure, sans base).

L'étape Titre exige le titre ET le niveau de classe : le niveau est obligatoire
mais se renseigne après la création (colonne nullable pour l'état pré-saisie).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from mvc.services.sequence_tunnel import (
    duree_lisible,
    mode_organisation,
    nb_savoirs_ouvrants,
    nb_savoirs_valides,
    statut_sequence_cible,
    statuts_pour_nature,
    steps,
)

_VUES = Path(__file__).resolve().parent.parent / "mvc" / "views" / "app"


def _etape_titre(sequence: dict[str, Any]) -> dict[str, Any]:
    return next(s for s in steps(sequence) if s["key"] == "titre")


def test_titre_sans_niveau_ne_complete_pas_l_etape() -> None:
    etape = _etape_titre({"Titre": "Essai", "niveau_classe_id": None})
    assert etape["done"] is False


def test_titre_et_niveau_completent_l_etape() -> None:
    """Complet = titre + niveau + organisation choisie (complément ADR-034)."""
    complet = {"Titre": "Essai", "niveau_classe_id": 3, "OrdreImpose": 1}
    assert _etape_titre(complet)["done"] is True
    sans_organisation = {"Titre": "Essai", "niveau_classe_id": 3}
    assert _etape_titre(sans_organisation)["done"] is False


def test_mode_organisation_a_preciser_tant_que_rien_est_choisi() -> None:
    """NULL/NULL = « à préciser » : aucun mode présélectionné à la création."""
    assert mode_organisation({}) is None
    assert mode_organisation({"ActiviteGlissante": None, "OrdreImpose": None}) is None


def test_mode_organisation_derive_des_drapeaux() -> None:
    """Choix exclusif de l'encadré « Activité », projeté sur les deux booléens.

    « glissante » prime quand les deux drapeaux sont posés (données créées quand
    les cases étaient indépendantes).
    """
    assert mode_organisation({"ActiviteGlissante": 0, "OrdreImpose": 0}) == "libre"
    assert mode_organisation({"ActiviteGlissante": 0, "OrdreImpose": 1}) == "ordre_impose"
    assert mode_organisation({"ActiviteGlissante": 1, "OrdreImpose": 0}) == "glissante"
    assert mode_organisation({"ActiviteGlissante": 1, "OrdreImpose": 1}) == "glissante"


def test_statut_cible_sequence_incomplete_reste_brouillon() -> None:
    """Titre ou niveau manquant : brouillon (ADR-037 : les savoirs sont sur la séance)."""
    assert statut_sequence_cible("", 3, None, 0, 0, 0) == "brouillon"
    assert statut_sequence_cible("Essai", None, None, 0, 0, 0) == "brouillon"


def test_statut_cible_titre_et_niveau_finalisent() -> None:
    """Finalisée = titre + niveau + organisation ; la publication attend une
    séance ouvrante. Sans organisation : brouillon (complément ADR-034)."""
    assert statut_sequence_cible("Essai", 3, 1, 0, 0, 0, "libre") == "finalise"
    assert statut_sequence_cible("Essai", 3, 1, 2, 0, 0, "ordre_impose") == "finalise"  # séances sans savoir ouvrant
    assert statut_sequence_cible("Essai", 3, None, 0, 0, 0, "glissante") == "finalise"  # hors référentiel, sans séance
    assert statut_sequence_cible("Essai", 3, 1, 0, 0, 0) == "brouillon"  # organisation à préciser


def test_statut_cible_publiee_par_seance_ouvrante() -> None:
    """Publiée = au moins une séance OUVRANTE (hors réf : au moins une séance)."""
    assert statut_sequence_cible("Essai", 3, 1, 2, 1, 0, "libre") == "publie"
    assert statut_sequence_cible("Essai", 3, None, 1, 0, 0, "libre") == "publie"  # hors référentiel


def test_statut_cible_attribuee_prime_sur_tout() -> None:
    """Une progression élève existe : « attribue », même si les données ont bougé."""
    assert statut_sequence_cible("Essai", 3, 1, 2, 1, 3) == "attribue"
    assert statut_sequence_cible("", None, 1, 0, 0, 1) == "attribue"


def test_statuts_proposes_selon_la_nature() -> None:
    """ADR-036 révisé : mobilisée est propre au certificatif ; apportée et
    consolidée n'ont pas de sens en épreuve. Nature inconnue -> formative."""
    assert statuts_pour_nature("formative") == ("prerequis", "apportee", "consolidee")
    assert statuts_pour_nature("certificative") == ("prerequis", "mobilisee")
    assert statuts_pour_nature(None) == ("prerequis", "apportee", "consolidee")


def test_savoir_valide_exige_niveau_et_statut() -> None:
    """Un savoir coché ne compte que si niveau cible ET statut sont saisis."""
    assert nb_savoirs_valides([
        {"NiveauCible": 2, "Statut": "apportee"},   # validé
        {"NiveauCible": None, "Statut": "apportee"},  # niveau manquant
        {"NiveauCible": 3, "Statut": None},           # statut manquant
        {"NiveauCible": 3, "Statut": ""},             # statut vide
    ]) == 1


def test_savoirs_ouvrants_selon_la_nature() -> None:
    """ADR-036 révisé : seuls apportée/consolidée (formative) ou mobilisée (CCF)
    OUVRENT une compétence ; un prérequis validé s'appuie sans ouvrir."""
    liens = [
        {"NiveauCible": 2, "Statut": "prerequis"},   # validé mais non ouvrant
        {"NiveauCible": 2, "Statut": "apportee"},    # ouvrant en formative
        {"NiveauCible": 3, "Statut": "mobilisee"},   # ouvrant en certificative
        {"NiveauCible": None, "Statut": "apportee"}, # non validé
    ]
    assert nb_savoirs_ouvrants(liens, "formative") == 1
    assert nb_savoirs_ouvrants(liens, "certificative") == 1
    assert nb_savoirs_ouvrants([{"NiveauCible": 1, "Statut": "prerequis"}], "formative") == 0


def test_duree_lisible_formats_et_indefinie() -> None:
    """Durée de séquence DÉRIVÉE du cumul des séances : formatage lisible."""
    assert duree_lisible(None) is None
    assert duree_lisible(0) is None
    assert duree_lisible(45) == "45 min"
    assert duree_lisible(120) == "2 h"
    assert duree_lisible(90) == "1 h 30"
    assert duree_lisible(65) == "1 h 05"


def test_les_formulaires_des_tunnels_ne_postent_pas_sur_base_url() -> None:
    """Régression : dans les tunnels séquence et séance, base_url est l'URL de
    l'éditeur (/sequence/editeur/{id}) alors que les routes d'enregistrement
    vivent sous /sequence/{id}/… — un POST sur base_url part en 404 silencieux
    et l'auto-save perd la saisie. (Le tunnel scénario, lui, partage son préfixe
    d'éditeur avec ses routes : base_url y est légitime.)
    """
    fautifs: list[str] = []
    for dossier in ("sequence_editeur", "seance_editeur"):
        for template in sorted((_VUES / dossier).glob("*.html")):
            contenu = template.read_text(encoding="utf-8")
            if 'hx-post="{{ base_url }}' in contenu or 'action="{{ base_url }}' in contenu:
                fautifs.append(f"{dossier}/{template.name}")
    assert fautifs == []
