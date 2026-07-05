# Trace de création — JSON canonique CIEL 2TNE

Ce document trace la **provenance** et la **chaîne de construction** du JSON
canonique de référentiel niveau-classe **CIEL 2TNE** (instructions §4, §6, §8).
Il est **antérieur** au JSON lui-même : il enregistre les sources et les décisions,
il ne contient pas encore le JSON canonique ni le schéma.

## Objet

Formaliser l'extraction du référentiel pour le niveau-classe **2ⁿᵈᵉ CIEL** (classe
de seconde, famille des métiers des transitions numérique et énergétique, spécialité
visée CIEL), sous forme de **JSON canonique de référentiel niveau-classe**.

## Point d'entrée dans la chaîne

La chaîne cible des instructions §4 est :

```text
.scpro CPRO → .odt exporté → référentiel officiel → extraction niveau-classe
            → JSON canonique → dictionnaire de données → import applicatif
```

**Écart de provenance assumé** : ici, la source n'est **pas** un export CPRO mais
directement les **référentiels officiels** (PDF Éducation nationale). On entre donc
dans la chaîne au nœud **« référentiel officiel »**. Un export `.scpro`/`.odt` CPRO
pourra, ultérieurement, compléter ou recouper la même extraction ; il n'est pas
requis pour ce niveau-classe.

## Sources retenues

Voir le registre : `../sources/README.md`.

| Source | Rôle pour CIEL 2TNE |
| --- | --- |
| `SRC-REF-TNE-2NDE` (Vademecum famille TNE, 2ⁿᵈᵉ) | **Couche famille** : compétences communes CC1–CC9 réellement travaillées/évaluées en 2ⁿᵈᵉ |
| `SRC-REF-CIEL-BACPRO` (Bac Pro CIEL, niveau 4) | **Cible diplôme** : pôles, activités E/R/D, compétences C01–C11, résultats attendus, critères, niveaux taxonomiques |
| `SRC-REF-CIEL-BTS` (BTS CIEL, niveau 5) | **Contexte** : poursuite d'études, cohérence verticale (facultatif) |

## Décision structurante : une extraction à deux couches

Le niveau-classe **2ⁿᵈᵉ** est particulier : l'élève n'est pas encore dans la
spécialité CIEL mais dans la **famille TNE**. Le JSON canonique CIEL 2TNE doit donc
articuler :

1. **Couche famille (2ⁿᵈᵉ réelle)** — activités et **compétences communes CC1–CC9**
   (+ compétences détaillées CC11, CC12, …) du Vademecum TNE ;
2. **Couche cible CIEL** — **pôles d'activités**, **activités professionnelles**
   (E1–E5, R1–R3, R5, D1–D3), **compétences C01–C11**, avec pour chaque compétence
   ses **connaissances associées + niveaux taxonomiques** et ses **critères
   d'évaluation** ; pour chaque activité ses **tâches**, **conditions d'exercice**
   et **résultats attendus** ;
3. **Mapping famille ↔ CIEL** — la correspondance CC ↔ C0x (le Vademecum TNE fournit
   déjà des liens compétences communes ↔ compétences des référentiels).

Distinctions à préserver (instructions §7) :

```text
resultats_attendus   = liés aux activités professionnelles
criteres_evaluation  = liés aux compétences
indicateurs_reussite = formulation pédagogique exploitable (dérivée, à formuler)
```

**Vocabulaire** : pôles d'activités, pas *rôles*.

## Étapes (à venir, hors de ce document)

1. **Ticket 02** — Définir le **contrat** du JSON canonique référentiel
   niveau-classe (structure à deux couches + mapping ci-dessus).
2. **Ticket 03** — Produire le **JSON canonique CIEL 2TNE minimal** conforme au
   contrat, avec provenance renseignée.
3. **Ticket 04** — Définir le **schéma JSON** de validation (`../schemas/`).
4. **Ticket 08+** — Dictionnaire de données puis modélisation Forge.

## Journal

- **2026-07-05** — Sources officielles fournies et enregistrées
  (`SRC-REF-CIEL-BACPRO`, `SRC-REF-TNE-2NDE`, `SRC-REF-CIEL-BTS`). Écart de
  provenance (référentiel officiel, non CPRO) acté. Décision « extraction à deux
  couches » posée comme entrée du contrat (ticket 02). Aucun JSON produit à ce stade.
