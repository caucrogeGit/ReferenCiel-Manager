# Banc d'essai — retours terrain vers Forge

RéférenCiel Manager sert de **banc d'essai** au framework Forge (ADR-005). Cette
rubrique consigne les **retours terrain** issus de l'usage réel : écarts,
frictions et suggestions, destinés à l'équipe qui maintient Forge.

Chaque retour est **fondé sur des preuves reproductibles** (commande + sortie) et
distingue clairement :

- **Défaut** — le squelette ou l'outil s'écarte d'un standard que Forge s'impose ;
- **Suggestion** — amélioration proposée, en tenant compte des choix de Forge
  (ex. squelette volontairement minimal, ADR-024) ;
- **À vérifier** — hypothèse à confirmer par un test.

On **révèle avant de corriger** (charte Forge, règle B) : on ne contourne pas en
silence, on documente et on remonte.

## Retours

| # | Sujet | Statut |
| --- | --- | --- |
| [001](retour-001-conformite-squelette.md) | Conformité du squelette `forge new` aux standards Forge (typage strict, config qualité, doc, tests) | À remonter |
| [002](retour-002-commande-skeleton-upgrade.md) | Commande de montée de squelette d'un projet existant (`forge skeleton:upgrade`) | À remonter |
| [003](retour-003-forge-migrations-provisioning-manuel.md) | `forge_migrations` absente après provisioning manuel de `db:init` (message trompeur) | À remonter |
| [004](retour-004-code-genere-non-conforme-portes-qualite.md) | Le code généré ne passe pas les portes qualité (pyright strict, ruff) | À remonter |
