# Ticket 22 : Bac à sable d'outils pédagogiques CIEL (décision d'architecture)

> Ticket **de décision** (cadrage).
> Produit **un ADR** et un **plan de tickets de
> suite**.
> Ne produit **aucun** outil, entité, contrôleur, vue ni migration : la
> réalisation relève des tickets que ce ticket aura décidés.
> La direction est
> laissée au jugement de l'agent Forge, dans les garde-fous ci-dessous.

## Contexte

Un collègue a généré (par IA, via Google AI Studio) une SPA pédagogique CIEL,
« **Portfolio CIEL** » (Lycée Sully).
Le porteur **apprécie ses outils
interactifs** et souhaite s'en **inspirer** pour offrir aux élèves un **bac à
sable** d'outils, mobilisable notamment depuis les activités **StarterWelcome**
(« que les welcomes pourraient utiliser »).

**On s'inspire des outils, on ne porte pas le build.** Le livrable du collègue est
un artefact React/Vite (sources non fournies) ; il est **structurellement
incompatible** avec ce projet (voir « Contraintes »).

### Où est la source d'inspiration

- Archive : `tmp/baociel-main.zip` (build minifié, 7 bundles empilés, un seul
  référencé par `index.html` : `assets/index-B-C6KRps.js`). Pas de sources.
- Stack du build : React 19 + react-router v7, **Tailwind via CDN**, imports React
  depuis **`aistudiocdn.com`** (importmap), icônes icons8, flux RSS sécurité
  (it-connect) via `api.rss2json.com`. Client-only, `localStorage`. **14
  `dangerouslySetInnerHTML`** (surface XSS si contenu externe non assaini).

### Inventaire des outils (routes du bundle), classés par faisabilité Forge

| Famille | Outils baociel | Voie Forge |
|---|---|---|
| **Calcul pur, sans état** | subnet-calculator, ohm's-law *calculator*, resistor-color-code, base64-encoder-decoder, password-generator, cron *describer/visualizer* | **SSR pur** : formulaire → POST → calcul **Python** (service testable) → rendu. **Zéro JS**, idiomatique Forge. |
| **Temps réel / animé** | oscilloscope-virtuel, rs232-simulator, ohm's-law *simulator* (sliders live), batak-pro (jeu de réflexes), Arduino « Blinky » | Nécessite du **JS vanilla servi depuis `'self'`** (nonce CSP), un module par outil. Pas de framework, pas de CDN. |

Environ **la moitié** des outils (les calculateurs) tombent naturellement dans le
modèle Forge sans dérogation.

## Objectif

**Décider** comment doter le projet d'un bac à sable d'outils pédagogiques
inspiré de baociel, et **planifier** sa réalisation.
Concrètement :

