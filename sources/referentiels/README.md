# Sources de référentiels — matériel de travail (NON canonique)

Ce dossier contient des **sources de travail** utilisées pour construire les
référentiels : exports/compilations issus de cpro-education, vademecum de famille
de métiers, etc.

> ⚠️ **Ces fichiers ne sont PAS canoniques.** Ils servent d'appui (structure,
> gain de temps), mais ne font pas foi. La vérité de construction reste le
> **canonique** dans `data/referentiels/*.json` (format `referentiel_niveau_classe`,
> validé contre le schéma et **contre cpro**), qui alimente l'importeur.

## Fichiers

- `referentiel-2TNE-complet-poles-activites-competences-criteres.json`
  Compilation de la **famille 2TNE entière** (compétences communes CC1-CC9 +
  les 5 spécialités : CIEL, MELEC, MFER, ICCER, MEE), avec pôles, activités,
  tâches codées, compétences et critères.
  Statut : **source de structure**. Divergences connues avec le canonique
  `2tne_ciel.json` (qui, lui, fait foi) : critères **paraphrasés** (le canonique
  a le verbatim cpro), **savoir-être non marqué**, et quelques associations
  activité→compétence moins complètes (R1-R3, D1-D3).

## Règle

Pour construire un nouveau canonique (ex. `2tne_melec.json`), on peut **s'appuyer**
sur ces sources, mais **chaque critère et association est validé contre cpro**
avant d'entrer dans `data/referentiels/`.
