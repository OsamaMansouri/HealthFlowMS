CREATE TABLE IF NOT EXISTS patient_features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pseudo_patient_id VARCHAR(100) NOT NULL,
    encounter_id VARCHAR(100),
    feature_version VARCHAR(20) NOT NULL,
    
    -- Demographics
    age_at_admission INTEGER,
    gender_encoded INTEGER,
    
    -- Clinical Features
    length_of_stay INTEGER,
    previous_admissions_30d INTEGER,
    previous_admissions_90d INTEGER,
    previous_admissions_365d INTEGER,
    charlson_comorbidity_index FLOAT,
    elixhauser_score FLOAT,
    
    -- Vital Signs
    heart_rate_last FLOAT,
    blood_pressure_systolic_last FLOAT,
    blood_pressure_diastolic_last FLOAT,
    respiratory_rate_last FLOAT,
    temperature_last FLOAT,
    oxygen_saturation_last FLOAT,
    
    -- Lab Values
    hemoglobin_last FLOAT,
    creatinine_last FLOAT,
    sodium_last FLOAT,
    potassium_last FLOAT,
    glucose_last FLOAT,
    wbc_count_last FLOAT,
    
    -- NLP Features
    nlp_sentiment_score FLOAT,
    nlp_urgency_score FLOAT,
    nlp_complexity_score FLOAT,
    nlp_entities_count INTEGER,
    nlp_medication_mentions INTEGER,
    nlp_symptom_mentions INTEGER,
    
    -- Diagnosis Features
    primary_diagnosis_code VARCHAR(20),
    diagnosis_count INTEGER,
    has_diabetes BOOLEAN DEFAULT FALSE,
    has_hypertension BOOLEAN DEFAULT FALSE,
    has_heart_failure BOOLEAN DEFAULT FALSE,
    has_copd BOOLEAN DEFAULT FALSE,
    has_ckd BOOLEAN DEFAULT FALSE,
    has_cancer BOOLEAN DEFAULT FALSE,
    
    -- Medication Features
    medication_count INTEGER,
    high_risk_medication_count INTEGER,
    
    -- Procedure Features
    procedure_count INTEGER,
    surgical_procedure BOOLEAN DEFAULT FALSE,
    
    -- Discharge Features
    discharge_disposition VARCHAR(50),
    discharge_to_home BOOLEAN,
    
    -- Metadata
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_patient_features_pseudo_id ON patient_features(pseudo_patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_features_encounter_id ON patient_features(encounter_id);
CREATE INDEX IF NOT EXISTS idx_patient_features_version ON patient_features(feature_version);