1. Trancher, dans **un ADR**, la **politique de rendu** des outils
   (SSR-pur d'abord vs hybride SSR + JS local servi depuis `'self'`), y compris la
   **politique JS client** du projet (activation ou non de `APP_CSP_NONCE_ENABLED`,
   modules JS locaux, interdiction CDN), c'est une décision structurante.
2. Décider le **modèle d'intégration** avec `StarterWelcome` : section `/sandbox`
   autonome d'abord, ou relation `StarterWelcome ↔ outil(s)` dès le départ
   (impacte le contrat d'entité + migration).
3. Produire un **plan de tickets de suite** (un ticket = un outil ou un petit lot),
   priorisé, avec un **premier incrément** recommandé (proposition : un
   calculateur SSR-pur, p. ex. `subnet-calculator`, pour valider le motif).

## Périmètre autorisé

Créer / modifier **uniquement** :

- `docs/adr/<NN>-bac-a-sable-outils-pedagogiques.md` (décision, format Forge :
  Statut, Date, Contexte, Décision, Conséquences, Alternatives écartées),
  numéro à attribuer à la suite des ADR projet existants ;
- ce fichier de ticket (statut / renvois) et, au besoin, de **nouveaux fichiers
  de tickets de suite** dans `docs/tickets/` (numérotés > 22) décrivant chaque
  incrément d'implémentation ;
- `docs/tickets/README.md` (statut) et `mkdocs.yml` (nav) si un document est ajouté ;
- éventuellement un pointeur dans `docs/roadmap/roadmap-referenciel-manager.md`.

## Hors périmètre

- **Aucune implémentation d'outil** : pas de contrôleur, de service, de vue, de
  route, de JS, ni de page `/sandbox` dans ce ticket.
- **Aucune modification de contrat d'entité, de SQL ni de migration**
  (l'intégration `StarterWelcome ↔ outil` est *décidée* ici, *réalisée* ailleurs).
- **Aucune reprise de code baociel** : ni React, ni Tailwind CDN, ni import depuis
  `aistudiocdn`, ni `dangerouslySetInnerHTML` sur contenu externe.
- Ne pas activer `APP_CSP_NONCE_ENABLED` dans ce ticket (la décision peut le
  *prévoir*, un ticket de suite l'*appliquera*).
- Ne pas déposer le zip ni ses bundles dans le dépôt (`tmp/` reste hors suivi).

## Garde-fous (rappel, cf. `docs/tickets/README.md`)

- **100% Forge** : outils construits en `mvc/` (contrôleurs/services/vues Jinja),
  routes explicites (ADR-029), via la CLI Forge quand un chemin existe. Pas de SPA.
- **CSP strict conservé** : `script-src 'self' 'nonce-…'`. **Aucun CDN**, aucun
  `unsafe-inline`. Tout JS éventuel est **local** (`'self'`) et chargé au nonce.
- **Sécurité par défaut** : CSRF sur les formulaires, pas de rendu HTML non assaini
  (le piège XSS de baociel ne doit pas être reproduit).
- **La base reste la vérité applicative** ; un outil sans état n'a pas à persister.

## Boucle de travail obligatoire

1. Ré-extraire `tmp/baociel-main.zip` au besoin ; confirmer l'inventaire d'outils
   et leur classement SSR-pur / JS-live (tableau ci-dessus).
2. Lire l'existant qui contraint la décision : `mvc/views/components/interactive.html`
   (charte « zéro JS », macros natives), `core/security/csp.py` (politique CSP),
   `config.py` (`APP_CSP_NONCE_ENABLED`), le contrat et les routes de
   `StarterWelcome` (`mvc/entities/starter_welcome/`, `mvc/routes/starter_welcome_routes.py`).
3. Rédiger l'**ADR** : Contexte (baociel + contraintes), Décision (rendu SSR-pur
   vs hybride ; politique JS client ; modèle d'intégration StarterWelcome),
   Conséquences, Alternatives écartées (dont « porter la SPA », écartée, motiver).
4. Écrire le **plan de tickets de suite** priorisé, avec le premier incrément
   recommandé et ses critères de validation esquissés.
5. Mettre à jour `docs/tickets/README.md`, la nav `mkdocs.yml` si besoin ; lancer
   `make check` (doc `mkdocs build --strict` incluse).

## Test prémortem (échecs plausibles malgré une apparence correcte)

- L'ADR **décide en réalité d'implémenter** (glisse hors périmètre) au lieu de
  cadrer + planifier.
- On **réintroduit un CDN** (Tailwind, aistudiocdn) ou `unsafe-inline` « pour aller
  vite » → CSP cassé, garde-fou violé.
- On calque l'archi baociel (**client-only + `dangerouslySetInnerHTML`**) au lieu du
  motif Forge (SSR + service Python testable).
- On **couple d'emblée** tous les outils à `StarterWelcome` alors qu'une section
  autonome suffirait pour le premier incrément (sur-ingénierie du modèle d'entité).
- **Confusion de vocabulaire** : « welcome » n'est **pas** un rôle mais l'entité
  `StarterWelcome` (activité starter rattachée à un `niveau_classe`, versionnée).
- L'ADR **oublie la politique JS client** (nonce, modules locaux) alors que les
  outils « live » en dépendront → décision incomplète.
- Numéro d'ADR **en collision** avec la numérotation projet existante.

## Critères de validation

- [ ] Un **ADR** existe, au format Forge, tranchant : rendu (SSR-pur vs hybride),
      politique JS client (CSP/nonce, local-only, zéro CDN), et intégration
      `StarterWelcome`.
- [ ] L'alternative « **porter la SPA React** » est explicitement **écartée et
      motivée** (CSP strict, zéro-JS, règle 100% Forge).
- [ ] Un **plan de tickets de suite** priorisé est fourni, avec un **premier
      incrément** recommandé (calculateur SSR-pur suggéré) et critères esquissés.
- [ ] **Aucun** outil, contrôleur, service, vue, route, JS, contrat, SQL ou
      migration produit ; `APP_CSP_NONCE_ENABLED` non modifié.
- [ ] `make check` vert ; `docs/tickets/README.md` et nav à jour ; `git status
      --short` ne montre que les fichiers attendus.

## Notes pour l'agent Forge

- La **décision de la suite t'appartient** : ce ticket te donne le contexte, les
  contraintes et un inventaire ; à toi de trancher l'architecture et de séquencer.
- Recommandation d'amorçage (non imposée) : **SSR-pur d'abord** + **section
  `/sandbox` autonome**, puis couplage `StarterWelcome ↔ outil` dans un second
  temps. Cela donne de la valeur vite, sans toucher au modèle d'entités ni au CSP.
- Rappel méthode projet : décision structurante = **ADR** ; ticket de programmation
  **fait à deux** (pairing) ; **valider la direction avant d'implémenter**.
