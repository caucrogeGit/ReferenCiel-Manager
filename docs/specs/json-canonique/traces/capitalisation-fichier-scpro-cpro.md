# Capitalisation - Exploitation d’un fichier `.scpro` exporté depuis CPRO

## 1. Objet du document

Ce document garde la trace du travail déjà réalisé autour d’un fichier `.scpro` exporté depuis CPRO.

Son objectif est simple : éviter de redécouvrir les mêmes choses à chaque reprise du projet RéférenCiel Manager.

Le fichier `.scpro` ne doit pas être traité comme un fichier isolé ou comme un format à deviner à nouveau.
Il fait partie d’une chaîne de transformation déjà cadrée :

```text
export CPRO .scpro
-> export ou conversion lisible .odt
-> contrôle avec les référentiels officiels
-> extraction ciblée pour un niveau de classe
-> JSON canonique de référentiel niveau-classe
-> schéma JSON
-> dictionnaire de données
-> import ou construction applicative
```

## 2. Décision principale

Le fichier `.scpro` exporté depuis CPRO est une **source exportée**.

Il ne devient pas directement le modèle applicatif de RéférenCiel Manager.

Il sert à produire ou vérifier un **JSON canonique de référentiel niveau-classe**.

Dans le cas travaillé, la cible est :

```text
JSON canonique CIEL 2TNE
```

Ce JSON formalise l’extraction des informations utiles pour une classe ou un niveau donné, notamment :

- formation ;
- niveau de classe ;
- pôles d’activités ;
- activités professionnelles ;
- tâches associées ;
- compétences ;
- critères d’évaluation ;
- résultats attendus ;
- indicateurs de réussite exploitables pédagogiquement ;
- relations activités-compétences ;
- provenance des données.

## 3. Ce que représente réellement le JSON produit

Le JSON issu du travail sur le `.scpro` et le `.odt` ne doit pas être appelé simplement “JSON de scénario”.

C’est trop réducteur.

La bonne formulation est :

```text
JSON canonique de référentiel niveau-classe
```

ou, pour le cas actuel :

```text
JSON canonique CIEL 2TNE
```

Il représente une vue structurée d’une partie du référentiel exploitable pour un niveau de classe donné.

Il ne décrit pas encore un parcours élève complet.

Il sert de socle à partir duquel RéférenCiel Manager pourra ensuite construire :

- des scénarios pédagogiques ;
- des starters Welcome ;
- des parcours ;
- des paliers ;
- des activités ;
- des checklists ;
- des évaluations par critères ;
- des suivis de progression.

## 4. Rôle respectif du `.scpro`, du `.odt` et du JSON canonique

### `.scpro`

Le fichier `.scpro` est l’export natif de CPRO.

Il sert de trace d’origine de l’extraction.

Il peut contenir une sélection issue d’un scénario CPRO, avec les éléments pédagogiques et référentiels mobilisés.

Règle :

```text
Le .scpro est une source de provenance, pas le format interne de RéférenCiel Manager.
```

### `.odt`

Le fichier `.odt` obtenu par export ou conversion depuis CPRO sert de version lisible et contrôlable humainement.

Il permet de vérifier plus facilement :

- les pôles ;
- les activités ;
- les compétences ;
- les critères ;
- les associations ;
- les formulations visibles dans l’export.

Règle :

```text
Le .odt sert au contrôle et à l’analyse, pas à la persistance applicative.
```

### JSON canonique

Le JSON canonique est la forme structurée retenue par RéférenCiel Manager.

Il sert à :

- stabiliser les données extraites ;
- documenter la provenance ;
- préparer le dictionnaire de données ;
- préparer le schéma JSON ;
- préparer les tests ;
- préparer l’import en base.

Règle :

```text
Le JSON canonique est la référence structurée de construction ou d’import.
```

## 5. Distinctions de vocabulaire à conserver

### Pôle d’activités, pas rôle

Dans le référentiel, on parle de :

```text
pôles d’activités
```

Il ne faut pas appeler cela des “rôles”.

Le terme `rôle` doit être réservé aux rôles applicatifs :

```text
eleve
professeur
administrateur
```

### Résultats attendus

Les résultats attendus sont liés aux activités professionnelles.

Exemple : une activité comme E1, E2, R1 ou R2 possède des tâches, des conditions d’exercice, une autonomie et des résultats attendus.

### Critères d’évaluation

Les critères d’évaluation sont liés aux compétences.

Ils permettent d’évaluer l’acquisition d’une compétence.

### Indicateurs de réussite

Les indicateurs de réussite sont des formulations pédagogiques exploitables dans RéférenCiel Manager.

Ils peuvent être :

- repris d’un résultat attendu ;
- repris d’un critère d’évaluation ;
- adaptés pour un niveau de classe ;
- reformulés par le professeur pour une activité, une checklist ou un scénario.

Formule à garder :

```text
résultats_attendus = liés aux activités professionnelles
criteres_evaluation = liés aux compétences
indicateurs_reussite = formulation pédagogique exploitable dans RéférenCiel Manager
```

## 6. Ce qui a déjà été établi sur le cas 2TNE / CIEL

Le travail précédent a permis de fixer cette idée :

```text
Le JSON CIEL 2TNE n’est pas une simple sauvegarde.
Il formalise une extraction ciblée des informations de référentiel utiles à un niveau de classe.
```

Le cas travaillé concerne notamment la classe de niveau :

```text
2TNE
```

Le document de référence 2TNE met en avant les compétences communes de la famille de métiers des transitions numérique et énergétique, notamment :

