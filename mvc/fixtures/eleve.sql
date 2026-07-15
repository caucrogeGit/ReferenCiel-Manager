-- Fixtures pour eleve, générées par forge fixtures:generate.
-- Relire avant de charger (forge fixtures:load).
-- ADR-022 : l'élève est rattaché à une CLASSE (classe_id) ; le niveau se déduit de la classe.
INSERT INTO eleve (Nom, Prenom, Identifiant, DateNaissance, UserId, classe_id, CreatedAt, UpdatedAt) VALUES ('Dupont', 'Marie', 'dupont-marie', '2009-05-15', (SELECT Id FROM users WHERE email = 'eleve@referenciel.local' LIMIT 1), (SELECT Id FROM classe WHERE Code = '2TNE-A' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
INSERT INTO eleve (Nom, Prenom, Identifiant, DateNaissance, UserId, classe_id, CreatedAt, UpdatedAt) VALUES ('Martin', 'Lucas', 'martin-lucas', '2009-03-10', NULL, (SELECT Id FROM classe WHERE Code = '2TNE-A' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
INSERT INTO eleve (Nom, Prenom, Identifiant, DateNaissance, UserId, classe_id, CreatedAt, UpdatedAt) VALUES ('Nguyen', 'Emma', 'nguyen-emma', '2009-07-22', NULL, (SELECT Id FROM classe WHERE Code = '2TNE-A' LIMIT 1), '2024-01-01 00:00:00', '2024-01-01 00:00:00');
