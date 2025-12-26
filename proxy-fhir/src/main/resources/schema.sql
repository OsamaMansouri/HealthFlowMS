-- HealthFlow FHIR Proxy Database Schema
-- This schema defines tables for storing FHIR resources synchronized from HAPI FHIR server

-- FHIR Patients Table
CREATE TABLE IF NOT EXISTS fhir_patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fhir_id VARCHAR(255) UNIQUE NOT NULL,
    resource_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fhir_patients_fhir_id ON fhir_patients(fhir_id);

-- FHIR Encounters Table
CREATE TABLE IF NOT EXISTS fhir_encounters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fhir_id VARCHAR(255) UNIQUE NOT NULL,
    patient_fhir_id VARCHAR(255),
    resource_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fhir_encounters_fhir_id ON fhir_encounters(fhir_id);
CREATE INDEX IF NOT EXISTS idx_fhir_encounters_patient_fhir_id ON fhir_encounters(patient_fhir_id);

-- FHIR Observations Table
CREATE TABLE IF NOT EXISTS fhir_observations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fhir_id VARCHAR(255) UNIQUE NOT NULL,
    patient_fhir_id VARCHAR(255),
    resource_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fhir_observations_fhir_id ON fhir_observations(fhir_id);
CREATE INDEX IF NOT EXISTS idx_fhir_observations_patient_fhir_id ON fhir_observations(patient_fhir_id);

-- FHIR Conditions Table
CREATE TABLE IF NOT EXISTS fhir_conditions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fhir_id VARCHAR(255) UNIQUE NOT NULL,
    patient_fhir_id VARCHAR(255),
    resource_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fhir_conditions_fhir_id ON fhir_conditions(fhir_id);
CREATE INDEX IF NOT EXISTS idx_fhir_conditions_patient_fhir_id ON fhir_conditions(patient_fhir_id);

-- FHIR Bundles Table
CREATE TABLE IF NOT EXISTS fhir_bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fhir_id VARCHAR(255) UNIQUE NOT NULL,
    resource_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fhir_bundles_fhir_id ON fhir_bundles(fhir_id);

-- Comments
COMMENT ON TABLE fhir_patients IS 'Stores FHIR Patient resources synchronized from HAPI FHIR server';
COMMENT ON TABLE fhir_encounters IS 'Stores FHIR Encounter resources with patient references';
COMMENT ON TABLE fhir_observations IS 'Stores FHIR Observation resources (vital signs, lab results)';
COMMENT ON TABLE fhir_conditions IS 'Stores FHIR Condition resources (diagnoses, problems)';
COMMENT ON TABLE fhir_bundles IS 'Stores FHIR Bundle resources';
