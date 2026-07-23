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
- `017-referentiels-livres-et-chargement-installation.md` : référentiels
  niveau-classe versionnés dans `data/referentiels/`, chargés en base à
  l'installation via `tools/charger_referentiels.py` (idempotent).
- `018-gestion-referentiel-atelier-coherent.md` : atelier de gestion du
  référentiel cohérent (édition adossée aux JSON canoniques).
- `019-modele-scenario-aligne-cpro-education.md` : modèle de scénario aligné sur
  le cadre CPRO Éducation nationale ; base de l'éditeur de scénario.
- `020-preline-ui-pour-la-couche-vues.md` : Preline UI adopté comme boîte à
  outils front de la **couche vues** (CSS/JS hors Forge, autorisé) ; navigation
  passée en sidebar filtrée par rôle, réhabillée à la charte.
- `021-etat-du-tunnel-dans-l-url.md` : état du tunnel de scénario porté par
  l'**URL** (jamais côté client), complétion **dérivée des données**,
  régénération partielle par fragments HTMX avec **dégradation gracieuse**
  (une seule route sert JS et sans-JS) ; Preline=chrome, HTMX=données.
- `022-parcours-objet-canonique-aplatissement.md` (**Accepté**) : **Parcours**
  devient l'objet canonique unique ; suppression des couches
  starter/version-starter/version-parcours et des affectations ; paliers
  directement sous le parcours ; nouvelles cardinalités (Scénario 1-1 Parcours
  via pivot, ProgressionParcours associative). Révise ADR-019.
- `023-modele-generique-voie-professionnelle.md` (**Accepté**) : modèle générique
  de la voie pro. Le pivot passe de `Formation -> NiveauClasse` à
  **`Cursus -> CursusEtape -> FormationNiveau`** ; séparation
  Formation/Referentiel/NiveauClasse/Certification/Classe ; le référentiel est
  re-scopé sur la **Formation** (retrait de `niveau_classe_id`) ; le concept
  académique s'appelle **Cursus** (pas Parcours, réservé au pédagogique de
  l'ADR-022) ; déroulé en 4 phases. Révise ADR-018.
- `024-generation-pdf-cote-application-weasyprint.md` (**Accepté**) : génération
  PDF **côté application** avec **WeasyPrint** (template Jinja vers HTML vers PDF).
  Couture d'extraction prête pour un futur opt-in `forge-mvc-pdf` : `render_pdf`
  (générique) séparé de `scenario_pdf` (métier). Première dépendance tierce de
  l'app (`weasyprint`, licence BSD).
- `025-renommage-sequence-seance.md` (**Accepté**) : sémantique Éducation
  nationale — **Parcours → Séquence**, **Palier → Séance**, partout (entités,
  tables, routes, vues, docs). Identifiants ASCII (`sequence`, `seance`),
  libellés accentués. Déroulé en 6 phases, la feuille d'abord. Annote ADR-022.
- `026-versionnement-objets-pedagogiques-publies.md` (**Accepté**) : « finalisé »
  = complétude **dérivée** (non un statut persisté) ; versionnement par snapshot
  à la publication.
- `027-scenario-hors-referentiel.md` (**Accepté**) : le référentiel devient
  **facultatif** pour un scénario (matières non adossées). Finalisation à deux
  régimes, étape « Liaison référentiel » grisée. Amende ADR-023.
- `028-connaissances-associees-ancrage-referentiel.md` (**Accepté**) : les
  **connaissances associées** sont des objets du référentiel (entité
  `Connaissance`, ancrée à la compétence, niveau taxonomique officiel).
  **Retrait de `savoir_associe`** (doublon libre de SEQ-02). Nouveau lien
  Séquence ↔ Connaissance portant le **niveau cible** (≠ officiel), le **statut**
  pédagogique et un commentaire. Branchement de l'import.

