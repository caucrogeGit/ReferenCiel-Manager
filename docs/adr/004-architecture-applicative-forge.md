# ADR-004 — Architecture applicative sur Forge (mvc/, contrats, migrations, services, repositories)

## Statut

Accepté (2026-07-05).

> Décision validée : **on utilise la structure Forge**. Cet ADR **réinterprète**
> le §18 des instructions (`docs/cadrage/instructions.md`), qui décrit une
> arborescence `app/domain/...` : celle-ci devient une cartographie *logique*, la
> structure *physique* étant le `mvc/` de Forge. C'est le prérequis architectural
> de tout code métier (ticket de tranche verticale Bloc A et suite du tunnel).

## Règle absolue : 100% Forge

RéférenCiel Manager part d'un **squelette généré par Forge** (dépôt
`git@github.com:caucrogeGit/ReferenCiel-Manager.git`). **Tout** le développement
applicatif reste **100% dans le framework Forge** : rien ne se fait en dehors de la
CLI `forge`, des contrats d'entité, des conventions `mvc/` et des opt-ins
`forge-mvc-*`. Aucune couche, dépendance ou pattern externe ne vient doubler ce que
Forge fournit. Toute exception à cette règle est une **décision structurante** qui
exige un nouvel ADR ; elle n'est jamais prise par dérive.

## Date

2026-07-05

## Contexte

RéférenCiel Manager est construite avec Forge. Deux visions d'organisation
coexistent aujourd'hui :

- **La convention Forge** (`CLAUDE.md`, `AGENTS.md`, ADR-001) : structure `mvc/`
  (`mvc/entities/<e>/<e>.json` comme contrat source de vérité, `.sql` généré,
  `mvc/models/`, `mvc/controllers/`, `mvc/views/`, `mvc/routes.py`), accès base
  via `core.database.db` avec paramètres `?`, pas d'ORM, **générateurs** Forge
  (`make:entity`, `make:crud`, `migration:make`), et « une seule façon officielle
  de faire chaque chose ».
- **L'arborescence cible des instructions (§18)** : `app/domain/...`,
  `app/services`, `app/infrastructure/repositories`, `app/infrastructure/migrations`,
  `app/web/{public,auth,student,teacher,admin}` — une organisation en couches de
  type hexagonal.

Ces deux visions sont en tension. Les tickets d'implémentation à venir
(repositories, importeur, chaîne Scenario) présupposent une couche
repository/service et une localisation du code qui ne sont pas tranchées. Or
`CLAUDE.md` range explicitement dans « à éviter » le fait de *contourner les
générateurs en recopiant du code à la main de façon divergente*.

Il faut décider, une fois, où vit le code et par quel chemin il est produit.

## Décision

On adopte une organisation **fidèle à Forge**, où l'arborescence `app/domain/...`
des instructions §18 devient une **cartographie logique**, pas une arborescence
physique concurrente.

1. **Structure physique = Forge `mvc/`.** Pas d'arbre `app/` parallèle qui
   redouble le MVC. Le code applicatif vit dans `mvc/entities`, `mvc/models`,
   `mvc/controllers`, `mvc/views`, `mvc/routes.py`.

2. **Les domaines (§18) sont une carte logique.** `identity`, `school`,
   `sources`, `referential`, `scenario`, `starter`, `learning`, `assessment`,
   `tracking`, `communication` servent à **nommer et regrouper** les entités et à
   organiser `docs/specs/`. Ils ne créent pas de dossiers physiques rivaux de
   `mvc/`.

3. **Entités via les générateurs.** Le contrat JSON `mvc/entities/<e>/<e>.json`
   (`schema_version` 1.0, `name` PascalCase) est la **source de vérité**. Le SQL
   et les migrations sont **générés** (`forge make:entity`, `db:apply`,
   `migration:make|apply`). On n'écrit pas le SQL d'entité à la main.

4. **Logique métier dans les models Forge.** Elle vit dans le fichier model
   **manuel** (jumeau sans `_base`), jamais dans un `*_base.py` régénérable. Ce
   que les instructions appellent « repository » s'exprime comme **méthodes de
   model** sur `core.database.db` (paramètres `?`). On n'introduit pas de couche
   repository écrite à la main tant qu'un besoin réel ne le justifie pas ; si un
   tel besoin apparaît, il fera l'objet d'un ADR dédié.

5. **Services métier = orchestration, pas persistance.** Un service est un module
   qui orchestre plusieurs models pour une règle métier transverse. Il s'appuie
   sur les models et `core.database.db`, ne réimplémente pas l'accès aux données,
   et reste **indépendant du détail des opt-ins** (appelés via des façades).

6. **Espaces web par convention de routes.** `public / auth / student / teacher /
   admin` sont des regroupements de contrôleurs et de routes nommées selon
   ADR-029 (chemin `/<controleur>/<methode>`, nom `<controleur>-<methode>`),
   montées explicitement dans `mvc/routes.py`. Ce n'est pas un sous-framework.

7. **Auth conservée, sécurité fine différée.** L'authentification, le CSRF et les
   sessions Forge restent **en place et actifs**. Ce qui est différé, c'est le
   **RBAC, la MFA, les permissions réelles** et le lien `CompteUtilisateur`
   ↔ `Eleve`. En conséquence, l'entité `Eleve` prévoit dès sa modélisation une
   **relation future** vers le compte (par exemple `user_id` nullable), pour ne
   pas imposer de migration douloureuse plus tard.

## Conséquences

- Une seule façon de faire, alignée sur Forge : générateurs préservés, code
  manuel isolé dans les jumeaux, SQL visible et paramétré.
- Le §18 des instructions est **explicitement réinterprété** comme organisation
  logique. Les instructions priment « sauf décision structurante contraire » ;
  cet ADR est cette décision, et le documente.
- Les tickets d'implémentation s'appuient sur `forge make:entity` /
  `migration:make` plutôt que sur du SQL ou des repositories écrits à la main.
- La porte reste ouverte : si le métier exige plus tard une couche
  repository/service plus formelle, elle sera introduite par un nouvel ADR, pas
  par dérive silencieuse.

## Alternatives écartées

- **Adopter `app/domain/...` en arborescence physique intégrale (hexagonal).**
  Rejetée : elle combat les générateurs Forge, introduit une seconde façon de
  faire et ouvre la dérive que `CLAUDE.md` proscrit. Le bénéfice de découplage ne
  compense pas la perte du cadre et des générateurs qui font la valeur de Forge.
- **Mettre la logique métier dans les contrôleurs.** Rejetée : logique hors des
  models, difficilement testable, contraire à l'esprit Forge.
- **Introduire d'emblée repositories et services formels partout.** Rejetée
  (pour l'instant) : couche spéculative avant besoin avéré ; on reste sur les
  models et on n'ajoute que sur besoin, via ADR.

## Suite

- ADR accepté : il conditionne le ticket de **tranche verticale Bloc A**
  (socle scolaire) et toute la suite du tunnel (`docs/tickets/README.md`).
- Ouvrir un ADR ultérieur pour la **sécurité applicative réelle** (CompteUtilisateur,
  RBAC, MFA, permissions) le moment venu.
