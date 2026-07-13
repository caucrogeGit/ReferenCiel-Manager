# Procédure — Créer un JSON canonique de référentiel niveau-classe

Guide opérationnel pour produire un fichier **JSON canonique** de type
`referentiel_niveau_classe`, de la collecte des sources jusqu'à l'import en base.

> **Cadre** : le JSON canonique est la **référence structurée d'import**, pas une
> sauvegarde ; la vérité applicative reste la base de données. Pas de « V0 fichier »
> ([ADR-002](../adr/002-json-canonique-et-persistance-applicative.md),
> [spécification](../specs/json-canonique/README.md)).

## Vue d'ensemble

```text
Sources officielles → JSON canonique → (dictionnaire de données) → import → Base
```

| # | Étape | Livrable | Où |
|---|---|---|---|
| 1 | Collecter et enregistrer les sources | entrées `SRC-…` | [registre-des-sources.md](../specs/json-canonique/registre-des-sources.md) |
| 2 | Tracer la provenance et les décisions | fiche de trace | [traces/](../specs/json-canonique/traces/) |
| 3 | Rédiger le JSON conforme au contrat | `mon-referentiel.json` | [contrat](../specs/json-canonique/contrat-referentiel-niveau-classe.md) |
| 4 | Valider contre le schéma | 0 erreur | [schemas/](../specs/json-canonique/schemas/) |
| 5 | Importer | référentiel en base | espace admin (ADR-008) |

## Prérequis

- Les **sources officielles** (référentiel PDF Éducation nationale, Vademecum de
  famille, éventuel export `.scpro`/`.odt` CPRO).
- Un identifiant **kebab-case** pour le document (ex. `ciel-2tne`).
- Le [contrat](../specs/json-canonique/contrat-referentiel-niveau-classe.md) et le
  [schéma](../specs/json-canonique/schemas/schema-json-canonique-referentiel-niveau-classe.json)
  sous les yeux.

---

## Étape 1 — Collecter et enregistrer les sources

Dans [registre-des-sources.md](../specs/json-canonique/registre-des-sources.md),
déclare **chaque** source avec un `source_id` stable. Une source, une ligne.

Champs d'une entrée `sources[]` (contrat §3) :

| Champ | Obligatoire | Exemple |
|---|:--:|---|
| `source_id` | oui | `referentiel-bac-pro-ciel` |
| `source_type` | oui | `pdf_officiel` \| `scpro` \| `odt` \| `starter` |
| `source_fichier` | oui | `referenciel-bac-pro-ciel.pdf` |
| `source_note` | non | « Référentiel officiel utilisé pour validation » |

> **Écart de provenance assumé** : on peut entrer dans la chaîne au nœud
> *référentiel officiel* plutôt que *CPRO* — c'est légitime, il suffit de le tracer
> (étape 2, champ `provenance.point_entree = "referentiel_officiel"`).

## Étape 2 — Tracer la provenance et les décisions

Avant d'écrire le JSON, crée une **fiche de trace** dans
[traces/](../specs/json-canonique/traces/) (modèle :
[trace CIEL 2TNE](../specs/json-canonique/traces/trace-creation-json-canonique-ciel-2tne.md)).
Elle enregistre :

- les **sources retenues** et leur rôle ;
- les **décisions structurantes** (ex. l'*extraction à deux couches* : couche
  **famille** + couche **cible diplôme**, avec le mapping entre les deux) ;
