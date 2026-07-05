# Registre des sources — chaîne du JSON canonique

Ce dossier catalogue les **sources originelles** utilisées pour construire les JSON
canoniques métier, et trace leur provenance (instructions §4, §5, §8).

> Rappel de la chaîne (instructions §8) :
> `source originelle → extraction → JSON canonique → schéma → dictionnaire de données → …`
> Enregistrer une source **n'est pas** produire le JSON canonique : c'est le
> point d'entrée tracé de la chaîne.

## Emplacements

- `sources/` (ce dossier) — les **originaux bruts** (PDF officiels, exports CPRO
  `.scpro`/`.odt`, etc.) et ce registre.
- `traces/` — la **trace de création** de chaque JSON canonique (chaîne suivie,
  décisions, écarts). Voir `traces/trace-creation-json-canonique-ciel-2tne.md`.
- `schemas/` — les schémas JSON de validation (ticket 04).
- `examples/` — les JSON canoniques produits (tickets 03+).

> Les fichiers binaires originaux ne sont pas encore déposés dans `sources/` : ils
> ont été fournis sous forme de texte extrait. Déposer les PDF officiels ici sous
> les noms indiqués ci-dessous pour compléter la traçabilité.

## Règle de provenance

```text
Toute donnée reprise, extraite, reconstruite ou adaptée depuis une source
conserve une trace de provenance.
```

## Sources enregistrées

### SRC-REF-CIEL-BACPRO — Référentiel Bac Pro CIEL

- **Fichier** : `referenciel-bac-pro-ciel.pdf`
- **Nature** : référentiel officiel (Éducation nationale), diplôme de **niveau 4**.
- **Rôle dans la chaîne** : **source principale** de l'extraction niveau-classe
  vers le JSON canonique CIEL 2TNE (cible diplôme, surtout 1ʳᵉ/Tⁿᵉ).
- **Inventaire structurel** (repères, non exhaustif) :
  - **3 pôles d'activités** → 3 blocs → unités :
    - Réalisation et maintenance de produits électroniques → bloc 1 → **U2**
    - Mise en œuvre de réseaux informatiques → bloc 2 → **U31**
    - Valorisation de la donnée et cybersécurité → bloc 3 → **U32**
  - **Activités professionnelles** : E1–E5 (produits électroniques), R1, R2, R3,
    R5 (réseaux), D1–D3 (donnée/cyber). *R4 (Gestion de projet) relève du niveau 5,
    hors Bac Pro.*
  - **Compétences C01–C11** : C01 Communiquer, C03 Participer à un projet,
    C04 Analyser une structure matérielle et logicielle, C06 Valider la conformité
    d'une installation, C07 Réaliser des maquettes et prototypes, C08 Coder,
    C09 Installer les éléments d'un système électronique ou informatique,
    C10 Exploiter un réseau informatique, C11 Maintenir un système électronique ou
    réseau informatique. *C02 (Organiser) et C05 (Concevoir) = niveau 5, non
    mobilisées en Bac Pro.*
  - Chaque activité décrit **tâches**, **conditions d'exercice**, **résultats
    attendus** ; chaque compétence décrit **connaissances associées + niveaux
    taxonomiques (1–3)** et **critères d'évaluation**.

### SRC-REF-TNE-2NDE — Vademecum famille des métiers TNE (seconde)

- **Fichier** : `referenciel-2tne.pdf`
- **Nature** : Vademecum officiel, **classe de seconde** « famille des métiers des
  transitions numérique et énergétique » (septembre 2021).
- **Rôle dans la chaîne** : source du **niveau-classe 2ⁿᵈᵉ**. C'est ce qui est
  **réellement travaillé et évalué en seconde** avant l'orientation vers une
  spécialité (dont CIEL). **Indispensable** au JSON canonique CIEL 2TNE.
- **Inventaire structurel** :
  - Famille regroupant : MELEC, MFER, ICCER, MEE, **SN → CIEL**.
  - **9 compétences communes CC1–CC9** en 4 activités :
    - Préparation : CC1 S'informer, CC2 Organiser, CC3 Analyser/exploiter
    - Réalisation & mise en service : CC4 Réaliser, CC5 Opérations préalables,
      CC6 Mettre en service
    - Maintenance : CC7 Réaliser une opération de maintenance
    - Communication : CC8 Renseigner les documents, CC9 Communiquer avec le client
  - Chaque CC est déclinée en **compétences détaillées** (CC11, CC12, …) et
    **reliée aux compétences des cinq référentiels** de la famille (dont SN/CIEL).

### SRC-REF-CIEL-BTS — Référentiel BTS CIEL

- **Fichier** : `referenciel-bts-ciel.pdf`
- **Nature** : référentiel officiel, diplôme de **niveau 5**, options A
  (« Informatique et réseaux ») et B (« Électronique et réseaux »).
- **Rôle dans la chaîne** : **source de contexte** (poursuite d'études post-Bac).
  Hors extraction 2TNE immédiate ; utile pour la cohérence verticale et les
  indicateurs de réussite ambitieux.
- **Inventaire structurel** (repères) : 3 pôles par option, activités E1–E5 /
  R1–R5 / D1–D5, compétences C01–C11 (dépendantes de l'option), niveaux
  taxonomiques 1–4.

### SRC-STARTER-WELCOME-RESEAU — Starter « Welcome Réseau » (2TNE CIEL)

- **Emplacement** : `sources/starters/welcome-reseau/` (racine du dépôt, hors
  `docs/` en raison des ~30 Mo d'images). Voir son `MANIFESTE.md`.
- **Nature** : source **pédagogique interne** (instructions §4) — un parcours créé
  et éprouvé en classe par le professeur.
- **Rôle dans la chaîne** : **2ᵉ exemple canonique** (type *Starter Welcome*),
  complémentaire du référentiel niveau-classe. Il **façonne le contrat du JSON
  canonique** (ticket 02) et fournit une instance complète de la chaîne
  « définition » (parcours → paliers → dossier technique / QCM / activité /
  checklist / corrigé).
- **État** : numérisé — 4 paliers ; dossiers techniques + paliers 3-4 en markdown
  natif ; QCM/activité/checklist/corrigé des paliers 1-2 **transcrits des PDF**
  (originaux conservés) ; 33 images inventoriées.
- **Anomalies signalées** (voir MANIFESTE) : corrigés P1+P2 groupés dans un seul
  fichier ; palier 1 sans checklist ; format de checklist divergent P2 vs P3.

## Vocabulaire (confirmé par les sources)

- On parle de **pôles d'activités**, pas de *rôles* (instructions §6). Le terme
  `rôles` reste réservé aux rôles applicatifs (`eleve`, `professeur`, `admin`).
- **résultats attendus** = liés aux **activités professionnelles** ;
  **critères d'évaluation** = liés aux **compétences** ;
  **indicateurs de réussite** = formulation pédagogique exploitable (à dériver).

## À retenir pour la suite

- Le JSON canonique **CIEL 2TNE** est à l'**intersection** de `SRC-REF-TNE-2NDE`
  (couche famille, CC1–CC9, réellement travaillée en 2ⁿᵈᵉ) et de
  `SRC-REF-CIEL-BACPRO` (cible diplôme, C01–C11, activités E/R/D). Le **contrat**
  (ticket 02) doit articuler ces deux couches et leur **mapping**.
- La provenance ici est le **référentiel officiel** (pas un export CPRO). Un export
  `.scpro`/`.odt` CPRO pourra compléter la même extraction plus tard.
