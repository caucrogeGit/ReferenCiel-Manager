# ADR-024 : Génération PDF côté application avec WeasyPrint

**Statut :** Accepté
**Date :** 2026-07-16

## Contexte

La section Titre du tunnel de scénario doit proposer, quand un scénario est
finalisé, le téléchargement d'une version PDF du scénario.

Forge ne fournit aucune brique PDF, et c'est cohérent.
La génération de PDF n'est pas une fonction du runtime WSGI.
Elle vit côté application, ou dans un opt-in à créer.

Deux avis du framework convergent sur la trajectoire.
Une capacité PDF réutilisable a bien sa place, à terme, dans un opt-in
`forge-mvc-pdf` (principe du noyau minimal plus briques opt-in).
Mais la politique de stabilité terrain de Forge recommande d'éprouver d'abord
l'usage côté application, puis de généraliser en opt-in une fois le besoin
prouvé.

Une contrainte de périmètre tranche pour le court terme.
Sur ce projet, tout le développement reste côté application.
Nous ne développons pas Forge lui-même, qui est une dépendance installée.
Construire l'opt-in `forge-mvc-pdf` relèverait du dépôt Forge, pas de cette
application.

## Décision

Nous générons le PDF **côté application**, avec **WeasyPrint**.

WeasyPrint rend un template Jinja en HTML puis en PDF.
C'est le geste le plus idiomatique pour Forge, déjà basé sur Jinja.
La mise en page reste un template, versionné avec le reste des vues.
La licence est BSD, compatible avec la trajectoire MIT de Forge.
Les dépendances système nécessaires (Pango, cairo, gdk-pixbuf, harfbuzz) sont
présentes sur la machine de développement.

Nous isolons une **couture d'extraction** vers le futur opt-in.

- `mvc/services/pdf.py` expose `render_pdf(html) -> bytes`, générique et sans
  connaissance métier.
  C'est le cœur destiné à migrer tel quel dans `forge-mvc-pdf`.
- `mvc/services/scenario_pdf.py` construit le HTML du scénario depuis un template
  et délègue la conversion à `render_pdf`.
  C'est le contenu, spécifique à l'application, qui reste ici.

`weasyprint` est ajouté à `requirements.txt`.
C'est la première dépendance tierce de l'application, hors paquets Forge.

L'accès est gardé.
La route `GET /conception/scenario/{id}/pdf` vit sous le préfixe `/conception`
(RBAC `conception.gerer`).
Elle refuse un scénario non finalisé.

## Conséquences

Le téléchargement PDF est disponible en un clic pour un scénario finalisé.

Le déploiement doit fournir les libs système de WeasyPrint.
C'est un prérequis à documenter pour la mise en production.

La frontière `render_pdf` (générique) versus `scenario_pdf` (métier) rend la
promotion ultérieure en opt-in `forge-mvc-pdf` mécanique.
Le jour venu, `render_pdf` migre dans le paquet Forge et l'application le
consomme, sans toucher au contenu.

## Alternatives écartées

**fpdf2**, pur Python et sans dépendance système.
La mise en page se pose à la main, sans template.
On s'éloigne de l'esprit Jinja de Forge et on duplique un travail de rendu que
le template exprime déjà.

**Vue imprimable plus impression navigateur**, sans aucune dépendance.
L'utilisateur passe par la boîte de dialogue d'impression du navigateur.
Ce n'est pas le téléchargement direct en un clic demandé.

**Créer tout de suite l'opt-in `forge-mvc-pdf`**.
C'est la bonne cible à terme, mais c'est un chantier dans le dépôt Forge, hors
du périmètre de cette application.
Il sera engagé une fois l'usage éprouvé sur le terrain.
