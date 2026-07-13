# `referentiel_importer` — import d'un référentiel niveau-classe

Persiste un JSON canonique **déjà validé** (voir `canonical_validator`) en base via
`core.database.db` (SQL visible et paramétré, esprit Forge). Logique **pure**,
indépendante de l'UI admin.

Décisions ([ADR-011](../../../docs/adr/011-importeur-referentiel-upsert-best-effort.md)) :

- **Upsert par identifiant** : ré-importer un même `identifiant` **remplace** le
  contenu du référentiel (purge des objets rattachés, dans l'ordre des dépendances,
  puis ré-insertion).
- **Best-effort avec rapport** : chaque élément est inséré isolément ; un échec est
  journalisé dans le rapport et **n'interrompt pas** l'import.

Les identifiants/codes locaux du canonique (`pole.id`, `activite.code`,
`competence.code`, `famille.code`) sont mappés vers les `Id` de la base au fil des
insertions, pour résoudre les FK et les liens `many_to_many` (`activite_competence`,
`cc_competence`).

## API publique

| Symbole | Signature | Rôle |
|---|---|---|
| `import_referentiel` | `(canonical: dict[str, Any]) -> ImportReport` | Importe un canonique validé. Retourne un rapport best-effort. |
| `ImportReport` | dataclass | Compte-rendu de l'import. |

### `ImportReport`

| Champ / propriété | Type | Rôle |
|---|---|---|
| `identifiant` | `str` | identifiant du référentiel importé |
| `referentiel_id` | `int \| None` | `Id` en base du référentiel |
| `remplacement` | `bool` | `True` si l'import a remplacé un référentiel existant |
| `inseres` | `dict[str, int]` | nombre d'objets insérés par catégorie (`competences`, `activites`, …) |
| `erreurs` | `list[str]` | messages d'échec (best-effort) |
| `ok` | `bool` (propriété) | `True` si aucune erreur |

## Usage

```python
from mvc.services.referentiel_importer import import_referentiel

rapport = import_referentiel(canonical)   # canonical déjà validé
total = sum(rapport.inseres.values())
if not rapport.ok:
    ...  # afficher rapport.erreurs
```

## Références

[ADR-011](../../../docs/adr/011-importeur-referentiel-upsert-best-effort.md) ; ticket 11
(chaîne référentiel). Dictionnaire :
`docs/specs/data-dictionary/dictionnaire-referentiel-niveau-classe.md`.
