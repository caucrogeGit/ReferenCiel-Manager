# Cadre du projet — RéférenCiel Manager

## Ce qu'est RéférenCiel Manager

RéférenCiel Manager est une **application métier pédagogique persistée**, bâtie
sur le framework Forge. Elle sert à construire, publier, affecter, évaluer et
suivre des objets métier pédagogiques (référentiels et parcours) à partir de
sources hétérogènes, tout en gardant une trace enrichie et documentée du sens
métier.

Ce n'est ni un simple visualiseur de fichiers, ni un générateur ponctuel de
documents : c'est une application dont l'**état vivant** est en base de données.

## Positionnement des trois niveaux

Le projet distingue clairement trois niveaux, qui ne se confondent pas :

| Niveau | Rôle | Ce que ce n'est pas |
| --- | --- | --- |
| **JSON canonique** | Référence structurée de construction ou d'import | Pas un fichier de sauvegarde ; pas la vérité en marche |
| **Dictionnaire de données** | Documentation métier enrichie et canonique | Pas un document purement manuel |
| **Base de données** | Vérité applicative en fonctionnement | Pas la source unique de conception |

Formule de référence :

```text
JSON canonique          = référence structurée de construction ou d'import
Dictionnaire de données = documentation métier enrichie et canonique
Base de données         = vérité applicative en fonctionnement
```

## Flux de construction

1. **Sources originelles** — exports CPRO, starters Welcome, référentiels
   officiels, documents pédagogiques, créations professeur.
2. **Transformation** — ces sources sont transformées en **JSON canoniques**
   métier : une forme structurée, stable et vérifiable.
3. **Dictionnaire de données** — généré ou prérempli à partir des JSON
   canoniques, puis enrichi des règles métier. Il devient la documentation
   canonique du domaine.
4. **Construction / import** — les JSON canoniques servent de référence pour
   construire ou importer les objets métier dans l'application.
5. **Persistance** — les objets métier utilisés, publiés, affectés, évalués ou
   suivis sont **persistés en base**, qui devient la vérité de l'application en
   fonctionnement.

```text
Sources → JSON canonique → (dictionnaire de données) → construction/import → Base de données
```

## Objets métier (aperçu, non implémenté à ce stade)

Le domaine visé comprend, à terme, des objets tels que référentiels, parcours,
paliers, évaluations et suivis. Leur modélisation Forge (entités, tables,
migrations) est **hors du périmètre du cadrage** : elle sera traitée dans des
tickets ultérieurs, selon la roadmap.

## Ce que ce ticket de cadrage ne fait pas

Le cadrage installe la méthode ; il **ne démarre pas** le développement :

- pas de table SQL, pas d'entité Forge, pas de migration ;
- pas de repository, pas de service métier ;
- pas de modification de `mvc/`, `app.py`, `config.py`, `schemas/`, `optins/`,
  `env/` ni `requirements.txt` ;
- pas de fichier YAML de parcours (`path.yml`, `palier.yml`, `qcm.yml`,
  `checklist.yml`) comme base principale ;
- pas de JSON canonique CPRO ou Welcome Réseau complet, pas de parcours exemple.

## Principes directeurs

- **La base est la vérité en marche.** Tout ce qui vit dans l'application est
  persisté.
- **Le JSON canonique est une référence, pas un état.** Il construit et importe,
  il ne remplace pas la base.
- **Le dictionnaire de données est enrichi, pas figé.** Il part du JSON canonique
  et reçoit les règles métier.
- **La V0 fichier est écartée.** Aucun retour à des fichiers plats comme base
  principale.
- **On respecte l'esprit Forge.** SQL visible, sécurité par défaut, générateurs
  plutôt que contournements, décisions structurantes en ADR.
