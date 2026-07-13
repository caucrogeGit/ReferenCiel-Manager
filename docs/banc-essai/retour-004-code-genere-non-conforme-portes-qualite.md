# Retour terrain 004 : Le code généré ne passe pas les portes qualité (pyright strict, ruff)

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** ✅ Résolu dans forge-mvc f38d5159 (2026-07-08), vérifié sur le banc d'essai.

## Environnement

- `forge-mvc` **e3197866**, Python **3.12**.
- Portes qualité du projet, alignées sur Forge (ADR-036 typage strict ; ruff) :
  `pyright` (strict par fichier) et `ruff` (`select = ["E","F"]`).

## Contexte

Génération de la première entité via `forge make:entity AnneeScolaire` puis
`forge sync:entity AnneeScolaire`.
Dès qu'on inclut `mvc/entities/` dans le
périmètre qualité, **le code généré fait échouer deux portes**, alors que Forge
**prône** précisément ces portes.

## Constats

### F10a : `<entite>_base.py` : `from_dict` non strict-clean (pyright)

```python
@classmethod
def from_dict(cls, data: dict) -> "AnneeScolaireBase":
    return cls(
        ...
        active=data.get("active"),   # dict non typé -> Unknown | None
        ...
    )
```

`data: dict` est un dict **non paramétré** → `data.get("active")` vaut
`Unknown | None`, passé au paramètre `active: bool` (non nullable) de `__init__`.

```
annee_scolaire_base.py:142:20 - error: Impossible d'affecter l'argument de type
« Unknown | None » au paramètre « active » de type « bool »  (reportArgumentType)
```

Latent aussi pour les autres champs non optionnels. **Cause** : `data` devrait être
typé `dict[str, object]` (ou un `TypedDict`), et les valeurs *coercées/castées* vers
le type du champ avant l'appel à `__init__`.

### F10b : `<entite>/__init__.py` : ré-export non conforme (ruff F401)

```python
from .annee_scolaire import AnneeScolaire   # ruff : F401 "imported but unused"
```

Le `__init__.py` généré ré-exporte l'API sans la forme idiomatique
(`import X as X` ou `__all__`), d'où un **faux positif** `F401` sous ruff.

## Impact

Un projet qui se tient à la **barre qualité de Forge** (typage strict, ruff) obtient
des portes **rouges** à cause du **code généré par le framework**, dès la première
entité.
Contournements appliqués localement (documentés dans `pyproject.toml`) :

- **pyright** : exclusion des `**/*_base.py` (régénérables, « pas notre code »,
  ADR-008) ;
- **ruff** : `per-file-ignores` `F401` sur les `**/__init__.py`.

Ces contournements sont acceptables (ce n'est pas notre code), mais ils **masquent**
un écart que le framework gagnerait à combler à la source.

## Proposition

Que les générateurs émettent du code **vert d'emblée** sous pyright strict + ruff :

1. **`from_dict`** : typer `data: dict[str, object]` (ou un `TypedDict` par entité)
   et *caster/coercer* explicitement chaque valeur vers le type du champ.
2. **`__init__.py`** : ré-export explicite (`from .x import X as X`) ou `__all__`.

Bénéfice : un projet peut inclure le code généré dans ses portes qualité **sans
exception**, cohérent avec l'exigence de qualité que Forge s'impose (ADR-036).

## Référence

Contournements : `pyproject.toml` (`[tool.pyright] exclude`,
`[tool.ruff.lint.per-file-ignores]`).
Entité de test : `AnneeScolaire` (ticket 07,
commit `ed5b673`).
