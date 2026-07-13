# Retour terrain 014 : `forge-mvc-admin` exige des champs snake_case, incompatibles avec les colonnes PascalCase de `forge-mvc-entities`

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** à remonter.

## Environnement

- `forge-mvc` **32f552cc**, opt-ins **`forge-mvc-entities`**, **`forge-mvc-admin`**,
  **`forge-mvc-files`** (32f552cc), `forge-mvc-mariadb`, Python 3.12.
- Contexte : exposer `ReferentielNiveauClasse` (entité générée par `forge-mvc-entities`)
  comme **ressource `AdminResource`** pour parcourir les référentiels importés (ticket 11).

## Constat

### F29 : Conventions de nommage de colonnes divergentes entre deux opt-ins Forge

- **Symptôme** : enregistrer une `AdminResource` avec les **vrais noms de colonnes** de
  l'entité échoue :

  ```text
  forge_mvc_admin.exceptions.AdminResourceError:
    list_fields : nom de champ invalide 'Identifiant' (snake_case attendu).
  ```

- **Cause** : deux conventions **incompatibles** :
  - **`forge-mvc-entities`** génère les colonnes des champs scalaires en **PascalCase**
    (`Identifiant`, `Version`, `Statut`, `ImporteLe`, `Code`, `Libelle`…), la PK en `Id`,
    et seules les FK en snake_case (`formation_id`).
  - **`forge-mvc-admin`** impose des noms de champ **snake_case**
    (`_FIELD_RE = ^[a-z][a-z0-9_]*$`, `resources.py`) et les utilise **tels quels comme
    identifiants de colonnes** dans le SQL (`query.py` : `SELECT <list_fields> FROM …`).

- **Conséquence** :
  - Les colonnes **mono-mot** passent **par chance** (MariaDB insensible à la casse :
    `identifiant` résout `Identifiant`), et le driver renvoie la clé telle qu'écrite
    (`row["identifiant"]` fonctionne).
  - Les colonnes **multi-mots** sont **inutilisables** : `importe_le` ≠ `ImporteLe` →
    `Unknown column 'importe_le'`.
    Impossible d'afficher `ImporteLe`, `RefCode`,
    `ConditionsExercice`, `NiveauTaxonomique`, `SourceFichier`, etc.
  - Sur un backend **sensible à la casse** (PostgreSQL selon la configuration), même les
    colonnes mono-mot casseraient.

- **Impact** : une entité `forge-mvc-entities` **ne peut pas** être exposée proprement en
  ressource `forge-mvc-admin`.
  Les deux opt-ins, pensés pour coexister, ne partagent pas
  la même convention de colonnes : l'intégration « entités → back-office » est bancale.

## Proposition

Aligner les deux opt-ins sur **une seule** convention de colonnes, au choix :

1. `forge-mvc-admin` accepte les noms de colonnes **tels que générés** par
   `forge-mvc-entities` (PascalCase + `Id` + FK snake_case) : assouplir `_FIELD_RE` et
   citer les identifiants tels quels ;
2. **ou** `AdminResource` accepte un **mapping `champ → colonne`** (nom logique snake_case
   côté admin, nom réel côté base), découplant l'affichage du schéma ;
3. **ou** `forge-mvc-entities` génère des colonnes **snake_case** (`identifiant`,
   `importe_le`) : cohérent avec les FK déjà en snake_case, et directement exploitable par
   l'admin et par du SQL portable.

L'option 3 est la plus radicale mais la plus cohérente (une seule convention partout) ;
l'option 2 est la plus souple.

## Contournement (projet)

Ressource enregistrée avec les seules colonnes **mono-mot** en snake_case
(`identifiant`, `version`, `statut`), `pk="id"` ; `ImporteLe` **absent** de la liste.
La
**création** via l'admin échoue (colonnes NOT NULL `identifiant`/FK hors `form_fields`),
acceptable ici : les référentiels entrent par l'**import**, pas à la main ; l'édition sert
au **statut** (workflow `brouillon`/`publie`/`archive`), et la suppression est bloquée par
les FK `RESTRICT`.

## Référence

`forge_mvc_admin/resources.py` (`_FIELD_RE`, `_validate_fields`), `forge_mvc_admin/query.py`
(`SELECT <list_fields>`).
Colonnes générées : `mvc/entities/*/*.sql` (PascalCase).
Contournement :
`mvc/routes/admin_routes.py`.
Flux : ticket 11 (parcours des référentiels importés).
