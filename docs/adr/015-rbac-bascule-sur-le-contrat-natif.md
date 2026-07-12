# ADR-015 — Bascule du RBAC sur le contrat natif (retrait partiel de la couche maison)

**Statut :** Accepté
**Date :** 2026-07-12

> Fait suite à l'[ADR-012](012-rbac-couche-fine-maison-sur-contrat.md), qu'il
> **amende partiellement** (il ne l'annule pas : la partie « garde par préfixe »
> reste maison).

## Contexte

L'[ADR-012](012-rbac-couche-fine-maison-sur-contrat.md) a introduit une couche RBAC
« fine maison » (`mvc/services/rbac.py`) parce que le resolveur natif de
`forge-mvc-rbac` lisait une **session dépréciée** (F30, [retour-015](../banc-essai/retour-015-rbac-resolveur-session-depreciee-et-schema-non-livre.md))
et renvoyait donc toujours des rôles vides sous l'auth moderne.

**F30 est corrigé côté Forge** (sha `e7cc3f1a`, 2026-07-12) : `get_request_roles`
n'appelle plus la session dépréciée — il lit **`request.roles`**, un point
d'injection que l'application alimente. Le RBAC contractuel natif
(`has_contract_permission`, `require_contract_permission_for_request`,
`get_contract_permissions`) devient donc **câblable** sur l'auth moderne, à condition
que l'app pose les rôles de l'utilisateur courant sur la requête.

Le contournement de l'ADR-012 n'a plus de raison d'être **sur sa partie résolution
des rôles / décision**. On peut réduire la couche maison et se réaligner sur le natif.

## Décision

1. **Middleware `request.roles`.** L'app installe un middleware
   (`check(request) → None`) qui, pour chaque requête, résout les **slugs** de rôles
   de l'utilisateur connecté (auth moderne → `user_roles`/`roles`) et les pose sur
   `request.roles`. C'est le maillon que le natif attend et que
   `current_user_roles` faisait — **déplacé en amont**, résolu **une fois par
   requête** au lieu d'une fois par garde/rendu.

2. **Décision via le natif.** Les gardes de route et le `can()` des vues s'appuient
   sur le chemin **contractuel** natif (`get_request_roles` → `request.roles`, puis
   `has_contract_permission` sur `rbac.json`). On retire les équivalents maison
   (`current_user_roles`, `can`, `require_permission`, `guarded`).

3. **`guard_prefix` conservé.** Le natif ne protège que **route par route**
   (décorateur sur handler) ; il n'a **aucun** équivalent de protection **par
   préfixe d'URL** en une passe post-enregistrement. `guard_prefix` reste donc
   **maison**, mais enveloppe désormais la **garde native**
   (`require_contract_permission_for_request`) au lieu de la garde maison. C'est la
   part de l'ADR-012 qui **subsiste**.

4. **Modèle contractuel maintenu.** On reste sur `rbac.json` (chemin contrat). On
   n'active **pas** le chemin base natif (`user_has_permission`), qui exigerait les
   tables `permissions`/`role_permissions` absentes — hors sujet ici.

## Conséquences

- **Positif** : dette F30 close côté app ; moins de code maison (résolution + `can`
  + gardes délèguent au natif) ; une seule source de vérité (contrat) et un seul
  resolveur (natif) ; rôles résolus une fois par requête (middleware).
- **Négatif / limites** : retrait **partiel** — `guard_prefix` reste maison (le
  natif ne couvre pas la garde par préfixe). Le RBAC garde **toute** l'app : la
  bascule impose une **vérification e2e par rôle** avant de committer (admin, prof,
  élève, anonyme : nav filtrée **et** URL tapées à la main).
- **Attention au cache contrat** : la couche maison **cachait** `rbac.json`
  (`_contract_cache`) ; `require_contract_permission_for_request` natif **recharge et
  revalide** le contrat à chaque requête. À mesurer / éventuellement encapsuler dans
  un helper qui cache, pour ne pas relire le fichier à chaque garde.
- **Réversibilité** : le middleware et `guard_prefix` restent isolés ; on peut
  revenir à la couche maison si le natif régressait.

## Alternatives écartées

- **Statu quo (garder la couche maison).** Rejetée : maintient une dette
  documentée (F30) alors que Forge l'a corrigée ; deux resolveurs de rôles pour rien.
  (Option légitime si le coût de bascule dépassait le gain — d'où le séquencement
  prudent ci-dessous.)
- **Retrait total (tout natif, sans code maison).** Impossible : pas de garde par
  préfixe native (§3). Il faudrait décorer à la main chaque handler de chaque
  `*_routes.py` — régression d'ergonomie et de couverture (routes futures).
- **Activer le chemin base natif** (`permissions`/`role_permissions`). Rejetée :
  imposerait un second modèle de permission et le DDL correspondant, pour aucun
  gain sur un contrat déjà en place.

## Plan de mise en œuvre (tickets de suite)

Séquencé pour rester vérifiable à chaque étape (le RBAC est critique) :

1. **T1 — Middleware `request.roles`.** Créer `RolesMiddleware.check(request)` qui
   pose `request.roles` (slugs, auth moderne → base ; `[]` si anonyme/tables
   absentes) et retourne `None`. Le câbler dans `app.py`
   (`Application(router, middlewares=[AuthMiddleware(...), RolesMiddleware()])`).
   *Validation* : `request.roles` est peuplé pour un compte connecté (log/test).

2. **T2 — Bascule des gardes de route.** Adapter `guard_prefix` pour envelopper
   `require_contract_permission_for_request` (natif, lit `request.roles`) au lieu de
   `guarded` maison. Introduire un cache de contrat si le rechargement par requête
   pèse. *Validation* : prof → 403 sur `/classe`, 200 sur `/mes-classes` ; anonyme
   → redirigé ; admin → tout.

3. **T3 — Bascule du `can()` Jinja.** Fournir le `can()` des vues via le contrat +
   `request.roles` (provider natif avec `permission_checker` contractuel, ou
   `rbac_context` maison réduit à lire `request.roles`). *Validation* : la nav
   filtrée est identique à aujourd'hui pour chaque rôle.

4. **T4 — Nettoyage.** Retirer de `mvc/services/rbac.py` les fonctions devenues
   inutiles (`current_user_roles`, `can`, `require_permission`, `guarded`,
   éventuellement `rbac_context`/`register_rbac_provider`). Conserver `guard_prefix`.
   *Validation* : `make check` vert ; **e2e complet par rôle** (smoke test des routes
   en admin/prof/élève/anonyme, réparti 200/403/302 inchangé).

5. **T5 — Doc.** Marquer l'ADR-012 « amendé par ADR-015 » ; noter le retrait dans
   [retour-015](../banc-essai/retour-015-rbac-resolveur-session-depreciee-et-schema-non-livre.md).

**Garde-fou** : ne committer qu'après la vérification e2e par rôle de T4 — une
régression RBAC est silencieuse (trop permissif) ou bloquante (trop restrictif).
