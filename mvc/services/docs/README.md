# Documentation des services (`mvc/services/`)

Documentation des services applicatifs (fichiers `.py` à la racine de
`mvc/services/`). Un service est un module qui orchestre une règle métier ou une
capacité transverse ; il s'appuie sur les models / le cœur Forge, sans réimplémenter
l'accès aux données ([ADR-004](../../../docs/adr/004-architecture-applicative-forge.md) §5).

| Service | Rôle | Doc |
|---|---|---|
| `canonical_validator` | Valide un JSON canonique contre son schéma (porte d'entrée de l'import) | [canonical_validator.md](canonical_validator.md) |
| `referentiel_importer` | Importe un référentiel niveau-classe validé en base (upsert best-effort) | [referentiel_importer.md](referentiel_importer.md) |
| `password_policy` | Politique de mot de passe unique, adossée au cœur | [password_policy.md](password_policy.md) |
| `media_fetcher` | Récupération de médias (yt-dlp), headless | [media_fetcher.md](media_fetcher.md) |
