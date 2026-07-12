# Retour terrain 015 — `forge-mvc-rbac` : resolveur adossé à une session dépréciée, schéma non livré, deux modèles de permission

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-005).
**Statut :** à remonter.

## Environnement

- `forge-mvc` **32f552cc**, opt-ins **`forge-mvc-rbac`**, `forge-mvc-entities`,
  `forge-mvc-mariadb`, Python 3.12.
- Auth : socle `users` (`forge auth:init`), connexion via
  **`core.auth.session.login_user`** (auth *moderne*, qui stocke uniquement
  `user.id` sous la clé `_auth_user_id`).
- Contexte : discriminer la **navigation** et **protéger les routes** par rôle
  (admin gère le socle scolaire ; professeur conçoit/évalue/suit). Contrat
  `mvc/security/rbac.json` validé (`rbac:validate` OK), rôles `admin` /
  `professeur` créés et affectés en base.

## Constats

### F30 — Le resolveur de rôles natif lit une session **dépréciée**, incompatible avec l'auth moderne

- **Symptôme** : quel que soit l'utilisateur connecté, les gardes contractuelles
  (`require_contract_permission_for_request`) et le `can()` refusent tout — les
  rôles remontent **toujours vides**, alors que `user_roles`/`roles` sont bien
  peuplées en base et que le contrat est valide.

- **Cause** — `forge_mvc_rbac/contract.py::get_request_roles` résout les rôles
  ainsi :

  ```python
  # 1. request.roles (injection directe, tests)
  # 2. session utilisateur -> champ "roles"
  utilisateur = get_user(request)          # core.security.session.get_user (DÉPRÉCIÉ)
  if utilisateur:
      roles = utilisateur.get("roles", [])  # attend un DICT user + champ "roles"
  ```

  `get_user` provient de `core.security.session` (**module déprécié**) et attend
  un **dictionnaire utilisateur** portant un champ `roles`, posé par l'ancien
  `authenticate_session`. Or l'auth moderne (`core.auth.session.login_user`)
  ne stocke **que** `user.id` (`_auth_user_id`) : ni dict user, ni champ `roles`.
  Résultat : `get_user(request)` renvoie vide → `roles = []` → tout est refusé.

- **Conséquence** : l'opt-in RBAC, tel quel, **n'est pas câblable** sur l'auth
  moderne. Les deux briques officielles de Forge (auth moderne + RBAC) ne se
  parlent pas. Aucun message n'alerte : on croit à un problème de contrat ou
  d'affectation de rôles, alors que le pont de session est manquant.

