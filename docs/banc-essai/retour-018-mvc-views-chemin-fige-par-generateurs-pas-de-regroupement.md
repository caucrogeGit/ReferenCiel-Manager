# Retour terrain 018 — `mvc/views/` : chemin de vue figé par les générateurs, séparation cadre/app impossible

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** à remonter.

## Environnement

- `forge-mvc` **`1d564a0c`**, `forge-mvc-entities` **`1d564a0c`**, Python 3.12.
- Application réelle « à taille moyenne » : ~40 entités métier, CRUD généré par
  `forge make:crud`.

## Contexte

Sur une application qui grandit (banc d'essai avec une quarantaine d'entités), le
dossier `mvc/views/` devient difficile à lire : les dossiers du **cadre** (livrés
par le squelette) et ceux **ajoutés par l'application** (une par entité) sont
mélangés à plat, sans séparation.

## F41 — Les générateurs figent `mvc/views/<snake>/` ; aucun regroupement possible

- **Symptôme** — `mvc/views/` compte **43 dossiers à la racine** :
  - **6 du cadre** (squelette Forge) : `components`, `errors`, `home`, `layouts`,
    `pages`, `partials` ;
  - **37 de l'application** : `auth` (`make:auth`) + **36 dossiers d'entités**
    (`eleve`, `professeur`, `parcours`, `qcm`, `evaluation`, …).

  Rien ne distingue visuellement le cadre de l'app : tout est au même niveau.

- **Cause** — `forge make:crud` (`forge_mvc_entities/make_crud.py`) écrit **en dur**
  dans `mvc/views/{snake}/` (`index.html`, `_table.html`, `_pagination.html`,
  `_results.html`, `show.html`, `form.html`). **Aucune option** de dossier ou de
  regroupement (`forge make:crud <Entite> [--dry-run]` — c'est tout). Les helpers
  `BaseController.render("<snake>/…")` résolvent par convention ce **même chemin
  plat**. Le projet compte déjà **154 appels `render("<entité>/…")`**.

- **Conséquence** — regrouper les vues d'application (p. ex. sous
  `mvc/views/entities/<snake>/`) pour dégager la racine est **impossible sans
  diverger du framework** :
  1. il faudrait réécrire les **154 `render(...)`** ;
  2. surtout, **chaque `make:crud` suivant recréerait `mvc/views/<snake>/` à la
     racine** — à déplacer **à la main** à chaque génération.

  C'est exactement le **contournement des générateurs** que la discipline Forge
  proscrit (« une seule façon officielle de faire chaque chose »,
  write-if-new / `skeleton:upgrade`). Le porteur est donc **bloqué** : soit il
  subit une racine `mvc/views/` de plus en plus illisible à mesure que l'app
  grandit, soit il diverge et le paie à chaque `make:crud`.

- **Suggestion** — permettre un **regroupement configurable des vues générées**,
  cohérent d'un bout à l'autre de la chaîne :
  - une **convention/config** (p. ex. `VIEWS_ENTITIES_DIR` ou un flag) que
    respectent **à la fois** `make:crud`, les `make:public-*` **et** la résolution
    de `render(...)` (pour que le contrat reste « une seule façon ») ;
  - cible naturelle : `mvc/views/entities/<snake>/` (ou `mvc/views/app/`), laissant
    la racine aux 6 dossiers du cadre.

  À défaut de l'implémenter, **documenter explicitement que le plat est la
  convention assumée** (et pourquoi), pour clore la question côté porteurs.

## Portée

Constat d'**ergonomie / convention des générateurs**, pas un bug fonctionnel. Il
n'apparaît qu'à l'échelle (peu visible sur un tutoriel à 2-3 entités, gênant sur
une application réelle) — précisément le cas d'usage que le banc d'essai fait
remonter. Non contournable côté projet sans diverger de la règle d'or.