- CC1 : s’informer sur l’intervention ou sur la réalisation ;
- CC2 : organiser la réalisation ou l’intervention ;
- CC3 : analyser et exploiter les données ;
- CC4 : réaliser une installation ou une intervention ;
- CC5 : effectuer les opérations préalables ;
- CC6 : mettre en service ;
- CC7 : réaliser une opération de maintenance ;
- CC8 : renseigner les documents ;
- CC9 : communiquer avec le client et/ou l’usager.

Le référentiel Bac Pro CIEL structure ensuite le diplôme autour de pôles d’activités, d’activités professionnelles, de blocs de compétences et de critères.

Dans le travail précédent, pour le pôle :

```text
Réalisation et maintenance de produits électroniques
```

et l’activité :

```text
E1 - Étude et conception de produits électroniques
```

les compétences associées retenues étaient notamment :

```text
C03 - Participer à un projet
C04 - Analyser une structure matérielle et logicielle
C07 - Réaliser des maquettes et prototypes
```

Cette association doit être conservée comme trace de travail, mais elle doit rester vérifiable dans le JSON canonique et dans les sources.

## 7. Structure minimale attendue du JSON canonique

Le JSON canonique de référentiel niveau-classe doit contenir au minimum :

```json
{
  "type": "referentiel_niveau_classe",
  "identifiant": "ciel-2tne",
  "version": "0.1.0",
  "formation": {},
  "niveau_classe": {},
  "sources": [],
  "poles_activites": [],
  "activites_professionnelles": [],
  "competences": [],
  "criteres_evaluation": [],
  "resultats_attendus": [],
  "indicateurs_reussite": [],
  "relations": {
    "activites_competences": [],
    "competences_criteres": [],
    "activites_resultats_attendus": []
  },
  "provenance": {}
}
```

Le JSON réel peut être plus riche, mais il ne doit pas perdre ces familles d’informations.

## 8. Provenance minimale à conserver

Chaque élément important doit pouvoir indiquer son origine.

Exemples de champs utiles :

```json
{
  "source_id": "cpro-scenario-export",
  "source_type": "scpro",
  "source_fichier": "ReferenCiel Manager.scpro",
  "source_note": "Export CPRO utilisé comme source de sélection"
}
```

```json
{
  "source_id": "cpro-odt-export",
  "source_type": "odt",
  "source_fichier": "ReferenCiel Manager_04_07_2026.odt",
  "source_note": "Export lisible utilisé pour contrôle humain"
}
```

```json
{
  "source_id": "referentiel-bac-pro-ciel",
  "source_type": "pdf_officiel",
  "source_fichier": "referenciel-bac-pro-ciel.pdf",
  "source_note": "Référentiel officiel utilisé pour validation"
}
```

Règle :

```text
Toute donnée reprise, extraite, reconstruite ou adaptée doit conserver une trace de provenance.
```

## 9. Ce qu’il ne faut pas refaire

Ne pas refaire à chaque fois :

- redéfinir ce qu’est un `.scpro` dans le projet ;
- confondre `.scpro` et format interne de l’application ;
- repartir sur une V0 fichier ;
- créer `path.yml`, `palier.yml`, `qcm.yml` ou `checklist.yml` comme source principale ;
- appeler le JSON produit “JSON de scénario” ;
- confondre pôles d’activités et rôles applicatifs ;
- confondre résultats attendus, critères d’évaluation et indicateurs de réussite ;
- importer directement un export CPRO en base sans passer par un JSON canonique contrôlé ;
- oublier le fichier `.odt` comme trace de contrôle humain ;
- oublier que la base de données sera la vérité applicative en fonctionnement après import.

## 10. Procédure à suivre pour un nouvel export CPRO

Pour tout nouveau fichier `.scpro` :

1. conserver le fichier brut dans un dossier de sources ou d’archives ;
2. produire ou récupérer une version `.odt` lisible ;
3. créer une trace de provenance ;
4. identifier le niveau de classe concerné ;
5. identifier le référentiel officiel à utiliser pour contrôle ;
6. extraire les pôles, activités, compétences, critères et résultats attendus ;
7. produire ou compléter le JSON canonique ;
8. valider le JSON avec le schéma JSON ;
9. générer ou préremplir le dictionnaire de données ;
10. seulement ensuite envisager l’import en base.

## 11. Emplacements recommandés dans le dépôt

```text
docs/specs/json-canonique/traces/
  trace-creation-json-canonique-cpro-2tne.md
  capitalisation-fichier-scpro-cpro.md

docs/specs/json-canonique/examples/
  json-canonique-ciel-2tne.json

docs/specs/json-canonique/schemas/
  schema-json-canonique-referentiel-niveau-classe.json

sources/
  cpro/
    scpro/
    odt/
  referentiels/
```

Si le dépôt ne possède pas encore de dossier `sources/`, ne pas le créer sans ticket dédié.

Dans l’immédiat, placer ce document dans :

```text
docs/specs/json-canonique/traces/capitalisation-fichier-scpro-cpro.md
```

## 12. Décision finale à retenir

La chaîne correcte est :

```text
.scpro CPRO
-> .odt de contrôle
-> JSON canonique de référentiel niveau-classe
-> schéma JSON
-> dictionnaire de données
-> modèle Forge
-> base de données
```

Le `.scpro` est une source importante.

Le JSON canonique est l’artefact pivot.

Le dictionnaire de données est la documentation métier enrichie.

La base de données est la vérité applicative en fonctionnement.
