# Décisions d'architecture (ADR)

Ce dossier consigne les décisions structurantes du projet : le *pourquoi*
autant que le *quoi*.
Chaque décision qui engage le projet dans la durée (architecture, convention,
dépendance) fait l'objet d'un fichier `docs/adr/<numero>-<sujet>.md`.

## Trame

Repartez du gabarit [`000-template.md`](000-template.md) : Statut, Date,
Contexte, Décision, Conséquences, Alternatives écartées.

## Journal

- `001-adopter-forge.md` : adoption de Forge et de ses conventions (posé par
  `forge agents:init`).
- `002-json-canonique-et-persistance-applicative.md` : JSON canonique = référence
  de construction/import ; base = vérité applicative.
- `003-architecture-applicative-forge.md` : architecture 100% Forge (`mvc/`,
  contrats d'entité, générateurs, migrations).
- `004-backend-base-de-donnees-mariadb.md` : backend MariaDB (opt-in installé par
  le porteur le moment venu).
- `005-standard-qualite-documentation-mkdocs-banc-essai.md` : qualité au niveau
  Forge, doc mkdocs vivante, rôle de banc d'essai.
- `006-strategie-de-test.md` : stratégie de test (méta, smoke, db).
- `007-typage-python-strict.md` : typage `# pyright: strict` par fichier sur le
  code produit.
- `008-import-json-canonique-par-upload-admin.md` : import du JSON canonique par
  upload admin (validation puis persistance).
- `009-montee-squelette-forge-en-place.md` : montée du squelette Forge en place
  (manifeste de propriété ; ni déplacement de dossier, ni force-push).

Numérotez les décisions suivantes `010`, `011`, etc., et ajoutez-les à ce
journal. Le gabarit `000-template.md` n'est pas une décision : c'est la trame.
