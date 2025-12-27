# HealthFlow-MS SonarQube Analysis Guide

## 🎯 Overview

This guide explains how to use SonarQube for code quality analysis across all HealthFlowMS services.

## 📋 What is SonarQube?

SonarQube is an automatic code review tool that detects:
- 🐛 **Bugs** - Code defects
- 🔒 **Security Vulnerabilities** - Security issues
- 📏 **Code Smells** - Maintainability issues
- 📊 **Code Coverage** - Test coverage percentage
- 🔄 **Code Duplication** - Duplicated code blocks

## 🚀 Quick Start

### 1. Start SonarQube

```bash
# Start SonarQube service
docker-compose up -d sonarqube

# Check if SonarQube is running
docker-compose ps sonarqube

# Wait for SonarQube to be ready (~2 minutes)
docker-compose logs -f sonarqube
```

### 2. Access SonarQube

- **URL:** http://localhost:9000
- **Default Credentials:**
  - Username: `admin`
  - Password: `admin`
  
⚠️ **You will be prompted to change the password on first login**

### 3. Generate Token

1. Login to SonarQube
2. Go to **My Account** → **Security**
3. Generate a new token
4. Name it: `healthflowms-token`
5. Copy the token (you'll need it for analysis)

## 📊 Analyzing Services

### Python Services (FastAPI)

```bash
# Install SonarQube scanner for Python
pip install sonar-scanner

# Analyze Score API
cd score-api
sonar-scanner \
  -Dsonar.login=YOUR_TOKEN_HERE

# Analyze DeID Service
cd ../deid
sonar-scanner \
  -Dsonar.login=YOUR_TOKEN_HERE

# Analyze Featurizer
cd ../featurizer
sonar-scanner \
  -Dsonar.login=YOUR_TOKEN_HERE

# Analyze Model Risque
cd ../model-risque
sonar-scanner \
  -Dsonar.login=YOUR_TOKEN_HERE

# Analyze Audit Fairness
cd ../audit-fairness
sonar-scanner \
  -Dsonar.login=YOUR_TOKEN_HERE
```

### Java Service (Spring Boot)

```bash
# Analyze Proxy FHIR (using Maven)
cd proxy-fhir
mvn clean verify sonar:sonar \
  -Dsonar.projectKey=healthflowms-proxy-fhir \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=YOUR_TOKEN_HERE
```

### TypeScript Service (React Frontend)

```bash
# Install dependencies
cd frontend
npm install

# Run tests with coverage
npm run test:coverage

# Analyze with SonarScanner
sonar-scanner \
  -Dsonar.login=YOUR_TOKEN_HERE
```

## 🔧 Using Docker Scanner (Recommended)

Instead of installing sonar-scanner locally, use the Docker image:

```bash
# Create a helper script
cat > analyze.sh << 'EOF'
#!/bin/bash

# SonarQube token (replace with your token)
SONAR_TOKEN="YOUR_TOKEN_HERE"

# Function to analyze a service
analyze_service() {
    SERVICE_NAME=$1
    SERVICE_DIR=$2
    
    echo "🔍 Analyzing $SERVICE_NAME..."
    
    docker run --rm \
        --network="healthflowms_default" \
        -v "$(pwd)/$SERVICE_DIR:/usr/src" \
        sonarsource/sonar-scanner-cli \
        -Dsonar.login=$SONAR_TOKEN
}

# Analyze all Python services
analyze_service "Score API" "score-api"
analyze_service "DeID" "deid"
analyze_service "Featurizer" "featurizer"
analyze_service "Model Risque" "model-risque"
analyze_service "Audit Fairness" "audit-fairness"

# Analyze Frontend
analyze_service "Frontend" "frontend"

echo "✅ Analysis complete! View results at http://localhost:9000"
EOF

chmod +x analyze.sh
./analyze.sh
```

## 📈 Viewing Results

1. Open http://localhost:9000
2. Click on **Projects**
3. Select a project to view:
   - **Overview** - Summary of issues
   - **Issues** - Detailed list of bugs, vulnerabilities, code smells
   - **Measures** - Metrics (coverage, complexity, duplication)
   - **Code** - Browse source code with issues highlighted

## 🎯 Quality Gates

### Default Quality Gate

SonarQube includes a default "So narQube way" quality gate:

- ✅ **Coverage** >= 80%
- ✅ **Duplicated Lines** < 3%
- ✅ **Maintainability Rating** >= A
- ✅ **Reliability Rating** >= A
- ✅ **Security Rating** >= A

### Custom Quality Gate for HealthFlow-MS

To create a custom quality gate:

1. Go to **Quality Gates**
2. Click **Create**
3. Name it: `HealthFlow-MS`
4. Add conditions:
   - Code Coverage >= 75%
   - New Code Coverage >= 80%
   - Bugs = 0 (on new code)
   - Vulnerabilities = 0 (on new code)
   - Security Hotspots Reviewed = 100%

## 🔗 Integration with Jenkins

Add SonarQube analysis to your Jenkinsfile:

```groovy
stage('SonarQube Analysis') {
    steps {
        script {
            def scannerHome = tool 'SonarScanner'
            withSonarQubeEnv('SonarQube') {
                sh "${scannerHome}/bin/sonar-scanner"
            }
        }
    }
}

stage('Quality Gate') {
    steps {
        timeout(time: 5, unit: 'MINUTES') {
            waitForQualityGate abortPipeline: true
        }
    }
}
```

## 📊 Services Configuration Summary

| Service | Language | Config File | Key Metrics |
|---------|----------|-------------|-------------|
| **Score API** | Python 3.11 | `score-api/sonar-project.properties` | Coverage, Complexity, Duplications |
| **DeID** | Python 3.11 | `deid/sonar-project.properties` | Security, Data handling |
| **Featurizer** | Python 3.11 | `featurizer/sonar-project.properties` | NLP code quality |
| **Model Risque** | Python 3.11 | `model-risque/sonar-project.properties` | ML code quality |
| **Audit Fairness** | Python 3.11 | `audit-fairness/sonar-project.properties` | Fairness algorithms |
| **Proxy FHIR** | Java 17 | `proxy-fhir/sonar-project.properties` | Java best practices |
| **Frontend** | TypeScript | `frontend/sonar-project.properties` | React code quality |

## 🐛 Troubleshooting

### SonarQube Won't Start

```bash
# Check logs
docker-compose logs sonarqube

# Restart
docker-compose restart sonarqube

# Check PostgreSQL
docker-compose ps postgres
```

### Analysis Fails

```bash
# Verify SonarQube is accessible
curl http://localhost:9000/api/system/status

# Check token is valid
# Go to SonarQube → My Account → Security → Tokens

# Verify sonar-project.properties exists
ls -la */sonar-project.properties
```

### Out of Memory

SonarQube requires significant memory. Increase Docker resources:

1. Docker Desktop → Settings → Resources
2. Increase Memory to at least **4GB**
3. Restart Docker

## 📚 Best Practices

1. **Run analysis before commits**
   ```bash
   git add .
   ./analyze.sh
   git commit -m "Your changes"
   ```

2. **Fix critical issues first**
   - Bugs > Vulnerabilities > Code Smells

3. **Maintain > 80% coverage**
   - Write tests for new code
   - Add tests for uncovered code

4. **Reduce code duplication**
   - Extract common functions
   - Use inheritance/composition

5. **Follow language conventions**
   - PEP 8 for Python
   - Google Java Style Guide for Java
   - Airbnb Style Guide for TypeScript

## 🔗 Links

- **SonarQube Documentation:** https://docs.sonarqube.org/
- **SonarScanner CLI:** https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/
- **Maven Plugin:** https://docs.sonarqube.org/latest/analysis/scan/sonarscanner-for-maven/
- **Python Coverage:** https://coverage.readthedocs.io/

---

**Happy Code Quality Analysis! 🎯**
