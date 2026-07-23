/* Persistance du repli de la sidebar (retour porteur).

   Le repli/déploiement passe par le minifieur Preline
   (data-hs-overlay-minifier="#app-sidebar"), dont l'état est purement client :
   chaque navigation (clic dans l'arbre « Famille pédagogique », lien de menu…)
   rechargeait la page avec le panneau déployé. On mémorise donc le choix de
   l'utilisateur dans localStorage et on le restaure au chargement — c'est lui
   qui a la main, pas la navigation.

   CSP oblige (script-src 'self') : pas de JS inline, tout passe par ce fichier. */
(function () {
    var CLE = 'sidebar-minified';

    /* Mémoriser le choix à chaque clic sur le minifieur (délégation : survit
       aux régénérations). L'état se lit APRÈS le basculement Preline, d'où le
       report au tick suivant. */
    document.addEventListener('click', function (e) {
        if (!e.target || !e.target.closest) return;
        if (!e.target.closest('[data-hs-overlay-minifier="#app-sidebar"]')) return;
        setTimeout(function () {
            var side = document.getElementById('app-sidebar');
            if (!side) return;
            try {
                /* Preline pose « minified » sur le panneau (et
                   « hs-overlay-minified » sur le body). */
                localStorage.setItem(CLE, side.classList.contains('minified') ? '1' : '0');
            } catch (err) { /* stockage indisponible : tant pis, pas bloquant */ }
        }, 0);
    });

    /* Restaurer l'état replié au chargement. On passe par un clic sur le
       minifieur pour laisser Preline gérer son propre état ; à défaut (bouton
       absent), on pose la classe directement. Attendre `load` : Preline
       s'initialise après le parsing. */
    window.addEventListener('load', function () {
        var voulu = null;
        try { voulu = localStorage.getItem(CLE); } catch (err) { /* défaut : déployé */ }
        if (voulu === '1') {
            var side = document.getElementById('app-sidebar');
            if (side && !side.classList.contains('minified')) {
                var bouton = document.querySelector('[data-hs-overlay-minifier="#app-sidebar"]');
                if (bouton) { bouton.click(); } else {
                    side.classList.add('minified');
                    document.body.classList.add('hs-overlay-minified');
                }
            }
        }
        /* Retirer le marqueur précoce posé sur <html> (sidebar-state-early.js) :
           Preline porte désormais l'état réel ; sans ce retrait, un déploiement
           manuel resterait visuellement replié. */
        document.documentElement.classList.remove('hs-overlay-minified');
    });
})();
