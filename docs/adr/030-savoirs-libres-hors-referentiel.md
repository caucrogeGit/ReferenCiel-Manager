# ADR-030 : Savoirs libres pour les séquences hors référentiel

**Statut :** Accepté
**Date :** 2026-07-20

## Contexte

L'ADR-028 a ancré les savoirs associés au référentiel : entité `Connaissance`
(rattachée à la compétence, niveau taxonomique officiel), sélectionnée par la
séquence via `sequence_connaissance` (niveau cible ≠ officiel, statut). Il a
**retiré** la liste de texte libre `savoir_associe`, en écartant l'alternative
« garder le savoir libre pour le hors référentiel » au motif qu'« une séquence
sans référentiel n'a pas de connaissances ».

**Retour terrain : ce pari est faux.** Les matières **non adossées à un
référentiel** (enseignements généraux, PSE, chef-d'œuvre, co-intervention…) ont
bel et bien des savoirs à faire figurer dans la séquence. Simplement, il n'existe
pas de référentiel où les piocher : **le professeur les définit librement**.

Or aujourd'hui, l'étape « Savoirs associés » d'une séquence hors référentiel ne
propose **que** de rattacher un référentiel — une impasse pour une matière qui
n'en a pas.

## Décision

L'étape « Savoirs associés » d'une séquence connaît **deux modes**, selon la
présence d'un référentiel sur le scénario appairé :

1. **Avec référentiel** — sélection **structurée** dans les connaissances du
   référentiel (entité `Connaissance` + lien `sequence_connaissance` : niveau
   cible, statut). **Inchangé** (ADR-028).

2. **Sans référentiel** — **savoirs libres** : le professeur **ajoute et retire**
   des savoirs en **texte libre**, exactement comme les indicateurs de réussite
   du scénario. Nouvelle table `savoir_libre` (`sequence_id`, `libelle`). Pas de
   niveau ni de statut : le professeur est libre.

L'étape hors référentiel propose **les deux** : ajouter des savoirs libres **et**
(en option) rattacher un référentiel pour passer au mode structuré.

Cette décision **amende l'alternative écartée d'ADR-028** : le savoir libre
revient, mais **scopé au cas hors référentiel**. Il n'y a pas de doublon avec
`Connaissance` : quand un référentiel est présent, seules les connaissances
structurées s'appliquent ; sans référentiel, seuls les savoirs libres.

## Conséquences

- **Nouvelle table `savoir_libre`** : `Id`, `sequence_id` (FK → `sequence`,
  cascade), `Libelle` (text), timestamps. Entité + relation + migration.
- **Modèle + endpoints** d'ajout/suppression, sur le patron des indicateurs de
  réussite (formulaire de saisie + croix de suppression, HTMX, dégradation sans
  JS).
- **UI** : dans `_connaissances.html`, la branche « sans référentiel » affiche la
  liste des savoirs libres (ajout/retrait) **et** le sélecteur de rattachement
  d'un référentiel.
- **Export** (PDF/MarkDown/JSON) : les savoirs libres rejoignent l'export de la
  séquence quand elle est hors référentiel, là où les connaissances structurées
  figurent sinon.
- **Frontière** : le savoir libre est au niveau **séquence**, pas séance (comme
  les connaissances structurées).
- **Verrou** : cohérent avec ADR-029, l'ajout de savoirs libres reste possible
  tant que rien ne l'interdit ; le verrou d'ADR-029 ne concerne que le
  **référentiel**, pas les savoirs libres (qui n'en dépendent pas).

## Alternatives écartées

- **`Connaissance` avec `competence_id` nullable** (stocker le savoir libre comme
  une connaissance sans compétence) : mélange référentiel et libre dans la même
  table, rend ambigu ce qui vient du référentiel et ce qui est saisi à la main.
  Écartée.
- **Garder seulement le rattachement de référentiel** (statu quo) : bloque les
  matières sans référentiel — précisément le retour terrain. Écartée.
- **Réutiliser le niveau cible / statut sur les savoirs libres** : sans
  référentiel, le niveau officiel n'existe pas et le statut de progression perd
  son ancrage ; on garde le savoir libre… libre. Écartée.

## Références

- `docs/adr/028-connaissances-associees-ancrage-referentiel.md` (amendé ici sur
  l'alternative « savoir libre »).
- `docs/adr/027-scenario-hors-referentiel.md` (matières non adossées).
- `docs/adr/029-appairage-scenario-sequence-a-la-creation.md` (verrou référentiel).
- Indicateurs de réussite du scénario (`_detail_competence.html`,
  `referentiel_atelier_model.ajouter_indicateur`) : patron d'ajout libre repris.
