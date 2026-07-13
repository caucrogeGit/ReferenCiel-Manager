# ADR-016 — Bascule du RBAC sur le contrat natif (retrait **total** de la couche maison)

**Statut :** Accepté et **réalisé** (2026-07-12)

> **Remplace** la couche RBAC maison de l'[ADR-013](013-rbac-couche-fine-maison-sur-contrat.md) :
> `mvc/services/rbac.py` est **supprimé**, tout le RBAC passe par l'opt-in natif.

## Contexte

L'[ADR-013](013-rbac-couche-fine-maison-sur-contrat.md) avait introduit une couche
RBAC « fine maison » parce que l'opt-in `forge-mvc-rbac` était, sous l'auth moderne,
inutilisable : resolveur de rôles sur session dépréciée (F30), pas de provider Jinja
contractuel, pas de garde par préfixe d'URL.

Ces trois manques ont été **corrigés côté Forge** (retour banc-essai du projet) :

| Manque | Correctif Forge | Ce qu'il rend inutile |
|---|---|---|
| **A** — résolveur de rôles autonome (`get_request_roles` résout en base via l'auth moderne, sans injection) | `67a32bcc` | `current_user_roles` + middleware d'injection |
| **B** — garde par **préfixe** (`PrefixPermissionMiddleware`) | `5ef21fa3` | `guard_prefix` |
| **C** — provider Jinja **contractuel** (`register_contract_rbac_provider`) | `1b1bb998` | `rbac_context` / `register_rbac_provider` |

Le contournement de l'ADR-013 n'a donc **plus aucune raison d'être** : on retire la
couche maison **en totalité**.

## Décision

1. **Résolution des rôles = native.** On s'appuie sur `get_request_roles`
   (auth moderne → `user_roles`/`roles`, auto-suffisant y compris sur une route
   **publique** qui affiche du RBAC — la home connectée). Plus de `current_user_roles`.

2. **`can()` des vues = provider contractuel natif.** `register_contract_rbac_provider()`
   (appelé dans `mvc/routes/__init__.py`, après l'import de l'opt-in, pour écraser le
   provider « table » auto-inscrit) adosse le `can()` des templates à `rbac.json`.

3. **Gardes de route = `PrefixPermissionMiddleware`.** La table préfixe → permission
   (`RBAC_PREFIX_RULES`, dans `mvc/routes/__init__.py`) est appliquée par le
   middleware natif, câblé dans `app.py` :
   `Application(router, middlewares=[AuthMiddleware("/login"), PrefixPermissionMiddleware(RBAC_PREFIX_RULES)])`.
   Le préfixe le plus spécifique gagne ; couvre les routes futures.

4. **Modèle contractuel conservé** (`rbac.json`) ; le chemin base natif
   (tables `permissions`/`role_permissions`) n'est pas utilisé.

5. **`mvc/services/rbac.py` supprimé.**

## Conséquences

- **Positif** : dette F30 close, **zéro code RBAC maison**, une seule source de
  vérité (contrat) et un seul resolveur (natif). Résolution des rôles centralisée.
  Alignement complet sur Forge (règle « 100 % Forge »).
- **Vérifié** : e2e par rôle (admin / professeur / élève / anonyme) — gardes d'URL
  **et** nav filtrée, home connectée comprise : comportement **identique** à la
  couche maison (admin voit tout ; professeur → 403 sur le socle ; élève → seul
  `/mon-parcours` ; anonyme → login).
- **Réversibilité** : `RBAC_PREFIX_RULES` + le câblage `app.py` restent isolés ; on
  pourrait revenir à une couche maison si le natif régressait.

## Alternatives écartées

- **Retrait partiel** (version initiale de cet ADR, avant les correctifs A/B/C) :
  gardait `current_user_roles` (fallback home publique) et `guard_prefix` faute
  d'équivalents natifs. Rendu **caduc** par les correctifs Forge : le retrait total
  est désormais possible et préférable (aucun code maison résiduel).
- **Chemin base natif** (`permissions`/`role_permissions`) : imposerait un second
  modèle + son DDL, pour aucun gain sur un contrat déjà en place.

## Câblage (référence)

- `mvc/routes/__init__.py` : `register_contract_rbac_provider()` + table
  `RBAC_PREFIX_RULES`.
- `app.py` : `PrefixPermissionMiddleware(RBAC_PREFIX_RULES)` dans les middlewares.
- Contrat : `mvc/security/rbac.json` (inchangé).
