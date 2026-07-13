# Retour terrain 019 — MFA : la revalidation step-up (`verify_mfa_revalidation`) exige une session dépréciée

**Destinataire :** équipe Forge (dépôt `caucrogeGit/Forge`).
**Émetteur :** projet RéférenCiel Manager (banc d'essai, ADR-006).
**Statut :** **RÉSOLU** côté Forge (2026-07-12, sha `6927a266`) — voir note sous F42.

## Environnement

- `forge-mvc-mfa` **1.0.0rc2**, `forge-mvc` 1.0.0rc2, auth moderne
  (`core.auth.session.login_user`), sessions `sessions-db` (MariaDB), Python 3.12.
- Contexte : câblage d'un **step-up** (re-preuve du 2ᵉ facteur avant désactivation de
  la MFA), au-dessus de l'enrôlement TOTP + challenge de login déjà en place
  ([ADR-015](../adr/015-mfa-totp-optionnelle.md)).

## Constat

### F42 — `verify_mfa_revalidation` / `_session_user_matches` lisent une session au format déprécié

- **Symptôme** : `verify_mfa_revalidation(request, user_id, code, factors, recovery)`
  retourne **toujours `None`**, même avec un code TOTP ou de secours **valide**,
  utilisateur **connecté** (session authentifiée), rate-limit vide, code non rejoué.

- **Cause** (`forge_mvc_mfa/mfa.py`, `verify_mfa_revalidation` → `_session_user_matches`) :

  ```python
  def _session_user_matches(request, expected_user_id):
      session = _resolve_mfa_session(request)
      if not _session_get(session, "authenticated"):
          return False
      user = _session_get(session, "user") or {}
      session_user_id = user.get("id")
      return session_user_id == expected_user_id
  ```

  La garde attend une session **`{"authenticated": True, "user": {"id": …}}`**. Or
  l'auth moderne (`login_user`) ne stocke **que** l'identifiant sous
  `AUTH_USER_ID_SESSION_KEY` — pas de dict `user`, pas de flag `authenticated`. Donc
  `_session_user_matches` renvoie `False`, `verify_mfa_revalidation` sort en
  `None` **avant même** de vérifier le code, et journalise
  `AUTH_EVENT_MFA_REVALIDATION_IDENTITY_MISMATCH`.

- **Portée** : c'est **exactement le F30** de
  [retour-015](retour-015-rbac-resolveur-session-depreciee-et-schema-non-livre.md)
  (le resolveur RBAC lisait la même session dépréciée), mais côté MFA. À noter :
  `verify_mfa_challenge` (au **login**) **fonctionne**, car il s'appuie sur
  `get_mfa_challenge_user_id` (clé de session posée par `start_mfa_challenge`), **pas**
  sur `_session_user_matches`. Seule la **revalidation step-up** est touchée.

- **Impact** : `verify_mfa_revalidation`, `has_recent_mfa_revalidation`,
  `require_recent_mfa` sont **inutilisables** avec l'auth moderne. Tout step-up bâti
  dessus refuse systématiquement l'accès.

- **Contournement (projet)** : ne pas utiliser l'API de revalidation ; vérifier le 2ᵉ
  facteur directement (`decrypt_totp_secret` + `verify_totp_code`, puis
  `verify_recovery_code`), comme le RBAC contourne son resolveur (ADR-013). Le
  step-up exige alors un code à chaque action sensible (pas de fenêtre de 10 min).

- **Correctif proposé** : aligner `_session_user_matches` sur l'auth moderne — lire
  `core.auth.session.get_authenticated_user_id(request)` (comme le fait déjà
  `start_mfa_challenge` via `get_mfa_challenge_user_id`) au lieu du dict `user`
  déprécié. Fix symétrique de celui attendu au F30.

- **RÉSOLU (2026-07-12, Forge sha `6927a266`)** : `_session_user_matches` lit
  désormais `_auth_user_id` (auth moderne) en priorité, avec repli sur la session
  legacy. `verify_mfa_revalidation` fonctionne donc avec l'auth moderne. Côté app, le
  **contournement a été retiré** : le step-up de désactivation MFA
  (`mvc/controllers/securite_controller.py`) rebranche l'API native
  (`verify_mfa_revalidation` / `has_recent_mfa_revalidation`), vérifié end-to-end.

## Référence

`forge_mvc_mfa/mfa.py` (`verify_mfa_revalidation`, `_session_user_matches`,
`_resolve_mfa_session`). Flux : espace Sécurité, step-up de désactivation MFA
(`mvc/controllers/securite_controller.py`).
