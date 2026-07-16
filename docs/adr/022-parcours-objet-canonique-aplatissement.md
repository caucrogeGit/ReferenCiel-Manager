# ADR-022 : Parcours comme objet canonique, aplatissement du cœur pédagogique

**Statut :** Accepté
**Date :** 2026-07-15

> **Note (ADR-025, 2026-07-16).** Les objets de cet ADR ont été renommés selon
> la sémantique de l'Éducation nationale : **Parcours → Séquence** et
> **Palier → Séance** (entités `Sequence`, `Seance`, `ProgressionSequence`,
> `ProgressionSeance`). Les cardinalités et la logique décrites ici restent
> valables telles quelles. Voir [ADR-025](025-renommage-sequence-seance.md).

## Contexte

Le cœur pédagogique empile aujourd'hui cinq niveaux au-dessus du palier :

```
NiveauClasse
 └─ StarterWelcome        (gabarit réutilisable)
     └─ VersionStarter    (version publiée du gabarit)
         └─ Parcours       (instance dérivée d'une version de starter)
             └─ VersionParcours  (version publiée du parcours)
                 └─ Palier
```

Deux couches « objet + version » se superposent : `StarterWelcome`+`VersionStarter`
puis `Parcours`+`VersionParcours`.
Les paliers ne sont pas rattachés au parcours mais à sa version.
L'affectation d'un élève passe par `AffectationParcours` vers une `VersionParcours`.

Le porteur juge cette hiérarchie surchargée pour l'usage réel.
L'application est liée à **un seul établissement**, chaque année scolaire repart
**vierge**, et un parcours se rattache à un **NiveauClasse** (par exemple `2TNE`)
qui est **stable d'une année sur l'autre**.
Un parcours est donc naturellement réutilisable d'année en année sans couche de
versionnement, et le gabarit `StarterWelcome` n'apporte pas de valeur distincte
du parcours lui-même.

Cette décision **révise ADR-019** et **contredit le cadrage/canonique**
(`docs/specs/json-canonique/contrat-starter-welcome.md`, dictionnaires) : elle
impose donc un ADR et une mise à jour des specs.

## Décision

1. **`Parcours` devient l'objet canonique unique** du domaine pédagogique.
   Il absorbe l'identité du starter : `identifiant` (unique), `titre`,
   `presentation`, `niveau_classe_id`, un `statut` de publication
   (brouillon/publié) et les indicateurs métier `activite_glissante` /
   `ordre_impose`.
   Il **contient directement ses `Palier`**.

2. **Entités supprimées** : `StarterWelcome`, `VersionStarter`,
   `VersionParcours`, `AffectationParcours`, `ProgressionEleve`,
   `InscriptionEleve`, `AffectationProfesseurClasse`.

3. **Cardinalités cibles** :

   ```
   AnnéeScolaire 1─n Classe
   NiveauClasse  1─n Classe
   NiveauClasse  1─n Parcours
   Parcours      1─n Palier
   Scénario      1─1 Parcours          (table pivot scenario_parcours, id technique)
   Élève         n─1 Classe            (FK eleve.classe_id)
   Classe        n─n Professeur        (pivot classe_professeur)
   Professeur    n─n Parcours          (pivot)
   Professeur    n─n Scénario          (inchangé)
   Élève         1─n ProgressionParcours n─1 Parcours
   ```

