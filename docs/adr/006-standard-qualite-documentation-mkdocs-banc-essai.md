# ADR-006 — Standard de qualité, documentation mkdocs et rôle de banc d'essai

## Statut

Accepté (2026-07-05).

> Trois exigences énoncées par le porteur du projet, actées ensemble car elles
> définissent **comment** RéférenCiel Manager est conduit : au niveau de Forge.

## Date

2026-07-05

## Contexte

RéférenCiel Manager est développé à 100% avec Forge (ADR-004) et sa base est la
vérité applicative (ADR-003). Au-delà de ces choix, le projet doit être **tenu au
même standard que le framework Forge lui-même** : Forge est explicite, testable,
documenté (mkdocs), gouverné par des ADR et une charte de principes non
négociables. Trois exigences en découlent, formulées par le porteur du projet :

1. **Même niveau de qualité que Forge.**
2. **Documentation mkdocs qui suit la progression du projet.**
3. **RéférenCiel Manager sert de banc d'essai pour valider Forge.**

## Décision

### 1. Exigence de qualité alignée sur Forge

Le projet applique les mêmes disciplines que Forge :

- **Décision structurante = un ADR** (format Forge), dans `docs/adr/`.
- **Petits tickets** à périmètre explicite, avec prémortem et critères
  (`docs/tickets/`).
- **Tests** avant d'élargir ; validation avant de livrer :
  `python -m pytest`, `forge doctor`, `forge project:check`, `ruff check .`,
  `mkdocs build --strict`.
- Respect des **principes de la charte Forge** : explicite plutôt que magique,
  SQL visible, préserver le code utilisateur, noyau minimal + opt-ins, une seule
  façon officielle de faire chaque chose, sécurisé par défaut.

### 2. Documentation mkdocs vivante

La documentation du projet est publiée avec **mkdocs** (thème *Material*), chaîne
alignée sur celle de Forge (`requirements-docs.txt` : `mkdocs`, `mkdocs-material`,
`pymdown-extensions`, `mkdocs-glightbox`).

- `mkdocs.yml` à la racine, `docs_dir: docs`, sortie `site/` (ignorée par git).
- La **navigation reflète l'état du projet** (cadrage, ADR, roadmap, tickets,
  spécifications) et **évolue ticket après ticket** : toute page ajoutée sous
  `docs/` est intégrée à la `nav`.
- **`mkdocs build --strict` doit passer** (fait partie de la validation avant de
  livrer) : pas de page orpheline, pas de lien cassé.

### 3. Rôle de banc d'essai du framework

RéférenCiel Manager **exerce Forge en conditions réelles** et sert à le valider.
En conséquence :

- On **privilégie les chemins Forge natifs** (générateurs, opt-ins, conventions),
  même quand un raccourci existerait — l'objectif est aussi de tester le framework.
- On **révèle** (charte Forge, règle B) toute **friction, limite ou incohérence**
  rencontrée dans Forge, au lieu de la contourner silencieusement ; ces retours
  peuvent alimenter le dépôt Forge.
- On note ces observations là où elles éclairent le travail (ADR, tickets, ou une
  rubrique dédiée si le volume le justifie).

## Conséquences

- Le site de doc est un livrable **continu** : il grandit avec le projet et se
  vérifie automatiquement (`--strict`).
- La barre de qualité est explicite et partagée : un écart devient visible.
- Le double objectif (livrer l'app **et** valider Forge) est assumé : il peut
  ralentir certains choix (préférer le natif, documenter une friction) mais c'est
  le prix du rôle de banc d'essai.

## Alternatives écartées

- **Documentation ad hoc** (README épars, sans site) : rejetée — sous le standard
  Forge, non navigable, non vérifiable.
- **Contourner une limite de Forge en silence** pour aller plus vite : rejetée —
  contraire au rôle de banc d'essai et à la charte (révéler avant de corriger).

## Suite

- Installer la chaîne doc (`pip install -r requirements-docs.txt`) et intégrer
  `mkdocs build --strict` à la checklist de validation.
- Ajouter chaque nouvelle page à la `nav` au fil des tickets.
