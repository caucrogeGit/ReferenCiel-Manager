-- Fixtures pour classe, générées par forge fixtures:generate.
-- Relire avant de charger (forge fixtures:load).
INSERT INTO classe (Code, Libelle, annee_scolaire_id, niveau_classe_id, CreatedAt, UpdatedAt) VALUES ('2TNE-A', 'Seconde TNE A', (SELECT Id FROM annee_scolaire WHERE Libelle = '2025-2026' LIMIT 1), (SELECT Id FROM niveau_classe WHERE Code = '2TNE' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
