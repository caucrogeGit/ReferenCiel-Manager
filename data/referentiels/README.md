# Référentiels livrés (`data/referentiels/`)

JSON canoniques de **référentiel niveau-classe** (`type: referentiel_niveau_classe`)
**livrés avec le projet** et **versionnés**. Ce sont des **données de référence**,
distinctes du jeu de démo (`mvc/fixtures/`, purgeable) : elles constituent le socle
métier chargé en base **une fois** à la mise en service par l'établissement.

## Cycle

```text
sources/referentiels/*.pdf   (documents originels)
        │  extraction (procédure docs/procedures/creation-json-canonique-referentiel.md)
        ▼
data/referentiels/*.json     (JSON canoniques, CE dossier — versionnés)
        │  tools/charger_referentiels.py  (validation + import, idempotent)
        ▼
Base de données              (vérité applicative)
```

## Charger en base

```bash
.venv/bin/python tools/charger_referentiels.py          # charge tous les *.json du dossier
.venv/bin/python tools/charger_referentiels.py --check   # valide seulement (aucune écriture)
```

Le chargement est **idempotent** : réimporter un référentiel (même `identifiant`)
remplace son contenu (upsert best-effort, [ADR-010](../../docs/adr/010-importeur-referentiel-upsert-best-effort.md)).

## Ajouter un référentiel

1. Produis le JSON en suivant la procédure :
   [docs/procedures/creation-json-canonique-referentiel.md](../../docs/procedures/creation-json-canonique-referentiel.md).
2. Dépose-le ici (`json-canonique-<identifiant>.json`).
3. Vérifie : `tools/charger_referentiels.py --check`, puis charge.

## Notes

- Ce dossier est aussi la **source unique** du jeu de démo : la fixture
  `mvc/fixtures/referentiel.py` charge le CIEL 2TNE **depuis ici** (pas de copie
  divergente).
- Décision : [ADR-016](../../docs/adr/016-referentiels-livres-et-chargement-installation.md).
