# ADR-017 : Référentiels livrés avec le projet et chargement à l'installation

**Statut :** Accepté
**Date :** 2026-07-13

## Contexte

Les **référentiels niveau-classe** (JSON canoniques, `type:
referentiel_niveau_classe`) sont le **socle métier** de l'application.
Ils doivent :

- **vivre dans le projet**, versionnés (traçables, revus, diffés) ;
- être **chargés en base** une fois l'application installée et mise en œuvre par
  l'établissement, une étape de **mise en service**, au même titre que
  `migration:apply`.

Deux mécanismes existants ne conviennent pas seuls :

- Le **jeu de démo** (`mvc/fixtures/`, ADR-078) est **purgeable et rejouable** : il
  modélise une démonstration, pas des données de référence de production.
- L'**import admin** (upload, ADR-009) est **interactif et unitaire** : adapté à
  l'ajout ponctuel par un utilisateur, pas à un chargement reproductible à
  l'installation.

Forge n'expose **pas** de mécanisme de commande applicative custom (pas de
`make:command`, pas de `mvc/commands/`).
Un chargement scripté est donc la voie
réaliste, dans la lignée des outils d'exploitation du projet (`tools/`).

## Décision

1. **Dossier livré** : `data/referentiels/` accueille les JSON canoniques de
   référentiel **versionnés**.
   C'est la **source unique** : le jeu de démo lui-même
   (`mvc/fixtures/referentiel.py`) charge le référentiel **depuis ce dossier**, pas
   depuis une copie.
2. **Script de chargement** : `tools/charger_referentiels.py` parcourt le dossier,
   **valide** chaque JSON (`canonical_validator`) puis l'**importe**
   (`referentiel_importer`, upsert best-effort, ADR-011).
   Il est **idempotent**
   (réimporter remplace) et expose `--check` (validation sans écriture).
3. **Exception assumée à la règle « 100 % Forge »** : ce script s'écarte des
   générateurs Forge.
   Il est cantonné à `tools/` (exploitation), réutilise les
   **services applicatifs** existants (aucune logique dupliquée) et est consigné
   par le présent ADR.

## Conséquences

**Positif**

- Les référentiels sont **versionnés** et **diffables** dans le dépôt.
- Chargement **reproductible** à l'installation (`python tools/charger_referentiels.py`).
- **Source unique** : plus de divergence entre le fichier de démo et le fichier livré.
- Le script réutilise validation + import : **pas de logique nouvelle** hors des services.

**Négatif / limites**

- Un script d'exploitation hors CLI Forge, **exception** documentée ici.
- **Réimport impossible à chaud** si des données applicatives (ex. `evaluation_critere`)
  référencent déjà les objets du référentiel : l'upsert purge les critères et la FK
  externe l'en empêche.
  Sans objet pour l'usage visé (chargement à l'installation, base
  vierge de données pédagogiques) ; à traiter dans `referentiel_importer` si un
  **réimport en cours d'exploitation** devient nécessaire.

## Alternatives écartées

- **Tout en fixtures** : mélange données de démo (purgeables) et données de
  référence (permanentes), sémantiquement incorrect.
- **Import admin uniquement** : manuel et unitaire, inadapté à une mise en service
  reproductible.
- **Commande Forge dédiée** (`forge referentiels:load`) : Forge n'offre pas de
  mécanisme de commande applicative custom à ce jour.
