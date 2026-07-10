# ADR-012 — Couche RBAC applicative « fine maison » adossée au contrat

**Statut :** Accepté
**Date :** 2026-07-10

## Contexte

La navigation doit être **discriminée par rôle** (l'admin gère le socle scolaire ;
le professeur conçoit, exécute, suit ; l'élève, plus tard, ne voit que son
parcours), et les **routes** doivent être protégées par permission — masquer une
rubrique de menu n'est que du confort, l'URL tapée à la main doit être refusée.

L'opt-in officiel **`forge-mvc-rbac`** est installé (contrat
`mvc/security/rbac.json` : rôles → permissions, validé par `rbac:validate`), et
les tables `roles` / `user_roles` sont peuplées ([migration RBAC](../banc-essai/retour-015-rbac-resolveur-session-depreciee-et-schema-non-livre.md)).
Mais son câblage **échoue** sur notre auth (constats [retour-015](../banc-essai/retour-015-rbac-resolveur-session-depreciee-et-schema-non-livre.md)) :

- **F30** : son resolveur (`get_request_roles`) lit `core.security.session`
  (**module déprécié**, dict utilisateur avec champ `roles`). Or l'auth moderne
  (`core.auth.session.login_user`) ne stocke que `user.id`. → rôles **toujours
  vides**, tout est refusé.
- **F31** : l'opt-in ne livre **aucun DDL** (le resolveur DB interroge
  `user_roles`/`roles`/`role_permissions`/`permissions`) ni commande
  `rbac:sync` contrat → base.
- **F32** : deux modèles de permission coexistent — `can()` Jinja **adossé base**
  vs gardes **adossées au contrat** — avec des sources de vérité différentes.

## Décision

Introduire une **couche RBAC applicative fine** (`mvc/services/rbac.py`) qui
**réutilise le contrat et le vérificateur du framework**, mais **fournit
elle-même la résolution des rôles** — le maillon que l'opt-in rate :

1. **Rôles = session moderne + base.** `get_authenticated_user_id` (auth moderne)
   → jointure `user_roles`/`roles`. Pas de dépendance à la session dépréciée.
2. **Décision = contrat.** On retient le modèle **contractuel** (`rbac.json`),
   via `has_contract_permission` du framework. Une seule source de vérité pour
   les permissions ; pas de tables `permissions`/`role_permissions` à maintenir
   en doublon (on esquive F31/F32).
3. **`can()` réinjecté** dans tous les rendus via
   `register_jinja_context_provider`, **enregistré en dernier** pour **écraser**
   le `can()` natif de l'opt-in (qui reste sur la session dépréciée).
4. **Gardes de route par domaine** : `guard_prefix` enveloppe, en une passe
   post-enregistrement (`router.iter_routes()`), tout handler d'un préfixe —
   sans éditer les fichiers de routes générés, et en couvrant les routes futures
   du même domaine. Socle → `socle.gerer`, conception → `conception.gerer`,
   exécution → `execution.gerer`, suivi → `suivi.voir`.

Permissions **grossières par domaine** (décision porteur) : `admin` a les cinq
(`socle`/`referentiel`/`conception`/`execution`/`suivi`), `professeur` a
conception/exécution/suivi. L'élève viendra avec une UI dédiée et un accès
« ses propres données » (différé).

## Conséquences

- **Positif** : nav et routes réellement pilotées par le rôle, vérifiées de bout
  en bout (admin voit tout ; professeur ne voit ni n'atteint le socle → 403 ;
  anonyme → 403). Aucune dépendance à une API dépréciée. Le contrat reste la
  seule source de vérité, versionnable avec le code. `make check` vert.
- **Négatif / dette** : on **contourne** le resolveur de l'opt-in au lieu de
  l'utiliser — à réviser si Forge corrige F30 (brancher le resolveur natif sur
  l'auth moderne rendrait la couche `can()`/gardes redondante). Le `can()` maison
  s'appuie sur l'**ordre d'enregistrement** des providers (le nôtre en dernier) :
  contrat implicite à surveiller. Les sous-entités hors nav sont gardées par leur
  préfixe de domaine, pas plus finement (suffisant tant qu'il n'y a que
  admin/professeur).
- **Réversibilité** : la couche est isolée (`mvc/services/rbac.py` + branchement
  dans `mvc/routes/__init__.py`) ; si l'opt-in devient compatible, on retire le
  provider et les gardes maison et on rebranche le natif.

## Alternatives écartées

- **Remplir aussi la session dépréciée** au login (dict user + `roles`) pour que
  le `can()`/gardes natifs marchent tels quels : rapide, mais s'appuie sur des
  **API dépréciées** (avertissements, cassables en Forge 2.0). Écarté au profit
  de la robustesse.
- **Modèle base (tables `permissions`/`role_permissions`) + resolveur DB natif** :
  impose d'écrire tout le DDL manquant (F31) et de synchroniser à la main le
  contrat et la base (pas de `rbac:sync`). Deux sources de vérité pour aucun gain
  ici. Écarté.
- **Attendre un correctif Forge** : bloquerait la discrimination par rôle, alors
  que le besoin est immédiat et le contournement isolé et réversible. Écarté.
