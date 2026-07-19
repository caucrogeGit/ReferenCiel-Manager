# ADR-028 : Connaissances associées, ancrage référentiel et niveau cible en séquence

**Statut :** Accepté
**Date :** 2026-07-19

## Contexte

SEQ-02 a introduit `savoir_associe` : une **liste de texte libre** de savoirs
rattachés à une séquence. Ce modèle traite le savoir comme une chaîne opaque,
sans ancrage ni niveau.

Or le cadre national contredit ce choix. Pour une seconde 2TNE orientée CIEL,
la source correcte est le **référentiel du Bac Pro CIEL**, qui emploie le terme
officiel **« connaissances associées »**. Elles ne sont pas une liste autonome :
elles sont **rattachées aux compétences** et portent un **niveau taxonomique**
officiel (1 information, 2 expression, 3 maîtrise d'outils, 4 maîtrise
méthodologique — le niveau 4 n'étant pas utilisé en Bac Pro).

Le projet possède **déjà** ce modèle, resté inexploité :

- l'entité **`Connaissance`** (`libelle`, `niveau_taxonomique` 1–4 nullable,
  `competence_id`), ancrée à la compétence (1..n) ;
- le **JSON canonique** du référentiel porte déjà `competences[].connaissances[]`
  avec `{ libelle, niveau_taxonomique }`.

`savoir_associe` est donc un **doublon appauvri** de `Connaissance`, ajouté sans
que l'entité existante ait été vue.

Deux manques subsistent, que ce cadrage éclaire :

1. **L'import ne branche pas les connaissances.** L'importeur *purge* la table
   `connaissance` mais **n'insère pas** les `connaissances[]` du canonique (il
   importe pôles, activités, compétences, critères, indicateurs, et saute les
   connaissances).
2. **Le niveau officiel n'est pas le niveau visé en seconde.** Le référentiel
   place par exemple les protocoles IPv4 au niveau 3 (objectif Bac Pro), mais une
   séquence de seconde peut ne viser que l'identification. Le **niveau cible d'une
   séquence** diffère du **niveau officiel** de la connaissance, et n'a nulle part
   où être enregistré.

## Décision

**1. `Connaissance` est l'objet référentiel unique.** Elle reste ancrée à une
compétence (1..n) et porte le `niveau_taxonomique` **officiel** (1–4). `source`
et `version` ne sont pas dupliqués : ils remontent via
`competence → referentiel_niveau_classe`.

**2. Retrait de `savoir_associe`.** L'entité, sa table, son modèle, ses routes et
l'UI livrée en SEQ-02 (incrément 4a) sont supprimés. Une seule façon de faire :
toute connaissance passe par `Connaissance`.

**3. Nouveau lien Séquence ↔ Connaissance** (`sequence_connaissance`, n-n),
porteur des données **pédagogiques propres à la séquence**, distinctes du
référentiel :

- `niveau_cible` (entier 1–4, nullable) — le niveau réellement visé **dans cette
  séquence**, potentiellement inférieur au niveau officiel ;
- `statut` (énumération) — la place de la connaissance dans la progression :
  `prerequis`, `apportee`, `mobilisee`, `consolidee` ;
- `commentaire` (texte, nullable) — précision pédagogique libre.

**4. Périmètre de sélection.** Une séquence ne peut lier que les connaissances du
**référentiel de son scénario appairé** (séquence → scénario 1-1 → référentiel →
compétences → connaissances). Une séquence hors référentiel (ADR-027) n'a pas de
connaissances liables — cohérent avec l'absence de compétences et de critères.

**5. Branchement de l'import.** L'importeur insère désormais les `connaissances[]`
par compétence (avec leur `niveau_taxonomique`), comblant le trou existant.

**6. Frontière.** Les connaissances sont au niveau **séquence**, pas séance —
comme le savoir libre qu'elles remplacent, et conformément à la frontière A de
SEQ-02 (la séquence porte le cadre, la séance porte l'opérationnel).

## Conséquences

- **Migration destructive** : `DROP TABLE savoir_associe` (table vierge, aucune
  donnée perdue). Retrait de l'entité, du modèle `savoir_associe_model`, des
  routes `sequence-savoir-*` et de la vue `_savoirs.html`.
- **Nouveau pivot `sequence_connaissance`** : `Id`, `sequence_id`
  (FK → `sequence`, cascade), `connaissance_id` (FK → `connaissance`, cascade),
  `NiveauCible` (int nullable), `Statut` (varchar), `Commentaire` (text nullable),
  `UNIQUE(sequence_id, connaissance_id)`. Cascade côté connaissance pour survivre
  à une ré-import du référentiel, comme `scenario_competence`.
- **Survie à la ré-import** : le niveau cible, le statut et le commentaire sont des
  données du professeur ; ils persistent tant que la connaissance existe. Si une
  connaissance disparaît d'un référentiel réimporté, son lien est purgé en cascade
  — perte assumée, cohérente avec les pivots référentiels existants.
- **Importeur** : ajout de l'insertion des connaissances, avec test.
- **UI séquence** : sélection en maître-détail (compétence → ses connaissances),
  avec réglage du niveau cible et du statut par connaissance retenue. Patron HTMX
  du tunnel scénario.
- **Export** : les connaissances (avec niveau cible et statut) rejoignent l'export
  PDF/MarkDown/JSON de la séquence, à la place du savoir libre. À traiter avec l'UI.

## Alternatives écartées

- **Garder `savoir_associe` en parallèle de `Connaissance`** : deux concepts
  concurrents pour la même chose, contraire à « une seule façon de faire ».
  Écartée (le cas hors référentiel n'est pas un besoin avéré de savoir libre :
  une séquence sans référentiel n'a pas de connaissances).
- **Porter le niveau cible sur `Connaissance`** : il écraserait le niveau officiel,
  partagé par toutes les séquences qui utilisent cette connaissance. Le niveau
  cible est propre à chaque séquence, il doit vivre sur le lien. Écartée.
- **Rattacher les connaissances à la séance** : le cadre (dont les connaissances)
  est porté par la séquence et le scénario (frontière A). Écartée.
- **`statut` en texte libre** : perd la sémantique de progression
  (prérequis/apportée/mobilisée/consolidée), exploitable plus tard pour chaîner
  les séquences. Écartée au profit d'une énumération.

## Références

- `docs/adr/023-modele-generique-voie-professionnelle.md` (référentiel voie pro).
- `docs/adr/025-renommage-sequence-seance.md` (séquence / séance).
- `docs/adr/027-scenario-hors-referentiel.md` (séquence sans référentiel).
- `docs/specs/json-canonique/contrat-referentiel-niveau-classe.md`
  (`competences[].connaissances[]`).
- `mvc/entities/connaissance/connaissance.json` (entité préexistante).
- `mvc/services/referentiel_importer.py` (trou d'import à combler).