- `029-appairage-scenario-sequence-a-la-creation.md` (**Accepté**) : réalise
  l'invariant **1-1 Scénario ↔ Séquence** (aujourd'hui déclaré mais jamais
  peuplé). La paire **naît ensemble**, atomiquement, quel que soit le point
  d'entrée ; `sequence.niveau_classe_id` devient **nullable** ; backfill des
  scénarios orphelins existants.

- `030-savoirs-libres-hors-referentiel.md` (**Accepté**) : **coexistence** dans
  « Savoirs associés » — avec référentiel, sélection structurée (ADR-028) ; sans
  référentiel, **savoirs libres** ajoutés en texte libre comme les indicateurs
  (nouvelle table `savoir_libre`). Amende l'alternative écartée d'ADR-028.

- `031-suppression-scenario-sequence-dissociation.md` (**Accepté**) : supprimer
  un scénario ou une séquence **dissocie** (le lien part, le partenaire reste) au
  lieu de cascader. Orphelins légitimes ; identifiant de séquence suffixé pour
  éviter les collisions ; pas de ré-appairage auto. Amende le point
  « suppression » différé d'ADR-029.

- `032-modele-seance-tunnel-cascade-evaluation.md` (**Accepté**) : la **séance**
  devient un **tunnel** ; sélection **en cascade** sans double saisie (la séance
  pioche dans la liaison du scénario) ; compétences observées + critères +
  indicateurs ; `ElementSeance` (déroulé ordonné polymorphe) ; **règle
  d'évaluation** (observations accumulées, le prof arbitre, pas d'auto-validation).
  Phases A→B→C.

- `033-suivi-evaluation-tableau-de-bord.md` (**Accepté**) : le **suivi/évaluation**
  devient un **tableau de bord multi-entrées** (tuiles Classe / Séquence…),
  lentilles d'un même graphe, convergeant vers une **feuille de positionnement**
  des critères (🔴🟠🟩, indicateur, production, aide). Étend `/suivi`.

- `034-cycle-statut-sequence-publication-explicite.md` (**Accepté**) : la séquence
  suit le cycle **brouillon → finalisé → publié → attribué**, entièrement
  **dérivé des données** : tunnel complet = finalisé, une séance liée = publié,
  une progression élève = attribué.
  Les **séances se lient dès « finalisé »**.

- `035-suppression-menu-execution-absorption-parcours.md` (**Accepté**) : le menu
  **Exécution disparaît**, absorbé par les parcours.
  L'**attribution** se fait depuis la carte de la séquence
  (`/sequence/{id}/attributions`, par classe ou par élève, retrait gardé), le
  **déroulé référence** les QCM/checklists de la séance (`qcm_id`/`checklist_id`),
  les routes CRUD restent actives pour le dépannage.

- `036-statuts-savoirs-declencheurs-evaluation.md` (**Accepté**) : les **statuts
  des savoirs** (ADR-028) deviennent la **charnière entre l'axe des contenus et
  l'axe évaluatif**.
  Séquence formative : savoirs **Apportée/Consolidée** = compétence à évaluer
  au scénario ; **CCF** : statuts attendus **Prérequis/Mobilisée**, évaluation
  pilotée par la grille d'épreuve.
  Signaux et suggestions, jamais de contrainte ; champ « nature » de séquence à
  introduire.

- `037-savoirs-associes-portes-par-la-seance.md` (**Accepté**) : les **savoirs
  associés descendent à la séance** (`seance_connaissance`), la séquence les
  **agrège** (comme durée et prérequis).
  Cascade ADR-036 inchangée d'un cran plus bas ; cycle ADR-034 révisé :
  finalisé = titre + niveau, **publié = une séance ouvrante**.

- `038-etape-gestion-des-tunnels.md` (**Accepté**) : chaque tunnel se termine
  par une étape **« Gestion »** (ressources, exports, attributions,
  suppression), **hors complétude** (engrenage au stepper).
  Les cartes redeviennent lecture + lien ; l'entrée **Séances** du menu
  disparaît.

Numérotez les décisions suivantes `013`, `014`, etc., et ajoutez-les à ce
journal.
Le gabarit `000-template.md` n'est pas une décision : c'est la trame.
