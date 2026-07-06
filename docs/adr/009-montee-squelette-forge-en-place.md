# ADR-009 — Montée de squelette Forge en place, guidée par un manifeste de propriété

## Statut

Accepté (2026-07-06).

> Encadre la manière dont le projet **suit l'évolution du framework Forge** (dépôt
> public qui bouge souvent), sans « tout reprendre » à chaque fois.

## Date

2026-07-06

## Contexte

Forge évolue régulièrement (paquet `forge-mvc` **et** squelette émis par
`forge new`). RéférenCiel Manager, en tant que **banc d'essai** (ADR-005), doit
récupérer ces apports fréquemment, mais **sans casser** son contenu métier, son
historique git ni son environnement.

Une première tentative de migration **par déplacement de dossiers**
(`mv Test → ReferenCiel-Manager`) a **cassé le `.venv`** : un environnement virtuel
contient des **chemins absolus** (shebangs, `pyvenv.cfg`) et n'est **pas
déplaçable**. Elle a aussi imposé un **force-push** qui réécrit l'historique public.

Le problème de fond recouvre **deux niveaux distincts** :

1. **Le framework** (`forge-mvc`, installé via un pin git dans `requirements.txt`) :
   une mise à jour = un **bump de pin** + réinstallation.
2. **Le squelette** (fichiers `app.py`, `mvc/`, `optins/registry.py`, CI, gabarit
   ADR…) : une mise à jour = rafraîchir les **fichiers appartenant au squelette**
   sans toucher aux **fichiers du projet**.

Rien ne permet de deviner automatiquement *qui possède quel fichier* : il faut le
**déclarer**.

## Décision

1. **Montée en place, jamais par déplacement.** On récupère les apports du
   squelette **dans le dossier existant** du projet. Aucun dossier n'est déplacé ni
   rencommé : le `.venv` et le `.git` (historique + `origin`) restent en place. Le
   push est un **fast-forward** (pas de réécriture d'historique).

2. **Manifeste de propriété.** L'opération est pilotée par un manifeste explicite
   qui classe chaque fichier/dossier en **squelette** (écrasable depuis un
   `forge new` neuf), **projet** (jamais touché), **pin** (bump du commit) ou
   **fusion idempotente**. Le manifeste et la procédure rejouable vivent dans
   [docs/procedures/montee-squelette-forge.md](../procedures/montee-squelette-forge.md).

3. **Environnement rafraîchi sur place.** Le `.venv` est mis à jour par
   `make setup`. Piège documenté : un pin git à **version inchangée** (`1.0.0rc2`)
   n'est **pas re-fetché** par pip → on **force** la réinstallation
   (`pip install --force-reinstall --no-deps`) de `forge-mvc` et
   `forge-mvc-testing` au commit cible.

## Conséquences

- Procédure **rejouable** et sûre : le risque « venv cassé » est éliminé, aucun
  force-push, aucun contenu métier perdu.
- Le manifeste doit être **tenu à jour** quand on ajoute un fichier structurant
  (nouveau fichier squelette ou projet).
- Une automatisation locale pourra s'appuyer dessus (`make forge-upgrade` pour le
  cas fréquent, `make skeleton-check` pour lister les écarts squelette).
- Le *bon* endroit reste le framework : le [retour-002](../banc-essai/retour-002-commande-skeleton-upgrade.md)
  propose une commande `forge skeleton:upgrade`.

## Alternatives écartées

- **Déplacer / renommer le dossier** (Test devient le projet) : rejeté — casse le
  `.venv` (chemins absolus) et impose un force-push.
- **Fork + merge git du squelette** : rejeté — le squelette n'est pas un dépôt
  commun avec le projet ; les historiques sont sans ancêtre commun.
- **Tout refaire à la main à chaque fois** : rejeté — c'est précisément le coût
  qu'on veut supprimer.

## Suite

- Rédiger le [retour-002](../banc-essai/retour-002-commande-skeleton-upgrade.md)
  (proposition `forge skeleton:upgrade`).
- Implémenter l'automatisation locale (`make forge-upgrade`, `make skeleton-check`)
  une fois le manifeste éprouvé sur une vraie mise à jour.
