-- Fixtures pour classe, générées par forge fixtures:generate.
-- Relire avant de charger (forge fixtures:load).
-- ADR-023 : la classe est rattachée à un formation_niveau (formation × niveau),
-- créé par structure.py. Trois classes du même niveau sur l'année 2025-2026.
INSERT INTO classe (Code, Libelle, annee_scolaire_id, formation_niveau_id, CreatedAt, UpdatedAt) VALUES ('2TNE-A', 'Seconde TNE A', (SELECT Id FROM annee_scolaire WHERE Libelle = '2025-2026' LIMIT 1), (SELECT Id FROM formation_niveau WHERE Code = '2TNE-2NDE' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
INSERT INTO classe (Code, Libelle, annee_scolaire_id, formation_niveau_id, CreatedAt, UpdatedAt) VALUES ('2TNE-B', 'Seconde TNE B', (SELECT Id FROM annee_scolaire WHERE Libelle = '2025-2026' LIMIT 1), (SELECT Id FROM formation_niveau WHERE Code = '2TNE-2NDE' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
INSERT INTO classe (Code, Libelle, annee_scolaire_id, formation_niveau_id, CreatedAt, UpdatedAt) VALUES ('2TNE-C', 'Seconde TNE C', (SELECT Id FROM annee_scolaire WHERE Libelle = '2025-2026' LIMIT 1), (SELECT Id FROM formation_niveau WHERE Code = '2TNE-2NDE' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
