# Dictionnaire de données : Socle scolaire (Bloc A)

Documentation métier enrichie du **Bloc A** (structure scolaire) : qui est dans
quelle classe, sur quelle année, à quel niveau.
Objets **persistés en base**.

> Mêmes principes que le [dictionnaire référentiel](dictionnaire-referentiel-niveau-classe.md#principes)
> (nommage PascalCase/snake_case, types et relations Forge, base = vérité,
> provenance).
> Ce bloc arrive **tôt** (tranche verticale, ticket 07).

## Distinction importante : élève ≠ compte utilisateur

`Eleve` et `Professeur` portent dès maintenant une **couture** vers un futur compte
applicatif (`user_id` **nullable**), pour ne pas imposer de migration douloureuse
quand l'authentification réelle arrivera (RBAC/MFA différés, voir mémoire projet).
On gère l'élève **en base sans encore gérer toute la sécurité**.

## Entités

### AnneeScolaire

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `libelle` | string | oui | ex. `2025-2026`, **unique** |
| `date_debut` | date | non | début d'année |
| `date_fin` | date | non | fin d'année |
| `active` | boolean | oui | une seule année active à la fois (règle applicative) |

### NiveauClasse

Entité **partagée** avec le domaine référentiel (mêmes `code`/`intitule`, ex.
`2TNE`). Définie une fois, référencée par `Classe` et `ReferentielNiveauClasse`.

### Classe

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `annee_scolaire_id` | many_to_one → AnneeScolaire | oui | année |
| `niveau_classe_id` | many_to_one → NiveauClasse | oui | niveau |
| `code` | string | oui | ex. `2TNE-A`, unique dans l'année |
| `libelle` | string | non | libellé lisible |

### Groupe

Sous-ensemble d'une classe (TP, îlots…).

| Champ | Type | Oblig. | Description |
|---|---|:--:|---|
| `classe_id` | many_to_one → Classe | oui | classe parente |
| `nom` | string | oui | ex. `Groupe 1` |

Relation : `eleves` (many_to_many → Eleve, pivot `groupe_eleve`).

### Eleve

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `nom` | string | oui | |
| `prenom` | string | oui | |
| `identifiant` | slug | non | identifiant élève (unique si présent) |
| `date_naissance` | date | non | |
| `user_id` | many_to_one → CompteUtilisateur | **non (nullable)** | **couture** vers le compte applicatif (auth différée) |

### Professeur

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `nom` | string | oui | |
| `prenom` | string | oui | |
| `user_id` | many_to_one → CompteUtilisateur | **non (nullable)** | couture vers le compte applicatif |

### InscriptionEleve

Un élève inscrit dans une classe pour une année.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `eleve_id` | many_to_one → Eleve | oui | élève |
| `classe_id` | many_to_one → Classe | oui | classe |
| `annee_scolaire_id` | many_to_one → AnneeScolaire | oui | année |
| `date_inscription` | date | non | |

Règle : `(eleve_id, classe_id, annee_scolaire_id)` **unique**.

### AffectationProfesseurClasse

Un professeur affecté à une classe pour une année.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `professeur_id` | many_to_one → Professeur | oui | professeur |
| `classe_id` | many_to_one → Classe | oui | classe |
| `annee_scolaire_id` | many_to_one → AnneeScolaire | oui | année |
| `role` | string | non | ex. professeur principal |

Règle : `(professeur_id, classe_id, annee_scolaire_id)` **unique**.

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| AnneeScolaire → Classe | many_to_one (inverse) | 1 année, n classes |
| NiveauClasse → Classe | many_to_one (inverse) | 1 niveau, n classes |
| Classe → Groupe | many_to_one (inverse) | 1 classe, n groupes |
| **Groupe ↔ Eleve** | many_to_many (pivot `groupe_eleve`) | n ↔ n |
| Eleve/Classe/Année → InscriptionEleve | many_to_one | pivot enrichi (date) |
| Professeur/Classe/Année → AffectationProfesseurClasse | many_to_one | pivot enrichi (rôle) |
| Eleve/Professeur → CompteUtilisateur | many_to_one **nullable** | couture auth (différée) |

## Règles transverses

- **Une seule `AnneeScolaire` active** (règle applicative).
- **Unicité** des inscriptions et affectations (voir ci-dessus).
- **Couture compte** : `user_id` nullable sur `Eleve` et `Professeur` ; le lien réel
  vers `CompteUtilisateur` (auth/RBAC/MFA) est un domaine différé (ADR ultérieur).
- **Sécurité applicative** (cloisonnement élève/professeur, RBAC) : hors de ce
  dictionnaire, traitée à l'arrivée de l'authentification réelle.

## Portée

Couvre le **socle scolaire (Bloc A)**.
L'**exécution** (affectation de séquences,
progression, évaluations ; Bloc B) et l'**authentification** relèvent de tickets
ultérieurs.
Les contrats d'entité Forge et migrations en découlent (tickets de
programmation, à faire ensemble).
