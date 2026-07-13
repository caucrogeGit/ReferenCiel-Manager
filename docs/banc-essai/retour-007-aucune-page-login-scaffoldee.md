# Retour terrain 007 — Aucune page de login fournie ni scaffoldée, alors que le cœur redirige vers `/login`

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** ✅ Résolu dans forge-mvc f38d5159 (2026-07-08) — vérifié sur le banc d'essai.

## Environnement

- `forge-mvc` **e3197866**, socle auth de base en place (`auth:init` + migration).
- `auth:doctor` : `core.auth.session.login_user`, `AuthUser` **disponibles**.

## Contexte

Ticket 07 : les routes du CRUD généré sont **protégées par défaut**
(`make:crud` → `router.group("/annee_scolaire")`). On veut une vue prof derrière
l'auth (garde-fou : ne pas désactiver l'auth).

## Constat

### F16 — Le cœur redirige vers `/login`, mais rien ne sert `/login` et aucune commande ne le scaffolde

- **Symptôme** : **aucune route protégée n'est atteignable**. Un utilisateur non
  authentifié est redirigé (302) vers `/login`, qui **n'existe pas** → 404. Impossible
  de se connecter, donc impossible d'atteindre quoi que ce soit de protégé.
- **Preuve** :
  - `core/security/decorators.py:34` et `:72` → `Response(302, headers={"Location": "/login"})` ;
  - `core/security/middleware.py:28` → `AuthMiddleware(login_url: str = "/login")`.
  - Le cœur fournit le **backend** (`login_user`, `AuthUser`) mais **ni route, ni
    contrôleur, ni vue** de login ; `forge routes:list` ne montre aucune route login.
  - Les commandes `auth:*` gèrent les **comptes** (`user:create/list/...`), pas
    l'**UI de connexion** ; il n'existe pas de `forge make:auth`.

C'est possiblement un **choix** (l'app possède son UI de login), mais en l'état la
chaîne « activer l'auth » est **incomplète** : un projet reste bloqué juste après
`auth:init` dès qu'il protège une route.

## Proposition

1. **Scaffolder optionnel** — `forge make:auth` (ou `forge auth:scaffold`) générant
   contrôleur + route `/login` (GET formulaire, POST → `login_user`) + vue, en
   *write-if-new*, dans le style de l'app (comme `make:crud`). Idéalement aussi
   `/logout`.
2. **À défaut, documenter** explicitement le câblage attendu : route `/login`,
   appel `core.auth.session.login_user`, et cible configurable via
   `AuthMiddleware(login_url=...)` — pour que la redirection en dur `/login` du cœur
   soit cohérente avec ce que l'app doit fournir.

## Contournement

Écriture manuelle d'un contrôleur `AuthController` + route `/login` + vue, câblés sur
`login_user` (à faire pour compléter le walking skeleton du ticket 07).

## Référence

`core/security/decorators.py`, `core/security/middleware.py`. Flux : ticket 07,
routes `make:crud` protégées.
