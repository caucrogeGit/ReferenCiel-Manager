# Décisions d'architecture (ADR)

Ce dossier consigne les décisions structurantes du projet : le *pourquoi*
autant que le *quoi*.
Chaque décision qui engage le projet dans la durée (architecture, convention,
dépendance) fait l'objet d'un fichier `docs/adr/<numero>-<sujet>.md`.

## Trame

Repartez du gabarit [`000-template.md`](000-template.md) : Statut, Date,
Contexte, Décision, Conséquences, Alternatives écartées.

## Journal

- `001-adopter-forge.md` : adoption de Forge et de ses conventions (posé par
  `forge agents:init`).
- `003-json-canonique-et-persistance-applicative.md` : JSON canonique = référence
  de construction/import ; base = vérité applicative.
- `004-architecture-applicative-forge.md` : architecture 100% Forge (`mvc/`,
  contrats d'entité, générateurs, migrations).
- `005-backend-base-de-donnees-mariadb.md` : backend MariaDB (opt-in installé par
  le porteur le moment venu).
- `006-standard-qualite-documentation-mkdocs-banc-essai.md` : qualité au niveau
  Forge, doc mkdocs vivante, rôle de banc d'essai.
- `007-strategie-de-test.md` : stratégie de test (méta, smoke, db).
- `008-typage-python-strict.md` : typage `# pyright: strict` par fichier sur le
  code produit.
- `009-import-json-canonique-par-upload-admin.md` : import du JSON canonique par
  upload admin (validation puis persistance).
- `010-montee-squelette-forge-en-place.md` : montée du squelette Forge en place
  (manifeste de propriété ; ni déplacement de dossier, ni force-push).
- `011-importeur-referentiel-upsert-best-effort.md` : importeur du référentiel
  (upsert par identifiant, best-effort avec rapport).
- `012-versionnement-identite-plus-version.md` : versionnement par entité
  d'identité + entité de version.
- `013-rbac-couche-fine-maison-sur-contrat.md` : couche RBAC applicative fine,
  adossée au contrat, contournant le resolveur déprécié de l'opt-in.
- `014-securite-applicative-reelle.md` : acte l'existant (auth, sessions, RBAC,
  liens comptes, CSRF/CSP) ; trajectoire durcissement mots de passe → MFA →
  permissions fines.
- `015-mfa-totp-optionnelle.md` : MFA TOTP optionnelle en self-service (T2) :
  enrôlement + codes de secours + challenge au login, secret chiffré (Fernet).
- `016-rbac-bascule-sur-le-contrat-natif.md` : manques du RBAC natif corrigés côté
  Forge (résolveur autonome, provider contractuel, `PrefixPermissionMiddleware`) →
  **retrait total** de la couche maison (`mvc/services/rbac.py` supprimé) ; remplace
  l'ADR-013.
  Vérifié e2e par rôle.

Numérotez les décisions suivantes `013`, `014`, etc., et ajoutez-les à ce
journal.
Le gabarit `000-template.md` n'est pas une décision : c'est la trame.
