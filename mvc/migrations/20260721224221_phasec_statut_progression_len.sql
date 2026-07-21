-- Migration Forge
-- Version: 20260721224221
-- Name: phaseC_statut_progression_len
-- ADR-033 : le cycle de vie côté élève inclut « en_attente_validation » (21 car.),
-- qui ne rentrait pas dans VARCHAR(20). Élargissement à VARCHAR(30).

ALTER TABLE progression_seance MODIFY Statut VARCHAR(30) NOT NULL;
ALTER TABLE progression_sequence MODIFY Statut VARCHAR(30) NOT NULL;
