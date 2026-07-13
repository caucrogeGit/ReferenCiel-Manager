# `password_policy` — politique de mot de passe

Source **unique** de la politique de mot de passe de l'application, adossée au cœur
Forge. Toute création ou réinitialisation passe par ici pour appliquer la même règle
(`core.auth.validate_new_password` : longueur minimale et maximale). Pas de règle
maison divergente : on centralise l'appel au cœur et on traduit son exception en
message affichable.

## API publique

| Symbole | Signature | Rôle |
|---|---|---|
| `valider_mot_de_passe` | `(password: str) -> str \| None` | `None` si le mot de passe respecte la politique du cœur ; sinon un message d'erreur affichable (français, fourni par le cœur). |

## Usage

```python
from mvc.services.password_policy import valider_mot_de_passe

message = valider_mot_de_passe(password)
if message is not None:
    erreurs.append(message)   # ré-afficher le formulaire avec l'erreur
```

Branché à la **création de compte** (`eleve_compte_controller`,
`professeur_compte_controller`) et au **flux de réinitialisation** (le cœur applique
la même validation dans `reset_password_with_token`).

## Références

[ADR-014](../../../docs/adr/014-securite-applicative-reelle.md) (T1 — durcissement
des mots de passe).
