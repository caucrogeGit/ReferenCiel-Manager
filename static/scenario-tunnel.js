/* Tunnel de scénario (éditeur, ADR-019) — interactions client.

   Étape Titre : le bloc « Enseignants co-auteurs » (#bloc-co-auteurs) n'a de sens
   qu'en co-intervention. On le révèle/masque selon la case #co_intervention.

   CSP oblige (script-src 'self') : pas de JS inline, tout passe par ce fichier.
   La section du tunnel est régénérée par HTMX ; on ne peut donc pas lier
   l'écouteur une fois pour toutes sur l'input. On délègue depuis document, et on
   resynchronise l'état initial après chaque swap HTMX. */
(function () {
    function sync() {
        var cb = document.getElementById('co_intervention');
        var bloc = document.getElementById('bloc-co-auteurs');
        if (cb && bloc) bloc.classList.toggle('hidden', !cb.checked);
    }

    // Clic sur la case : bascule immédiate (délégation, survit aux swaps HTMX).
    document.addEventListener('change', function (e) {
        if (e.target && e.target.id === 'co_intervention') sync();
    });

    // État initial : chargement direct et après chaque régénération HTMX de l'étape.
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', sync);
    } else {
        sync();
    }
    document.addEventListener('htmx:afterSwap', sync);
})();
