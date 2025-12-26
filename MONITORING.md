# HealthFlowMS Monitoring and CI/CD

This directory contains configuration for monitoring (Prometheus + Grafana) and CI/CD (Jenkins) infrastructure.

## 📊 Monitoring Stack

### Prometheus
**Port:** 9090  
**URL:** http://localhost:9090

Prometheus scrapes metrics from all HealthFlowMS microservices every 15 seconds.

**Monitored Services:**
- proxy-fhir (Spring Boot Actuator) - `/actuator/prometheus`
- score-api (FastAPI) - `/metrics`
- deid (FastAPI) - `/metrics`
- featurizer (FastAPI) - `/metrics`
- model-risque (FastAPI) - `/metrics`
- audit-fairness (FastAPI) - `/metrics`
- postgres - `/metrics`

**Configuration:** `monitoring/prometheus/prometheus.yml`

### Grafana
**Port:** 3000  
**URL:** http://localhost:3000  
**Credentials:** admin / admin

Grafana provides visualization dashboards for all metrics collected by Prometheus.

**Pre-configured:**
- Prometheus datasource (automatic)
- Dashboard provisioning enabled

**Configuration:**
- Datasource: `monitoring/grafana/provisioning/datasources/prometheus.yml`
- Dashboards: `monitoring/grafana/provisioning/dashboards/`

---

## 🚀 CI/CD Pipeline

### Jenkins
**Port:** 8080  
**URL:** http://localhost:8080  

Jenkins provides automated build, test, and deployment pipelines.

**Features:**
- Docker-in-Docker support
- Maven for Java builds
- Python 3 for Python services
- Pre-installed plugins: Git, Docker Workflow, Blue Ocean

**Pipeline Stages:**
1. Checkout code from Git
2. Build Java services (Maven)
3. Build Python services (pip install)
4. Run tests (parallel)
5. Build Docker images
6. Deploy to staging (on develop branch)

**Configuration:**
- Dockerfile: `jenkins/Dockerfile`
- Pipeline: `Jenkinsfile` (root directory)

---

## 🚀 Quick Start

### Start All Services
```bash
docker-compose up -d
```

This will start:
- All 8 HealthFlowMS microservices
- PostgreSQL database
- Redis cache
- **Prometheus** (metrics collection)
- **Grafana** (visualization)
- **Jenkins** (CI/CD)

### Access Monitoring

**Prometheus:**
```bash
# Open browser
http://localhost:9090

# Check targets status
http://localhost:9090/targets

# Query metrics
http://localhost:9090/graph
```

**Grafana:**
```bash
# Open browser
http://localhost:3000

# Login: admin / admin
# Datasource is pre-configured
# Import or create dashboards
```

**Jenkins:**
```bash
# Open browser
http://localhost:8080

# Setup wizard is disabled
# Configure your first pipeline
```

---

## 📈 Available Metrics

### Spring Boot (proxy-fhir)
- JVM metrics (memory, threads, GC)
- HTTP request metrics (rate, duration, errors)
- Database connection pool metrics
- Custom application metrics

**Endpoint:** http://localhost:8081/actuator/prometheus

### FastAPI Services
- HTTP request metrics
- Request duration histograms
- Active requests gauge
- Custom business metrics

**Endpoint:** http://localhost:808X/metrics (replace X with service port)

---

## 🔧 Configuration

### Add Metrics to Python Services

1. Install Prometheus client:
```bash
pip install prometheus-client
```

2. Add to FastAPI app:
```python
from prometheus_client import make_asgi_app
from fastapi import FastAPI

app = FastAPI()

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

3. Restart service:
```bash
docker-compose restart <service-name>
```

### Create Grafana Dashboard

1. Open Grafana: http://localhost:3000
2. Click "+" → "Dashboard"
3. Add panel with Prometheus query
4. Example queries:
   - `rate(http_requests_total[5m])` - Request rate
   - `http_request_duration_seconds` - Request latency
   - `jvm_memory_used_bytes` - JVM memory usage

---

## 📦 Volumes

Persistent data is stored in Docker volumes:
- `prometheus_data` - Prometheus time-series database (15 days retention)
- `grafana_data` - Grafana dashboards and settings
- `jenkins_data` - Jenkins configuration and build history

---

## 🛠️ Troubleshooting

### Prometheus targets are down
```bash
# Check service logs
docker logs healthflow-<service-name>

# Verify metrics endpoint
curl http://localhost:8081/actuator/prometheus
```

### Grafana datasource not working
```bash
# Check Prometheus is running
docker ps | grep prometheus

# Test Prometheus from Grafana container
docker exec healthflow-grafana curl http://prometheus:9090/-/healthy
```

### Jenkins build fails
```bash
# Check Jenkins logs
docker logs healthflow-jenkins

# Verify Docker socket is mounted
docker exec healthflow-jenkins docker ps
```

---

## 📚 Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Spring Boot Actuator](https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
