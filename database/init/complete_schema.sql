-- HealthFlowMS Database Schema - Complete
-- All tables for score-api, deid, featurizer, model-risque, and audit-fairness

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- Authentication & User Management (score-api)
-- ============================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'researcher',
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Insert default users
INSERT INTO users (username, email, hashed_password, full_name, role, department)
VALUES 
    ('admin', 'admin@healthflow.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MV7skW', 'Administrator', 'admin', 'IT'),
    ('clinician', 'clinician@healthflow.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MV7skW', 'Dr. Smith', 'clinician', 'Cardiology'),
    ('researcher', 'researcher@healthflow.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MV7skW', 'Research Team', 'researcher', 'Research'),
    ('auditor', 'auditor@healthflow.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MV7skW', 'Audit Team', 'auditor', 'Compliance')
ON CONFLICT (username) DO NOTHING;

-- ============================================
-- De-identification (deid service)
-- ============================================

CREATE TABLE IF NOT EXISTS deid_patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pseudo_id VARCHAR(100) UNIQUE NOT NULL,
    original_fhir_id VARCHAR(100),
    age_group VARCHAR(20),
    gender VARCHAR(20),
    zip_code_prefix VARCHAR(10),
    anonymization_method VARCHAR(50) DEFAULT 'HIPAA_Safe_Harbor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_deid_pseudo_id ON deid_patients(pseudo_id);
CREATE INDEX IF NOT EXISTS idx_deid_fhir_id ON deid_patients(original_fhir_id);

CREATE TABLE IF NOT EXISTS deid_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operation VARCHAR(50) NOT NULL,
    patient_fhir_id VARCHAR(100),
    pseudo_id VARCHAR(100),
    user_id VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

CREATE INDEX IF NOT EXISTS idx_deid_audit_timestamp ON deid_audit_log(timestamp);

-- ============================================
-- Feature Extraction (featurizer service)
-- ============================================

CREATE TABLE IF NOT EXISTS patient_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pseudo_patient_id VARCHAR(100) NOT NULL,
    age INTEGER,
    gender VARCHAR(20),
    num_encounters INTEGER DEFAULT 0,
    num_conditions INTEGER DEFAULT 0,
    num_observations INTEGER DEFAULT 0,
    avg_los FLOAT,
    max_los FLOAT,
    has_diabetes BOOLEAN DEFAULT false,
    has_hypertension BOOLEAN DEFAULT false,
    has_heart_disease BOOLEAN DEFAULT false,
    has_copd BOOLEAN DEFAULT false,
    num_medications INTEGER DEFAULT 0,
    num_procedures INTEGER DEFAULT 0,
    clinical_text_features JSONB,
    nlp_entities JSONB,
    feature_vector JSONB,
    extraction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_features_pseudo_id ON patient_features(pseudo_patient_id);
CREATE INDEX IF NOT EXISTS idx_features_timestamp ON patient_features(extraction_timestamp);

-- ============================================
-- Risk Predictions (model-risque service)
-- ============================================

CREATE TABLE IF NOT EXISTS risk_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pseudo_patient_id VARCHAR(100) NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(20),
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    shap_values JSONB,
    top_risk_factors JSONB,
    model_version VARCHAR(50),
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    discharge_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_pseudo_id ON risk_predictions(pseudo_patient_id);
CREATE INDEX IF NOT EXISTS idx_predictions_risk_score ON risk_predictions(risk_score);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON risk_predictions(prediction_timestamp);

-- ============================================
-- Fairness Metrics (audit-fairness service)
-- ============================================

CREATE TABLE IF NOT EXISTS fairness_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_date DATE NOT NULL,
    demographic_parity_ratio FLOAT,
    equalized_odds_ratio FLOAT,
    overall_auc FLOAT,
    total_predictions INTEGER,
    metrics_by_gender JSONB,
    metrics_by_age_group JSONB,
    metrics_by_race JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fairness_date ON fairness_metrics(metric_date);

CREATE TABLE IF NOT EXISTS fairness_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    recommendations TEXT,
    metric_value FLOAT,
    threshold_value FLOAT,
    affected_group VARCHAR(100),
    is_resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_severity ON fairness_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON fairness_alerts(is_resolved);

-- ============================================
-- Audit Logs (score-api)
-- ============================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(100),
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);

-- ============================================
-- Comments
-- ============================================

COMMENT ON TABLE users IS 'User accounts for authentication and authorization';
COMMENT ON TABLE deid_patients IS 'Anonymized patient data (HIPAA Safe Harbor)';
COMMENT ON TABLE patient_features IS 'Extracted ML features for risk prediction';
COMMENT ON TABLE risk_predictions IS 'ML model predictions with SHAP explanations';
COMMENT ON TABLE fairness_metrics IS 'Fairness and bias metrics tracking';
COMMENT ON TABLE fairness_alerts IS 'Automated fairness violation alerts';
COMMENT ON TABLE audit_logs IS 'Audit trail for all system actions';
