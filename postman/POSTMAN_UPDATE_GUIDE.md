# HealthFlowMS - Collection Postman Mise à Jour

## Nouveaux Endpoints Ajoutés

### 10. Prometheus - Monitoring (9090)

#### 10.1 Check Prometheus Health
```
GET {{base_url}}:9090/-/healthy
```
Vérifier que Prometheus est opérationnel.

#### 10.2 Get All Targets
```
GET {{base_url}}:9090/api/v1/targets
```
Récupérer l'état de tous les targets (services monitorés).

#### 10.3 Query Metrics - Service UP Status
```
GET {{base_url}}:9090/api/v1/query?query=up
```
Vérifier quels services sont UP (1) ou DOWN (0).

#### 10.4 Query Metrics - HTTP Requests Total
```
GET {{base_url}}:9090/api/v1/query?query=http_requests_total
```
Nombre total de requêtes HTTP par service.

---

### 11. Grafana - Dashboards (3000)

#### 11.1 Check Grafana Health
```
GET {{base_url}}:3000/api/health
```
Vérifier que Grafana est opérationnel.

#### 11.2 Get Datasources
```
GET {{base_url}}:3000/api/datasources
```
Lister toutes les sources de données (Prometheus).

#### 11.3 Search Dashboards
```
GET {{base_url}}:3000/api/search
```
Rechercher les dashboards disponibles.

---

### 12. Jenkins - CI/CD (8088)

#### 12.1 Check Jenkins Status
```
GET {{base_url}}:8088/
```
Page d'accueil Jenkins.

#### 12.2 Get Jenkins Version
```
GET {{base_url}}:8088/api/json
```
Informations sur l'instance Jenkins.

---

### 13. ProxyFHIR - Actuator Metrics

#### 13.1 Get Actuator Health (Detailed)
```
GET {{base_url}}:8081/actuator/health
```
Health check détaillé avec composants.

#### 13.2 Get Prometheus Metrics
```
GET {{base_url}}:8081/actuator/prometheus
```
Métriques au format Prometheus (JVM, HTTP, DB).

#### 13.3 Get All Metrics
```
GET {{base_url}}:8081/actuator/metrics
```
Liste de toutes les métriques disponibles.

#### 13.4 Get Specific Metric - JVM Memory
```
GET {{base_url}}:8081/actuator/metrics/jvm.memory.used
```
Utilisation mémoire JVM.

---

## Instructions d'Import

Pour ajouter ces endpoints à votre collection Postman existante:

1. **Ouvrir Postman**
2. **Sélectionner la collection "HealthFlow"**
3. **Créer les nouveaux dossiers:**
   - "10. Prometheus - Monitoring (9090)"
   - "11. Grafana - Dashboards (3000)"
   - "12. Jenkins - CI/CD (8088)"
   - "13. ProxyFHIR - Actuator Metrics"

4. **Ajouter les requêtes** dans chaque dossier selon la documentation ci-dessus

---

## Mise à Jour de la Description

Nouvelle description de la collection:

```
Collection complète pour tester tous les microservices HealthFlow-MS

## Services Microservices:
- ScoreAPI (8085) - API principale
- HAPI FHIR (8090) - Serveur FHIR
- ProxyFHIR (8081) - Synchronisation FHIR
- DeID (8082) - Anonymisation
- Featurizer (8083) - Extraction features
- ModelRisque (8084) - Prédictions ML
- AuditFairness (8086) - Dashboard équité

## Infrastructure & Monitoring:
- Prometheus (9090) - Collecte de métriques
- Grafana (3000) - Visualisation dashboards
- Jenkins (8088) - CI/CD Pipeline

## Utilisateurs:
- admin / admin123
- clinician / admin123
- researcher / admin123
- auditor / admin123
```

---

## Exemples de Requêtes Complètes

### Prometheus - Query avec paramètres
```json
{
  "method": "GET",
  "url": "{{base_url}}:9090/api/v1/query",
  "params": {
    "query": "rate(http_requests_total[5m])"
  }
}
```

### Grafana - Avec authentification
```json
{
  "method": "GET",
  "url": "{{base_url}}:3000/api/datasources",
  "headers": {
    "Authorization": "Basic YWRtaW46YWRtaW4="
  }
}
```
(Base64 de "admin:admin")

---

## Tests Automatiques

Ajouter ces scripts de test pour les nouveaux endpoints:

### Prometheus Targets Test
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    var activeTargets = jsonData.data.activeTargets;
    console.log('Active targets: ' + activeTargets.length);
    
    activeTargets.forEach(function(target) {
        console.log('- ' + target.labels.job + ': ' + target.health);
    });
}
```

### Grafana Health Test
```javascript
if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    console.log('Grafana database: ' + jsonData.database);
    console.log('Grafana version: ' + jsonData.version);
}
```

---

## Résumé des Ports

| Service | Port | Type |
|---------|------|------|
| score-api | 8085 | Microservice |
| deid | 8082 | Microservice |
| featurizer | 8083 | Microservice |
| model-risque | 8084 | Microservice |
| audit-fairness | 8086 | Microservice |
| proxy-fhir | 8081 | Microservice |
| hapi-fhir | 8090 | Microservice |
| **prometheus** | **9090** | **Monitoring** |
| **grafana** | **3000** | **Monitoring** |
| **jenkins** | **8088** | **CI/CD** |
| postgres | 5432 | Database |
| redis | 6379 | Cache |
