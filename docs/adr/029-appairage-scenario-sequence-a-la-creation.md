# ADR-029 : Appairage 1-1 Scénario ↔ Séquence réalisé à la création

**Statut :** Accepté
**Date :** 2026-07-20

## Contexte

Le modèle pose un **1-1 strict** entre Scénario et Séquence : le pivot
`scenario_sequence` porte une contrainte UNIQUE sur `scenario_id` **et** sur
`sequence_id`. Le scénario porte le cadre (contexte, compétences, critères) ; la
séquence porte le cadre institutionnel, les connaissances et les séances
(frontière A, ADR-028).

Or **cet invariant n'est jamais réalisé** :

- `creer_scenario` insère uniquement la ligne scénario — ni séquence jumelle, ni
  lien ;
- la création inline de séquence (récente) crée au contraire des séquences
  **orphelines**, sans scénario.

Résultat constaté en base : deux scénarios finalisés, **zéro séquence**, **zéro
lien**. La liste `/sequence` est donc vide alors que des scénarios existent —
incohérence directement visible.

Un blocage technique empêche l'appairage automatique côté scénario :
`sequence.niveau_classe_id` est **NOT NULL**, alors qu'un scénario n'a **pas de
niveau de classe** à sa création.

## Décision

**1. L'invariant est réalisé, la paire naît ensemble.** Tout scénario a
exactement une séquence et réciproquement. La création est **atomique**
(transaction : la paire complète, ou rien), quel que soit le point d'entrée :

- **Scénario-first** (`/conception/scenario`) : `creer_scenario` crée le scénario
  **et** sa séquence jumelle (titre partagé, niveau vide, statut brouillon,
  identifiant dérivé) **et** le lien.
- **Séquence-first** (`/sequence`) : la création crée la séquence **et** son
  scénario jumeau (titre partagé, **hors référentiel** par défaut, ADR-027)
  **et** le lien.

**2. `niveau_classe_id` devient nullable.** La séquence peut naître sans niveau ;
il se renseigne ensuite dans le tunnel séquence (étape Titre). Migration additive
(NOT NULL → NULL), contrat `sequence.json` aligné.

**3. Titre partagé.** Le titre est saisi une fois et porté par les deux objets,
le scénario faisant foi (recopié à la création). Décision antérieure du porteur.

**4. Identifiant de séquence.** Dérivé du titre (slug) à la création, éditable
ensuite. Pas de contrainte d'unicité.

**5. Reprise de données (backfill).** Chaque scénario existant sans séquence
reçoit une séquence jumelle (titre = scénario, niveau vide, brouillon) et le
lien. Script ponctuel, réversible.

## Conséquences

- **Migration** : `sequence.niveau_classe_id` passe de NOT NULL à **nullable**
  (additive, non destructive).
- **Création transactionnelle** : `creer_scenario` et la création de séquence
  écrivent scénario + séquence + lien dans une transaction (tout ou rien).
- **Tunnel séquence** : l'étape Titre accepte un niveau vide (`select` avec une
  option « — »), puisque la séquence peut naître sans niveau.
- **Backfill** : script créant les séquences manquantes des scénarios orphelins,
  puis leurs liens. Réversible (suppression des séquences créées).
- **`/sequence`** ne liste plus que des séquences réellement appairées.
- **Suppression (à préciser, hors périmètre immédiat)** : comme la relation est
  1-1, supprimer un objet devrait supprimer la paire. La règle exacte (cascade,
  verrous pour un scénario « utilisé ») sera tranchée dans un incrément dédié.

## Alternatives écartées

- **`niveau_classe_id` avec valeur par défaut** (ex. « seconde ») plutôt que
  nullable : masque une donnée non renseignée derrière une valeur arbitraire.
  Écartée.
- **Scénario-first uniquement** (la séquence n'existe que comme projection du
  scénario, pas de création indépendante) : plus simple, mais abandonne le
  workflow « je crée d'abord la séquence » voulu par le porteur. Écartée.
- **Appairage manuel a posteriori** (l'utilisateur lie les deux objets après
  coup) : fragile, l'invariant 1-1 resterait violable (orphelins). Écartée.

## Références

- `docs/adr/022-parcours-objet-canonique-aplatissement.md` (aplatissement du
  cœur, 1-1).
- `docs/adr/027-scenario-hors-referentiel.md` (la séquence-first crée un scénario
  hors référentiel).
- `docs/adr/028-connaissances-associees-ancrage-referentiel.md` (frontière A).
- Pivot `scenario_sequence` (UNIQUE sur `scenario_id` et `sequence_id`).
