# `canonical_validator` — validation du JSON canonique

**Porte d'entrée** de l'import : un fichier JSON canonique non conforme est **refusé**
avec des messages lisibles **avant tout import** en base. Le schéma vit dans
`docs/specs/json-canonique/schemas/` (ticket 04).

## API publique

| Symbole | Signature | Rôle |
|---|---|---|
| `validate_referentiel_canonical` | `(data: Any) -> list[str]` | Valide `data` contre le schéma du référentiel niveau-classe (JSON Schema Draft 2020-12). Retourne la liste **triée** des messages d'erreur — **vide** si le document est conforme. |

## Usage

```python
from mvc.services.canonical_validator import validate_referentiel_canonical

erreurs = validate_referentiel_canonical(canonical)
if erreurs:
    return _refuser(request, erreurs)   # ne rien importer
# … le document est conforme : on peut importer
```

Appelé par `referentiel_import_controller` juste après lecture du fichier uploadé,
avant `referentiel_importer.import_referentiel`. `jsonschema` n'étant pas typé, il
est confiné derrière un `Any` explicite.

## Références

[ADR-008](../../../docs/adr/008-import-json-canonique-par-upload-admin.md) (import par
upload admin) ; schéma : `docs/specs/json-canonique/schemas/` (ticket 04).
