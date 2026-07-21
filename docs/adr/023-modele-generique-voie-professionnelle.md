# ADR-023 : Modèle générique de la voie professionnelle (Cursus, FormationNiveau, Certification)

**Statut :** Accepté
**Date :** 2026-07-15

> **Amendé par [ADR-027](027-scenario-hors-referentiel.md) (2026-07-19).** Le référentiel — obligatoire ici pour un scénario — devient **facultatif** pour les matières **non adossées** à un référentiel (enseignements généraux, PSE, chef-d'œuvre). Un scénario peut alors exister avec `referentiel_id` NULL et se finalise sur le seul contexte.

## Contexte

Le cœur « référentiel » lie aujourd'hui un référentiel à **exactement une
formation ET un niveau de classe**, les deux requis, en 1-1
(`referentiel_niveau_classe.formation_id` + `niveau_classe_id`).

Ce modèle a été révélé insuffisant en construisant le tunnel de scénario.
Le référentiel importé `ciel-2tne` était affiché « Bac Pro CIEL (2TNE) », ce qui
confond deux objets distincts.
Or, selon l'Éducation nationale, **2TNE n'est pas le diplôme CIEL** : c'est une
seconde commune « famille des métiers des transitions numérique et énergétique »,
qui mène à plusieurs bacs professionnels (CIEL, MELEC, ICCER, MEE, MFER).
La 2TNE n'est donc pas une certification et ne doit pas être modélisée comme un
diplôme.

En généralisant à toute la voie professionnelle, le modèle
`Formation -> NiveauClasse` ne suffit pas.
Une même certification s'atteint par **plusieurs chemins** :

```
Bac Pro CIEL, voie scolaire        : 2TNE -> 1re CIEL -> Terminale CIEL
Bac Pro CIEL, apprentissage        : 2de CIEL -> 1re CIEL -> Terminale CIEL
Bac Pro CIEL, après un CAP         : CAP -> 1re CIEL -> Terminale CIEL
```

Il existe aussi des spécialités hors famille de métiers, des CAP préparés en un,
deux ou trois ans, des passerelles et des poursuites d'études (BP, BMA, BTS, FCIL,
certificat de spécialisation).
Une famille de métiers ne concerne d'ailleurs que la seconde sous statut scolaire.

Le pivot ne peut donc plus être `Formation -> NiveauClasse`.
Il faut introduire explicitement le **cursus** (le chemin), et séparer ce qui est
enseigné (la formation), ce qui est décrit officiellement (le référentiel), la
position scolaire générique (le niveau de classe), le diplôme visé (la
certification) et l'instance locale d'une année (la classe).

Cette décision révise **ADR-018** (le référentiel n'est plus « par niveau de
classe ») et impose une mise à jour des specs canoniques
(`docs/specs/json-canonique/`).
Elle **ne modifie pas** la couche pédagogique de l'ADR-022 : voir le point sur le
conflit de nommage ci-dessous.

## Décision

### Séparation des concepts

```
Formation       : ce qui est enseigné (un contenu professionnel)
Referentiel     : ce qui décrit officiellement ce contenu
NiveauClasse    : position scolaire générique (vocabulaire)
FormationNiveau : application d'une formation à un niveau
Certification   : diplôme ou titre visé
Cursus          : succession ordonnée d'étapes vers une certification
CursusEtape     : une étape ordonnée d'un cursus (un FormationNiveau)
Classe          : instance locale pour une année scolaire
TransitionCursus: orientation ou passerelle possible entre étapes
RelationFormation : relation structurelle entre formations (structure nationale)
```

Le véritable pivot devient **`Cursus -> CursusEtape -> FormationNiveau`**, et non
plus `Formation -> NiveauClasse`.

### Conflit de nommage avec l'existant (décidé)

L'application possède déjà une entité `Parcours` (ADR-022), qui est un **parcours
pédagogique** : une séquence de `Palier` porteurs d'activités, checklists et QCM,
avec suivi élève (`ProgressionParcours`, `ProgressionPalier`, `BilanEleve`).
C'est un objet distinct du chemin scolaire décrit ici.

