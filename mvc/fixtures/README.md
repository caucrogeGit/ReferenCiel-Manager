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

- **6 comptes** authentifiables : 1 admin, 3 professeurs, 2 élèves (voir plus bas) ;
- le **référentiel CIEL 2TNE** importé (pôles, activités, compétences, critères,
  indicateurs…) depuis `data/referentiels/2tne_ciel.json` ;
- **3 classes** (2TNE-A/B/C, année 2025-2026), **3 professeurs** (Bernard, Moreau,
  Petit) affectés aux classes (avec recouvrement), **9 élèves** répartis 3 par classe ;
- des **scénarios adossés au référentiel** (Installer une liaison Ethernet, Configurer
  un poste client, Mettre en service un commutateur) **et hors référentiel**
  (co-intervention, PSE), chacun **appairé à sa séquence** (ADR-029) ;
- pour la séquence Ethernet : des **séances** qui **observent** des compétences/critères
  (avec indicateurs), des **progressions** de la classe 2TNE-A à **statuts variés**
  (file « à évaluer »), et une **observation évaluée** + un **bilan publié** pour
  Dupont Marie (lisible dans son espace élève).

## Structure

| Type | Fichiers | Rôle |
|---|---|---|
| **Factories** | `factories/*_factory.py` | Définissent des lignes **déterministes** (pas de Faker aléatoire) ; résolvent les FK par `reference()` (sous-requête `SELECT Id …`). Génèrent les `.sql` via `fixtures:generate`. |
| **SQL** | `annee_scolaire.sql`, `classe.sql`, `professeur.sql`, `eleve.sql` | `INSERT` du socle, alignés sur leurs factories. Relire avant de charger. |
| **Callables** | `comptes.py`, `referentiel.py`, `pedagogie.py`, `bilan.py` | Logique métier que du SQL statique ne peut pas exprimer : hachage des mots de passe, import du référentiel, appairage scénario↔séquence (ADR-029), agrégats. Sous-classent `Fixture` (`tables`, `depends_on`, `load()`). |

**Ordre de chargement** (résolu par `depends_on` + graphe FK) :
`comptes` → `referentiel` → SQL du socle (année, prof, classe, élève) →
`pedagogie` (scénarios, séquences, séances, progressions) → `bilan`.

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

| Rôle | Identifiant | Mot de passe | Rattachement |
|---|---|---|---|
| Admin | `admin@referenciel.local` | `admin1234` | administration, import, socle |
| Professeur | `prof@referenciel.local` | `prof1234` | Bernard (2TNE-A, 2TNE-B) |
| Professeur | `prof2@referenciel.local` | `prof1234` | Moreau (2TNE-B, 2TNE-C) |
| Professeur | `prof3@referenciel.local` | `prof1234` | Petit (2TNE-A, 2TNE-C) |
| Élève | `eleve@referenciel.local` | `eleve1234` | Dupont Marie (2TNE-A) — a un bilan publié |
| Élève | `eleve2@referenciel.local` | `eleve1234` | Garcia Hugo (2TNE-B) |

> Mots de passe de **démo** uniquement. La politique réelle (ADR-014) et la MFA
> (ADR-015) s'appliquent au fonctionnement normal.

## Référence

Opt-in `forge-mvc-fixtures` (ADR-074/077/078 du framework) ; banc d'essai :
`docs/banc-essai/retour-020-fixtures-references-ordre-et-scenario-coherent.md`
(F43–F52, tous résolus).
