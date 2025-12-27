# 🚀 Jenkins CI/CD Pipeline - Configuration Guide

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Pipeline Stages](#pipeline-stages)
- [Credentials Setup](#credentials-setup)
- [Multi-Branch Pipeline](#multi-branch-pipeline)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Jenkins CI/CD pipeline for HealthFlowMS provides automated:

- ✅ **Multi-service builds** (7 microservices in parallel)
- ✅ **Automated testing** (pytest for Python, JUnit for Java)
- ✅ **Code quality analysis** (SonarQube integration)
- ✅ **Docker image building** and tagging
- ✅ **Docker registry push** (Docker Hub or private registry)
- ✅ **Automated deployment** (staging and production)
- ✅ **Health checks** post-deployment

---

## 📦 Prerequisites

Before using the Jenkins pipeline, ensure you have:

- ✅ Docker and Docker Compose installed
- ✅ Jenkins running (via `docker-compose up -d jenkins`)
- ✅ GitHub repository access
- ✅ Docker Hub account (or private registry)
- ✅ SonarQube running (optional, for code quality)

---

## 🚀 Quick Start

### 1. Start Jenkins

```bash
# Start Jenkins service
docker-compose up -d jenkins

# Wait for Jenkins to be ready (~2 minutes)
docker-compose logs -f jenkins
# Look for: "Jenkins is fully up and running"
```

### 2. Access Jenkins

Open http://localhost:8088

**Default Credentials (JCasC configured):**
- Username: `admin`
- Password: `admin123`

> ⚠️ **Change these credentials in production!**

### 3. Configure Credentials

Go to **Dashboard → Manage Jenkins → Credentials**

Add the following credentials:

#### Docker Registry Credentials
- **Kind:** Username with password
- **ID:** `docker-registry`
- **Username:** Your Docker Hub username
- **Password:** Your Docker Hub password/token
- **Description:** Docker Registry Credentials

#### GitHub Credentials
- **Kind:** Username with password
- **ID:** `github-credentials`
- **Username:** Your GitHub username
- **Password:** GitHub Personal Access Token
- **Description:** GitHub Credentials

### 4. Create Pipeline Job

The Jenkins Configuration as Code (JCasC) automatically creates:

1. **HealthFlowMS-Pipeline** - Multi-branch pipeline
2. **Deploy-All-Services** - One-click deployment
3. **Run-All-Tests** - Execute all unit tests

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `jenkins/` directory:

```bash
cp jenkins/.env.example jenkins/.env
```

Edit `.env` and configure:

```bash
# Jenkins Admin
JENKINS_ADMIN_USER=admin
JENKINS_ADMIN_PASSWORD=your-secure-password

# Docker Registry
DOCKER_USERNAME=your-docker-username
DOCKER_PASSWORD=your-docker-token

# GitHub
GITHUB_USERNAME=OsamaMansouri
GITHUB_TOKEN=your-github-pat

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Docker Compose Configuration

The `docker-compose.yml` includes Jenkins with:

```yaml
jenkins:
  build:
    context: ./jenkins
    dockerfile: Dockerfile
  container_name: healthflow-jenkins
  ports:
    - "8088:8080"    # Jenkins UI
    - "50000:50000"  # Jenkins agent port
  volumes:
    - jenkins_data:/var/jenkins_home
    - /var/run/docker.sock:/var/run/docker.sock  # Docker-in-Docker
  privileged: true
```

---

## 🔄 Pipeline Stages

### 1. 🔍 Checkout
- Clones the Git repository
- Retrieves commit information (author, message)

### 2. 🏗️ Build Services (Parallel)
Builds all 7 services in parallel:
- **Python services:** Creates virtual environments, installs dependencies
  - Score-API
  - DeID
  - Featurizer
  - Model-Risque
  - Audit-Fairness
- **Java service:** Maven build for Proxy-FHIR
- **Frontend:** npm install and build

### 3. 🧪 Run Tests (Parallel)
Executes tests for all services:
- **Python:** pytest with coverage reports
- **Java:** JUnit tests via Maven
- **Coverage:** Generates HTML and XML reports

### 4. 📊 Code Quality Analysis
- Runs SonarQube scanner (if configured)
- Only on `main`, `develop`, or `dark` branches
- Uploads code quality metrics

### 5. 🐳 Build Docker Images (Parallel)
Builds Docker images for all services:
- Tags with Git commit hash (short SHA)
- Tags with `latest`
- **Example:** `healthflowms/score-api:abc1234` and `healthflowms/score-api:latest`

### 6. 📤 Push Docker Images
- Only on `main` or `develop` branches
- Pushes all images to Docker registry
- Uses credentials from Jenkins credentials store

### 7. 🚀 Deploy
- **develop branch** → Deploys to **staging** (automatic)
- **main branch** → Deploys to **production** (manual approval required)
- Uses `docker-compose up -d` for deployment

### 8. ✅ Health Check
Verifies all services are healthy:
- Score-API: http://localhost:8085/health
- DeID: http://localhost:8082/health
- Featurizer: http://localhost:8083/health
- Model-Risque: http://localhost:8084/health
- Proxy-FHIR: http://localhost:8081/actuator/health

---

## 🔐 Credentials Setup

### Create GitHub Personal Access Token

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Set scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `admin:repo_hook` (Full control of repository hooks)
4. Generate token and copy it
5. Add to Jenkins credentials as `github-credentials`

### Create Docker Hub Access Token

1. Go to Docker Hub → **Account Settings** → **Security** → **New Access Token**
2. Set description: `Jenkins HealthFlowMS`
3. Set permissions: **Read, Write, Delete**
4. Generate token and copy it
5. Add to Jenkins credentials as `docker-registry`

### SonarQube Token (Optional)

1. Login to SonarQube (http://localhost:9000)
2. Go to **My Account** → **Security** → **Generate Token**
3. Name: `jenkins-healthflowms`
4. Generate and copy token
5. Add as Jenkins secret text credential with ID `sonar-token`

---

## 🌿 Multi-Branch Pipeline

### Branch Strategy

The pipeline supports different branches:

| Branch | Build | Test | Docker Build | Docker Push | Deploy |
|--------|-------|------|--------------|-------------|--------|
| **main** | ✅ | ✅ | ✅ | ✅ | Production (manual) |
| **develop** | ✅ | ✅ | ✅ | ✅ | Staging (auto) |
| **dark** | ✅ | ✅ | ✅ | ❌ | No deployment |
| **feature/*** | ✅ | ✅ | ✅ | ❌ | No deployment |

### Creating a Multi-Branch Pipeline

1. **Dashboard** → **New Item**
2. Enter name: `HealthFlowMS-Pipeline`
3. Select **Multibranch Pipeline**
4. Configure:
   - **Branch Sources:** Git
   - **Repository URL:** `https://github.com/OsamaMansouri/HealthFlowMS.git`
   - **Credentials:** Select `github-credentials`
   - **Behaviors:** Discover branches, Discover tags
   - **Script Path:** `Jenkinsfile`
5. Save

### Automatic Branch Discovery

Jenkins will automatically:
- Detect new branches
- Create pipeline jobs for each branch
- Run builds on commits
- Clean up deleted branches

---

## 🎯 Available Jenkins Jobs

### 1. HealthFlowMS-Pipeline (Multi-Branch)
- **Description:** Main CI/CD pipeline with all stages
- **Trigger:** Automatic on Git push
- **Duration:** ~15-20 minutes

### 2. Deploy-All-Services
- **Description:** Quick deployment of all services
- **Trigger:** Manual
- **Duration:** ~5 minutes
- **Use case:** Emergency deployments, rollbacks

### 3. Run-All-Tests
- **Description:** Execute all unit tests
- **Trigger:** Manual or scheduled
- **Duration:** ~10 minutes
- **Use case:** Pre-deployment verification

---

## 🔧 Customization

### Add Email Notifications

Edit `Jenkinsfile`, in the `post` section:

```groovy
post {
    success {
        emailext(
            subject: "✅ Build #${BUILD_NUMBER} - SUCCESS",
            body: "Pipeline completed successfully!",
            to: "team@healthflow.local"
        )
    }
    failure {
        emailext(
            subject: "❌ Build #${BUILD_NUMBER} - FAILED",
            body: "Pipeline failed. Check: ${BUILD_URL}",
            to: "team@healthflow.local"
        )
    }
}
```

### Add Slack Notifications

Add to `Jenkinsfile`:

```groovy
post {
    always {
        slackSend(
            channel: '#healthflowms-builds',
            color: currentBuild.result == 'SUCCESS' ? 'good' : 'danger',
            message: "${env.JOB_NAME} - Build #${env.BUILD_NUMBER}: ${currentBuild.result}"
        )
    }
}
```

### Add Health Check Retries

Modify health check stage:

```groovy
stage('✅ Health Check') {
    steps {
        retry(3) {
            sh 'curl -f http://localhost:8085/health'
        }
    }
}
```

---

## 🐛 Troubleshooting

### Issue: Jenkins won't start

**Solution:**
```bash
# Check logs
docker-compose logs jenkins

# Restart Jenkins
docker-compose restart jenkins

# Check permissions
sudo chown -R 1000:1000 jenkins_data/
```

### Issue: Pipeline fails at "Build Docker Images"

**Problem:** Docker socket permission denied

**Solution:**
```bash
# Add Jenkins user to docker group (inside container)
docker exec -u root healthflow-jenkins usermod -aG docker jenkins
docker-compose restart jenkins
```

### Issue: Tests fail with "ModuleNotFoundError"

**Problem:** Python virtual environment not activated

**Solution:** Ensure each test stage activates venv:
```bash
. venv/bin/activate
pytest tests/
```

### Issue: Maven build fails

**Problem:** Maven not found or Java version mismatch

**Solution:**
```bash
# Check Maven installation
docker exec healthflow-jenkins mvn -version

# Check Java version
docker exec healthflow-jenkins java -version
```

### Issue: Docker push fails

**Problem:** Invalid credentials

**Solution:**
1. Verify Docker credentials in Jenkins
2. Test login manually:
```bash
docker login docker.io
docker push healthflowms/score-api:test
```

### Issue: Health checks fail after deployment

**Problem:** Services not ready yet

**Solution:** Increase wait time in Jenkinsfile:
```groovy
sh '''
    echo "⏳ Waiting for services..."
    sleep 60  # Increase from 30 to 60 seconds
    docker-compose ps
'''
```

---

## 📊 Viewing Build Results

### Build Status
- **Dashboard** → Select your pipeline
- View:
  - ✅ Build history
  - 📊 Test results
  - 📈 Coverage trends
  - ⏱️ Build duration

### Test Reports
- **Build** → **Test Results**
- View:
  - Passed/failed tests
  - Test duration
  - Stack traces for failures

### Coverage Reports
- **Build** → **Coverage Report - Score API**
- View HTML coverage report

### Console Output
- **Build** → **Console Output**
- View full build logs

---

## 🔄 Rebuild Docker Image

If you make changes to Jenkins configuration:

```bash
# Rebuild Jenkins image
docker-compose build jenkins

# Restart Jenkins with new image
docker-compose up -d jenkins

# Verify changes
docker-compose logs -f jenkins
```

---

## 📚 Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Jenkins Configuration as Code](https://github.com/jenkinsci/configuration-as-code-plugin)
- [Docker Pipeline Plugin](https://plugins.jenkins.io/docker-workflow/)
- [Blue Ocean UI](https://www.jenkins.io/projects/blueocean/)

---

## ✅ Best Practices

1. **Use multi-branch pipelines** for automatic branch detection
2. **Tag Docker images** with Git commit hash for traceability
3. **Run tests in parallel** to reduce build time
4. **Archive test reports** for historical analysis
5. **Use credentials store** - never hardcode secrets
6. **Enable health checks** after deployment
7. **Set build timeouts** to prevent hanging builds
8. **Clean up old builds** to save disk space
9. **Monitor build metrics** in Grafana
10. **Notify team** on build failures

---

**Congratulations!** 🎉 Your Jenkins CI/CD pipeline is now fully configured for HealthFlowMS!
