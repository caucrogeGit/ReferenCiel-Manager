-- Fixtures pour affectation_professeur_classe, générées par forge fixtures:generate.
-- Relire avant de charger (forge fixtures:load).
INSERT INTO affectation_professeur_classe (Role, professeur_id, classe_id, annee_scolaire_id, CreatedAt, UpdatedAt) VALUES ('Professeur principal', (SELECT Id FROM professeur WHERE Nom = 'Bernard' LIMIT 1), (SELECT Id FROM classe WHERE Code = '2TNE-A' LIMIT 1), (SELECT Id FROM annee_scolaire WHERE Libelle = '2025-2026' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
