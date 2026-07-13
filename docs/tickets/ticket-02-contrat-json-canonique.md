# Ticket 02 — Contrat du JSON canonique (enveloppe commune + référentiel niveau-classe)

> Ticket **documentaire** (spécification). Ne produit **pas** de JSON réel, ni de
> schéma, ni d'entité. Prérequis architectural déjà acté (ADR-004).

## Objectif

Spécifier le **contrat** du JSON canonique (la forme attendue, pas le contenu) :

1. une **enveloppe commune** à tous les JSON canoniques (discriminant de `type`,
   identifiant, version, sources, provenance) — pensée pour héberger aussi bien le
   type « référentiel niveau-classe » que le futur type « Starter Welcome » ;
2. le **corps du type « référentiel niveau-classe »** en **deux couches** :
   couche **famille TNE** (`CC1–CC9`) + couche **cible CIEL** (`C01–C11`,
   pôles/activités) + **mapping** entre les deux.

Fondé sur : la capitalisation `.scpro` (§7 squelette, §8 provenance, §10 procédure),
la trace `trace-creation-json-canonique-ciel-2tne.md` (deux couches), le registre
des sources, les deux référentiels (`SRC-REF-CIEL-BACPRO`, `SRC-REF-TNE-2NDE`) et le
starter Welcome Réseau (pour valider l'enveloppe commune).

## Périmètre autorisé

Créer / modifier **uniquement** :

- `docs/specs/json-canonique/contrat-referentiel-niveau-classe.md` (la spécification
  du contrat) ;
- au besoin, enrichir `docs/specs/json-canonique/README.md` (pointeur vers le
  contrat) ;
- `mkdocs.yml` (nav) et `docs/tickets/README.md` (statut) ;
- un **fragment d'illustration** minimal **dans** le contrat (pas un fichier JSON
  canonique séparé).

## Hors périmètre

- Pas de **JSON canonique réel complet** (ticket 03).
- Pas de **schéma JSON de validation** (ticket 04).
- Pas de **contrat complet du type « Starter Welcome »** — ici on ne pose que
  l'**enveloppe commune** ; le corps « starter » aura son propre ticket.
- Pas de dictionnaire de données, d'entité Forge, de SQL, de migration.
- Pas de **réorganisation du layout `sources/`** (adjacent, relève du ticket 01).
- Pas de dépôt des fichiers `.scpro` / `.odt` (non fournis à ce stade).
- Ne pas inventer de champs non fondés sur les sources.

## Boucle de travail obligatoire

1. Relire les entrées (capitalisation §7/§8/§10 ; trace CIEL 2TNE ; registre des
   sources ; structure des 2 référentiels ; structure du starter).
2. Définir l'**enveloppe commune** : `type`, `identifiant`, `version`, `sources[]`,
   `provenance{}` (modèle §8 : `source_id`, `source_type`, `source_fichier`,
   `source_note`). Vérifier qu'elle convient au starter comme au référentiel.
3. Spécifier le **corps « référentiel niveau-classe »** : `formation`,
   `niveau_classe`, `poles_activites[]`, `activites_professionnelles[]`
   (+ `taches`, `conditions_exercice`, `resultats_attendus`), `competences[]`
   (+ `criteres_evaluation`), `indicateurs_reussite[]`,
   `relations{activites_competences, competences_criteres, activites_resultats_attendus}`.
4. Ajouter la **couche famille** (`CC1–CC9`) et le **mapping** `CC ↔ C0x`.
5. Poser les **invariants** : identifiants uniques ; toute relation référence des
   ids existants ; provenance obligatoire pour tout élément repris/extrait ;
   distinctions de vocabulaire (voir prémortem).
6. Fournir un **fragment vérifiable** issu de la trace de travail (§6 de la
   capitalisation) : pôle « Réalisation et maintenance de produits électroniques »,
   activité **E1**, compétences **C03, C04, C07**.
7. Vérifier la **couverture** contre les 2 référentiels ; noter ce que le starter
   impose (ou non) à l'enveloppe commune.
8. Mettre à jour nav + `docs/tickets/README.md` ; lancer `make check`.

## Test prémortem (échecs plausibles malgré une apparence correcte)

- Le contrat ne modélise **qu'une couche** (oubli de la famille `CC1–CC9`) →
  régression vs la trace CIEL 2TNE.
- Confusion **`resultats_attendus` / `criteres_evaluation` / `indicateurs_reussite`**
  (rappel : liés aux activités / aux compétences / formulation pédagogique).
- On appelle les **pôles d'activités** des « rôles ».
- **Provenance rendue optionnelle** → perte de traçabilité (règle §8).
- On **glisse vers le JSON réel** (ticket 03) ou le **schéma** (ticket 04) au lieu du
  contrat.
- **Enveloppe commune trop couplée** au référentiel → inutilisable pour le Starter
  Welcome.
- On **invente des champs** non présents dans les sources.
- Le naming des traces diverge (`...-cpro-2tne` vs `...-ciel-2tne`) sans être aligné.

## Critères de validation

- [ ] Le contrat distingue **enveloppe commune** et **corps typé** (`type`).
- [ ] La couche **famille (CC1–CC9)**, la couche **CIEL (C01–C11)** et le **mapping**
      sont tous les trois spécifiés.
- [ ] Vocabulaire respecté : pôles ≠ rôles ; `resultats_attendus` / `criteres` /
      `indicateurs` distincts et correctement rattachés.
- [ ] **Provenance obligatoire**, modèle §8 repris.
- [ ] Un **fragment d'illustration vérifiable** (E1 / C03,C04,C07) est fourni.
- [ ] **Aucun** JSON canonique complet, schéma, entité ou SQL produit.
- [ ] `make check` vert ; nav et `docs/tickets/README.md` à jour.

## Notes de réconciliation (issues de l'analyse des sources)

1. Deux portes d'entrée de provenance **convergentes** : CPRO (`.scpro`/`.odt`) et
   référentiels officiels (PDF). Le même JSON canonique accepte plusieurs sources.
2. Le squelette §7 de la capitalisation est la **base** du corps « référentiel » ;
   la couche famille vient de la trace CIEL 2TNE.
3. Layout `sources/` (`cpro/`, `referentiels/`, `starters/`) : à ranger au ticket 01.
4. `.scpro`/`.odt` non déposés : CIEL 2TNE se construit d'abord depuis les
   référentiels ; les exports CPRO compléteront la provenance ensuite.
