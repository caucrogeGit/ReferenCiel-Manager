# Retour terrain 021 : session orpheline (`AuthMiddleware`), split SQL en commentaire, cycle serveur

**Statut :** ✅ **traité côté Forge et adopté** (montée `0aef2f01` / `1.0.0rc2`).
**F53** (ADR-079, split SQL conscient des commentaires), **F54/F55** (ADR-080,
`user_loader` : sujet authentifié autoritaire), **F56** (ADR-081, horodatages en
autorité Python).
Adoption applicative : REFCIEL-ADOPT-021-001 (contournements
retirés).
Seule la **piste** `forge run`/port reste non traitée (cause externe).

## Environnement

- Framework : `forge-mvc` + opt-ins (rbac, mfa, sessions-db, mariadb, entities,
  fixtures…), sha `38501db6`.
- Application : RéférenCiel Manager (banc d'essai). Backend MariaDB.
- Contexte : session de test manuel de l'application (navigation par rôle,
  ajout d'une relation d'entité, redémarrages du serveur).

## Constats

### F53 : `migration:apply` : le découpeur SQL coupe sur un `;` présent dans un commentaire `--`

- **Symptôme** : une migration dont un **commentaire** `--` contient un `;` échoue
  à l'application :
  `You have an error in your SQL syntax … near '<texte situé après le ;>'`.
  Exemple réel (commentaire d'intention) :

  ```sql
  -- un eleve a 1 et 1 seul niveau_classe ; un niveau_classe a 0..n eleves
  ALTER TABLE eleve ADD COLUMN niveau_classe_id BIGINT UNSIGNED NULL;
  ```

  Le `;` du commentaire est traité comme un **séparateur d'instruction** : la
  seconde moitié du commentaire (« un niveau_classe a 0..n eleves … ») devient une
  « instruction » envoyée telle quelle au serveur → erreur de syntaxe.

- **Cause** : le découpage des instructions d'une migration se fait sur `;` **sans
  ignorer les commentaires** (`-- …` en fin de ligne comme en ligne pleine).

- **Correctif proposé** : retirer/ignorer les commentaires `--` (et `/* … */`)
  avant le split sur `;`, ou utiliser un découpeur conscient des commentaires et
  des littéraux. **Même famille que le retour-012** (split SQL cassé par une
  apostrophe) : le découpeur naïf sur `;` mérite d'être fiabilisé une fois pour
  toutes (commentaires **et** chaînes).

- **Contournement appliqué** : ne mettre aucun `;` dans les commentaires de migration.
- **✅ Corrigé Forge** (ADR-079, commit `0aef2f01`, `1.0.0rc2`) : le découpeur
  `split_sql_statements` est désormais **conscient des commentaires** (`--`, `/* … */`).
  Vérifié dans ce projet : un commentaire contenant à la fois un `;` **et** une
  apostrophe (le cas `retour-012` / F27) ne casse plus le découpage. **La règle
  interne « pas de `;` ni de `'` dans les commentaires de migration » est levée**
  (adoption REFCIEL-ADOPT-021-001, étape 1).

### F54 : `AuthMiddleware` : présence d'un `user_id` ≠ existence du compte (session orpheline)

- **Symptôme** : après un rechargement de fixtures qui **réassigne les `id`** des
  comptes (ou après suppression d'un compte encore connecté), la session pointe
  vers un `user_id` qui **n'existe plus**. L'application reste pourtant « connectée »
  (menu profil affiché, pas de redirection) au lieu de renvoyer au login.

- **Cause** : `AuthMiddleware.check` (`core/security/middleware.py`) délègue à
  `core.auth.session.is_authenticated`, qui ne teste que la **présence** d'un
  identifiant en session :

  ```python
  def is_authenticated(request):
      return get_authenticated_user_id(request) is not None  # existence NON vérifiée
  ```

  Une session dont le sujet a disparu passe donc le middleware.

- **Correctif proposé** : permettre à `AuthMiddleware` de valider l'**existence**
  du sujet : p. ex. un `user_loader` optionnel (comme `current_user`/le provider
  RBAC en disposent déjà) ; si le sujet est introuvable, **fermer la session**
  (`logout_user` + purge du cookie) et rediriger vers `login_url`. La simple
  redirection sans fermeture reboucle sur les entrées publiques
  (`/` → `/login` → toujours « authentifié » → `/`).

- **Contournement appliqué** : middleware applicatif `SessionIntegrityMiddleware`
  (vérifie l'existence en base, ferme la session, redirige) placé avant
  `AuthMiddleware`, plus un rejeu du contrôle dans le contrôleur de la racine `/`
  (publique, hors chaîne de middlewares).
- **✅ Corrigé Forge** (ADR-080, `0aef2f01`) : `AuthMiddleware` accepte un
  `user_loader` et valide l'existence **et** l'activité du sujet, fermant la
  session orpheline (logout + purge cookie). Contournement **retiré** :
  `mvc/middlewares/session_integrity.py` supprimé ; la home publique résout le
  sujet via `current_user()` natif (REFCIEL-ADOPT-021-001, étape 2).

### F55 : Deux définitions de `is_authenticated` dans le contexte de rendu (à confirmer)

- **Observation** : le contexte des templates reçoit `is_authenticated` de **deux**
  sources potentielles :
  - `BaseController.render` (`core/mvc/controller/base_controller.py`) :
    `is_authenticated = _is_authenticated(request)` (basé sur la **session**) ;
  - le provider Jinja RBAC (`forge_mvc_rbac/jinja.py`) :
    `is_authenticated = current_user is not None` (basé sur le **loader**).

  Pour une session **orpheline** (F54), ces deux valeurs **divergent** (session : vrai,
  loader : faux). Selon l'ordre de fusion du contexte, la vue peut afficher un état
  incohérent (menu authentifié **ou** bouton de connexion).

- **Piste** : converger vers **une** définition (idéalement adossée au loader, donc
  à l'existence réelle du sujet), pour que `is_authenticated`, `can(...)` et
  `current_user` soient toujours cohérents. À confirmer par un test dédié.
- **✅ Corrigé Forge** (ADR-080, `0aef2f01`) : `make_contract_jinja_context` accepte
  un `user_loader` ; le provider Jinja adossé au loader rend `is_authenticated` /
  `current_user` **autoritaires** (une orpheline est vue non authentifiée, plus de
  menu fantôme). Câblé dans `mvc/routes/__init__.py`, enregistré après l'opt-in
  pour écraser le provider « table » auto-inscrit (REFCIEL-ADOPT-021-001, étape 3).

### F56 : `make:crud` expose les horodatages et `timestamps: true` ne pose pas de défaut SQL

- **Symptôme** : pour une entité avec `options.timestamps: true`, le CRUD généré par
  `make:crud` **expose `created_at` / `updated_at`** dans le formulaire
  (`DateTimeField(required=True)` + champs `datetime-local` dans `form.html`) :
  l'utilisateur devrait **saisir à la main** les horodatages, ce qui n'a pas de sens.
  En parallèle, les colonnes générées sont `CreatedAt/UpdatedAt DATETIME NOT NULL`
  **sans `DEFAULT`**, donc le modèle doit les fournir explicitement à chaque
  `INSERT`/`UPDATE`.

- **Cause** : `timestamps: true` est traité comme deux champs ordinaires, présents
  dans le formulaire, le modèle (`INSERT`/`UPDATE`) et la vue, au lieu d'être
  **gérés automatiquement** (par la base ou par le framework).

- **Impact** : sur une application réelle, **tous** les CRUD (ici 36) portent ce
  défaut ; le corriger a demandé une reprise transverse (migration + 36 formulaires +
  36 modèles + 36 vues).

- **Correctif proposé** : que `timestamps: true` implique, à la génération :
  1. **exclusion** de `created_at`/`updated_at` des formulaires et des vues ;
  2. **exclusion** des `INSERT`/`UPDATE` applicatifs (le modèle ne les fournit plus) ;
  3. un schéma SQL avec `CreatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP` et
     `UpdatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`.

- **Contournement appliqué** : migration transverse posant les défauts/`ON UPDATE`
  sur les 43 tables horodatées, puis retrait de `created_at`/`updated_at` des 36
  formulaires, modèles et vues.
- **✅ Corrigé Forge** (ADR-081, `0aef2f01`), **autorité Python** retenue (et non
  la base) : le normaliseur marque `created_at`/`updated_at` `managed` ; `make:crud`
  génère des modèles qui posent les valeurs via `datetime.now(timezone.utc)` (INSERT
  les deux, UPDATE `updated_at` seul, `created_at` stable), formulaires exclus, DDL
  **sans** `DEFAULT`. Adoption (REFCIEL-ADOPT-021-001, étape 4, option B) : les 37
  modèles d'entité repassés en autorité Python (via régénération contrôlée par le
  générateur officiel), migration corrective `timestamps_python_authority` retirant
  les `DEFAULT`/`ON UPDATE`. **Note** : contrairement à notre premier stopgap
  (autorité base), Forge a tranché l'autorité **Python** ; toutes les voies de seed
  (`.sql` générés par `fixtures:generate` + `apply_timestamps`, `referentiel_importer`
  via `NOW()`) fournissent déjà les horodatages, donc le retrait des défauts ne casse
  rien (`make check` vert). Le bug latent `classe_model` (INSERT 6 `?` / 4 valeurs)
  est corrigé au passage.

## Piste (non prouvée) : `forge run` : libération du port au redémarrage

Symptôme rapporté : au redémarrage, le port de dev est **parfois** « déjà utilisé ».
**Honnêteté du banc d'essai** : dans notre cas, la cause dominante était
**externe** au framework : un *port forwarding* de l'éditeur (VS Code) qui survit à
l'arrêt du serveur, **plus** un `forge run` détaché (lancé en arrière-plan) devenu
orphelin.
Ce n'est donc **pas** un bug `forge run` avéré.

Deux pistes tout de même, à vérifier côté framework :

1. **`SO_REUSEADDR`** sur le socket d'écoute du serveur de dev : évite les
   « address already in use » liés à un socket en `TIME_WAIT` après un arrêt.
2. **Arrêt propre des workers** : garantir qu'un `SIGINT`/`SIGTERM` sur `forge run`
   termine aussi l'éventuel worker/reloader (pas d'orphelin qui garde le port).

## Synthèse

| Réf | Sujet | Gravité | État |
|---|---|---|---|
| F53 | Split SQL coupe sur `;` en commentaire | moyen | ✅ corrigé Forge (ADR-079, `0aef2f01`) |
| F54 | Session orpheline non invalidée | moyen | ✅ corrigé Forge (ADR-080, `0aef2f01`) |
| F55 | `is_authenticated` à deux sources | faible | ✅ corrigé Forge (ADR-080, `0aef2f01`) |
| F56 | `make:crud` expose les horodatages ; pas de défaut SQL | moyen | ✅ corrigé Forge (ADR-081, `0aef2f01`), autorité Python |
| - | `forge run` / port (SO_REUSEADDR, arrêt propre) | faible | piste, non prouvée |

## Référence

`core/security/middleware.py` (`AuthMiddleware.check`),
`core/auth/session.py` (`is_authenticated`, `get_authenticated_user_id`),
`forge_mvc_rbac/jinja.py` (contexte `current_user`/`is_authenticated`),
découpeur SQL des migrations (opt-in entities).
Voir aussi
`retour-012` (split SQL cassé par une apostrophe) : même famille que F53.
