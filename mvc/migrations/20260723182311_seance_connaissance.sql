-- Migration Forge
-- Version: 20260723182311
-- Name: seance_connaissance
-- ADR-037 : les savoirs associés descendent à la SÉANCE. Nouveau pivot
-- seance_connaissance (miroir de sequence_connaissance), FK en cascade
-- (les savoirs partent avec la séance ou la connaissance ré-importée).
-- Reprise : les savoirs de séquence existants migrent vers la PREMIÈRE séance
-- (ordre le plus bas) de leur séquence ; ceux d'une séquence sans séance
-- restent dans l'ancien pivot (déprécié), récupérables — aucune perte muette.

CREATE TABLE IF NOT EXISTS seance_connaissance (
    Id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    seance_id BIGINT UNSIGNED NOT NULL,
    connaissance_id BIGINT UNSIGNED NOT NULL,
    NiveauCible INT NULL,
    Statut VARCHAR(20) NULL,
    Commentaire TEXT NULL,
    CreatedAt DATETIME NOT NULL,
    UpdatedAt DATETIME NOT NULL,
    PRIMARY KEY (Id),
    UNIQUE KEY uq_seance_connaissance (seance_id, connaissance_id),
    CONSTRAINT fk_seance_connaissance_seance_id FOREIGN KEY (seance_id)
        REFERENCES seance (Id) ON DELETE CASCADE,
    CONSTRAINT fk_seance_connaissance_connaissance_id FOREIGN KEY (connaissance_id)
        REFERENCES connaissance (Id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Reprise : savoirs de séquence -> première séance de la séquence.
INSERT INTO seance_connaissance (seance_id, connaissance_id, NiveauCible, Statut, Commentaire, CreatedAt, UpdatedAt)
SELECT premiere.Id, sk.connaissance_id, sk.NiveauCible, sk.Statut, sk.Commentaire, sk.CreatedAt, NOW()
FROM sequence_connaissance sk
JOIN seance premiere ON premiere.Id = (
    SELECT s2.Id FROM seance s2
    WHERE s2.sequence_id = sk.sequence_id
    ORDER BY s2.Ordre, s2.Id LIMIT 1
);

-- Purge des lignes migrées (celles des séquences SANS séance restent).
DELETE sk FROM sequence_connaissance sk
WHERE EXISTS (SELECT 1 FROM seance s2 WHERE s2.sequence_id = sk.sequence_id);
