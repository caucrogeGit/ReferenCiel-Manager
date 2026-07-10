# Dictionnaire de données — Parcours

Documentation **métier enrichie** du domaine « parcours » : ce qui **organise le travail
élève** (instructions §12), en aval du starter et en amont de l'affectation. Objets
**persistés en base** (ADR-002).

> Place dans la chaîne : `scénario → starter Welcome → **parcours** → affectation →
> paliers → contenus`. Le starter est le **gabarit réutilisable** ; le **parcours** le met
> en œuvre (dérivé d'une version de starter) et se **découpe en paliers**.

## Principes

- **Nommage / types / relations** : conventions Forge (comme les autres dictionnaires).
- **Base = vérité** (ADR-002). Le parcours est **créé par le professeur** (dérivé d'un
  starter publié).
- **Versionnement (ADR-011)** : `Parcours` = identité stable ; `VersionParcours` = version
  (cycle de vie `brouillon`/`publie`/`archive`). Un parcours **publié et affecté ne change
  pas** sous les pieds de l'élève (instructions §…, jalon 4).

## Entités

### Parcours

L'**identité** d'un parcours, **dérivé** d'une version de starter réutilisable.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `titre` | string | oui | nom du parcours |
| `version_starter_id` | many_to_one → VersionStarter | oui | **starter-source** dont il dérive |

### VersionParcours

Une **version** d'un parcours (cycle de vie ; contenu rattaché).

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `parcours_id` | many_to_one → Parcours | oui | identité parente |
| `version` | string | oui | semver ; unique `(parcours_id, version)` |
| `statut` | string | oui | `brouillon` \| `publie` \| `archive` |

### Palier

Le **découpage du parcours** en étapes (ticket 16). Rattaché à une **version** de parcours.

| Champ | Type | Oblig. | Description / règle |
|---|---|:--:|---|
| `version_parcours_id` | many_to_one → VersionParcours | oui | version de parcours parente |
| `ordre` | integer | oui | rang 1..n, **unique** dans la version `(version_parcours_id, ordre)` |
| `titre` | string | oui | |
| `theme` | string | non | |
| `production_attendue` | string | non | ex. « Un câble droit conforme » |
| `dossier_technique_fichier` | string | oui | référence de contenu (bundle, opt-in `files`) |

## Relations (récapitulatif)

| Relation | Type Forge | Cardinalité |
|---|---|---|
| VersionStarter → Parcours | many_to_one (inverse) | 1 version de starter, n parcours dérivés |
| Parcours → VersionParcours | many_to_one (inverse) | 1 identité, n versions (ADR-011) |
| VersionParcours → Palier | many_to_one (inverse) | 1 version, n paliers |

## Règles métier & cycle de vie

- **Dérivation** : un parcours référence une `VersionStarter` (généralement `publie`).
- **Ordre des paliers** unique et contigu (1..n) dans la version de parcours.
- **Cycle de vie** sur `VersionParcours` (ADR-011) ; une version `publie` et **affectée**
  ne se modifie pas (jalon 4).
- **Contenus de palier** (dossier technique, QCM, activité, checklist) : tickets ultérieurs
  (19), rattachés au **Palier** — voir aussi le [dictionnaire Starter Welcome](dictionnaire-starter-welcome.md)
  (gabarit de contenu réutilisable).

## Portée

Couvre `Parcours`, `VersionParcours`, `Palier` (tickets 15-16). En amont : le
[**Starter Welcome**](dictionnaire-starter-welcome.md) (gabarit) ; en aval :
l'**affectation** et l'**exécution élève** (Bloc B, tickets 17+).
