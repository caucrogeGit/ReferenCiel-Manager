# ADR-008 : Typage Python strict (pyright)

## Statut

Accepté (2026-07-05).

> Applique au projet le standard de typage de Forge (Forge ADR-036), exigé par le porteur : **le code produit est 100% Python typé strict**.

## Date

2026-07-05

## Contexte

Forge est typé et vérifié statiquement avec **Pyright** (moteur de Pylance : la CI voit ce que voit l'éditeur), configuré dans `pyproject.toml [tool.pyright]`, en **strict par fichier** (`# pyright: strict` en tête).
Le porteur exige la même chose pour RéférenCiel Manager : tout code que **nous** produisons doit passer pyright en mode strict.

RéférenCiel Manager démarre presque vierge : appliquer le strict dès maintenant est peu coûteux et évite toute dette de typage.

## Décision

1. **Vérificateur : Pyright**, configuré dans `pyproject.toml [tool.pyright]` (`pythonVersion = "3.12"`, `venv = ".venv"`).
2. **Strict par fichier** : chaque fichier `.py` que nous écrivons porte `# pyright: strict` en tête (convention Forge).
   `include` liste nos chemins de code produit ; il s'étend à chaque fichier applicatif manuel écrit.
3. **Périmètre du cliquet strict** : tout fichier que nous **écrivons ou éditons à la main** (hors `*_base.py` régénérables).
   Actuellement : `tests/`, `conftest.py`, `optins/registry.py`, `mvc/routes.py`, `mvc/controllers/home_controller.py`.
   `include` s'étend à chaque nouveau fichier applicatif manuel.
   **Exclus** : les fichiers purement régénérables (`*_base.py`) et le framework installé (`.venv`), que nous ne maintenons pas.
   Toute lacune de typage exposée par le squelette généré est un **finding de banc d'essai** (ADR-006), révélé et non contourné en silence.
4. **`pyright` fait partie de la validation avant de livrer**, aux côtés de `python -m pytest`, `ruff check .`, `forge project:check`, `mkdocs build --strict`.
5. **ruff** est aligné **exactement** sur la config de Forge (`select = ["E","F"]`, `line-length = 120`, `ignore` E501/E741/E402) : on ne durcit pas plus que Forge, pour que le squelette généré reste vert.

## Conséquences

- Notre code est typé strict dès la première ligne ; aucune dette à rattraper.
- Un projet fraîchement généré par `forge new` livre `optins/registry.py` avec `register_optins(router)` **non typé** ; notre cliquet strict l'a exposé.
  On l'a **corrigé localement** (`router: Router`, import sous `TYPE_CHECKING`) et placé sous strict.
  **Finding de banc d'essai** : le squelette Forge devrait livrer ce fichier typé.
  À vérifier au moment d'activer un opt-in : `forge opt-in:enable` **préserve-t-il** le typage manuel de ce fichier ?
- La barre de typage est explicite et exécutable (`pyright` en CI).

## Alternatives écartées

- **Strict global** sur tout le dépôt (squelette inclus) : rejeté, force le strict sur du code généré non maîtrisé, produit du bruit, brouille la frontière framework/app.
- **Mypy** : écarté, Forge s'appuie sur Pyright (cohérence éditeur/CI) ; on suit le même outil (100% Forge, cohérence de banc d'essai).
- **Suppressions locales (`# type: ignore`)** pour passer vite : rejeté, contraire au strict réel et au rôle de banc d'essai (révéler la cause).

## Suite

- Marquer `# pyright: strict` tout nouveau fichier produit et l'ajouter à `include` si nécessaire ; garder `pyright` à 0 erreur.
- Consigner les findings de typage du squelette Forge (banc d'essai) au fil de l'eau.
