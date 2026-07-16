/* Comportements UI globaux, CSP-safe (script-src 'self' interdit le JS inline).
   Remplace des handlers inline retirés des templates :
   - form[data-confirm]        : confirmation avant envoi (suppressions classiques) ;
   - [data-open-modal="ID"]    : ouvre la <dialog> native d'identifiant ID ;
   - form[data-prevent-submit] : neutralise l'envoi (formulaires de démonstration).
   Les tableaux CRUD, eux, utilisent hx-confirm de htmx (déjà CSP-safe). */
(function () {
    // Modale de confirmation stylée (<dialog> du layout), en remplacement du
    // window.confirm() natif. La soumission d'un form[data-confirm] est asynchrone :
    // on l'intercepte, on ouvre la modale, puis on resoumet à la validation via un
    // drapeau data-confirmed (pour ne pas rouvrir la modale en boucle).
    var confirmDialog = document.getElementById('confirm-dialog');
    var pendingForm = null;

    function resubmit(form) {
        if (!form) return;
        form.dataset.confirmed = '1';
        if (typeof form.requestSubmit === 'function') form.requestSubmit();
        else form.submit();
    }

    document.addEventListener('submit', function (e) {
        var form = e.target;
        if (!form || !form.matches) return;
        if (form.matches('form[data-prevent-submit]')) {
            e.preventDefault();
            return;
        }
        if (form.matches('form[data-confirm]')) {
            // Déjà confirmé : on laisse passer (et on nettoie le drapeau).
            if (form.dataset.confirmed === '1') {
                delete form.dataset.confirmed;
                return;
            }
            e.preventDefault();
            var message = form.getAttribute('data-confirm');
            // Repli si <dialog> indisponible : confirm natif.
            if (!confirmDialog || typeof confirmDialog.showModal !== 'function') {
                if (window.confirm(message)) resubmit(form);
                return;
            }
            pendingForm = form;
            var msgEl = document.getElementById('confirm-dialog-message');
            if (msgEl) msgEl.textContent = message;
            confirmDialog.showModal();
        }
    });

    if (confirmDialog) {
        confirmDialog.addEventListener('click', function (e) {
            if (e.target.closest('[data-confirm-ok]')) {
                var form = pendingForm;
                pendingForm = null;
                confirmDialog.close();
                resubmit(form);
            } else if (e.target.closest('[data-confirm-cancel]')) {
                pendingForm = null;
                confirmDialog.close();
            }
        });
        // Fermeture par Échap ou clic backdrop : on oublie le formulaire en attente.
        confirmDialog.addEventListener('close', function () { pendingForm = null; });
    }

    // Ouverture d'une modale <dialog> native.
    document.addEventListener('click', function (e) {
        var trigger = e.target.closest ? e.target.closest('[data-open-modal]') : null;
        if (!trigger) return;
        var dlg = document.getElementById(trigger.getAttribute('data-open-modal'));
        if (dlg && typeof dlg.showModal === 'function') dlg.showModal();
    });

    // Flash éphémère : consommé côté serveur, mais son <div> vit hors des zones
    // rafraîchies par HTMX (ex. #tunnel-corps). On le retire après quelques secondes
    // et dès qu'une requête HTMX part (navigation), pour qu'il ne traîne pas.
    function hideFlash() {
        var flashes = document.querySelectorAll('[data-flash]');
        for (var i = 0; i < flashes.length; i++) flashes[i].remove();
    }
    if (document.querySelector('[data-flash]')) {
        window.setTimeout(hideFlash, 5000);
    }
    document.addEventListener('htmx:beforeRequest', hideFlash);
})();
