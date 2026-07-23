# pyright: strict
"""Logique pure du tunnel d'édition de séquence (miroir de scenario_tunnel).

Même patron que le tunnel scénario (ADR-019, ADR-021) : bornage de l'étape,
complétion dérivée des données (jamais persistée), navigation entre étapes.
La séquence porte le cadre institutionnel (SEQ-02) et les connaissances
associées (ADR-028) ; sa liaison au référentiel passe par le scénario appairé.
"""
from __future__ import annotations

from typing import Any, cast

ETAPES: tuple[str, ...] = ("titre", "cadre", "gestion")

LIBELLES: dict[str, str] = {
    "titre": "Titre",
    "cadre": "Cadre institutionnel",
    "gestion": "Gestion",
}


# Modes d'organisation de l'encadré « Activité » (étape Titre) : choix exclusif
# en interface, projeté sur les deux booléens ActiviteGlissante / OrdreImpose
# (conservés en base et dans le JSON canonique).
ORGANISATIONS: tuple[str, ...] = ("libre", "ordre_impose", "glissante")

# Nature de la séquence (ADR-036) : contextualise les statuts attendus des
# savoirs (formative : tout le cycle ; certificative/CCF : prérequis et
# mobilisée seulement) et les signaux de cohérence savoirs <-> liaison.
NATURES: tuple[str, ...] = ("formative", "certificative")
NATURE_LABELS: dict[str, str] = {
    "formative": "Formative",
    "certificative": "Certificative (CCF)",
}

# Statuts de savoir PROPOSÉS selon la nature (ADR-036 révisé) : « Mobilisée »
# est propre au certificatif (en formatif, un savoir réutilisé se déclare
# « Prérequis ») ; « Apportée » et « Consolidée » n'ont pas de sens en épreuve.
STATUTS_PAR_NATURE: dict[str, tuple[str, ...]] = {
    "formative": ("prerequis", "apportee", "consolidee"),
    "certificative": ("prerequis", "mobilisee"),
}


def statuts_pour_nature(nature: object) -> tuple[str, ...]:
    """Statuts de savoir proposés pour la nature donnée (formative par défaut)."""
    return STATUTS_PAR_NATURE.get(str(nature or "formative"), STATUTS_PAR_NATURE["formative"])


def savoir_valide(lien: dict[str, Any]) -> bool:
    """Un savoir retenu n'est VALIDÉ que si niveau cible ET statut sont saisis.

    Seuls les savoirs validés comptent dans la complétude de l'étape et dans la
    finalisation de la séquence (ADR-036 révisé).
    """
    return lien.get("NiveauCible") is not None and bool(lien.get("Statut"))


def nb_savoirs_valides(liens: "list[dict[str, Any]]") -> int:
    """Nombre de savoirs retenus ET validés (niveau cible + statut saisis)."""
    return sum(1 for lien in liens if savoir_valide(lien))


# Statuts OUVRANTS (ADR-036 révisé) : ceux qui font qu'une compétence est
# réellement TRAVAILLÉE par la séquence. Un savoir en simple « prérequis »
# n'ouvre pas la compétence : on s'appuie dessus, on ne la travaille pas.
STATUTS_OUVRANTS: dict[str, tuple[str, ...]] = {
    "formative": ("apportee", "consolidee"),
    "certificative": ("mobilisee",),
}


def statuts_ouvrants_pour_nature(nature: object) -> tuple[str, ...]:
    """Statuts ouvrants pour la nature donnée (formative par défaut)."""
    return STATUTS_OUVRANTS.get(str(nature or "formative"), STATUTS_OUVRANTS["formative"])


def savoir_ouvrant(lien: dict[str, Any], nature: object) -> bool:
    """Le savoir est validé ET son statut ouvre la compétence pour cette nature."""
    return savoir_valide(lien) and str(lien.get("Statut")) in statuts_ouvrants_pour_nature(nature)


def nb_savoirs_ouvrants(liens: "list[dict[str, Any]]", nature: object) -> int:
    """Nombre de savoirs ouvrants : c'est LUI qui conditionne la complétude de
    l'étape Savoirs et la finalisation (une séquence adossée à un référentiel
    sert à travailler des compétences, pas seulement à s'appuyer sur elles)."""
    return sum(1 for lien in liens if savoir_ouvrant(lien, nature))


def mode_organisation(sequence: dict[str, Any]) -> "str | None":
    """Mode d'organisation dérivé des deux drapeaux booléens.

    None = « à préciser » (les deux drapeaux sont NULL, état de création) : le
    choix doit être CONSCIENT, il conditionne la complétude de l'étape Titre et
    la finalisation (complément ADR-034). « glissante » prime si les deux sont
    posés (données historiques) ; la première sauvegarde normalise.
    """
    glissante = sequence.get("ActiviteGlissante")
    impose = sequence.get("OrdreImpose")
    if glissante:
        return "glissante"
    if impose:
        return "ordre_impose"
    if glissante is None and impose is None:
        return None
    return "libre"


