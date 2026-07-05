# Roadmap — RéférenCiel Manager

Trajectoire courte du projet. Elle fixe l'ordre des grandes étapes ; le détail
d'exécution vit dans les tickets (`docs/tickets/`) et les décisions structurantes
dans les ADR (`docs/adr/`).

## Principe

On avance par **petits incréments testés**. Chaque étape est cadrée par un
ticket à périmètre explicite. La base de données est la vérité applicative en
fonctionnement ; le JSON canonique est la référence de construction et d'import.

## Étapes

### 0. Cadrage (en cours)

- Installer les documents de cadrage et la méthode de travail.
- Acter la décision JSON canonique / persistance (ADR-002).
- Aucun code métier, aucune table, aucune entité.
- Voir le ticket 00.

### 1. Spécifier le JSON canonique

- Préciser la structure des JSON canoniques métier (format, champs, invariants).
- Décrire le mapping sources → JSON canonique.
- Rester documentaire : pas encore de JSON canonique CPRO ou Welcome complet.

### 2. Dictionnaire de données

- Générer/préremplir le dictionnaire à partir des JSON canoniques.
- L'enrichir des règles métier.

### 3. Modélisation Forge des objets métier

- Décrire les entités (contrats JSON Forge), tables et migrations.
- Persister les objets métier en base (vérité applicative).
- S'appuyer sur les générateurs Forge (`make:entity`, `make:crud`, migrations).

### 4. Import et construction

- Construire/importer les objets métier depuis les JSON canoniques.
- Valider la cohérence entre référence (JSON) et état (base).

### 5. Usage applicatif

- Publier, affecter, évaluer et suivre les objets métier persistés.
- Ajouter les fonctionnalités optionnelles via les opt-ins Forge, à la demande.

## Hors trajectoire immédiate

- Réintroduire une V0 fichier ou des `*.yml` de parcours comme base principale.
- Créer un parcours exemple ou les JSON canoniques CPRO / Welcome Réseau complets
  avant que la spécification ne soit posée.