- **Suivi (2026-07-12)** : correction en **deux temps** côté Forge.
  - Sur `d2b5157c`, F30 n'était corrigé qu'à moitié : le chemin **base**
    (`authorization.py`, `jinja.py`, `resolver.py`) passait à
    `get_authenticated_user_id`, mais le chemin **contrat**
    (`contract.py::get_request_roles`) lisait encore `get_user` (session dépréciée).
  - **RÉSOLU sur `e7cc3f1a`** : `get_request_roles` **n'appelle plus** `get_user`. Il
    lit désormais `request.roles` (point d'injection canonique sous l'auth moderne :
    l'app pose les rôles de `current_user` sur la requête via un middleware), avec
    repli sur la session legacy. Le RBAC contractuel natif est donc **câblable** sur
    l'auth moderne, à condition que l'app alimente `request.roles`.
  - **Conséquence projet** : le retrait de la couche maison RBAC (ADR-012) redevient
    possible — via un middleware qui pose `request.roles` — mais reste un chantier à
    part (`guard_prefix` n'a toujours pas d'équivalent natif). Voir le suivi de
    l'[ADR-012](../adr/012-rbac-couche-fine-maison-sur-contrat.md).

### F31 — L'opt-in ne livre **aucun schéma SQL** ni commande de synchronisation contrat → base

- **Symptôme** : le resolveur DB (`forge_mvc_rbac/resolver.py`) interroge
  **quatre tables** —

  ```sql
  -- SELECT_USER_PERMISSIONS_SQL
  FROM user_roles ur
  JOIN roles r            ON r.id  = ur.role_id
  JOIN role_permissions rp ON rp.role_id = r.id
  JOIN permissions p       ON p.id  = rp.permission_id
  ```

  `user_roles`, `roles`, `role_permissions`, `permissions` — mais le paquet
  `forge_mvc_rbac` **ne contient aucun fichier `.sql`** (`find … -name '*.sql'`
  → vide). Il faut écrire **à la main** tout le schéma (4 tables) et le seed.

- **Aggravant** : le contrat `mvc/security/rbac.json` (rôles → permissions) et
  ces tables sont **deux mondes disjoints**. La CLI de l'opt-in n'expose que
  `rbac:validate` et `rbac:audit` — **pas de `rbac:sync`** pour projeter le
  contrat dans `permissions`/`role_permissions`. Le resolveur DB ne verra donc
  **jamais** les permissions déclarées au contrat, sauf à peupler les tables
  soi-même en doublon du contrat.

- **Conséquence** : deux sources de vérité à tenir manuellement synchronisées,
  sans outil. Cf. déjà signalé partiellement en retour-006 (socle auth/RBAC non
  provisionné) ; ici le manque porte spécifiquement sur `roles`,
  `role_permissions`, `permissions` et l'absence de synchronisation.

### F32 — Deux modèles de permission dans le **même** opt-in, sans pont documenté

- Le `can()` Jinja par défaut (`forge_mvc_rbac/jinja.py::make_auth_jinja_can` →
  `resolver.user_has_permission`) est **adossé à la base** (les 4 tables ci-dessus).
- Les gardes recommandées côté route (`require_contract_permission…`) sont
  **adossées au contrat** (`get_contract_permissions` lit `rbac.json`).

  Deux mécanismes coexistent, avec des **sources de vérité différentes** (tables
  DB vs JSON), tous deux **branchés sur la résolution de rôles cassée** de F30.
  Rien dans l'opt-in n'indique lequel privilégier ni comment les réconcilier.

## Contournement retenu côté projet (couche fine maison)

Sans toucher l'opt-in, une couche applicative (`mvc/services/rbac.py`) fournit
le maillon manquant et **contourne le resolveur cassé** :

1. **Rôles depuis la session moderne + base** : `get_authenticated_user_id`
   (moderne) → jointure `user_roles`/`roles`. C'est le maillon que F30 rate.
2. **Décision déléguée au contrat** : `has_contract_permission` (framework) sur
   `rbac.json` — on retient le modèle **contrat** (F32), plus simple à versionner
   et sans tables `permissions`/`role_permissions` à maintenir (esquive F31).
3. **`can()` réinjecté** via `register_jinja_context_provider`, enregistré **en
   dernier** pour **écraser** le `can()` natif de l'opt-in (qui, lui, reste sur
   la session dépréciée et les tables non livrées).
4. **Gardes de route** par préfixe (passe post-enregistrement sur
   `router.iter_routes()`), pour protéger l'URL et pas seulement le menu.

Vérifié de bout en bout : `admin@` (rôle `admin`) voit tout ; `prof@` (rôle
`professeur`) voit Conception/Exécution/Suivi mais pas Admin ; un anonyme sur une
route socle reçoit **403**.

## Propositions

- **F30** : brancher `get_request_roles` sur l'auth moderne — résoudre `user.id`
  via `core.auth.session.get_authenticated_user_id`, puis charger les rôles par
  un resolveur applicatif (loader injectable), au lieu de dépendre du dict de la
  session dépréciée. À défaut, documenter explicitement l'incompatibilité et le
  pont à écrire.
- **F31** : livrer le DDL des 4 tables (migration ou `sql/` de l'opt-in) **et**
  une commande `rbac:sync` projetant le contrat `rbac.json` dans
  `permissions`/`role_permissions`, pour une seule source de vérité.
- **F32** : clarifier la doctrine (contrat *ou* base) et, si les deux subsistent,
  garantir qu'ils lisent la **même** résolution de rôles, elle-même compatible
  auth moderne.