Le concept académique introduit par cet ADR s'appelle donc **`Cursus`** (et
**`CursusEtape`**, **`TransitionCursus`**), afin de **ne pas écraser** le
`Parcours` pédagogique existant.
Le `Parcours` pédagogique est conservé tel quel ; son rattachement éventuel à un
`FormationNiveau` (plutôt qu'à un `NiveauClasse` nu) est un raffinement ultérieur,
hors de cet ADR.

### Entités et cardinalités cibles

```
Certification   1─n Cursus                     (certification_cible)
Cursus          1─n CursusEtape
CursusEtape     n─1 FormationNiveau            (+ ordre, obligatoire, conditions)
FormationNiveau n─1 Formation
FormationNiveau n─1 NiveauClasse
Formation       1─n Referentiel               (versions successives)
Formation       n─1 Certification              (optionnel : « prépare »)
Formation       n─n Formation                  (RelationFormation, structure nationale)
FormationNiveau n─n FormationNiveau            (TransitionCursus, passerelles)
Classe          n─1 FormationNiveau
```

- **`Formation`** représente un contenu enseigné, pas nécessairement un diplôme.
  Elle porte un `type` (`FAMILLE_METIERS`, `SPECIALITE_BAC_PRO`, `CAP`, `BP`,
  `BMA`, `CERTIFICAT_SPECIALISATION`, `FCIL`, `BTS`, `AUTRE`).
  Elle peut préparer une certification (`certification_id` optionnel) : 2TNE n'en
  prépare aucune, CIEL prépare le Bac Pro CIEL.

- **`NiveauClasse`** devient un vocabulaire indépendant
  (`SECONDE_PRO`, `PREMIERE_PRO`, `TERMINALE_PRO`, `CAP_ANNEE_1`, `CAP_ANNEE_2`,
  `CAP_ANNEE_3`, `BP_ANNEE_1`, ...).
  Il n'appartient ni au référentiel ni à une seule formation.

- **`FormationNiveau`** dit qu'une formation peut être enseignée à un niveau donné
  (`formation_id`, `niveau_classe_id`, `code`, `libelle`, `ordre_indicatif`).
  C'est l'unité adressable : `CIEL + SECONDE_PRO` existe pour l'apprentissage,
  `2TNE + SECONDE_PRO` pour la voie scolaire.
  On ne fige donc jamais `CIEL = [Première, Terminale]` : ce serait vrai d'un seul
  parcours, pas de tous.

- **`Referentiel`** (l'entité `ReferentielNiveauClasse` renommée) appartient à la
  **formation**, pas au niveau.
  On retire `niveau_classe_id` du référentiel.
  La cardinalité est **1-n** (une formation a des versions successives de son
  référentiel), mais l'historisation des versions est différée (voir phase 4) :
  on démarre avec **un référentiel actif par formation**.
  La contrainte « une seule version active par formation et par nature » est
  **applicative**, MariaDB ne faisant pas d'unique partiel simplement.
  Tout le contenu de référentiel (pôles, activités, compétences, critères,
  indicateurs, sources) reste rattaché à `Referentiel`, inchangé.

- **`Certification`** (diplôme ou titre) est séparée de la formation et du cursus
  (`code`, `libelle`, `type`, `niveau_rncp`, `autorite_certificatrice`, `statut`).
  Elle est reliée au **cursus** (cible) et à la **formation** (« prépare ») ;
  les deux liens sont conservés (décision du porteur).

- **`Cursus`** est un chemin déterminé vers une certification, avec une
  `modalite` (`SCOLAIRE`, `APPRENTISSAGE`, `FORMATION_CONTINUE`, `MIXTE`).
  Une même certification a plusieurs cursus (scolaire via 2TNE, apprentissage
  direct, passerelle après CAP).

- **`CursusEtape`** ordonne les étapes (`cursus_id`, `formation_niveau_id`,
  `ordre`, `obligatoire`, `condition_entree`, `condition_sortie`).

- **`RelationFormation`** exprime la **structure nationale** entre formations
  (`formation_source_id`, `formation_cible_id`, `type_relation` :
  `REGROUPE`, `APPARTIENT_A`, `SPECIALISATION_DE`, ...).
  Exemple : `2TNE REGROUPE CIEL`, `2TNE REGROUPE MELEC`, etc.
  Cette relation n'implique pas qu'un élève suive toutes ces formations : le
  chemin réel de l'élève est porté par `CursusEtape`.

- **`TransitionCursus`** exprime les **orientations et passerelles** entre étapes
  (`formation_niveau_source_id`, `formation_niveau_cible_id`, `type_transition` :
  `ORIENTATION`, `PASSERELLE`, `REORIENTATION`, `POURSUITE_ETUDES`, ...).
  Elle est distincte de `RelationFormation` : l'une décrit la structure, l'autre
  les passages possibles.

- **`Classe`** est rattachée à un `FormationNiveau` (et non plus à un
  `NiveauClasse` nu), plus son `annee_scolaire`.

### Exemple de référence

```
Cursus BAC-PRO-CIEL-SCOLAIRE (cible : Bac Pro CIEL, modalité SCOLAIRE)
  1. 2TNE / SECONDE_PRO
  2. CIEL / PREMIERE_PRO
  3. CIEL / TERMINALE_PRO

Cursus BAC-PRO-CIEL-APPRENTISSAGE (cible : Bac Pro CIEL, modalité APPRENTISSAGE)
  1. CIEL / SECONDE_PRO
  2. CIEL / PREMIERE_PRO
  3. CIEL / TERMINALE_PRO
```

### Déroulé par phases (via le flux Forge)

La refonte est plus large que l'ADR-022 et une partie n'est pas encore utilisée
par l'application.
Elle est donc découpée en incréments courts, l'application restant verte
(`make check`) à chaque étape.

1. **Backbone** : `Formation` (+ `type`), `NiveauClasse` générique,
   `FormationNiveau`, `Referentiel` re-scopé sur `Formation` (retrait de
   `niveau_classe_id`).
   Migration des données 2TNE et CIEL.
   Affichage du tunnel via `FormationNiveau`.
   Résout le défaut d'origine (2TNE n'est plus « Bac Pro CIEL »), tunnel intact.
2. **`Certification`** et **`RelationFormation`** (`2TNE REGROUPE ...`).
3. **`Cursus`** et **`CursusEtape`** (le pivot académique) ; `Classe` repointée
   sur `FormationNiveau`.
4. **`TransitionCursus`** (passerelles) et historisation des versions de
   référentiel.

## Conséquences

- **Le tunnel de scénario reste fonctionnel** : `Scenario -> Referentiel` est
  conservé (le référentiel existe toujours, seulement re-scopé sur la formation).
- **La couche pédagogique de l'ADR-022 est intacte** : `Parcours`, `Palier`,
  `ProgressionParcours`, `ProgressionPalier` ne sont pas touchés, grâce au
  nommage `Cursus` distinct.
- **Correction métier durable** : le modèle couvre familles de métiers,
  spécialités hors famille, CAP à durée variable, apprentissage, passerelles et
  poursuites d'études, sans exception structurelle.
- **Rayon d'impact** : renommage `ReferentielNiveauClasse -> Referentiel`
  (table + FK aval des entités de contenu), ajout de six entités, réalignement de
  `Classe`.
  À conduire phase par phase pour garder l'application verte.
- **Specs à mettre à jour** : le JSON canonique déclare aujourd'hui une seule
  `formation` ; il évoluera pour porter la formation, ses `FormationNiveau` et,
  le cas échéant, ses relations, avec adaptation de l'importeur puis re-import.
- **Historisation des versions différée** (assumé) : on démarre avec un
  référentiel actif par formation, l'historique arrive en phase 4.
- **Exécution via le flux Forge uniquement** (`make:entity`, `make:relation`,
  `migration:make`/`migration:apply`, `entity:validate`), aucun SQL généré édité à
  la main.

## Réalisation (2026-07-22) — CRUD FormationNiveau (socle)

Première brique concrète de ce modèle : `FormationNiveau` reçoit un CRUD admin
(`/formation_niveau`, gardé par `socle.gerer`), généré par `forge make:crud`.

Cela tranche une question restée ouverte : qui crée un `formation_niveau` dans
l'application en marche. L'entité est obligatoire (`classe.formation_niveau_id`
NOT NULL) et lue partout (classe, suivi, mes-classes), mais n'avait aucun chemin
d'écriture hors fixtures. L'établissement compose désormais ses couples
formation × niveau à la main, dans le socle.

L'import du référentiel amène la `formation` et le `niveau_classe` (tous deux au
contrat du canonique). Le pont `formation_niveau` n'est, lui, pas au canonique :
il reste une donnée d'établissement, saisie via ce CRUD (ou semée par les fixtures
pour la démo, cf. `mvc/fixtures/structure.py`). Le reste du modèle (Cursus,
CursusEtape, TransitionCursus, Certification) demeure aux phases ultérieures.

### Alternatives écartées

- **Réutiliser le `Parcours` existant pour le cursus académique** : rejeté, cela
  ferait s'effondrer toute la mécanique pédagogique (paliers, progressions,
  scénarios, QCM) qui partage ce nom pour un autre concept.
- **Garder `Referentiel` en 1-1 sur la formation** : rejeté, une formation a des
  versions successives de référentiel ; le 1-n est nécessaire (même si
  l'historique est différé).
- **Rester sur `Formation -> NiveauClasse`** (avec un simple n-n de débouchés) :
  rejeté, cela ne couvre ni l'apprentissage (entrée directe en spécialité), ni
  les CAP à durée variable, ni les passerelles, ni les poursuites d'études.
- **Tout livrer d'un bloc** : rejeté au profit d'un déroulé par phases, pour
  garder l'application fonctionnelle et testée à chaque incrément.
