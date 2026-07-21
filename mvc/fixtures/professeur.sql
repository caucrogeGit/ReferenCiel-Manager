-- Fixtures pour professeur, générées par forge fixtures:generate.
-- Relire avant de charger (forge fixtures:load).
-- Trois professeurs, chacun rattaché à un compte (voir comptes.py).
INSERT INTO professeur (Nom, Prenom, UserId, CreatedAt, UpdatedAt) VALUES ('Bernard', 'Julie', (SELECT Id FROM users WHERE email = 'prof@referenciel.local' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
INSERT INTO professeur (Nom, Prenom, UserId, CreatedAt, UpdatedAt) VALUES ('Moreau', 'Karim', (SELECT Id FROM users WHERE email = 'prof2@referenciel.local' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
INSERT INTO professeur (Nom, Prenom, UserId, CreatedAt, UpdatedAt) VALUES ('Petit', 'Sophie', (SELECT Id FROM users WHERE email = 'prof3@referenciel.local' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
