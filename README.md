# HealthFlowMS - Hospital Readmission Prediction System

A comprehensive microservices-based healthcare management system for predicting hospital readmission risk using FHIR standards, Machine Learning (XGBoost), and Natural Language Processing (BioBERT, spaCy).

## 📋 Overview

**HealthFlowMS** is a complete hospital readmission prediction system that:

- Uses **FHIR (Fast Healthcare Interoperability Resources)** standards for medical data integration
- Implements **HIPAA Safe Harbor** compliant data anonymization
- Provides **XGBoost-based risk predictions** with **SHAP explainability**
- Extracts **30+ clinical features** including NLP analysis of clinical notes
- Offers **fairness auditing** to detect and correct prediction biases
- Features a modern **React/TypeScript frontend** for intuitive user interaction

**Model Performance:** AUC-ROC 0.82 | Precision 0.78 | Recall 0.74 | F1-Score 0.76

## 🏗️ Architecture

The system consists of **8 microservices** following a modern microservices architecture:

| Service           | Port | Technology                | Role                                      |
| ----------------- | ---- | ------------------------- | ----------------------------------------- |
| **HAPI FHIR**     | 8090 | HAPI FHIR Server          | Reference FHIR server                     |
| **ProxyFHIR**     | 8081 | Java 17 / Spring Boot 3.2 | FHIR synchronization & proxy              |
| **DeID**          | 8082 | Python 3.11 / FastAPI     | HIPAA Safe Harbor anonymization           |
| **Featurizer**    | 8083 | Python 3.11 / FastAPI     | Feature extraction + NLP (BioBERT, spaCy) |
| **ModelRisque**   | 8084 | Python 3.11 / FastAPI     | ML prediction (XGBoost 2.0, SHAP 0.44)    |
| **ScoreAPI**      | 8085 | Python 3.11 / FastAPI     | Main REST API with JWT authentication     |
| **AuditFairness** | 8086 | Python 3.11 / Dash        | Fairness dashboard & bias detection       |
| **Frontend**      | 8087 | React 18.2 / TypeScript   | User interface                            |

### Technology Stack

**Backend:**

- **Java 17** + Spring Boot 3.2.0 (ProxyFHIR)
- **Python 3.11** + FastAPI 0.109.0 (Python services)
- **PostgreSQL 15** (Central database)

**Frontend:**

- **React 18.2** + **TypeScript**
- **Vite 5.0** (Build tool)
- **Tailwind CSS** (Styling)
- **Recharts 2.10.3** (Data visualization)
- **Axios 1.6.2** (HTTP client)

**Machine Learning:**

- **XGBoost 2.0.3** (Prediction model)
- **SHAP 0.44.1** (Explainability)
- **BioBERT** (transformers) (NLP for clinical text)
- **spaCy 3.7.2** (Named entity recognition)

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (20.10+)
- **Git**

### Running the Project

1. **Clone the repository:**

   ```bash
   git clone https://github.com/OsamaMansouri/HealthFlowMS.git
   cd HealthFlowMS
   ```

2. **Start all services:**

   ```bash
   docker-compose up -d
   ```

3. **Check service status:**

   ```bash
   docker-compose ps
   ```

4. **View logs:**

   ```bash
   docker-compose logs -f [service-name]
   ```

5. **Stop all services:**

   ```bash
   docker-compose down
   ```

6. **Create default users (first time setup):**

   ```bash
   docker exec -it healthflow-score-api python -c "
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
           print(f'Created user: {u[\"username\"]}')
       else:
           print(f'User {u[\"username\"]} already exists')
   "
   ```

## 🔐 Login Credentials

**Default users** (change passwords in production!):

| Username     | Password   | Role       | Access Level                     |
| ------------ | ---------- | ---------- | -------------------------------- |
| `admin`      | `admin123` | admin      | Full system access               |
| `clinician`  | `admin123` | clinician  | Patient management & predictions |
| `researcher` | `admin123` | researcher | Read-only access to data         |
| `auditor`    | `admin123` | auditor    | Audit logs & fairness dashboard  |

**To login:**

1. Open http://localhost:8087 in your browser
2. Use any of the credentials above
3. The `admin` account has full access to all features

⚠️ **Security Note:** These are default credentials for development. **Change all passwords immediately in production environments!**

## 🧪 Testing with Postman

A comprehensive **Postman collection** is available to test all microservices:

**Location:** `postman/HealthFlow.postman_collection.json`

### Import the Collection

1. **Open Postman** (Desktop app or web)
2. Click **Import** → **Upload Files**
3. Select `postman/HealthFlow.postman_collection.json`
4. The collection will be imported with all endpoints organized by service

### Collection Structure

The collection includes **9 main sections**:

