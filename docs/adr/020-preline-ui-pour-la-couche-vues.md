# ADR-020 : Preline UI comme boîte à outils front de la couche vues

**Statut :** Accepté
**Date :** 2026-07-14

## Contexte

La navigation applicative était une barre horizontale à menus déroulants
(`partials/nav.html` + `static/nav.css`, CSS pur, sans JS).
Elle sature avec le nombre de rubriques du projet : « Structure scolaire »
compte une dizaine de liens, « Exécution » autant.
Le porteur a validé un modèle de sidebar verticale (repliable, overlay mobile)
issu de la bibliothèque Preline UI.

La règle projet « 100 % Forge » (ADR-003, [[forge-only-hard-rule]]) vise le
**code applicatif** : backend, `mvc/`, contrats, base, opt-ins.
Le porteur a précisé que la **couche vues (CSS et JS)** peut, elle, accueillir
des éléments hors Forge.
Ce cadre autorise l'adoption d'une bibliothèque front.

Le socle CSS est déjà Tailwind v4 (config CSS-first dans `static/src/input.css`,
build via `npm run build:css`).
Preline v4 est compatible Tailwind v4 et fournit ses variantes sous forme de
`@custom-variant` (fichier `preline/variants.css`), plus un bundle JS autonome.

## Décision

1. **Preline UI** devient la boîte à outils front de la couche vues.
   Il est réservé à la présentation : aucune logique métier, aucun accès
   données, aucun contournement d'un générateur Forge.

2. **CSS** : `static/src/input.css` importe `preline/variants.css` (variantes
   `hs-overlay-*`, `hs-accordion-*`, `hs-dropdown-*`) et scanne le bundle
   Preline via `@source`.
   Le rebuild reste `npm run build:css`.

3. **JS** : le bundle navigateur est vendu dans le dépôt
   (`static/vendor/preline.js`, copié depuis `node_modules`) et chargé en fin de
   `layouts/base.html`.
   Il s'auto-initialise au chargement, ce qui convient à un rendu serveur
   multi-pages.

4. **Charte préservée** : les composants Preline sont réhabillés avec les tokens
   du projet (`text-muted`, `bg-forge-soft`, `border-line`, `rounded-card`...).
   On n'introduit pas la palette `stone`/`neutral` ni le mode sombre du modèle
   d'origine.

5. **Navigation** : `partials/nav.html` devient une sidebar filtrée par rôle
   (les gardes `can(...)` d'ADR-016 sont conservées à l'identique).
   Les macros de rendu vivent dans `components/nav_macros.html`.
   `layouts/base.html` porte le layout (sidebar fixe, décalage du contenu via
   `static/sidebar.css`, barre supérieure mobile) et élargit le contenu
   (`max-w-7xl` fluide au lieu de `max-w-3xl`).

## Conséquences

- Le dépôt gagne une dépendance front (`preline` dans `package.json`) et un
  fichier vendu (`static/vendor/preline.js`, ~430 Ko non compressé).
  À réactualiser manuellement lors d'une montée de version Preline.
- Le masquage par rôle reste du confort : les routes sensibles demeurent
  protégées par `guarded(...)`, inchangé.
- L'ancien `static/nav.css` est supprimé.
  Le décalage du contenu utilise `:has()` (non exprimable en utilitaires
  Tailwind), isolé dans `static/sidebar.css`.
- Le repli « minifié » masque les libellés et laisse les icônes ;
  les accordéons de domaine sont alors repliés.

## Alternatives écartées

- **Garder la barre horizontale** : ne passe pas à l'échelle avec le nombre de
  rubriques, débordait déjà.
- **Réécrire une sidebar en CSS pur (sans JS, sans Preline)** : faisable et sans
  dépendance, mais le porteur a validé le modèle Preline et autorisé le JS front.
  Le coût de réimplémentation (overlay accessible, repli, accordéons) n'était
  pas justifié.
- **Copier le markup Preline tel quel** : il s'appuie sur la palette `stone` et
  le mode sombre, hors charte, et suppose un build incluant ses variantes.
  Rejeté au profit d'un réhabillage aux tokens du projet.
