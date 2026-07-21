# ADR-031 : Suppression d'un scénario ou d'une séquence — dissociation, pas cascade

**Statut :** Accepté
**Date :** 2026-07-20

## Contexte

L'ADR-029 a établi que la paire Scénario ↔ Séquence **naît ensemble** (1-1),
mais a laissé la règle de **suppression** explicitement « à préciser ». Le
retour terrain la tranche : supprimer un objet ne doit **pas** supprimer son
partenaire — on veut conserver le travail réalisé (séances, savoirs, cadre) même
si l'autre face de la paire disparaît.

Un bug l'a révélé : l'identifiant de séquence (slug du titre, sous contrainte
`uq_sequence_identifiant`) entrait en collision quand on recréait un scénario
dont la séquence jumelle précédente avait **survécu** à la suppression du
scénario (`IntegrityError: Duplicate entry 'test'`).

## Décision

**1. Dissociation, pas cascade.** Supprimer un scénario efface la **ligne de
liaison** (pivot `scenario_sequence`, `ON DELETE CASCADE`) mais **garde la
séquence**. Inversement, supprimer une séquence garde le scénario. Aucun des deux
objets ne disparaît quand on supprime l'autre. *(C'était déjà le comportement via
le pivot ; on l'acte.)*

**2. Invariant assoupli.** L'invariant d'ADR-029 devient : la paire **naît
ensemble** (1-1 à la création), mais chaque objet est **supprimable
indépendamment**. Un objet dont le partenaire a été supprimé devient
**orphelin** — un état **légitime**, pas une anomalie.

**3. Identifiant tolérant aux collisions.** L'identifiant de séquence est suffixé
(`test`, `test-2`, `test-3`…) si le slug du titre est déjà pris, car une séquence
dissociée garde son identifiant. *(Déjà implémenté.)*

**4. Nettoyage explicite.** Pour retirer complètement une paire, on supprime les
**deux** objets, chacun depuis sa liste. Il n'y a pas de suppression en cascade
du partenaire — c'est un choix, pas un oubli.

**5. Pas de ré-appairage automatique.** Une orpheline reste orpheline. Réutiliser
une orpheline ou la relier à un nouveau scénario ajouterait de la complexité
(laquelle réutiliser ? fusion des titres ?) sans besoin avéré. Reporté à un
ticket dédié si le besoin se confirme.

## Conséquences

- **Code de suppression inchangé** (déjà dissociant, pivot cascade) : acté et
  documenté.
- `_identifiant_sequence_unique` suffixe à la création (déjà en place).
- **Limite connue — export d'une séquence orpheline.** L'export PDF/MarkDown/JSON
  passe par le **scénario** ; une séquence sans scénario n'est donc **pas
  exportable** en l'état. Un export côté séquence serait un ticket dédié.
- Le **tunnel séquence** reste fonctionnel pour une orpheline (mode hors
  référentiel, savoirs libres — ADR-030).
- Un **scénario orphelin** (séquence supprimée) reste éditable ; il lui manque le
  contenu porté par la séquence (cadre institutionnel, savoirs, séances).
- **Finalisation (ADR-029).** Supprimer un objet finalisé reste permis (sauf
  statut « utilisé », déjà verrouillé) et dissocie ; le partenaire survit,
  dissocié.
- **Accumulation d'orphelins.** Supprimer en masse des scénarios laisse leurs
  séquences en base (et inversement). C'est le comportement attendu ; le
  nettoyage se fait objet par objet.

## Alternatives écartées

- **Cascade (supprimer le partenaire)** : contraire au retour terrain — on veut
  garder le travail de la séquence quand le scénario part. Écartée.
- **Interdire la suppression d'un objet lié** (forcer à délier d'abord) : lourd,
  et le pivot fait déjà le déliage proprement à la suppression. Écartée.
- **Ré-appairage / réutilisation de l'orpheline à la création** : complexité sans
  besoin avéré. Reportée.
- **Rendre l'identifiant de séquence non unique** (supprimer la contrainte) :
  possible, mais l'identifiant reste un repère technique utile ; on préfère le
  suffixe, moins invasif. Écartée.

## Références

- `docs/adr/029-appairage-scenario-sequence-a-la-creation.md` (le point
  « suppression » y était différé ; amendé ici).
- Pivot `scenario_sequence` (`ON DELETE CASCADE` des deux côtés).
- `_identifiant_sequence_unique` (`mvc/models/scenario_editeur_model.py`).
