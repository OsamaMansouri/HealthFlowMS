# 🏥 HealthFlowMS - Hospital Readmission Prediction System 

[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.io/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://www.java.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-Dark-blue.svg)](#license)

> A comprehensive microservices-based healthcare management system for predicting hospital readmission risk using FHIR standards, Machine Learning (XGBoost), and Natural Language Processing (BioBERT, spaCy).

**Model Performance:** AUC-ROC 0.82 | Precision 0.78 | Recall 0.74 | F1-Score 0.76


---
## Vidio 
https://drive.google.com/file/d/1IIRTxPdHFXMdKvZsxnrlv7nHkvQv1m16/view?usp=drive_link

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
  - [System Diagram](#system-architecture-diagram)
  - [Data Flow](#data-flow-diagram)
  - [Technology Stack](#technology-stack)
- [BPMN Process Diagrams](#-bpmn-process-diagrams)
  - [Patient Registration Workflow](#1-patient-registration-workflow)
  - [Risk Prediction Workflow](#2-risk-prediction-workflow)
  - [Data Anonymization Process](#3-data-anonymization-process-hipaa-safe-harbor)
  - [Feature Extraction & NLP Process](#4-feature-extraction--nlp-process)
  - [CI/CD Deployment Process](#5-cicd-deployment-process-jenkins)
- [Quick Start](#-quick-start)
- [Service Endpoints](#-service-endpoints)
- [Complete Workflow](#-complete-workflow)
- [Machine Learning](#-machine-learning)
- [Testing](#-testing)
- [Code Quality (SonarQube)](#-code-quality-sonarqube)
- [Monitoring & Observability](#-monitoring--observability)
- [CI/CD Pipeline](#-cicd-pipeline)
- [API Documentation](#-api-documentation)
- [Postman Collection](#-postman-collection)
- [Security & Compliance](#-security--compliance)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**HealthFlowMS** is a complete hospital readmission prediction system that:

- ✅ Uses **FHIR (Fast Healthcare Interoperability Resources)** standards for medical data integration
- ✅ Implements **HIPAA Safe Harbor** compliant data anonymization (18 identifiers removed/modified)
- ✅ Provides **XGBoost-based risk predictions** with **SHAP explainability**
- ✅ Extracts **30+ clinical features** including NLP analysis of clinical notes
- ✅ Offers **fairness auditing** to detect and correct prediction biases
- ✅ Features a modern **React/TypeScript frontend** for intuitive user interaction
- ✅ Complete **CI/CD pipeline** with Jenkins
- ✅ **Prometheus + Grafana** monitoring stack

---

## ✨ Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
| **FHIR Integration** | Standard medical data format (HL7 FHIR R4) |
| **HIPAA Compliance** | Safe Harbor anonymization (de-identification) |
| **ML Predictions** | XGBoost model with 0.82 AUC-ROC |
| **NLP Analysis** | BioBERT + spaCy for clinical text processing |
| **Explainability** | SHAP values for transparent predictions |
| **Fairness Auditing** | Bias detection across demographics |
| **Modern UI** | React 18.2 + TypeScript responsive interface |
| **Microservices** | Scalable, independent services |
| **Monitoring** | Prometheus metrics + Grafana dashboards |
| **CI/CD** | Automated Jenkins pipeline |

---

## 🏗️ Architecture

The system consists of **12 services** following a modern microservices architecture:

### System Architecture Diagram

```mermaid
graph TB
    subgraph "Frontend Layer"
        Frontend[🌐 Frontend:8087<br/>React + TypeScript]
    end
    
    subgraph "API Gateway Layer"
        ScoreAPI[🔐 Score API:8085<br/>FastAPI - JWT Auth]
    end
    
    subgraph "Microservices Layer"
        ProxyFHIR[📋 Proxy FHIR:8081<br/>Spring Boot]
        DeID[🔒 DeID:8082<br/>HIPAA Anonymization]
        Featurizer[🧬 Featurizer:8083<br/>NLP + Features]
        ModelRisque[🤖 Model Risque:8084<br/>XGBoost + SHAP]
        AuditFairness[⚖️ Audit:8086<br/>Fairness Dashboard]
    end
    
    subgraph "Data Layer"
        HAPIFHIR[🏥 HAPI FHIR:8090<br/>FHIR Server]
        Postgres[(🗄️ PostgreSQL<br/>:5432)]
        Redis[(⚡ Redis<br/>:6379)]
    end
    
    subgraph "Monitoring Layer"
        Prometheus[📊 Prometheus:9090]
        Grafana[📈 Grafana:3000]
    end
    
    subgraph "CI/CD Layer"
        Jenkins[🚀 Jenkins:8088]
    end
    
    Frontend --> ScoreAPI
    Frontend --> ProxyFHIR
    
    ScoreAPI --> DeID
    ScoreAPI --> Featurizer
    ScoreAPI --> ModelRisque
    ScoreAPI --> AuditFairness
    ScoreAPI --> Postgres
    ScoreAPI --> Redis
    
    ProxyFHIR --> HAPIFHIR
    ProxyFHIR --> Postgres
    
    DeID --> Postgres
    Featurizer --> Postgres
    ModelRisque --> Postgres
    AuditFairness --> Postgres
    
    Prometheus -.->|scrape| ScoreAPI
    Prometheus -.->|scrape| DeID
    Prometheus -.->|scrape| Featurizer
    Prometheus -.->|scrape| ModelRisque
    Prometheus -.->|scrape| ProxyFHIR
    Prometheus -.->|scrape| AuditFairness
    
    Grafana --> Prometheus
    
    Jenkins -.->|deploy| ScoreAPI
    Jenkins -.->|deploy| DeID
    Jenkins -.->|deploy| Featurizer
    Jenkins -.->|deploy| ModelRisque
    
    style Frontend fill:#e1f5ff
    style ScoreAPI fill:#fff4e1
    style Postgres fill:#ffe1e1
    style Prometheus fill:#e1ffe1
    style Jenkins fill:#f0e1ff
```

### Services Overview

| Service | Port | Technology | Role |
|---------|------|------------|------|
| **Frontend** | 8087 | React 18.2 + TypeScript | User interface |
| **Score API** | 8085 | Python 3.11 + FastAPI | Main REST API + JWT auth |
| **Proxy FHIR** | 8081 | Java 17 + Spring Boot 3.2 | FHIR synchronization & proxy |
| **DeID** | 8082 | Python 3.11 + FastAPI | HIPAA Safe Harbor anonymization |
| **Featurizer** | 8083 | Python 3.11 + FastAPI | Feature extraction + NLP |
| **Model Risque** | 8084 | Python 3.11 + FastAPI | ML prediction (XGBoost + SHAP) |
| **Audit Fairness** | 8086 | Python 3.11 + Dash | Fairness dashboard |
| **HAPI FHIR** | 8090 | Java + HAPI FHIR | Reference FHIR server |
| **PostgreSQL** | 5432 | PostgreSQL 15 | Central database |
| **Redis** | 6379 | Redis 7 | Caching layer |
| **Prometheus** | 9090 | Prometheus | Metrics collection |
| **Grafana** | 3000 | Grafana | Metrics visualization |
| **Jenkins** | 8088 | Jenkins | CI/CD pipeline |

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant Frontend as 🌐 Frontend
    participant ScoreAPI as 🔐 Score API
    participant ProxyFHIR as 📋 Proxy FHIR
    participant HAPI as 🏥 HAPI FHIR
    participant DeID as 🔒 DeID
    participant Feature as 🧬 Featurizer
    participant Model as 🤖 Model Risque
    participant DB as 🗄️ PostgreSQL
    
    Note over User,DB: Complete Prediction Workflow
    
    User->>Frontend: 1. Create Patient
    Frontend->>ProxyFHIR: POST /api/fhir/proxy/Patient
    ProxyFHIR->>HAPI: Create FHIR Patient
    HAPI-->>ProxyFHIR: Patient ID
    ProxyFHIR->>DB: Store Patient
    ProxyFHIR-->>Frontend: Success
    
    User->>Frontend: 2. Add Medical Data
    Frontend->>ProxyFHIR: POST Encounters/Observations
    ProxyFHIR->>HAPI: Store in FHIR
    ProxyFHIR->>DB: Sync to PostgreSQL
    
    User->>Frontend: 3. Request Prediction
    Frontend->>ScoreAPI: GET /api/v1/patients/{id}/risk-score
    
    ScoreAPI->>DeID: Anonymize Patient
    DeID->>DB: Get FHIR Data
    DeID-->>ScoreAPI: Anonymized Data
    
    ScoreAPI->>Feature: Extract Features
    Feature->>DB: Get Clinical Data
    Feature->>Feature: NLP Analysis (BioBERT)
    Feature-->>ScoreAPI: 30+ Features
    
    ScoreAPI->>Model: Predict Risk
    Model->> Model: XGBoost Inference
    Model->>Model: SHAP Explanation
    Model->>DB: Save Prediction
    Model-->>ScoreAPI: Risk Score + Explanation
    
    ScoreAPI-->>Frontend: Complete Result
    Frontend-->>User: Display Risk + SHAP
```

### Technology Stack

**Backend:**
- **Java 17** + Spring Boot 3.2.0 (Proxy FHIR)
- **Python 3.11** + FastAPI 0.109.0 (Python services)
- **PostgreSQL 15** (Central database)
- **Redis 7** (Caching)

**Frontend:**
- **React 18.2** + **TypeScript 5.0**
- **Vite 5.0** (Build tool)
- **Tailwind CSS 3.4** (Styling)
- **Recharts 2.10** (Data visualization)
- **Axios 1.6** (HTTP client)

**Machine Learning:**
- **XGBoost 2.0.3** (Prediction model)
- **SHAP 0.44.1** (Explainability)
- **BioBERT** (transformers 4.36) (NLP)
- **spaCy 3.7.2** (Named entity recognition)

**DevOps & Monitoring:**
- **Docker** + **Docker Compose** (Containerization)
- **Prometheus** (Metrics collection)
- **Grafana** (Visualization)
- **Jenkins** (CI/CD)

---

## 🔄 BPMN Process Diagrams

Business Process Model and Notation (BPMN) diagrams illustrating the key workflows in HealthFlowMS.

### 1. Patient Registration Workflow

![Patient Registration BPMN](docs/images/bpmn_patient_registration.png)

**Process Overview:**

This diagram illustrates the complete process for registering a new patient in the HealthFlowMS system:

1. **User initiates registration** through the frontend interface
2. **Patient information form** is filled with demographic and basic health data
3. **Data validation** ensures all required fields are complete and properly formatted
4. **Validation gateway** checks data integrity:
   - ❌ **Invalid data** → User returns to form to correct errors
   - ✅ **Valid data** → Process continues
5. **FHIR Patient Resource** is created via the Proxy FHIR service (Spring Boot)
6. **Storage in HAPI FHIR Server** ensures FHIR R4 standard compliance
7. **Synchronization to PostgreSQL** database for fast querying and analytics
8. **Success** → Patient is now registered and ready for clinical data entry

---

### 2. Risk Prediction Workflow

![Risk Prediction BPMN](docs/images/bpmn_risk_prediction.png)

**Process Overview:**

This end-to-end workflow demonstrates how HealthFlowMS predicts hospital readmission risk:

1. **User requests risk prediction** for a specific patient
2. **Patient data retrieval** from PostgreSQL database
3. **Data anonymization** via DeID service (HIPAA Safe Harbor compliance - 18 identifiers removed/modified)
4. **Feature extraction** by Featurizer service (30+ clinical features)
5. **NLP analysis** using BioBERT and spaCy on clinical notes to extract semantic information
6. **Risk prediction** using XGBoost machine learning model
7. **SHAP explanation generation** for interpretable AI - shows which factors contributed to the risk score
8. **Results storage** in database for audit trail
9. **Risk level assessment**:
   - 🔴 **High risk (≥ 0.7)** → Alert clinical staff for immediate intervention
   - 🟢 **Low/Medium risk (< 0.7)** → Standard notification
10. **Display results** to user with risk level, score, and top contributing factors

---

### 3. Data Anonymization Process (HIPAA Safe Harbor)

![Data Anonymization BPMN](docs/images/bpmn_anonymization.png)

**Process Overview:**

This diagram shows the HIPAA Safe Harbor compliant de-identification process:

1. **Receive patient data** requiring anonymization
2. **Load FHIR data** from database
3. **Parallel processing** of 18 HIPAA identifiers (as per Safe Harbor method):
   - Remove/hash patient names
   - Generalize dates (keep year only, shift by random offset)
   - Remove contact information (phone, email, fax)
   - Remove unique identifiers (SSN, MRN, account numbers)
   - Generalize geographic data (state level only, no cities/zip codes)
   - Generalize ages (>89 years → "90+", children in age groups)
4. **Convergence** after all identifiers processed
5. **Create mapping** between original patient ID and pseudo-patient ID
6. **Store anonymized data** for ML training and research
7. **Audit log creation** for compliance tracking
8. **Completion** → Anonymized data ready for use

---

### 4. Feature Extraction & NLP Process

![Feature Extraction BPMN](docs/images/bpmn_feature_extraction.png)

**Process Overview:**

This workflow demonstrates how HealthFlowMS extracts 30+ clinical features for ML prediction:

1. **Receive patient data** for feature extraction
2. **Parallel feature extraction** across four categories:
   
   **a) Demographic Features Subprocess:**
   - Age, gender, race, ethnicity
   
   **b) Clinical Features Subprocess:**
   - Vital signs (heart rate, blood pressure, temperature, SpO2)
   - Laboratory results (hemoglobin, creatinine, glucose, electrolytes)
   - Length of stay, admission type
   
   **c) Comorbidity Indices Subprocess:**
   - Charlson Comorbidity Index
   - Elixhauser Comorbidity Score
   
   **d) NLP Analysis Subprocess:**
   - Load BioBERT pre-trained model
   - Extract medical entities (diseases, medications, procedures)
   - Calculate sentiment and urgency scores from clinical notes
   - Count entity types for complexity assessment

3. **Feature convergence** after all parallel processes complete
4. **Combine features** into a single feature vector (30+ dimensions)
5. **Feature validation** ensures completeness:
   - ❌ **Missing features** → Apply imputation or default values
   - ✅ **Complete** → Continue
6. **Completion** → Features ready for XGBoost model

---

### 5. CI/CD Deployment Process (Jenkins)

![CI/CD Pipeline BPMN](docs/images/bpmn_cicd.png)

**Process Overview:**

This diagram illustrates the automated Jenkins CI/CD pipeline:

1. **Code commit** to GitHub repository (develop or main branch)
2. **Jenkins pipeline triggered** automatically via webhook
3. **Code checkout** from Git repository
4. **Parallel build process**:
   - **Java services:** Maven clean package (Proxy FHIR)
   - **Python services:** pip install requirements (All FastAPI services)
5. **Build convergence** after all services built
6. **Parallel testing**:
   - **JUnit tests** for Java services
   - **pytest tests** for Python services (score-api, deid, featurizer, model-risque)
7. **Test convergence** after all tests complete
8. **Test result gateway**:
   - ❌ **Tests failed** → Build fails, notify developers
   - ✅ **Tests passed** → Continue deployment
9. **Build Docker images** for all services
10. **Tag Docker images** with version and commit hash
11. **Branch-based deployment**:
    - **develop branch** → Deploy to staging environment for QA testing
    - **main branch** → Deploy to production environment
12. **Success** → All services deployed and running

---

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (20.10+)
- **Git**
- **8GB RAM** minimum (recommended: 16GB)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/OsamaMansouri/HealthFlowMS.git
cd HealthFlowMS
```

#### 2. Start All Services

```bash
# Start all 12 services
docker-compose up -d

# This will start:
# - All 8 microservices
# - PostgreSQL + Redis
# - Prometheus + Grafana
# - Jenkins
```

#### 3. Check Service Status

```bash
docker-compose ps

# Expected output:
# ✔ healthflow-frontend         Running
# ✔ healthflow-score-api        Running
# ✔ healthflow-deid             Running
# ✔ healthflow-featurizer       Running
# ✔ healthflow-model-risque     Running
# ✔ healthflow-audit-fairness   Running
# ✔ healthflow-proxy-fhir       Running
# ✔ healthflow-postgres         Healthy
# ✔ healthflow-redis            Running
# ✔ healthflow-prometheus       Running
# ✔ healthflow-grafana          Running
# ✔ healthflow-jenkins          Running
```

#### 4. Initialize Database (First Time Only)

```bash
# Create all database tables
docker exec healthflow-score-api python -c "
import sys
sys.path.insert(0, '/app')
from app.database import Base, engine
from app.models import User, ApiAuditLog, RiskPrediction, DeidPatient
Base.metadata.create_all(bind=engine)
print('✅ Database tables created!')
"
```

#### 5. Create Default Users

```bash
docker exec healthflow-score-api python -c "
import sys
sys.path.insert(0, '/app')
from app.database import SessionLocal
from app.services import UserService

db = SessionLocal()
user_service = UserService(db)

users = [
    {'username': 'admin', 'password': 'admin123', 'role': 'admin', 'email': 'admin@healthflow.local', 'full_name': 'Administrator'},
    {'username': 'clinician', 'password': 'admin123', 'role': 'clinician', 'email': 'clinician@healthflow.local', 'full_name': 'Clinical User'},
    {'username': 'researcher', 'password': 'admin123', 'role': 'researcher', 'email': 'researcher@healthflow.local', 'full_name': 'Researcher'},
    {'username': 'auditor', 'password': 'admin123', 'role': 'auditor', 'email': 'auditor@healthflow.local', 'full_name': 'Auditor'}
]

for u in users:
    if not user_service.get_user_by_username(u['username']):
        user_service.create_user(u['username'], u['email'], u['password'], u['full_name'], u['role'])
        print(f'✅ Created user: {u[\"username\"]}')
    else:
        print(f'ℹ️  User {u[\"username \"]} already exists')
"
```

#### 6. Access the Application

Open your browser and navigate to:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:8087 | admin / admin123 |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **Jenkins** | http://localhost:8088 | (see setup wizard) |

### Login Credentials

**Default users** (⚠️ Change passwords in production!):

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| `admin` | `admin123` | admin | Full system access |
| `clinician` | `admin123` | clinician | Patient management & predictions |
| `researcher` | `admin123` | researcher | Read-only access to data |
| `auditor` | `admin123` | auditor | Audit logs & fairness dashboard |

---

## 🌐 Service Endpoints

### User-Facing Services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8087 | Main user interface |
| **Grafana** | http://localhost:3000 | Monitoring dashboards |
| **Jenkins** | http://localhost:8088 | CI/CD pipeline |
| **Audit Fairness** | http://localhost:8086 | Fairness dashboard |

### API Documentation (Swagger/OpenAPI)

| Service | URL | Description |
|---------|-----|-------------|
| **Score API** | http://localhost:8085/docs | Main REST API |
| **DeID Service** | http://localhost:8082/docs | De-identification API |
| **Featurizer** | http://localhost:8083/docs | Feature extraction API |
| **Model Risque** | http://localhost:8084/docs | ML prediction API |
| **Proxy FHIR** | http://localhost:8081/actuator | Spring Boot Actuator |
| **HAPI FHIR** | http://localhost:8090/fhir | FHIR server |

### Key API Endpoints

**Score API (Main API):**

```bash
POST /api/v1/auth/login              # Login with JWT
GET  /api/v1/patients                # List patients
GET  /api/v1/patients/{id}/risk-score # Get risk score
GET  /api/v1/patients/{id}/risk-explanation # SHAP explanation
GET  /api/v1/dashboard/stats         # Dashboard statistics
```

**Proxy FHIR:**

```bash
POST /api/fhir/sync                  # Trigger FHIR sync
GET  /api/fhir/patients              # List patients
POST /api/fhir/proxy/Patient         # Create patient (proxy)
```

**Model Risque:**

```bash
POST /api/predict                    # Predict risk
GET  /api/predict/{patient_id}       # Get prediction
GET  /api/predict/{patient_id}/explanation # SHAP explanation
```

---

## 📊 Complete Workflow

### End-to-End Prediction Workflow

```mermaid
graph LR
    A[1. Create Patient] --> B[2. Add Medical Data]
    B --> C[3. Sync to PostgreSQL]
    C --> D[4. Anonymize HIPAA]
    D --> E[5. Extract Features]
    E --> F[6. NLP Analysis]
    F --> G[7. XGBoost Prediction]
    G --> H[8. SHAP Explanation]
    H --> I[9. Fairness Audit]
    I --> J[10. Display Results]
    
    style A fill:#e1f5ff
    style D fill:#ffe1e1
    style G fill:#e1ffe1
    style J fill:#f0e1ff
```

### Workflow Steps in Detail

1. **Create Patient** → HAPI FHIR (via Proxy FHIR)
2. **Add Medical Data** → Encounters, Observations, Conditions
3. **Sync to PostgreSQL** → Proxy FHIR synchronization
4. **Anonymize** → DeID service (HIPAA Safe Harbor - 18 identifiers removed)
5. **Extract Features** → Featurizer (30+ features)
6. **NLP Analysis** → BioBERT + spaCy on clinical notes
7. **Predict Risk** → XGBoost model inference
8. **Generate Explanations** → SHAP values for interpretability
9. **Fairness Audit** → Bias detection across demographics
10. **Visualize** → Frontend displays risk score + SHAP explanations

---

## 🤖 Machine Learning

### Model: XGBoost

**Hyperparameters:**

```python
{
    "n_estimators": 500,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "eval_metric": "auc"
}
```

**Performance Metrics:**

| Metric | Value |
|--------|-------|
| **AUC-ROC** | **0.82** |
| **Precision** | **0.78** |
| **Recall** | **0.74** |
| **F1-Score** | **0.76** |

### Features (30+)

**Feature Categories:**

1. **Demographics:** age, gender
2. **Clinical:** length of stay, previous admissions (30d, 90d, 365d)
3. **Comorbidities:** Charlson index, Elixhauser score
4. **Vital Signs:** heart rate, blood pressure, temperature, SpO2
5. **Laboratory:** hemoglobin, creatinine, glucose, electrolytes
6. **NLP Features:** sentiment_score, urgency_score, complexity_score, entities_count

### Explainability: SHAP

**SHAP (SHapley Additive exPlanations)** provides:

- ✅ Feature contribution values for each prediction
- ✅ Top risk factors identification
- ✅ Clinically interpretable explanations
- ✅ Visualization of feature importance

**Example SHAP Output:**

```json
{
  "risk_score": 0.73,
  "risk_level": "HIGH",
  "top_risk_factors": [
    {"feature": "previous_admissions_30d", "shap_value": 0.15, "contribution": "+15%"},
    {"feature": "charlson_index", "shap_value": 0.12, "contribution": "+12%"},
    {"feature": "age", "shap_value": 0.08, "contribution": "+8%"}
  ]
}
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── score-api/
│   ├── test_auth.py           # Authentication tests
│   ├── test_health.py         # Health check tests
│   └── conftest.py            # Pytest fixtures
├── deid/
│   └── test_deid_service.py   # Anonymization tests
├── featurizer/
│   └── test_feature_service.py # Feature extraction tests
├── model-risque/
│   └── test_model_service.py   # ML prediction tests
└── proxy-fhir/
    └── src/test/java/          # JUnit tests
```

### Running Tests

#### Python Services (pytest)

```bash
# Run all tests for a service
docker exec healthflow-score-api pytest tests/ -v

# Run specific test file
docker exec healthflow-score-api pytest tests/test_auth.py -v

# Run with coverage
docker exec healthflow-score-api pytest --cov=app --cov-report=html tests/
```

#### Java Service (JUnit)

```bash
# Run tests in Docker
docker exec healthflow-proxy-fhir mvn test

# Run specific test class
docker exec healthflow-proxy-fhir mvn test -Dtest=FhirProxyControllerTest
```

### Test Coverage

| Service | Tests | Coverage |
|---------|-------|----------|
| Score API | 15+ test cases | 85% |
| DeID | 10+ test cases | 80% |
| Featurizer | 12+ test cases | 78% |
| Model Risque | 8+ test cases | 75% |
| Proxy FHIR | 20+ test cases | 82% |

### Available Test Cases

**Score API:**
- ✅ User login with valid credentials
- ✅ User login with invalid credentials
- ✅ Token validation
- ✅ Current user retrieval
- ✅ Dashboard statistics
- ✅ Health check endpoint

**DeID Service:**
- ✅ Patient anonymization (HIPAA Safe Harbor)
- ✅ Batch anonymization
- ✅ Mapping retrieval
- ✅ Audit log creation

**Featurizer:**
- ✅ Feature extraction from patient data
- ✅ NLP analysis of clinical notes
- ✅ Batch feature extraction
- ✅ BioBERT entity extraction

**Model Risque:**
- ✅ Risk prediction
- ✅ SHAP explanation generation
- ✅ Batch predictions
- ✅ High-risk patient identification

---

## 🎯 Code Quality (SonarQube)

### Overview

**SonarQube** provides automated code quality and security analysis for all HealthFlowMS Python services.

**URL:** http://localhost:9000  
**Credentials:** admin / admin (change on first login)  
**Project:** healtiMS

### What SonarQube Analyzes

- 🐛 **Bugs** - Code defects and potential errors
- 🔒 **Security Vulnerabilities** - Security issues and hotspots
- 📏 **Code Smells** - Maintainability issues
- 📊 **Code Coverage** - Test coverage percentage  
- 🔄 **Code Duplication** - Duplicated code blocks
- 📈 **Complexity** - Cyclomatic complexity

### Quick Start

#### 1. Start SonarQube

```bash
# Start SonarQube service
docker-compose up -d sonarqube

# Check status
docker-compose ps sonarqube

# Wait for SonarQube to be ready (~2 minutes)
docker-compose logs -f sonarqube
# Look for: "SonarQube is operational"
```

#### 2. Access & Configure

1. Open http://localhost:9000
2. Login with `admin` / `admin`
3. **Change password** when prompted
4. Go to **My Account** → **Security** → **Generate Token**
5. Name: `healthflowms-token`
6. Copy the token

#### 3. Create Project (First Time Only)

1. Click **"+"** or **"Create Project"**
2. Choose **"Manually"**
3. Enter:
   - Project key: `healtiMS`
   - Display name: `HealthFlow-MS`
4. Click **"Set Up"**

#### 4. Run Analysis

**Using sonar-scanner (Local install):**

```bash
# Navigate to project root
cd c:\Users\Dark\Desktop\5iir\HealthFlowMS

# Run analysis
C:\sonar-scanner-8.0.1.6346-windows-x64\bin\sonar-scanner.bat
```

**Note:** The configuration is in `sonar-project.properties` at the root. Update your token in this file before running.

**Or use Docker:**

```bash
docker run --rm \
  --network=healthflowms_default \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli \
  -Dsonar.projectKey=healtiMS \
  -Dsonar.token=YOUR_TOKEN_HERE
```

### Analyzed Services

**Current Analysis Scope:**

| Service | Language | Lines of Code | Status |
|---------|----------|---------------|--------|
| **Score API** | Python 3.11 | ~2,000 | ✅ Analyzed |
| **DeID** | Python 3.11 | ~800 | ✅ Analyzed |
| **Featurizer** | Python 3.11 | ~1,200 | ✅ Analyzed |
| **Model Risque** | Python 3.11 | ~1,000 | ✅ Analyzed |
| **Audit Fairness** | Python 3.11 | ~600 | ✅ Analyzed |

**Configuration:** [sonar-project.properties](file:///c:/Users/Dark/Desktop/5iir/HealthFlowMS/sonar-project.properties)

### Viewing Results

1. Open http://localhost:9000
2. Click on the **"healtiMS"** project
3. Explore:
   - **Overview** - Quality gate status, key metrics
   - **Issues** - All bugs, vulnerabilities, code smells
   - **Measures** - Detailed metrics (coverage, complexity, duplication)
   - **Code** - Browse source code with highlighted issues
   - **Activity** - Analysis history

### Quality Metrics

After analysis, you'll see:

- ✅ **Total Lines of Code** - All Python services combined
- ✅ **Bugs** - Logic errors and potential issues
- ✅ **Vulnerabilities** - Security weaknesses
- ✅ **Code Smells** - Maintainability issues
- ✅ **Technical Debt** - Estimated time to fix issues
- ✅ **Duplications** - Percentage of duplicated code
- ✅ **Complexity** - Cyclomatic complexity score

### Best Practices

1. **Run before commits**: Analyze code before pushing
2. **Fix critical issues first**: Bugs > Vulnerabilities > Code Smells
3. **Maintain quality gate**: Keep project passing quality standards
4. **Reduce duplication**: Extract common code to functions
5. **Follow PEP 8**: Python code style guidelines

### Troubleshooting

**SonarQube won't start:**
```bash
# Check if database exists
docker exec healthflow-postgres psql -U healthflow -l | grep sonarqube

# If missing, create it:
docker exec healthflow-postgres psql -U healthflow -c "CREATE DATABASE sonarqube;"

# Restart SonarQube
docker-compose restart sonarqube
```

**Analysis fails:**
- Verify SonarQube is accessible: http://localhost:9000/api/system/status
- Check your token is valid in SonarQube → My Account → Security
- Ensure `sonar-project.properties` has correct token

**📚 Complete Guide:** [SONARQUBE.md](file:///c:/Users/Dark/Desktop/5iir/HealthFlowMS/SONARQUBE.md)

---

## 📈 Monitoring & Observability

### Monitoring Stack Architecture

```mermaid
graph TB
    subgraph "Microservices"
        MS1[Score API:8085<br/>/metrics]
        MS2[DeID:8082<br/>/metrics]
        MS3[Featurizer:8083<br/>/metrics]
        MS4[Model Risque:8084<br/>/metrics]
        MS5[Proxy FHIR:8081<br/>/actuator/prometheus]
    end
    
    subgraph "Monitoring"
        Prom[Prometheus:9090<br/>Scrape every 15s]
        Graf[Grafana:3000<br/>Dashboards]
    end
    
    MS1 -->|metrics| Prom
    MS2 -->|metrics| Prom
    MS3 -->|metrics| Prom
    MS4 -->|metrics| Prom
    MS5 -->|metrics| Prom
    
    Prom -->|data| Graf
    
    style Prom fill:#e1ffe1
    style Graf fill:#e1f5ff
```

### Prometheus

**URL:** http://localhost:9090

**Configuration:**
- Scrape interval: 15 seconds
- Retention: 15 days
- Metrics path: `/metrics` (FastAPI) or `/actuator/prometheus` (Spring Boot)

**Monitored Services:**
- ✅ proxy-fhir (Spring Boot Actuator)
- ✅ score-api (FastAPI with prometheus-client)
- ✅ deid (FastAPI with prometheus-client)
- ✅ featurizer (FastAPI with prometheus-client)
- ✅ model-risque (FastAPI with prometheus-client)
- ✅ audit-fairness (FastAPI with prometheus-client)
- ✅ postgres (postgres-exporter)

### Grafana

**URL:** http://localhost:3000  
**Credentials:** admin / admin

**Pre-configured:**
- ✅ Prometheus datasource (automatic)
- ✅ Dashboard provisioning enabled
- ✅ HealthFlow dashboard included

**Dashboard Panels:**

1. **Services Status** - UP/DOWN status for all services
2. **Request Rate (req/s)** - HTTP requests per second by service
3. **Request Latency (p95)** - 95th percentile latency
4. **Anonymizations (24h)** - DeID service real API calls
5. **Feature Extractions (24h)** - Featurizer real API calls
6. **Risk Predictions (24h)** - Model Risque real API calls
7. **FHIR Operations (24h)** - Proxy FHIR real API calls
8. **Request Distribution** - Pie chart of requests by service
9. **CPU Usage** - CPU usage by service
10. **Memory Usage (MB)** - Memory consumption

> **Note:** All metrics are filtered to show only real API calls (excluding `/health`, `/metrics`, `/docs` endpoints).

### Available Metrics

**HTTP Metrics:**
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency histogram
- `http_requests_in_progress` - Active requests

**System Metrics:**
- `process_cpu_seconds_total` - CPU usage
- `process_resident_memory_bytes` - Memory usage
- `process_open_fds` - Open file descriptors

**Database Metrics:**
- `pg_up` - PostgreSQL status
- `pg_stat_database_*` - Database statistics

---

## 🚀 CI/CD Pipeline

### Jenkins

**URL:** http://localhost:8088

**Features:**
- ✅ Docker-in-Docker support
- ✅ Maven for Java builds (Proxy FHIR)
- ✅ Python 3 + pip for Python services
- ✅ Pre-installed plugins: Git, Docker Workflow, Blue Ocean

### Pipeline Architecture

```mermaid
graph LR
    A[1. Checkout] --> B[2. Build]
    B --> C[3. Test]
    C --> D{Tests Pass?}
    D -->|Yes| E[4. Build Docker]
    D -->|No| F[❌ Fail]
    E --> G[5. Push Images]
    G --> H{Branch?}
    H -->|develop| I[6. Deploy Staging]
    H -->|main| J[6. Deploy Production]
    I --> K[✅ Success]
    J --> K
    
    style A fill:#e1f5ff
    style D fill:#ffe1e1
    style E fill:#e1ffe1
    style K fill:#d4f1d4
    style F fill:#ffd4d4
```

### Pipeline Stages

**Jenkinsfile** (located at project root):

```groovy
pipeline {
    agent any
    
    stages {
        stage('1. Checkout') {
            steps {
                git branch: '${BRANCH_NAME}', url: 'https://github.com/OsamaMansouri/HealthFlowMS.git'
            }
        }
        
        stage('2. Build Java Services') {
            steps {
                dir('proxy-fhir') {
                    sh 'mvn clean package -DskipTests'
                }
            }
        }
        
        stage('3. Build Python Services') {
            parallel {
                stage('Score API') {
                    steps {
                        dir('score-api') {
                            sh 'pip install -r requirements.txt'
                        }
                    }
                }
                stage('DeID') {
                    steps {
                        dir('deid') {
                            sh 'pip install -r requirements.txt'
                        }
                    }
                }
                // ... other services
            }
        }
        
        stage('4. Run Tests') {
            parallel {
                stage('Test Java') {
                    steps {
                        dir('proxy-fhir') {
                            sh 'mvn test'
                        }
                    }
                }
                stage('Test Python') {
                    steps {
                        sh 'docker exec healthflow-score-api pytest tests/ -v'
                    }
                }
            }
        }
        
        stage('5. Build Docker Images') {
            steps {
                sh 'docker-compose build'
            }
        }
        
        stage('6. Deploy') {
            when {
                branch 'develop'
            }
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}
```

### Triggering Builds

**Manual:**
```bash
# Navigate to Jenkins
http://localhost:8088

# Click "New Item" → "Pipeline"
# Configure Git repository and Jenkinsfile
# Click "Build Now"
```

**Automatic (Webhook):**
- Configure GitHub webhook: `http://your-server:8088/github-webhook/`
- Builds trigger automatically on push

---

## 📚 API Documentation

Each service provides interactive API documentation via Swagger/OpenAPI:

| Service | Swagger UI |
|---------|------------|
| **Score API** | http://localhost:8085/docs |
| **DeID** | http://localhost:8082/docs |
| **Featurizer** | http://localhost:8083/docs |
| **Model Risque** | http://localhost:8084/docs |

### Example API Calls

**1. Login:**

```bash
curl -X POST http://localhost:8085/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**2. Get Risk Score:**

```bash
curl -X GET http://localhost:8085/api/v1/patients/12345/risk-score \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "patient_id": "12345",
  "risk_score": 0.73,
  "risk_level": "HIGH",
  "prediction_timestamp": "2024-12-26T00:00:00Z"
}
```

**3. Get SHAP Explanation:**

```bash
curl -X GET http://localhost:8084/api/predict/12345/explanation \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response:
{
  "pseudo_patient_id": "12345",
  "risk_score": 0.73,
  "top_risk_factors": [
    {"feature": "previous_admissions_30d", "shap_value": 0.15},
    {"feature": "charlson_index", "shap_value": 0.12}
  ]
}
```

---

## 📮 Postman Collection

A comprehensive **Postman collection** is available to test all microservices.

**Location:** `postman/HealthFlow.postman_collection.json`

### Import Collection

1. **Open Postman** (Desktop or Web)
2. Click **Import** → **Upload Files**
3. Select `postman/HealthFlow.postman_collection.json`
4. Collection imported with 50+ endpoints!

### Collection Structure

The collection includes **9 main sections**:

1. **Authentication (ScoreAPI:8085)** - Login, token, current user
2. **HAPI FHIR Server (8090)** - FHIR resource creation
3. **ProxyFHIR (8081)** - FHIR sync operations
4. **DeID - Anonymisation (8082)** - HIPAA de-identification
5. **Featurizer (8083)** - Feature extraction + NLP
6. **ModelRisque - ML (8084)** - Risk predictions + SHAP
7. **ScoreAPI - Endpoints (8085)** - Dashboard, patients, scores
8. **AuditFairness Dashboard (8086)** - Fairness metrics
9. **Complete Workflow Test** - End-to-end flow

### Quick Start with Postman

```bash
# 1. Start services
docker-compose up -d

# 2. Import collection in Postman

# 3. Run "1.1 Login - Get Token"
#    Token automatically saved to {{token}} variable

# 4. Run complete workflow:
#    Navigate to "9. Complete Workflow Test"
#    Run requests in order (Step 1 → Step 6)
```

---

## 🔒 Security & Compliance

### HIPAA Compliance

**De-Identification (HIPAA Safe Harbor):**

The DeID service removes/modifies **18 HIPAA identifiers**:

1. ✅ Names
2. ✅ Geographic subdivisions smaller than state
3. ✅ Dates (except year)
4. ✅ Phone numbers
5. ✅ Fax numbers
6. ✅ Email addresses
7. ✅ Social Security numbers
8. ✅ Medical record numbers
9. ✅ Health plan beneficiary numbers
10. ✅ Account numbers
11. ✅ Certificate/license numbers
12. ✅ Vehicle identifiers
13. ✅ Device identifiers/serial numbers
14. ✅ URLs
15. ✅ IP addresses
16. ✅ Biometric identifiers
17. ✅ Full-face photos
18. ✅ Other unique identifying numbers

**Age Generalization:**
- Ages > 89 → "90+"
- Ages 0-17 → Age groups (0-4, 5-9, 10-14, 15-17)
- Ages 18-89 → Kept as-is

### Authentication & Security

- ✅ **JWT (JSON Web Tokens)** for API authentication
- ✅ **bcrypt** password hashing (cost factor: 12)
- ✅ **Role-based access control** (RBAC): admin, clinician, researcher, auditor
- ✅ **CORS** configuration for secure cross-origin requests
- ✅ **Audit logging** for all actions
- ✅ **HTTPS ready** (configure reverse proxy for production)

### Security Best Practices

**Production Deployment:**

1. ⚠️ **Change default passwords immediately**
2. ⚠️ **Use environment variables for secrets**
3. ⚠️ **Enable HTTPS/TLS** with valid certificates
4. ⚠️ **Configure firewall rules**
5. ⚠️ **Regular security audits**
6. ⚠️ **Keep dependencies updated**

---

## 📁 Project Structure

```
HealthFlowMS/
├── score-api/                 # Main REST API (FastAPI)
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── auth.py           # JWT authentication
│   │   ├── models.py         # Database models
│   │   ├── services.py       # Business logic
│   │   ├── cache.py          # Redis caching
│   │   └── config.py         # Configuration
│   ├── tests/                # Pytest tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── deid/                     # De-identification service
│   ├── app/
│   │   ├── main.py
│   │   ├── deid_service.py   # HIPAA Safe Harbor logic
│   │   ├── models.py
│   │   └── schemas.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── featurizer/               # Feature extraction + NLP
│   ├── app/
│   │   ├── main.py
│   │   ├── feature_service.py
│   │   ├── nlp_service.py    # BioBERT + spaCy
│   │   └── models.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── model-risque/             # Risk prediction service
│   ├── app/
│   │   ├── main.py
│   │   ├── model_service.py  # XGBoost + SHAP
│   │   └── models.py
│   ├── models/
│   │   └── readmission_model.pkl
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── audit-fairness/           # Fairness dashboard (Dash)
│   ├── app/
│   │   ├── main.py
│   │   ├── fairness_service.py
│   │   └── models.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── proxy-fhir/               # FHIR proxy (Java/Spring Boot)
│   ├── src/
│   │   ├── main/java/com/healthflow/fhirnew/
│   │   │   ├── controller/
│   │   │   ├── service/
│   │   │   ├── model/
│   │   │   └── config/
│   │   └── test/java/
│   ├── pom.xml
│   └── Dockerfile
│
├── frontend/                 # React/TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.tsx
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── nginx.conf
│   └── Dockerfile
│
├── database/                 # Database initialization
│   ├── init/
│   │   ├── init_database.py
│   │   └── create_default_users.py
│   └── backup/               # Database backups
│
├── monitoring/               # Monitoring configuration
│   ├── prometheus/
│   │   └── prometheus.yml    # Prometheus config
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml
│           └── dashboards/
│               └── healthflow_dashboard.json
│
├── jenkins/                  # Jenkins configuration
│   └── Dockerfile
│
├── postman/                  # Postman API collection
│   └── HealthFlow.postman_collection.json
│
├── docs/                     # Documentation
│   └── images/               # Screenshots & diagrams
│
├── docker-compose.yml        # Docker Compose configuration
├── Jenkinsfile               # CI/CD pipeline
├── README.md                 # This file
├── ARCHITECTURE.md           # Architecture documentation
├── MONITORING.md             # Monitoring documentation
├── README_TESTS.md           # Testing documentation
└── .gitignore
```

---

## 💻 Development

### Running Individual Services

**Python Services (Local Development):**

```bash
# Example: Score API
cd score-api

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://healthflow:healthflow123@localhost:5432/healthflow"
export SECRET_KEY="your-secret-key"

# Run service
uvicorn app.main:app --reload --port 8085
```

**Java Service (Proxy FHIR):**

```bash
cd proxy-fhir

# Build with Maven
mvn clean package

# Run
java -jar target/app.jar
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://healthflow:healthflow123@postgres:5432/healthflow

# JWT
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# FHIR
FHIR_SERVER_URL=http://hapi-fhir:8090/fhir

# CORS
CORS_ORIGINS=http://localhost:8087,http://localhost:3000
```

### Building Docker Images

```bash
# Build all services
docker-compose build

# Build single service
docker-compose build score-api

# Build with no cache
docker-compose build --no-cache deid

# Build and start
docker-compose up -d --build
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs for a service
docker-compose logs -f score-api

# View last 100 lines
docker-compose logs --tail=100 deid

# View logs for multiple services
docker-compose logs -f score-api deid featurizer
```

### Database Management

**Access PostgreSQL:**

```bash
# Connect to database
docker exec -it healthflow-postgres psql -U healthflow -d healthflow

# List tables
\dt

# Describe table
\d fhir_patients

# Query
SELECT * FROM users;

# Exit
\q
```

**Backup Database:**

```bash
# Manual backup
docker exec healthflow-postgres pg_dump -U healthflow healthflow > backup.sql

# Restore
docker exec -i healthflow-postgres psql -U healthflow healthflow < backup.sql
```

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]

# Rebuild and restart
docker-compose up -d --build [service-name]
```

#### 2. CORS Errors in Frontend

```bash
# Check score-api CORS configuration
docker-compose logs score-api | grep CORS

# Restart score-api
docker-compose restart score-api

# Verify CORS headers
curl -I http://localhost:8085/api/v1/health
```

#### 3. Database Connection Issues

```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# Test connection
docker exec healthflow-postgres pg_isready -U healthflow

# Check logs
docker-compose logs postgres
```

#### 4. Port Already in Use

```bash
# Windows: Find process using port
netstat -ano | findstr :8085

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

#### 5. Out of Memory

```bash
# Check Docker resource limits
docker stats

# Stop unnecessary services
docker-compose stop backup

# Increase Docker memory in Docker Desktop:
# Settings → Resources → Memory (16GB recommended)
```

#### 6. Jenkins Not Starting

```bash
# Check logs
docker-compose logs jenkins

# Get initial admin password
docker exec healthflow-jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# Restart Jenkins
docker-compose restart jenkins
```

#### 7. Grafana Dashboard Not Loading

```bash
# Check Prometheus is running
docker-compose ps prometheus

# Test Prometheus
curl http://localhost:9090/-/healthy

# Restart Grafana
docker-compose restart grafana
```

### Stopping Services

```bash
# Stop all services (keeps volumes)
docker-compose down

# Stop and remove volumes (⚠️ deletes data!)
docker-compose down -v

# Stop individual service
docker-compose stop score-api
```

### Cleanup

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune -a

# Remove everything (⚠️ nuclear option!)
docker system prune -a --volumes
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Workflow

1. **Fork the repository**

```bash
git clone https://github.com/yourusername/HealthFlowMS.git
cd HealthFlowMS
```

2. **Create a feature branch**

```bash
git checkout -b feature/amazing-feature
```

3. **Make your changes**

   - Follow existing code style
   - Add tests for new features
   - Update documentation
   - Test locally with `docker-compose up`

4. **Run tests**

```bash
# Python tests
docker exec healthflow-score-api pytest tests/ -v

# Java tests
docker exec healthflow-proxy-fhir mvn test
```

5. **Commit your changes**

```bash
git add .
git commit -m "Add amazing feature"
```

6. **Push to your fork**

```bash
git push origin feature/amazing-feature
```

7. **Open a Pull Request**

   - Go to GitHub
   - Click "New Pull Request"
   - Describe your changes
   - Submit!

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Use Black formatter

**Java:**
- Follow Google Java Style Guide
- Use meaningful variable names
- Add Javadoc comments

**TypeScript:**
- Follow Airbnb style guide
- Use ESLint
- Add JSDoc comments

---

## 📄 License

**Dark**

---

## 🔗 Links

- **GitHub Repository:** https://github.com/OsamaMansouri/HealthFlowMS
- **API Documentation:** Available at `/docs` endpoint of each service
- **Contact:** mansouri.osama@gmail.com

---

## 📊 Stats & Badges

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Services](https://img.shields.io/badge/Services-12-green)
![ML Model](https://img.shields.io/badge/ML-XGBoost-orange)
![AUC](https://img.shields.io/badge/AUC--ROC-0.82-brightgreen)
![HIPAA](https://img.shields.io/badge/HIPAA-Compliant-red)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

---

<div align="center">

**HealthFlowMS** - Transforming healthcare through AI-powered risk prediction 🏥

Made with ❤️ by the Dark Team

</div>
