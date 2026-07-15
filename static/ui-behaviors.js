/* Comportements UI globaux, CSP-safe (script-src 'self' interdit le JS inline).
   Remplace des handlers inline retirés des templates :
   - form[data-confirm]        : confirmation avant envoi (suppressions classiques) ;
   - [data-open-modal="ID"]    : ouvre la <dialog> native d'identifiant ID ;
   - form[data-prevent-submit] : neutralise l'envoi (formulaires de démonstration).
   Les tableaux CRUD, eux, utilisent hx-confirm de htmx (déjà CSP-safe). */
(function () {
    // Confirmation / neutralisation avant soumission (le submit remonte au document).
    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form || !form.matches) return;
        if (form.matches('form[data-prevent-submit]')) {
            e.preventDefault();
            return;
        }
        if (form.matches('form[data-confirm]') &&
            !window.confirm(form.getAttribute('data-confirm'))) {
            e.preventDefault();
        }
    });

    // Ouverture d'une modale <dialog> native.
    document.addEventListener('click', function (e) {
        var trigger = e.target.closest ? e.target.closest('[data-open-modal]') : null;
        if (!trigger) return;
        var dlg = document.getElementById(trigger.getAttribute('data-open-modal'));
        if (dlg && typeof dlg.showModal === 'function') dlg.showModal();
    });
})();
