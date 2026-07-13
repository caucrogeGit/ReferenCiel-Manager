# ADR-010 — Importeur du référentiel : upsert par identifiant, import best-effort avec rapport

**Statut :** Accepté
**Date :** 2026-07-09

## Contexte

Le ticket 11 (phase ⑤) construit l'**importeur** qui fait entrer un référentiel
niveau-classe en base depuis son **JSON canonique**. Le schéma (ticket 09-10) est en
place : 12 entités + relations, 20 entités au total. L'[ADR-008](008-import-json-canonique-par-upload-admin.md)
a déjà tranché le **mode d'entrée** : upload d'un JSON canonique dans l'**espace admin**,
validé contre le [schéma JSON](../specs/json-canonique/schemas/) puis importé.

Restaient deux arbitrages structurants, tranchés avec le porteur :

1. **Que faire au ré-import** d'un référentiel déjà présent (idempotence / versionnement) ?
2. **Comment gérer la transaction** (un fichier = beaucoup d'INSERT) ?

Le canonique porte des **identifiants locaux** (`id` de pôle, d'activité…) servant à
lier les objets entre eux (`pole_id`, `relations.activites_competences`, etc.) ; ces id
locaux doivent être **mappés** vers les `Id` de la base à l'import.

## Décision

1. **Architecture (conforme ADR-008).** Upload dans l'**espace admin** (opt-in
   `forge-mvc-admin`), gestion du fichier par `forge-mvc-files`. À l'upload : (1)
   **validation** contre le schéma JSON (fichier non conforme refusé) ; (2) **routage**
   par le champ `type` de l'enveloppe ; (3) appel du **service d'import**. Le service
   d'import est un **module applicatif à logique pure** (JSON validé → `core.database.db`),
   **indépendant de l'UI**, donc testable seul et réutilisable (CLI, seed).

2. **Upsert par identifiant.** Ré-importer un référentiel de même `identifiant` **met à
   jour** l'enregistrement existant et ses objets rattachés (stratégie
   *remplacer le contenu* du référentiel), plutôt que d'échouer ou d'accumuler des
   doublons. Simple à l'usage en phase de construction (on itère sur un référentiel).

3. **Import best-effort avec rapport.** L'import **insère ce qui est valide** et
   **journalise** les éléments en échec (référence orpheline, contrainte violée) dans un
   **rapport d'import** rendu à l'admin, plutôt qu'un rollback global. La base peut donc
   rester dans un état **partiel**, explicitement signalé par le rapport.

4. **Mapping des id locaux.** Le service tient une table de correspondance
   `id local (canonique) → Id (base)` par type d'objet, construite au fil des insertions,
   pour résoudre les FK (`pole_id`, `activite_id`…) et les liens m2m
   (`activites_competences`, `cc_competences`).

5. **Provenance.** Les entrées `sources[]` du canonique deviennent des lignes `Source`
   rattachées au référentiel ; le **fichier uploadé est conservé** comme trace.

## Conséquences

- **Positif** : boucle d'itération rapide (ré-upload d'un référentiel corrigé) ; un
  fichier partiellement erroné n'empêche pas d'importer le reste ; le rapport rend les
  erreurs visibles ; le service pur est testable sans l'admin.
- **Tensions assumées (à border quand le versionnement arrivera)** :
  - l'**upsert** ré-écrit un référentiel même `publie` → **assouplit** la règle du
    dictionnaire « un référentiel publié et affecté n'est pas modifié librement ». À
    l'introduction du versionnement (ADR à venir), l'upsert devra être **restreint aux
    statuts `brouillon`**, un `publie` devenant figé.
  - le **best-effort** peut laisser un référentiel **partiellement importé** → tension
    avec l'invariant « références résolues » du contrat. Le **rapport** doit donc être
    **exploitable** (liste précise des rejets) et l'admin doit pouvoir **re-uploader**
    une version corrigée (d'où l'intérêt de l'upsert).
- **Sécurité** : fonction **réservée aux administrateurs** (rôle `admin`, RBAC le moment
  venu). L'opt-in admin et files sont installés par le **porteur** (comme le backend).

## Alternatives écartées

- **Version figée** (un `publie` jamais réécrit ; une nouvelle version = nouvel
  enregistrement `brouillon`) : plus fidèle à la règle de versionnement, mais lourde
  tant que le versionnement lui-même n'est pas implémenté ; reportée avec lui.
- **Transaction tout-ou-rien** (rollback global au moindre échec) : garantit l'invariant
  « références résolues », mais bloque tout import dès une erreur mineure et prive
  l'admin d'un rapport granulaire en phase de mise au point.
