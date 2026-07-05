# RéférenCiel Manager

**Application métier pédagogique persistée**, construite à 100% avec le framework
[Forge](https://forgemvc.com). Elle sert à créer, organiser, affecter, suivre et
évaluer des parcours pédagogiques (spécialité **CIEL**), à partir de référentiels
officiels, de JSON canoniques métier et de starters réutilisables.

> Ce site documente le projet **au fil de sa progression**. Il est généré avec
> mkdocs (voir [ADR-005](adr/005-standard-qualite-documentation-mkdocs-banc-essai.md)).

## Principes de lecture

- **Instructions prioritaires** : [cadrage/instructions.md](cadrage/instructions.md)
  — la référence qui prime sur tout le reste.
- **Cadre métier** : [cadre du projet](cadrage/cadre-projet-referenciel-manager.md).
- Les **décisions structurantes** sont tracées en [ADR](adr/001-adopter-forge.md).

## Les trois niveaux (formule de référence)

```text
JSON canonique          = référence structurée de construction ou d'import
Dictionnaire de données = documentation métier enrichie et canonique
Base de données         = vérité applicative en fonctionnement
```

## Repères du projet

- **Framework** : 100% Forge (structure `mvc/`, CLI `forge`, contrats d'entité,
  opt-ins). Voir [ADR-003](adr/003-architecture-applicative-forge.md).
- **Base de données** : SQLite (proposé). Voir
  [ADR-004](adr/004-backend-base-de-donnees-sqlite.md).
- **Trajectoire** : [roadmap](roadmap/roadmap-referenciel-manager.md) et
  [tickets](tickets/README.md).
- **Sources & JSON canonique** : [spécification](specs/json-canonique/README.md),
  [registre des sources](specs/json-canonique/sources/README.md).

## Rôle particulier

RéférenCiel Manager est aussi un **banc d'essai du framework Forge** : le projet
exerce Forge en profondeur et remonte toute friction rencontrée. Exigence de
qualité alignée sur celle de Forge (ADR-005).