# Cycle de statut de la séquence (ADR-034, miroir du scénario ADR-019) :
# ENTIÈREMENT dérivé des données, jamais saisi.
# brouillon -> finalise (tunnel complet) -> publie (au moins une séance liée)
# -> attribue (au moins une progression élève). Les séances se lient dès
# « finalise » ; l'attribution aux élèves passe par les séquences publiées.
STATUTS_SEQUENCE: tuple[str, ...] = ("brouillon", "finalise", "publie", "attribue")


def statut_sequence_cible(
    titre: object,
    niveau_classe_id: object,
    referentiel_id: object,
    nb_seances: int,
    nb_seances_ouvrantes: int,
    nb_attributions: int,
    organisation: "str | None" = None,
) -> str:
    """Statut recalculé d'une séquence d'après ses données (jamais saisi).

    Cycle ADR-034 révisé par l'ADR-037 (les savoirs vivent sur la séance) :
    - « attribue » prime sur tout : au moins un élève a une progression sur la
      séquence, elle est en usage (et figée par instantané, ADR-026) ;
    - « finalise » = titre ET niveau ET organisation des séances renseignés
      (le cadre est posé — l'organisation est un choix conscient, complément
      ADR-034 sur retour porteur) ;
    - « publie » = finalisée ET au moins une séance OUVRANTE (ayant ≥ 1 savoir
      ouvrant) — hors référentiel : au moins une séance, les savoirs libres
      restant au niveau séquence ;
    - « brouillon » sinon.
    """
    if nb_attributions > 0:
        return "attribue"
    if not (bool(titre) and niveau_classe_id is not None and organisation is not None):
        return "brouillon"
    seances_qualifiantes = nb_seances_ouvrantes if referentiel_id is not None else nb_seances
    return "publie" if seances_qualifiantes > 0 else "finalise"


def duree_lisible(minutes: "int | None") -> "str | None":
    """Cumul de minutes en libellé lisible (« 45 min », « 2 h », « 1 h 30 »).

    None si la durée est indéfinie (aucune séance, ou durées non renseignées).
    """
    if minutes is None or minutes <= 0:
        return None
    heures, restant = divmod(minutes, 60)
    if heures == 0:
        return f"{restant} min"
    if restant == 0:
        return f"{heures} h"
    return f"{heures} h {restant:02d}"


def parse_id(raw: object) -> "int | None":
    """Entier depuis une valeur de requête, ou None — jamais d'exception."""
    try:
        return int(cast("int", raw))
    except (TypeError, ValueError):
        return None


def borner_etape(raw: str) -> str:
    """Étape demandée, bornée à la liste connue (défaut : titre)."""
    return raw if raw in ETAPES else "titre"


def steps(
    sequence: dict[str, Any],
) -> list[dict[str, Any]]:
    """Barre d'étapes : la complétion est DÉRIVÉE des données, jamais persistée.

    - Titre : le titre est rempli (obligatoire à la création) ET le niveau de
      classe est choisi ET l'organisation des séances est choisie (obligatoires,
      mais renseignés après la création — complément ADR-034).
    - Cadre institutionnel : facultatif (ne bloque jamais) ; il héberge aussi
      les savoirs libres des séquences hors référentiel (ADR-030/037).
    Les savoirs associés vivent sur les SÉANCES (ADR-037) et les séances se
    parcourent par l'arbre « Famille pédagogique » : ni les uns ni les autres
    ne sont plus des étapes du tunnel séquence.
    """
    return [
        {
            "key": "titre",
            "label": LIBELLES["titre"],
            "badge": "",
            "done": (bool(sequence.get("Titre"))
                     and sequence.get("niveau_classe_id") is not None
                     and mode_organisation(sequence) is not None),
        },
        {
            "key": "cadre",
            "label": LIBELLES["cadre"],
            "badge": "",
            "done": True,
        },
        {
            # Gestion (ADR-038) : exports, attributions, suppression. Étape
            # d'outillage, hors complétude (drapeau `outil` : ni coche ni cercle).
            "key": "gestion",
            "label": LIBELLES["gestion"],
            "badge": "",
            "done": True,
            "outil": True,
        },
    ]


def navigation(etape: str) -> dict[str, Any]:
    """Position dans le tunnel et étapes précédente/suivante (None aux bornes)."""
    position = ETAPES.index(etape) + 1
    return {
        "etape": etape,
        "position": position,
        "total": len(ETAPES),
        "prev": (
            {"key": ETAPES[position - 2], "label": LIBELLES[ETAPES[position - 2]]}
            if position > 1
            else None
        ),
        "next": (
            {"key": ETAPES[position], "label": LIBELLES[ETAPES[position]]}
            if position < len(ETAPES)
            else None
        ),
    }
