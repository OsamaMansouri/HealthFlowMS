# HealthFlowMS - Complete Project Documentation

This document summarizes the complete HealthFlowMS project based on Rapport.tex.

## 📋 Project Overview

**HealthFlowMS** is a comprehensive hospital readmission prediction system based on a modern microservices architecture. The system uses FHIR standards for medical data integration, combines advanced Machine Learning (XGBoost) and Natural Language Processing (BioBERT, spaCy) to analyze clinical data, and provides risk predictions with explainability via SHAP.

**Performance:** XGBoost model achieves 0.82 AUC-ROC

## 🏗️ Architecture

### 8 Microservices:

| Service | Port | Technology | Role |
|---------|------|------------|------|
| HAPI FHIR | 8090 | HAPI FHIR Server | Reference FHIR server |
| ProxyFHIR | 8081 | Java/Spring Boot 3.2 | FHIR synchronization |
| DeID | 8082 | Python/FastAPI | Data anonymization (HIPAA Safe Harbor) |
| Featurizer | 8083 | Python/FastAPI | Feature extraction + NLP (BioBERT, spaCy) |
| ModelRisque | 8084 | Python/FastAPI | ML prediction (XGBoost 2.0, SHAP 0.44) |
| ScoreAPI | 8085 | Python/FastAPI | Main REST API with JWT auth |
| AuditFairness | 8086 | Python/Dash | Fairness dashboard |
| Frontend | 8087 | React 18.2/TypeScript | User interface |

## 🔧 Technology Stack

### Frontend
- **React 18.2** - UI framework
- **TypeScript** - Type safety
- **Vite 5.0** - Build tool
- **Tailwind CSS** - Styling
- **Recharts 2.10.3** - Data visualization
- **Axios 1.6.2** - HTTP client

### Proxy-FHIR (Java)
- **Java 17** - Programming language
- **Spring Boot 3.2.0** - Framework
- **HAPI FHIR Client 6.10.0** - FHIR client
- **Spring Data JPA** - Data access
- **PostgreSQL** - Database

### Python Services
- **Python 3.11** - Programming language
- **FastAPI 0.109.0** - Web framework
- **SQLAlchemy 2.0** - ORM
- **XGBoost 2.0.3** - ML model
- **SHAP 0.44.1** - Explainability
- **BioBERT** (transformers) - NLP
- **spaCy 3.7.2** - NLP
- **Dash 2.14.2** - Dashboard (AuditFairness)

## 📡 API Endpoints

### ProxyFHIR
```
POST /api/fhir/sync              # Trigger synchronization
GET  /api/fhir/patients          # List patients
GET  /api/fhir/patients/{id}     # Patient details
GET  /api/fhir/encounters        # List encounters
POST /api/fhir/proxy/Patient     # Create patient (proxy)
GET  /health                     # Healthcheck
```

### ScoreAPI
```
POST /api/v1/auth/login          # Login
POST /api/v1/auth/refresh       # Refresh token
GET  /api/v1/patients            # List patients
GET  /api/v1/patients/{id}/risk-score  # Risk score
GET  /api/v1/patients/{id}/risk-explanation  # SHAP explanation
GET  /api/v1/dashboard/stats    # Dashboard statistics
```

### DeID
```
POST /api/deid/patient           # Anonymize patient
GET  /api/deid/patient/{id}      # Get anonymized patient
```

### Featurizer
```
POST /api/features/extract       # Extract features
GET  /api/features/{patient_id}   # Get features
POST /api/nlp/analyze            # Analyze clinical text
```

### ModelRisque
```
POST /api/predict                # Predict risk
GET  /api/predict/{patient_id}    # Get prediction
GET  /api/shap/{patient_id}      # SHAP explanation
```

## 🎨 Frontend Pages

1. **Login** (`/login`) - Authentication
2. **Dashboard** (`/`) - Overview with statistics
3. **Patients List** (`/patients`) - Patient management
4. **Patient Detail** (`/patients/:id`) - Complete patient info + SHAP
5. **Workflow** (`/patient-workflow`) - Guided patient creation workflow
6. **Predictions** (`/predictions`) - Aggregated predictions analysis

## 🗄️ Database Schema

### Main Tables:
- `fhir_patients` - FHIR patient data
- `fhir_encounters` - Hospitalizations
- `fhir_observations` - Vital signs & lab results
- `fhir_conditions` - Diagnoses
- `deid_patients` - Anonymized patients
- `patient_features` - Extracted features (30+)
- `risk_predictions` - Risk scores + SHAP explanations
- `users` - System users
- `api_audit_logs` - Audit trail

## 🤖 Machine Learning

### Model: XGBoost
- **n_estimators:** 500
- **max_depth:** 6
- **learning_rate:** 0.05
- **Performance:** AUC-ROC 0.82

### Features (30+):
- Demographics: age, gender
- Clinical: length of stay, previous admissions
- Comorbidities: Charlson index, Elixhauser score
- Vital signs: heart rate, blood pressure, temperature
- Laboratory: hemoglobin, creatinine, glucose
- NLP: sentiment_score, urgency_score, complexity_score, entities_count

### Explainability: SHAP
- Provides feature contributions
- Identifies risk factors
- Clinically interpretable

## 🔒 Security & Compliance

- **HIPAA Safe Harbor** compliant anonymization
- **JWT authentication** for API access
- **bcrypt** password hashing
- **Audit logging** for all actions

## 📊 Workflow

1. Create patient in HAPI FHIR (via ProxyFHIR)
2. Add medical data (encounters, observations, conditions)
3. Sync to PostgreSQL (ProxyFHIR)
4. Anonymize (DeID service)
5. Extract features (Featurizer + NLP)
6. Predict risk (ModelRisque + XGBoost)
7. Generate SHAP explanations
8. Display in Frontend/AuditFairness

## 📝 Source Code Status

✅ **Complete:**
- score-api (Python/FastAPI)
- deid (Python/FastAPI)
- featurizer (Python/FastAPI)
- model-risque (Python/FastAPI)
- audit-fairness (Python/Dash)

⚠️ **Missing Source:**
- proxy-fhir (Java source - only compiled .class files)
- frontend (React/TypeScript source - only built files)

**Note:** Docker containers are running and functional, but source code was not included in Docker images (multi-stage builds).

