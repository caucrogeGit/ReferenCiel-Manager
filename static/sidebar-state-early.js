/* Application PRÉCOCE de l'état replié de la sidebar (anti-flash).

   Chargé SYNCHRONE dans le <head> : si l'utilisateur avait replié le panneau,
   on pose « hs-overlay-minified » sur <html> AVANT le premier rendu — les
   variantes hs-overlay-minified:* s'appliquent par ancêtre, la page se peint
   directement repliée, sans flash ouverture/fermeture.
   Le relais est pris après chargement par sidebar-state.js, qui synchronise
   Preline puis retire ce marqueur. CSP : fichier statique, pas de JS inline. */
(function () {
    try {
        if (localStorage.getItem('sidebar-minified') === '1') {
            document.documentElement.classList.add('hs-overlay-minified');
        }
    } catch (err) { /* stockage indisponible : rendu par défaut */ }
})();
