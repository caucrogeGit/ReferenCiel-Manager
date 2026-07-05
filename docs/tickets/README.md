# Tickets — RéférenCiel Manager

Ce dossier organise la conduite du projet par **tickets**. Un ticket est une
unité de travail à périmètre explicite : il déclare ce qu'il fait, ce qu'il ne
fait pas, et ses critères de validation.

Référence de méthode : `docs/cadrage/instructions.md`.
Cadre métier : `docs/cadrage/cadre-projet-referenciel-manager.md`.
Trajectoire : `docs/roadmap/roadmap-referenciel-manager.md`.

## Principe

- **Un ticket = une responsabilité.** On avance par petits incréments testés.
- **Périmètre explicite.** Chaque ticket liste le périmètre autorisé *et* le
  hors-périmètre.
- **Prémortem.** Avant de clore, on imagine comment le ticket aurait pu échouer
  malgré une apparence correcte, et on corrige.
- **Validation.** Un ticket n'est terminé que si ses critères sont tous vérifiés,
  et que `git status --short` ne montre que les fichiers attendus.

## Anatomie d'un ticket

Un ticket destiné à Claude Code ou Codex décrit au minimum :

1. **Objectif** ;
2. **Périmètre autorisé** ;
3. **Hors périmètre** ;
4. **Boucle de travail obligatoire** ;
5. **Test prémortem** ;
6. **Critères de validation**.

## Deux blocs métier à ne pas mélanger

Le tunnel distingue deux blocs (voir instructions §16, cadre §8) :

- **Bloc A — structure scolaire** : qui est dans quelle classe, sur quelle année,
  à quel niveau. Objets : `AnneeScolaire`, `NiveauClasse`, `Classe`, `Groupe`,
  `Eleve`, `Professeur`, `InscriptionEleve`, `AffectationProfesseurClasse`.
  **Ce bloc arrive tôt** (tranche verticale).
- **Bloc B — exécution pédagogique élève** : ce que fait l'élève dans un parcours
  affecté. Objets : `AffectationParcours`, `ProgressionEleve`,
  `ProgressionPalier`, `TentativeQCM`, `ReponseQCM`, `ChecklistEleve`,
  `DepotEleve`, `ValidationProfesseur`, `EvaluationActivite`, `EvaluationCritere`,
  `BilanEleve`. **Ce bloc arrive après les parcours** : on ne suit pas une
  progression sans parcours affecté.

## Garde-fous permanents

Valables pour tous les tickets, sauf décision structurante contraire (ADR) :

- La base de données est la vérité applicative en fonctionnement ; le JSON
  canonique est une référence de construction/import ; le dictionnaire de données
  est la documentation métier enrichie.
- **Pas de V0 fichier** : aucun `path.yml`, `palier.yml`, `qcm.yml` ou
  `checklist.yml` comme base principale.
- **Ne pas contourner les générateurs Forge** : entités via `forge make:entity`
  (contrat JSON = source de vérité), migrations via `forge migration:make`. Pas
  de SQL ni de repositories écrits à la main si Forge fournit le chemin attendu
  (voir ADR-003).
- **Différer RBAC/MFA ≠ désactiver l'auth Forge** : l'authentification, le CSRF
  et les sessions restent actifs. On diffère seulement les permissions réelles,
  la MFA et le lien `CompteUtilisateur` ↔ `Eleve`.
- **Prévoir la couture compte** : `Eleve` porte dès son dictionnaire une relation
  future vers `CompteUtilisateur` (par exemple `user_id` nullable).
- **Emplacement des schémas** : le schéma du JSON canonique vit dans
  `docs/specs/json-canonique/schemas/`, **pas** dans les `schemas/` de Forge.
- On ne supprime pas le briefing Forge de `AGENTS.md` / `CLAUDE.md`.
- On n'élargit pas le périmètre d'un ticket sans validation.

## Tunnel de travail (ordre des tickets)

> L'ADR-003 (architecture Forge) est le **prérequis architectural du code métier**.
> Il est **accepté** : on utilise la structure Forge (`mvc/`, contrats d'entité,
> générateurs). Le code métier commence à la tranche verticale Bloc A (ticket 07).

| # | Ticket | Bloc | Statut |
| --- | --- | --- | --- |
| 00 | Installer le cadre projet dans le squelette Forge | — | Terminé |
| 01 | Installer l'arborescence des sources et la traçabilité (registre + trace de provenance ; référentiels officiels Bac Pro CIEL, Vademecum TNE 2ⁿᵈᵉ, BTS CIEL enregistrés) | Sources | En cours |
| 02 | Définir le contrat du JSON canonique référentiel niveau-classe — **extraction à deux couches** : famille TNE (CC1–CC9) + cible CIEL (C01–C11) + mapping | Sources | À faire |
| 03 | Produire le JSON canonique CIEL 2TNE minimal | Sources | À faire |
| 04 | Définir le schéma JSON du référentiel niveau-classe (`docs/specs/json-canonique/schemas/`) | Sources | À faire |
| 05 | Dictionnaire de données du socle scolaire (AnneeScolaire, NiveauClasse, Classe, Groupe, Eleve `user_id?`, Professeur, InscriptionEleve, AffectationProfesseurClasse) | A | À faire |
| 06 | **ADR-003 — Architecture Forge (mvc/ vs app/, contrats, migrations, services, repositories)** — prérequis du code | — | Terminé (Accepté) |
| 07 | Tranche verticale Bloc A (walking skeleton) : contrats d'entité → migrations Forge → accès données → vue professeur minimale listant classes/élèves (derrière l'auth Forge, sans RBAC/MFA) | A | À faire |
| 08 | Dictionnaire de données Référentiel (PôleActivité, ActivitéProfessionnelle, TâcheProfessionnelle, RésultatAttendu, Compétence, CritèreObservable, IndicateurRéussite) | Référentiel | À faire |
| 09 | Modèle relationnel + contrats d'entité référentiel | Référentiel | À faire |
| 10 | Migrations référentiel (via `forge`) | Référentiel | À faire |
| 11 | Importeur JSON canonique → base référentielle | Référentiel | À faire |
| 12 | Dictionnaire de données `Scenario` | Scénario | À faire |
| 13 | Chaîne `Scenario` (contrat, migration, service, interface prof minimale, tests de persistance) | Scénario | À faire |
| 14 | `StarterWelcome` (+ `VersionStarter`) | Starter | À faire |
| 15 | `Parcours` + `VersionParcours` | Parcours | À faire |
| 16 | `Palier` (découpage du parcours) — ticket explicite | Parcours | À faire |
| 17 | `AffectationParcours` à une classe ou à des élèves | B | À faire |
| 18 | `ProgressionEleve` (+ `ProgressionPalier`) | B | À faire |
| 19 | QCM / checklist / activité / dépôt élève (définition + tentative/réponse/dépôt) | B | À faire |
| 20 | Suivi professeur par classe | B | À faire |
| 21 | Évaluation par critères et bilan | B | À faire |

### Après le tunnel (sécurité applicative réelle)

Différé volontairement, à ouvrir par un ADR dédié le moment venu :
`CompteUtilisateur`, connexion applicative, RBAC, MFA, permissions réelles, lien
`CompteUtilisateur` ↔ `Eleve`.
