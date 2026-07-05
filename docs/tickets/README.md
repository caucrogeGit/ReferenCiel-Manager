# Tickets — RéférenCiel Manager

Ce dossier organise la conduite du projet par **tickets**. Un ticket est une
unité de travail à périmètre explicite : il déclare ce qu'il fait, ce qu'il ne
fait pas, et ses critères de validation.

## Principe

- **Un ticket = une responsabilité.** On avance par petits incréments testés.
- **Périmètre explicite.** Chaque ticket liste le périmètre autorisé *et* le
  hors-périmètre.
- **Prémortem.** Avant de clore, on imagine comment le ticket aurait pu échouer
  malgré une apparence correcte, et on corrige.
- **Validation.** Un ticket n'est terminé que si ses critères de validation sont
  tous vérifiés, et que `git status --short` ne montre que les fichiers attendus.

## Anatomie d'un ticket

Un ticket décrit au minimum :

1. **Objectif** — le but, en une ou deux phrases.
2. **Périmètre autorisé** — les fichiers/dossiers que le ticket peut créer ou
   modifier.
3. **Hors périmètre** — ce que le ticket ne doit surtout pas toucher.
4. **Boucle de travail** — les étapes ordonnées.
5. **Test prémortem** — les causes probables d'échec silencieux.
6. **Critères de validation** — les conditions objectives de clôture.

## Garde-fous permanents

Valables pour tous les tickets, sauf décision structurante contraire (ADR) :

- La base de données est la vérité applicative en fonctionnement.
- Le JSON canonique est une référence de construction/import, pas un état.
- Pas de V0 fichier : aucun `path.yml`, `palier.yml`, `qcm.yml` ou
  `checklist.yml` comme base principale.
- On respecte l'esprit Forge (SQL visible, sécurité par défaut, générateurs).
- On ne supprime pas le briefing Forge de `AGENTS.md` / `CLAUDE.md`.

## Suivi

| Ticket | Sujet | Statut |
| --- | --- | --- |
| 00 | Installer le cadre projet dans le squelette Forge | En cours |

Les tickets suivants seront ajoutés au fil de la roadmap
(`docs/roadmap/roadmap-referenciel-manager.md`).
