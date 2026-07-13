# Fixtures — jeu de démonstration (`mvc/fixtures/`)

Jeu de données de **démonstration** de RéférenCiel Manager, piloté 100 % par
`forge-mvc-fixtures` (opt-in `fixtures`). Depuis la bascule (retour terrain 020,
sha framework `38501db6`), ce dossier **fait foi** : il remplace l'ancien
`tools/seed_demo.py`, supprimé.

> Rappel cadrage : les fixtures **construisent un état applicatif** en base (la vérité
> en fonctionnement), elles ne sont pas une sauvegarde. Le référentiel provient du
> JSON canonique via l'importeur — pas d'un `.yml` de démo.

## Ce que le jeu produit

Un scénario **cohérent** de bout en bout, rejouable :

- **3 comptes** authentifiables, un par rôle (voir plus bas) ;
- le **référentiel CIEL 2TNE** importé (15 tables : pôles, activités, compétences,
  critères observables…) depuis
  `docs/specs/json-canonique/examples/json-canonique-ciel-2tne.json` ;
- une **classe 2TNE-A** (année 2025-2026), un **professeur** (Bernard) et des **élèves**
  (dont Dupont Marie) inscrits et affectés ;
- la **chaîne pédagogique** (starter → scénario → progression → évaluations) et un
  **bilan** publié pour Dupont.

## Structure

| Type | Fichiers | Rôle |
|---|---|---|
| **Factories** | `factories/*_factory.py` | Définissent des lignes **déterministes** (pas de Faker aléatoire) ; résolvent les FK par `reference()` (sous-requête `SELECT Id …`). Génèrent les `.sql` via `fixtures:generate`. |
| **SQL** | `annee_scolaire.sql`, `classe.sql`, `eleve.sql`, `professeur.sql`, `inscription_eleve.sql`, `affectation_professeur_classe.sql` | `INSERT` **générés** depuis les factories. Ne pas éditer à la main : régénérer. |
| **Callables** | `comptes.py`, `referentiel.py`, `bloc_b.py`, `bilan.py` | Logique métier que du SQL statique ne peut pas exprimer : hachage des mots de passe, import du référentiel, agrégats. Sous-classent `Fixture` (`tables`, `depends_on`, `load()`). |

**Ordre de chargement** (résolu par `depends_on` + graphe FK) :
`comptes` → `referentiel` → SQL factories (année, prof, élève, classe, inscription,
affectation) → `bloc_b` → `bilan`.

## Commandes

```bash
# (Re)générer un .sql depuis sa factory (affiche ; ne touche pas la base)
forge fixtures:generate annee_scolaire

# Charger le jeu complet en base
forge fixtures:load          # affichage seul (charte §7)
forge fixtures:load --run    # exécute

# Vider les tables ciblées (démontage inverse, FK gérées)
forge fixtures:purge --run

# Cycle rejouable / idempotent (repart d'un état propre)
forge fixtures:purge --run && forge fixtures:load --run
```

Le cycle `purge && load` est **idempotent** : rejouable à volonté, y compris avec le
callable multi-tables `referentiel.py`, sans erreur de clé étrangère ni doublon.

## Comptes de démonstration

| Rôle | Identifiant | Mot de passe | Accès |
|---|---|---|---|
| Admin | `admin@referenciel.local` | `admin1234` | administration, import, socle |
| Professeur | `prof@referenciel.local` | `prof1234` | `/mes-classes`, `/suivi`, `/bilan` |
| Élève | `eleve@referenciel.local` | `eleve1234` | `/mon-parcours` |

> Mots de passe de **démo** uniquement. La politique réelle (ADR-014) et la MFA
> (ADR-015) s'appliquent au fonctionnement normal.

## Référence

Opt-in `forge-mvc-fixtures` (ADR-074/077/078 du framework) ; banc d'essai :
`docs/banc-essai/retour-020-fixtures-references-ordre-et-scenario-coherent.md`
(F43–F52, tous résolus).
