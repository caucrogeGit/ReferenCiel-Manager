# ADR-027 : Scénario hors référentiel (matières non adossées)

**Statut :** Accepté
**Date :** 2026-07-19

## Contexte

L'ADR-023 a rendu le **référentiel obligatoire** dès la création d'un scénario
(périmètre voie professionnelle, référentiel CIEL). Or, en lycée professionnel,
certaines matières **ne sont pas adossées à un référentiel professionnel** :

- les **enseignements généraux** (français, mathématiques, histoire-géographie,
  langues, EPS, arts appliqués) ;
- parfois la PSE, le chef-d'œuvre, une co-intervention.

Un professeur de ces matières doit pouvoir concevoir un scénario (et sa séquence
appairée) **sans compétences ni critères** issus d'un référentiel. La règle de
finalisation actuelle exige `contexte complet + ≥1 activité + ≥1 critère`, tous
tirés du référentiel : **impossible à satisfaire sans référentiel**. Cas rare,
mais réel.

## Décision

Le référentiel devient **facultatif** pour un scénario.

1. **`referentiel_id` nullable** : un scénario peut exister **sans** référentiel
   (exception explicite à l'ADR-023).
2. **Discriminant implicite** : l'**absence** de référentiel (`referentiel_id`
   IS NULL) est le **seul** signal. Pas de champ ni de case à cocher supplémentaire.
3. **Finalisation à deux régimes** (complétude *dérivée*, ADR-026) :
   - **avec référentiel** → contexte complet **+ ≥1 activité + ≥1 critère** (règle
     actuelle) ;
   - **sans référentiel** → **contexte complet seul**.
4. **Tunnel** : l'étape **« Liaison référentiel »** est **grisée / inactive**
   quand `referentiel_id` est NULL (il n'y a rien à lier).
5. **Paire inchangée** : le 1-1 Scénario ↔ Séquence et la frontière A (ADR / SEQ-02)
   ne bougent pas ; un scénario hors référentiel a simplement `referentiel_id`
   NULL et des pivots compétences/critères vides.

## Conséquences

- **Exception à l'ADR-023** : le référentiel reste la règle **par défaut**, mais
  n'est plus une **contrainte dure**. L'ADR-023 est amendé sur ce point.
- `recalculer_statut` (finalisation) doit **se brancher** sur `referentiel_id`
  NULL pour ne pas exiger activité/critère.
- Le contrôle de création du scénario doit **accepter l'absence** de référentiel.
- **Migration** : `scenario.referentiel_id` passe de `NOT NULL` à **nullable**
  (additive, non destructive).
- **Manque aval (hors périmètre)** : l'**évaluation par critères observables**
  (`evaluation_critere → critere_observable`) **ne s'applique pas** à un scénario
  sans référentiel — il n'a pas de critères. Le professeur évaluera autrement
  (appréciation libre, critères « maison »). À concevoir dans un ticket dédié.

## Alternatives écartées

- **Case à cocher « liaison obligatoire »** (un booléen dédié sur le scénario) :
  ajoute une information **redondante** avec « `referentiel_id` est NULL ». Écartée
  au profit du discriminant implicite, plus simple.
- **Choix explicite à la création** (« adossé / hors référentiel ») : même
  redondance, et alourdit le formulaire de création. Écarté.
- **Référentiel toujours obligatoire (statu quo ADR-023)** : bloque purement et
  simplement les matières non adossées. Écarté.

## Références

- `docs/adr/023-modele-generique-voie-professionnelle.md` (référentiel obligatoire,
  amendé ici).
- `docs/adr/026-versionnement-objets-pedagogiques-publies.md` (« finalisé » =
  complétude dérivée ; la finalisation à deux régimes s'y rattache).
- `docs/specs/data-dictionary/dictionnaire-scenario.md` (règle de finalisation).
