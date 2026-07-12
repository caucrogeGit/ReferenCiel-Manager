-- Fixtures pour professeur, générées par forge fixtures:generate.
-- Relire avant de charger (forge fixtures:load).
INSERT INTO professeur (Nom, Prenom, UserId, CreatedAt, UpdatedAt) VALUES ('Bernard', 'Julie', (SELECT Id FROM users WHERE email = 'prof@referenciel.local' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