1. **Authentication (ScoreAPI:8085)** - Login, get token, current user
2. **HAPI FHIR Server (8090)** - Create patients, encounters, conditions, observations
3. **ProxyFHIR (8081)** - Sync FHIR data, get synced patients
4. **DeID - Anonymisation (8082)** - Anonymize patients, get audit logs
5. **Featurizer (8083)** - Extract features, NLP analysis
6. **ModelRisque - ML (8084)** - Predict risk, SHAP explanations
7. **ScoreAPI - Endpoints (8085)** - Dashboard stats, risk scores, audit logs
8. **AuditFairness Dashboard (8086)** - Fairness metrics, bias alerts
9. **Complete Workflow Test** - End-to-end workflow from patient creation to prediction

### Using the Collection

1. **Set the base URL:**

   - The collection uses `{{base_url}}` variable (default: `http://localhost`)
   - You can change it in Postman: Collection → Variables → `base_url`

2. **Login first:**

   - Run **"1.1 Login - Get Token"** request
   - The token is automatically saved to `{{token}}` variable
   - All authenticated requests will use this token

3. **Run the complete workflow:**
   - Use **"9. Complete Workflow Test"** folder
   - Run requests in order (Step 1 → Step 6)
   - Variables are automatically set between steps

### Quick Test

```bash
# 1. Start services
docker-compose up -d

# 2. Import Postman collection
# Open Postman → Import → postman/HealthFlow.postman_collection.json

# 3. Run "1.1 Login - Get Token" (uses admin/admin123)

# 4. Test any endpoint - token is automatically included!
```

## 📡 Service Endpoints

Once running, access services at:

| Service            | URL                        | Description                 |
| ------------------ | -------------------------- | --------------------------- |
| **Frontend**       | http://localhost:8087      | Main user interface         |
| **Score API**      | http://localhost:8085/docs | API documentation (Swagger) |
| **DeID Service**   | http://localhost:8082/docs | De-identification API docs  |
| **Featurizer**     | http://localhost:8083/docs | Feature extraction API docs |
| **Model Risque**   | http://localhost:8084/docs | ML prediction API docs      |
| **Audit Fairness** | http://localhost:8086      | Fairness dashboard          |
| **Proxy FHIR**     | http://localhost:8081      | FHIR proxy API              |
| **HAPI FHIR**      | http://localhost:8090/fhir | FHIR server                 |

### Key API Endpoints

**ScoreAPI (Main API):**

```bash
POST /api/v1/auth/login              # Login with JWT
GET  /api/v1/patients                # List patients
GET  /api/v1/patients/{id}/risk-score # Get risk score
GET  /api/v1/patients/{id}/risk-explanation # SHAP explanation
GET  /api/v1/dashboard/stats         # Dashboard statistics
```

**ProxyFHIR:**

```bash
POST /api/fhir/sync                  # Trigger FHIR sync
GET  /api/fhir/patients              # List patients
POST /api/fhir/proxy/Patient         # Create patient (proxy)
```

**ModelRisque:**

```bash
POST /api/predict                    # Predict risk
GET  /api/shap/{patient_id}          # SHAP explanation
```

## 🔄 Workflow

The complete workflow follows these steps:

1. **Create Patient** → HAPI FHIR (via ProxyFHIR)
2. **Add Medical Data** → Encounters, Observations, Conditions
3. **Sync to PostgreSQL** → ProxyFHIR synchronization
4. **Anonymize** → DeID service (HIPAA Safe Harbor)
5. **Extract Features** → Featurizer (30+ features + NLP)
6. **Predict Risk** → ModelRisque (XGBoost)
7. **Generate Explanations** → SHAP values
8. **Visualize** → Frontend / AuditFairness dashboard

## 🤖 Machine Learning

### Model: XGBoost

**Hyperparameters:**

- n_estimators: 500
- max_depth: 6
- learning_rate: 0.05
- subsample: 0.8
- colsample_bytree: 0.8

**Performance Metrics:**

- AUC-ROC: **0.82**
- Precision: **0.78**
- Recall: **0.74**
- F1-Score: **0.76**

### Features (30+)

The system extracts features from multiple sources:

- **Demographics:** age, gender
- **Clinical:** length of stay, previous admissions (30d, 90d, 365d)
- **Comorbidities:** Charlson index, Elixhauser score
- **Vital Signs:** heart rate, blood pressure, temperature, SpO2
- **Laboratory:** hemoglobin, creatinine, glucose, electrolytes
- **NLP Features:** sentiment_score, urgency_score, complexity_score, entities_count

### Explainability: SHAP

SHAP (SHapley Additive exPlanations) provides:

- Feature contribution values
- Risk factor identification
- Clinically interpretable explanations

## 🔒 Security & Compliance

- **HIPAA Safe Harbor** compliant anonymization (18 identifiers removed/modified)
- **JWT authentication** for API access
- **bcrypt** password hashing
- **Audit logging** for all actions
- **CORS** configuration for secure cross-origin requests