4. **Lien Scénario ↔ Parcours** : table pivot `scenario_parcours` à identifiant
   technique, avec `scenario_id` et `parcours_id` **uniques chacun**.
   Le 1-1 est ainsi garanti, la navigation est symétrique (du scénario vers le
   parcours et l'inverse), et chaque objet peut exister sans l'autre puis être
   rattaché dans n'importe quel ordre.

5. **`ProgressionParcours` devient l'entité associative** entre un élève et un
   parcours.
   Elle appartient à **un seul élève** (`n-1 Élève`) et vise **un seul parcours**
   (`n-1 Parcours`), et porte l'état de progression.
   Elle remplace à la fois `AffectationParcours` (l'affectation) et
   `ProgressionEleve` (le suivi).
   `ProgressionPalier` et `BilanEleve`, qui pointaient sur `ProgressionEleve`,
   sont repointés sur `ProgressionParcours`.

6. **`Palier` est repointé** de `VersionParcours` vers `Parcours`
   (`palier.parcours_id`).

7. **L'année scolaire est conservée mais portée par la seule `Classe`**
   (`Classe n-1 AnnéeScolaire`).
   Elle est retirée des jointures `Élève↔Classe` et `Classe↔Professeur` :
   l'année d'un élève ou d'un professeur se déduit de sa classe.

8. **Le dossier technique devient un conteneur de ressources.**
   Une nouvelle entité **`DossierTechnique`** (`titre`, `palier_id`) est
   rattachée au palier en **1-1** et **remplace** le champ
   `palier.dossier_technique_fichier` (on passe d'un fichier unique à un
   contenu structuré).
   Elle contient **1-n `RessourceDossier`** :

   ```
   Palier ─1─1─ DossierTechnique ─┬─ 1─n RessourceDossier
                                  └─ 1─1 QCM de validation ── questions…
   ```

   `RessourceDossier` est une **table unique typée** : `type`
   (`markdown` | `video` | `audio` | `lien`), `titre`, `ordre`,
   `dossier_technique_id`, et le contenu selon le type :

   | `type` | champ porteur |
   |--------|---------------|
   | `markdown` | `contenu` (texte) |
   | `video` | `media_ref` (référence média) |
   | `audio` | `media_ref` (référence média) |
   | `lien` | `url` (lien externe, non téléchargé) |

   **Audio et vidéo sont traités uniformément** par une même `media_ref` :
   la vidéo pointe aujourd'hui la table `videos` de `forge-mvc-video`, et
   l'audio la référencera de la même façon une fois `forge-mvc-audio` passé
   à un modèle persisté (retour terrain 022, F58).
   L'ingestion (streaming vers média stocké) passera par `media_fetcher`
   (yt-dlp) branché sur les opt-ins.

9. **Le `QCM` est repointé** de `Palier` vers `DossierTechnique`
   (`qcm.dossier_technique_id`, 1-1) : le dossier porte son QCM de validation
   (avec son `seuil_validation` existant).
   L'`Activité` reste sous le `Palier` ; l'obligation de réussir le QCM avant
   l'activité est une **règle de progression** (logique métier), pas une FK.

## Conséquences

- **Perte du gel de version pour les élèves** (assumée) : sans `VersionParcours`,
  modifier un parcours affecte les progressions en cours.
  Acceptable en mono-établissement à année vierge.
- **Pas d'historique d'inscription élève** (assumé) : un élève est dans une seule
  classe à la fois ; changer d'année = changer de classe.
  L'information reste reconstructible depuis la base si un besoin apparaît.
- **Réutilisation naturelle** : un parcours rattaché à un `NiveauClasse` stable se
  réemploie d'année en année sans versionnement.
- **Rayon d'impact large** (~moitié de l'application) : contrôleurs, routes,
  modèles et vues des sept entités supprimées à retirer ; fixtures `bloc_b` à
  réécrire ; FK aval (`Palier`, `ProgressionPalier`, `BilanEleve`) à recâbler.
- **Specs à mettre à jour** : le contrat canonique `starter_welcome` devient un
  contrat `parcours` ; dictionnaires de données à réviser.
  Le retrait de « Starters Welcome » et « Paliers » du menu latéral (déjà fait)
  découle de cette décision.
- **Exécution via le flux Forge** uniquement (`make:entity`, `make:relation`,
  `migration:make`/`migration:apply`), par étapes, sur branche.
  L'application est en développement (données = jeu de démo) : pas de migration
  de données de production à préserver, les fixtures sont reconstruites.
- **Câblage média différé** : les opt-ins `forge-mvc-video`/`forge-mvc-audio`
  ne sont pas activables en l'état (dépendance `core.http.bearer` absente du
  Core installé, retour terrain 022 / F57).
  `RessourceDossier` est donc **modélisée maintenant** (le champ `media_ref`
  existe), mais l'ingestion et la lecture média seront branchées une fois le
  Core aligné.
  L'audio est déjà modélisé comme la vidéo (référence unique) en anticipant son
  passage en BDD (F58).

## Alternatives écartées

- **Garder `VersionParcours`** (aplatir seulement la couche starter) : rejeté.
  Le porteur veut les paliers directement sous le parcours, et le gel de version
  n'est pas nécessaire dans un établissement unique à année vierge.
- **Fusionner `Scénario` et `Parcours` en une seule entité** puisque le lien est
  1-1 : rejeté.
  Ce sont deux faces distinctes (conception d'un côté, mise en œuvre de l'autre),
  créées indépendamment ; le pivot à identifiant technique les garde séparées.
- **FK nullable directe pour le lien Scénario-Parcours** au lieu d'un pivot :
  rejeté au profit du pivot, qui évite une colonne nulle et donne une navigation
  symétrique.