- le **vocabulaire** (on parle de **pôles d'activités**, jamais de « rôles »).

Cette fiche est **antérieure** au JSON : elle explique le *pourquoi* des choix.

## Étape 3 — Rédiger le JSON conforme au contrat

Le document = **enveloppe commune** + **corps typé** (`type`).

### 3.1 Enveloppe commune (contrat §2)

| Champ | Type | Exemple |
|---|---|---|
| `type` | enum | `"referentiel_niveau_classe"` |
| `identifiant` | kebab-case | `"ciel-2tne"` |
| `version` | semver | `"0.1.0"` |
| `sources` | array | voir étape 1 |
| `provenance` | object | `{ "date_extraction": "AAAA-MM-JJ", "methode": "extraction manuelle", "point_entree": "referentiel_officiel" }` |

### 3.2 Cadre (contrat §4.1)

| Champ | Contenu |
|---|---|
| `formation` | `{ "code", "intitule" }` (ex. Bac Pro CIEL) |
| `niveau_classe` | `{ "code", "intitule" }` (ex. `2TNE`) |

### 3.3 Couche cible (contrat §4.2)

| Collection | Champs principaux de chaque élément |
|---|---|
| `poles_activites[]` | `id`, `intitule`, `source_ids` |
| `activites_professionnelles[]` | `id`, `code` (`E1`/`R2`/`D3`…), `intitule`, `pole_id`, `taches[]`, `conditions_exercice{ moyens[], autonomie }`, `resultats_attendus[]` (`{ id, libelle }`), `source_ids` |
| `competences[]` | `id`, `code` (`C01`…`C11`), `intitule`, `connaissances[]` (`{ libelle, niveau_taxonomique }`), `criteres_evaluation[]` (`{ id, libelle }`), `source_ids` |
| `indicateurs_reussite[]` | `id`, `libelle`, `origine` (`resultat_attendu` \| `critere` \| `reformulation`), `ref` (id d'origine), `source_ids` |

### 3.4 Couche famille (contrat §5)

| Collection | Champs |
|---|---|
| `famille_competences[]` | `code` (`CC1`…`CC9`), `intitule`, `source_ids` |

### 3.5 Relations (contrat §4.3 et §5)

```text
relations {
  activites_competences[]       : { activite: <code>,   competences: [<code>...] }
  competences_criteres[]        : { competence: <code>,  criteres: [<id>...] }
  activites_resultats_attendus[]: { activite: <code>,    resultats: [<id>...] }
  cc_competences[]              : { cc: <CCx>,           competences: [<C0x>...] }  # mapping famille ↔ cible
}
```

## Invariants à respecter (contrat §6)

- Tout `id` / `code` est **unique** dans sa collection.
- Toute relation ne référence que des `id`/`code` **existants** (références résolues).
- Tout élément extrait porte un **`source_ids` non vide** (provenance obligatoire).
- Garder les trois notions **distinctes** :

  ```text
  resultats_attendus   = liés aux activités professionnelles
  criteres_evaluation  = liés aux compétences
  indicateurs_reussite = formulation pédagogique dérivée (à formuler)
  ```

- On dit **pôles d'activités**, jamais « rôles » (réservés à `eleve`, `professeur`,
  `administrateur`).

## Étape 4 — Valider contre le schéma

Le [schéma JSON](../specs/json-canonique/schemas/schema-json-canonique-referentiel-niveau-classe.json)
(Draft 2020-12) est la **porte de validation des uploads** (ADR-008).

- **Vérifié par le schéma** : familles obligatoires, types, énumérations (`type`,
  `source_type`, `point_entree`, `origine`), motifs des codes (`E1`/`R2`/`D3`,
  `C0x`, `CCx`), semver, niveaux taxonomiques 1–4. Les champs additionnels sont
  tolérés (le document « peut être plus riche »).
- **Vérifié par l'importeur** (hors schéma) : **unicité** des `id`/`code` et
  **résolution** des références de `relations` — invariants non exprimables en
  JSON Schema pur.

Valider en ligne de commande (service `canonical_validator` (`mvc/services/canonical_validator.py`)) :

```bash
.venv/bin/python - <<'PY'
import json
from mvc.services.canonical_validator import validate_referentiel_canonical
data = json.load(open("chemin/vers/mon-referentiel.json", encoding="utf-8"))
erreurs = validate_referentiel_canonical(data)
print("OK — conforme au schéma" if not erreurs else "\n".join(erreurs))
PY
```

`validate_referentiel_canonical(data)` retourne la **liste triée** des erreurs —
**vide** si le document est conforme.

## Étape 5 — Importer en base

- **Référentiel livré (voie recommandée)** : dépose le JSON dans
  **`data/referentiels/`** (versionné) et charge-le avec le script
  d'installation ([ADR-016](../adr/016-referentiels-livres-et-chargement-installation.md)) :

  ```bash
  .venv/bin/python tools/charger_referentiels.py --check   # valide seulement
  .venv/bin/python tools/charger_referentiels.py           # valide + importe (idempotent)
  ```

- **Ajout ponctuel** : espace **admin → Référentiel → Importer un référentiel**
  (upload, ADR-008). Le fichier est **validé** (étape 4) puis persisté par le
  service `referentiel_importer` (`mvc/services/referentiel_importer.py`) —
  **upsert best-effort** par `identifiant` (réimporter remplace ; un échec unitaire
  n'interrompt pas l'import et figure au rapport).
- **Jeu de démo** : la fixture callable `mvc/fixtures/referentiel.py` charge le
  référentiel **depuis `data/referentiels/`** (source unique) au `forge fixtures:load`.

> ⚠️ Le réimport d'un référentiel **déjà utilisé** par des évaluations
> (`evaluation_critere` référençant ses critères) échoue (contrainte FK) : le
> chargement est prévu **à l'installation**, sur une base vierge de données
> pédagogiques (voir ADR-016).

---

## Squelette de démarrage

Point de départ vierge, conforme à l'enveloppe et aux collections attendues
(remplace les valeurs et complète les collections). **Une seule source montrée**,
ajoute-en autant que nécessaire.

```json
{
  "type": "referentiel_niveau_classe",
  "identifiant": "mon-referentiel",
  "version": "0.1.0",
  "sources": [
    {
      "source_id": "referentiel-officiel",
      "source_type": "pdf_officiel",
      "source_fichier": "referentiel-officiel.pdf",
      "source_note": "Référentiel officiel de référence"
    }
  ],
  "provenance": {
    "date_extraction": "2026-01-01",
    "methode": "extraction manuelle",
    "point_entree": "referentiel_officiel"
  },
  "formation": { "code": "", "intitule": "" },
  "niveau_classe": { "code": "", "intitule": "" },
  "poles_activites": [
    { "id": "pole-1", "intitule": "", "source_ids": ["referentiel-officiel"] }
  ],
  "activites_professionnelles": [
    {
      "id": "act-1",
      "code": "E1",
      "intitule": "",
      "pole_id": "pole-1",
      "taches": [],
      "conditions_exercice": { "moyens": [], "autonomie": "" },
      "resultats_attendus": [
        { "id": "ra-1", "libelle": "" }
      ],
      "source_ids": ["referentiel-officiel"]
    }
  ],
  "competences": [
    {
      "id": "comp-1",
      "code": "C01",
      "intitule": "",
      "connaissances": [
        { "libelle": "", "niveau_taxonomique": 1 }
      ],
      "criteres_evaluation": [
        { "id": "cr-1", "libelle": "" }
      ],
      "source_ids": ["referentiel-officiel"]
    }
  ],
  "famille_competences": [
    { "code": "CC1", "intitule": "", "source_ids": ["referentiel-officiel"] }
  ],
  "indicateurs_reussite": [
    { "id": "ind-1", "libelle": "", "origine": "critere", "ref": "cr-1", "source_ids": ["referentiel-officiel"] }
  ],
  "relations": {
    "activites_competences": [
      { "activite": "E1", "competences": ["C01"] }
    ],
    "competences_criteres": [
      { "competence": "C01", "criteres": ["cr-1"] }
    ],
    "activites_resultats_attendus": [
      { "activite": "E1", "resultats": ["ra-1"] }
    ],
    "cc_competences": [
      { "cc": "CC1", "competences": ["C01"] }
    ]
  }
}
```

> **Modèle complet** : pour un exemple réel et riche, pars de
> [json-canonique-ciel-2tne.json](../specs/json-canonique/examples/json-canonique-ciel-2tne.json)
> (2 sources, 3 pôles, 5 activités, 8 compétences) et adapte-le.

## Checklist finale

- [ ] Sources déclarées au registre (`source_id` stables).
- [ ] Fiche de trace créée (sources + décisions + vocabulaire).
- [ ] Enveloppe complète : `type`, `identifiant`, `version`, `sources`, `provenance`.
- [ ] Cadre : `formation`, `niveau_classe`.
- [ ] Couches remplies : pôles, activités, compétences (+ famille et mapping).
- [ ] Chaque élément extrait porte un `source_ids` **non vide**.
- [ ] `id`/`code` uniques ; relations pointant vers des éléments existants.
- [ ] Distinction `resultats_attendus` / `criteres_evaluation` / `indicateurs_reussite` respectée.
- [ ] Validation schéma : **0 erreur** (étape 4).
- [ ] Import admin réussi (rapport sans erreur).

## Références

- Spécification : [README JSON canonique](../specs/json-canonique/README.md)
- Contrat : [contrat-referentiel-niveau-classe.md](../specs/json-canonique/contrat-referentiel-niveau-classe.md)
- Schéma : [schema-json-canonique-referentiel-niveau-classe.json](../specs/json-canonique/schemas/schema-json-canonique-referentiel-niveau-classe.json)
- Exemple : [json-canonique-ciel-2tne.json](../specs/json-canonique/examples/json-canonique-ciel-2tne.json)
- Registre des sources : [registre-des-sources.md](../specs/json-canonique/registre-des-sources.md)
- Décision : [ADR-002](../adr/002-json-canonique-et-persistance-applicative.md), import : ADR-008
- Services : `canonical_validator` (`mvc/services/canonical_validator.py`), `referentiel_importer` (`mvc/services/referentiel_importer.py`)