## 📦 Project Structure

```
HealthFlowMS/
├── score-api/          # Main REST API (FastAPI)
│   ├── app/
│   │   ├── main.py     # FastAPI application
│   │   ├── auth.py     # JWT authentication
│   │   ├── models.py   # Database models
│   │   └── services.py # Business logic
│   ├── Dockerfile
│   └── requirements.txt
├── deid/              # De-identification service
├── featurizer/        # Feature extraction + NLP
│   ├── app/
│   │   ├── feature_service.py
│   │   └── nlp_service.py
│   └── models/        # ML models
├── model-risque/      # Risk prediction service
│   ├── app/
│   │   └── model_service.py
│   └── models/
│       └── readmission_model.pkl
├── audit-fairness/    # Fairness dashboard (Dash)
├── proxy-fhir/        # FHIR proxy (Java/Spring Boot)
│   └── src/main/java/
├── frontend/          # React/TypeScript frontend
│   └── src/
│       ├── components/
│       ├── pages/
│       └── services/
├── database/          # Database initialization
│   └── init/          # Initialization scripts
├── docs/              # Documentation
│   ├── images/        # Screenshots & diagrams
│   └── Rapport.tex     # Complete project report
├── postman/           # Postman API collection
│   └── HealthFlow.postman_collection.json
├── docker-compose.yml # Docker Compose configuration
└── README.md
```

## 🔧 Development

### Running Individual Services

**Python Services:**

```bash
cd score-api
docker build -t healthflowms-score-api .
docker run -p 8085:8085 healthflowms-score-api
```

**Java Service (ProxyFHIR):**

```bash
cd proxy-fhir
mvn clean package
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
```

### Testing

Each service includes test files:

```bash
# Python services
cd score-api
pytest

# Java service
cd proxy-fhir
mvn test
```

## 📊 Frontend Pages

1. **Login** (`/login`) - Authentication with JWT
2. **Dashboard** (`/`) - Overview with statistics and charts
3. **Patients List** (`/patients`) - Patient management with filters
4. **Patient Detail** (`/patients/:id`) - Complete patient info + SHAP explanations
5. **Workflow** (`/patient-workflow`) - Guided patient creation workflow
6. **Predictions** (`/predictions`) - Aggregated predictions analysis

## 🗄️ Database Schema

**Main Tables:**

- `fhir_patients`, `fhir_encounters`, `fhir_observations`, `fhir_conditions` - FHIR data
- `deid_patients` - Anonymized patients
- `patient_features` - Extracted features (30+)
- `risk_predictions` - Risk scores + SHAP explanations
- `users` - System users
- `api_audit_logs` - Audit trail

## 📝 Documentation

- **Rapport.tex** - Complete project report (1842 lines) with architecture, ML details, workflows
- **PROJECT_DOCUMENTATION.md** - Summary of key project information
- **docs/images/** - Screenshots, BPMN diagrams, database schemas

## ⚠️ Important Notes

- **Frontend and proxy-fhir source code:** These services are running from pre-built Docker images. Source code was not included in the Docker images (multi-stage builds). The containers are functional and can be used as-is.
- **Database:** PostgreSQL is automatically set up with docker-compose configuration.
- **All Python services:** Complete source code is available and can be modified/rebuilt.

## 🎯 Key Features

- ✅ **FHIR Integration** - Standard medical data format
- ✅ **HIPAA Compliance** - Safe Harbor anonymization
- ✅ **ML Predictions** - XGBoost with 0.82 AUC-ROC
- ✅ **NLP Analysis** - BioBERT + spaCy for clinical notes
- ✅ **Explainability** - SHAP for transparent predictions
- ✅ **Fairness Auditing** - Bias detection and correction
- ✅ **Modern UI** - React/TypeScript frontend
- ✅ **Microservices** - Scalable, independent services

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 👥 Team

**Groupe 8 - EMSI (École Marocaine des Sciences de l'Ingénieur)**

- **Osama Mansouri** - mansouri.osama@gmail.com
- **Sohaib Laarichi** - Sohaiblaatichi112@gmail.com
- **Abouelkemhe Salah Eddine** - slaaaheddine@gmail.com

**Supervisors:**

- Pr. Mohamed LACHGAR (Microservices)
- Pr. Oumayma OUEDRHIRI (Machine Learning)
- Pr. Hiba TABBAA (Data Mining & NLP)

## 📄 License

[Your License Here]

## 🔗 Links

- **GitHub Repository:** https://github.com/OsamaMansouri/HealthFlowMS
- **API Documentation:** Available at `/docs` endpoint of each service

---

**HealthFlowMS** - Transforming healthcare through AI-powered risk prediction 🏥🤖
