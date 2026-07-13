# Cadre du projet : RéférenCiel Manager

> Document de cadrage métier principal.
> Il complète les instructions prioritaires
> (`docs/cadrage/instructions.md`), qui l'emportent en cas de tension.
> Décision structurante associée : `docs/adr/003-json-canonique-et-persistance-applicative.md`.

## 1. Ce qu'est RéférenCiel Manager

RéférenCiel Manager est une **application métier pédagogique persistée**, bâtie
sur le framework Forge.
Elle sert à **créer, organiser, affecter, suivre et
évaluer** des parcours pédagogiques pour différentes classes de niveau, à partir
de scénarios pédagogiques, de référentiels de formation, de JSON canoniques
métier et de starters Welcome réutilisables.

Ce n'est pas seulement un outil de création de parcours : c'est une application
de **conception, de diffusion, de suivi et d'évaluation** pédagogique, dont
l'état vivant réside en base de données.

## 2. Ce que RéférenCiel Manager n'est pas

- un gestionnaire de PDF ou un visualiseur de Markdown ;
- une V0 fichier ou un simple dossier de fichiers YAML ;
- un clone de CPRO, un ENT ou un LMS généraliste ;
- une simple interface CRUD sans métier.

Différence avec CPRO : CPRO suit et structure **l'évaluation par compétences** ;
RéférenCiel Manager structure **le parcours pédagogique qui conduit** à cette
évaluation.
Il peut s'inspirer de la logique CPRO sans en dépendre techniquement.

## 3. Les trois niveaux (formule de référence)

```text
JSON canonique          = référence structurée de construction ou d'import
Dictionnaire de données = documentation métier enrichie et canonique
Base de données         = vérité applicative en fonctionnement
```

| Niveau | Rôle | Ce que ce n'est pas |
| --- | --- | --- |
| **JSON canonique** | Référence structurée de construction ou d'import | Pas une sauvegarde technique ; pas la vérité en marche |
| **Dictionnaire de données** | Documentation métier enrichie et canonique | Pas un document purement manuel ; pas un simple export du JSON |
| **Base de données** | Vérité applicative en fonctionnement | Pas la source unique de conception |

Une fois un objet importé, modifié, publié ou affecté, l'application ne dépend
plus d'un fichier externe pour connaître son état réel : la base fait foi.

## 4. Sources et provenance

Les données proviennent de trois familles de sources :

- **Institutionnelles / officielles** : référentiel officiel Bac Pro CIEL,
  référentiels publiés par l'Éducation nationale, documents académiques et
  d'accompagnement.
- **Exportées / reconstruites** : fichiers `.scpro` CPRO, fichiers `.odt`
  exportés ou convertis depuis CPRO, exports structurés, JSON canoniques dérivés.
- **Pédagogiques internes** : starters Welcome (dont Welcome Réseau), dossiers
  techniques, QCM, checklists, activités, ressources professeur, contenus
  importés d'une autre instance.

Règle : **toute donnée reprise, extraite, reconstruite ou adaptée conserve une
trace de provenance**. La chaîne d'un référentiel niveau-classe est documentée
(ex. `trace-creation-json-canonique-cpro-2tne.md`) :

```text
.scpro CPRO -> .odt exporté -> référentiel officiel -> extraction niveau-classe
            -> JSON canonique métier -> dictionnaire de données -> import applicatif
```

## 5. JSON canonique de référentiel niveau-classe

Le JSON issu d'un `.scpro` CPRO et d'un `.odt` exporté **n'est pas un simple
JSON de scénario** : c'est un **JSON canonique de référentiel niveau-classe**
(ex. *JSON canonique CIEL 2TNE*).
Il formalise l'extraction du référentiel Bac
Pro CIEL pour un niveau de classe donné : formation, niveau, pôles d'activités,
activités professionnelles, tâches, résultats attendus, compétences, critères,
relations activité↔compétence, indicateurs de réussite, provenance.

**Vocabulaire** : le référentiel officiel parle de **pôles d'activités**, pas de
*rôles*. Le terme `rôles` est réservé aux rôles applicatifs (`eleve`,
`professeur`, `administrateur`).

## 6. Trois notions à ne pas confondre

```text
resultats_attendus   = liés aux activités professionnelles
criteres_evaluation  = liés aux compétences
indicateurs_reussite = formulation pédagogique exploitable dans RéférenCiel Manager
```

Les indicateurs de réussite peuvent être repris d'un résultat attendu ou d'un
critère, adaptés à un niveau de classe, ou reformulés par le professeur pour un
scénario, un starter, un parcours, une activité ou une checklist.

## 7. Chaîne pédagogique centrale

```text
Référentiel
-> extraction niveau-classe
-> JSON canonique de référentiel niveau-classe
-> compétences -> critères observables
-> scénario pédagogique -> starter Welcome
-> parcours -> affectation (classe ou élève)
-> paliers -> dossier technique -> QCM de compréhension
-> activité -> checklist
-> progression élève -> suivi professeur
-> évaluation par critères -> bilan professeur
```

Points forts :

- le **QCM** vérifie la compréhension d'un dossier technique ; il **ne valide pas
  une compétence** ;
- l'**activité** est le lieu d'observation des compétences ; l'évaluation se fait
  dans l'activité, à partir de **critères observables** ;
- l'**affectation** transforme un parcours disponible en travail réel ;
- la **progression** garde l'état réel de l'élève ; le **suivi professeur**
  identifie les élèves bloqués, en avance ou à évaluer.

## 8. Séparation définition / exécution

- **Définition pédagogique** (contenus conçus par le professeur) : référentiel,
  vue niveau-classe, compétence, critère, indicateur, scénario, starter,
  parcours, palier, dossier technique, QCM, activité, checklist, règle de passage.
- **Exécution élève** (état produit par l'usage) : affectation, progression,
  tentative et réponse QCM, checklist remplie, dépôt élève, validation
  professeur, évaluation, observation, bilan.

Règle forte : **un parcours publié et affecté ne doit pas changer sous les pieds
d'un élève.**

## 9. Versionnement

Un objet pédagogique publié n'est pas modifié librement s'il est déjà utilisé :
on affecte une **version publiée**, jamais un brouillon mutable.
Statuts :

```text
brouillon -> publie -> archive
```

Sont versionnés dès que nécessaire : référentiel, vue niveau-classe, scénario,
starter, parcours, palier, dossier technique, activité, QCM, checklist.

## 10. Sécurité et rôles (cadre)

Rôles minimaux : `eleve`, `professeur`, `administrateur`. Principes :

- un élève ne voit que ses propres parcours ;
- un professeur ne voit que ses classes ou celles autorisées ;
- les ressources professeur restent protégées, y compris contre l'accès direct
  par URL ou par QR code ;
- MFA disponible pour les comptes professeur et administrateur.

Le détail des permissions est fixé dans `docs/cadrage/instructions.md` (§19-20).

## 11. Ce que le cadrage ne fait pas encore

Le cadrage installe la méthode et la vision ; il **ne démarre pas** le
développement applicatif :

- pas de table SQL, d'entité Forge, de migration, de repository, de service ;
- pas de modification de `mvc/`, `app.py`, `config.py`, `schemas/`, `optins/`,
  `env/`, `requirements.txt` ;
- pas de fichier YAML de parcours (`path.yml`, `palier.yml`, `qcm.yml`,
  `checklist.yml`) comme base principale : la V0 fichier est écartée ;
- pas de JSON canonique CPRO ou Welcome Réseau complet, pas de parcours exemple,
  à ce stade.

La trajectoire de construction est décrite dans
`docs/roadmap/roadmap-referenciel-manager.md`.
