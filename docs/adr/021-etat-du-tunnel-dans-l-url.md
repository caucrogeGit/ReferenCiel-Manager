# ADR-021 : État du tunnel dans l'URL, régénération partielle par fragments

**Statut :** Accepté
**Date :** 2026-07-14

## Contexte

L'éditeur de scénario (ADR-019) est un tunnel de saisie sur un agrégat :
étapes Titre, Contexte, Liaison référentiel, Ressources, dont l'étape Liaison
est un maître-détail imbriqué (pôles vers activités, compétences vers critères).

Le porteur pose une contrainte structurante : on ne quitte jamais la page
maître.
Changer d'étape, de pôle actif, de compétence active, cocher un critère,
ajouter une ressource ne doivent provoquer aucun rechargement complet.

Deux pièges se présentent.
Le premier est la tentation d'une SPA masquée : porter l'état côté client en
JavaScript, avec un comptage dupliqué et une logique métier hors du serveur.
Le second est un éditeur inutilisable sans JavaScript, contraire à l'esprit
Forge (explicite, pas de magie).

Le socle front vend déjà HTMX et Preline (ADR-020).
Forge expose `render(..., raw=True)`, qui rend un template sans le layout : de
quoi renvoyer un fragment.

## Décision

1. **L'état du tunnel vit dans l'URL, jamais côté client.**
   La query string porte l'étape et la sélection courante :
   `?etape=titre|contexte|liaison|ressources`, `&pole=<id>`,
   `&competence=<id>`, `&fragment=<cible>`.
   Aucun état n'est gardé en mémoire du navigateur.

2. **La complétion est dérivée des données, jamais persistée.**
   Une étape est faite si le titre est rempli, si un champ de contexte est
   saisi, si un référentiel est rattaché avec au moins une liaison, si une
   ressource existe (voir `_steps`).
   Aucune colonne, aucune migration ne sont ajoutées pour l'UI : l'état est
   non-falsifiable et reconstruit à chaque requête.

3. **Chaque interaction porte un `href` ET un `hx-get`/`hx-post` vers la même
   URL.**
   Avec JavaScript, HTMX intercepte et remplace un fragment ciblé.
   Sans JavaScript, le navigateur suit le lien ou poste le formulaire, et la
   page rend le même état à la bonne étape.
   Une seule route sert les deux cas : la dégradation gracieuse est gratuite,
   pas un second chemin de code.

4. **Répartition des rôles : Preline tient le chrome, HTMX porte les données.**
   Preline gère la sidebar, les overlays, les accordéons.
   HTMX gère la régénération partielle des fragments métier.
   Pas de state client, pas de logique de comptage dupliquée en JS.

5. **Détection serveur par l'en-tête `HX-Request`.**
   Le contrôleur rend le partial seul via `render(..., raw=True)` quand
   l'en-tête est présent, la page complète sinon.
   Le cochage unitaire (`basculer_activite`, `basculer_critere`) renvoie le
   bloc maître-détail concerné pour que le compteur de la colonne de gauche
   suive ; le POST global `enregistrer_liaison` reste en place pour le mode
   sans JavaScript.

6. **Sécurité inchangée.**
   Tout `hx-post` porte le `csrf_token` comme un formulaire classique.
   Les routes de cochage sont gardées par le préfixe `/conception`
   (`conception.gerer`, ADR-016), au même titre que les autres routes de
   conception.

## Conséquences

- Le tunnel reste entièrement utilisable sans JavaScript : navigation par
  liens, cochage par bouton, enregistrement par POST.
- Aucune persistance ajoutée pour l'interface : pas d'entité, pas de migration,
  pas de colonne.
- Cette doctrine fixe le modèle d'interaction des écrans métier suivants
  (`mon_parcours`, `evaluation`, `suivi`, `bilan_eleve`) : état dans l'URL,
  fragments serveur, dégradation gracieuse, zéro state client.
- Charger HTMX active d'un coup les `hx-get` déjà présents (inertes jusqu'ici)
  dans les vues CRUD : recherche, tri et pagination deviennent réactifs, sans
  y toucher, en ciblant `#crud-results`.

## Alternatives écartées

- **State client en JavaScript (SPA masquée)** : duplique le comptage et la
  logique métier hors du serveur, casse la dégradation gracieuse, contraire à
  l'esprit Forge.
- **Deux chemins de code séparés (une route API JSON pour HTMX, une route HTML
  pour le sans-JS)** : double la surface à maintenir et fait diverger les deux
  comportements.
  Une seule route qui rend soit la page, soit le fragment, garde les deux
  modes en phase par construction.
- **Persister l'étape courante et la complétion en base** : impose une
  migration pour une préoccupation purement UI, et rend l'état falsifiable.
