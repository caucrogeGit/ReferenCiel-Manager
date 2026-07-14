/* Surlignage de la rubrique active dans la sidebar.
   Côté client : le contexte de rendu Forge n'expose pas la route courante et on
   ne modifie pas le framework. On compare window.location.pathname aux liens de
   la sidebar (plus long préfixe gagnant), on marque le lien actif et on ouvre
   l'accordéon parent le cas échéant.

   Chargé APRÈS preline.js : les accordéons sont déjà initialisés, on force donc
   l'ouverture nous-mêmes (classe .active sur le <li>, révélation du contenu). */
(function () {
    function run() {
        var side = document.getElementById('app-sidebar');
        if (!side) return;

        var path = window.location.pathname.replace(/\/+$/, '') || '/';
        var best = null, bestLen = -1;

        side.querySelectorAll('a[href^="/"]').forEach(function (a) {
            var href = (a.getAttribute('href') || '').replace(/\/+$/, '') || '/';
            var match = href === '/'
                ? path === '/'
                : (path === href || path.indexOf(href + '/') === 0);
            if (match && href.length > bestLen) { best = a; bestLen = href.length; }
        });

        if (!best) return;
        best.classList.add('is-active');
        best.setAttribute('aria-current', 'page');

        // Ouvrir l'accordéon contenant le lien actif (le cas échéant).
        var li = best.closest('.hs-accordion');
        if (!li) return;
        li.classList.add('active');
        var content = li.querySelector('.hs-accordion-content');
        if (content) { content.classList.remove('hidden'); content.style.height = ''; }
        var toggle = li.querySelector('.hs-accordion-toggle');
        if (toggle) { toggle.classList.add('is-active'); toggle.setAttribute('aria-expanded', 'true'); }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }
})();
