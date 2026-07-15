# Retour terrain 022 : opt-ins média — `core.http.bearer` absent du Core, et audio sans BDD

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** **Ouvert** (2026-07-15).

## Environnement

- `forge-mvc` (Core) **1.0.0rc2**, `forge-mvc-audio` **1.0.0rc2**,
  `forge-mvc-video` **1.0.0rc2**, Python 3.12, backend MariaDB.
- Contexte : câblage des opt-ins média pour un « dossier technique » de palier
  (ressources markdown/vidéo/audio/lien), via `forge opt-in:enable video/audio`.
- Core et opt-ins ne sont pas sur l'index pip public : ils proviennent de la
  distribution Forge.

## Constats

### F57 : les opt-ins `video`/`audio` rc2 importent `core.http.bearer`, absent du Core rc2 (Défaut)

- **Symptôme** : après `forge opt-in:enable video --apply` puis
  `audio --apply` (inscription OK, couches `optins/video|audio/` générées),
  **toute** charge de l'application échoue :

  ```
  $ forge migration:status
  ...
  File ".../forge_mvc_audio/http.py", line 27, in <module>
      from core.http.bearer import is_bearer_authorized
  ModuleNotFoundError: No module named 'core.http.bearer'
  ```

  Comme `optins/registry.py` importe `register_audio`/`register_video` au
  démarrage, l'app ne charge plus : `forge run`, `pytest`, `migration:*` cassés.

- **Cause** : les deux modules HTTP dépendent d'un symbole absent du Core installé.

  ```
  $ grep -n "core.http.bearer" .venv/.../forge_mvc_audio/http.py
  27:from core.http.bearer import is_bearer_authorized
  $ grep -n "core.http.bearer" .venv/.../forge_mvc_video/http.py
  28:from core.http.bearer import is_bearer_authorized
  $ ls .venv/.../core/http/ | grep -i bearer   # → rien
  ```

  Les opt-ins média rc2 attendent une **auth par jeton bearer**
  (`core.http.bearer.is_bearer_authorized`, pour protéger les endpoints de
  lecture/streaming) que **le build rc2 du Core n'expose pas**. La contrainte
  `Requires-Dist: forge-mvc<2,>=1.0.0rc2` est pourtant satisfaite : le
  **désalignement est interne à la borne rc2** (les opt-ins sont en avance sur
  le Core publié sous le même numéro).

- **Impact** : opt-ins média inutilisables en l'état ; l'activation laisse
  l'application non démarrable jusqu'au `opt-in:disable`.

- **Contournement appliqué** : `forge opt-in:disable video/audio --apply` a
  restauré l'app (registre revenu à l'identique, 86 tests verts). Les packages
  restent installés mais non câblés.

- **Attendu** : soit le Core rc2 **expose `core.http.bearer`** (module d'auth
  bearer, comme l'annoncent les docstrings des opt-ins « l'auth vit dans ce
  module, jamais dans Forge Core » — mais l'import pointe bien vers `core.*`),
  soit les opt-ins déclarent une **borne de version précise** vers le Core qui
  le fournit (pour un échec `pip`/`opt-in:enable` explicite plutôt qu'un
  `ModuleNotFoundError` au runtime).

### F58 : `forge-mvc-audio` est sans BDD, souhait d'un modèle à état comme `forge-mvc-video` (Suggestion)

- **Constat** : `forge-mvc-audio` est **volontairement sans état** (docstring :
  « aucune base de données », fichiers retrouvés par `uuid` sur disque), là où
  `forge-mvc-video` est **à état** (migration `20260601120000_create_videos.sql`,
  `storage/repository.py`, table `videos`).

- **Suggestion** : aligner l'audio sur la vidéo, c.-à-d. lui donner un **modèle
  persisté** (table type `audios` + repository), pour que l'application traite
  audio et vidéo **de façon uniforme** (une même référence d'entité côté métier,
  au lieu d'un uuid disque d'un côté et d'un id de table de l'autre).

- **Bénéfice côté application** : notre entité `RessourceDossier` (ressource
  d'un dossier technique) peut alors référencer **audio et vidéo par le même
  mécanisme**, sans cas particulier. C'est le sens dans lequel nous modélisons
  dès maintenant (ADR-022), en anticipant ce passage de l'audio en BDD.

## Synthèse

- **F57 (Défaut, bloquant)** : opt-ins média rc2 dépendent de
  `core.http.bearer`, absent du Core rc2 → activation impossible sans casser
  l'app. À corriger côté Forge (livrer le module au Core, ou verrouiller la
  version).
- **F58 (Suggestion)** : donner à `forge-mvc-audio` un modèle persisté comme
  `forge-mvc-video`, pour un traitement audio/vidéo uniforme.

## Référence

- Côté application : la modélisation du dossier technique et de
  `RessourceDossier` est actée dans
  [ADR-022](../adr/022-parcours-objet-canonique-aplatissement.md) ; le câblage
  effectif des opt-ins média est **différé** jusqu'à la résolution de F57.
