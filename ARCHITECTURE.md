# Architecture HealthFlow-MS

## Vue d'ensemble

HealthFlow-MS est une application de prédiction de réadmission hospitalière basée sur une architecture de microservices. Chaque service a une responsabilité spécifique et communique avec les autres via des API HTTP.

## Pourquoi Docker ?

Docker est essentiel pour ce projet car :

1. **Isolation** : Chaque microservice fonctionne dans son propre conteneur, isolé des autres
2. **Simplicité de déploiement** : Un seul fichier `docker-compose.yml` démarre tous les services
3. **Environnement uniforme** : Le code fonctionne de la même manière sur votre machine, en test, et en production
4. **Gestion des dépendances** : Chaque service a ses propres dépendances (Python, Java, Node.js) sans conflits
5. **Réseau automatique** : Docker crée un réseau interne où les services peuvent communiquer par leur nom (ex: `postgres`, `score-api`)

## Architecture des Microservices

### 1. Frontend (Port 8087)

- **Technologie** : React + TypeScript
- **Rôle** : Interface utilisateur web
- **Communication** : Appelle les autres services via HTTP
- **Dépendances** : Aucune (sert juste les fichiers statiques)

### 2. Score API (Port 8085)

- **Technologie** : Python FastAPI
- **Rôle** : Point d'entrée principal, authentification, orchestration
- **Communication** :
  - Reçoit les requêtes du frontend
  - Appelle `featurizer` pour extraire les caractéristiques
  - Appelle `model-risque` pour calculer le score
  - Appelle `proxy-fhir` pour créer des patients
- **Base de données** : PostgreSQL (utilisateurs, sessions)

### 3. DeID Service (Port 8082)

- **Technologie** : Python FastAPI
- **Rôle** : Anonymisation des données selon HIPAA Safe Harbor
- **Communication** :
  - Reçoit les données du frontend via `score-api`
  - Lit les données depuis PostgreSQL
  - Retourne les données anonymisées
- **Base de données** : PostgreSQL (patients FHIR)

### 4. Featurizer (Port 8083)

- **Technologie** : Python FastAPI
- **Rôle** : Extraction de caractéristiques (features) pour le modèle ML
- **Communication** :
  - Reçoit les données anonymisées
  - Utilise NLP (BioBERT, spaCy) pour analyser les notes cliniques
  - Retourne 30+ caractéristiques numériques
- **Dépendances** : Modèles ML pré-entraînés

### 5. Model Risque (Port 8084)

- **Technologie** : Python FastAPI
- **Rôle** : Calcul du score de risque de réadmission
- **Communication** :
  - Reçoit les caractéristiques du `featurizer`
  - Utilise XGBoost pour prédire le risque
  - Utilise SHAP pour expliquer la prédiction
  - Retourne le score et les explications
- **Dépendances** : Modèle XGBoost entraîné

### 6. Proxy FHIR (Port 8081)

- **Technologie** : Java Spring Boot
- **Rôle** : Proxy et synchronisation avec HAPI FHIR
- **Communication** :
  - Reçoit les requêtes du frontend via `score-api`
  - Synchronise les données avec HAPI FHIR
  - Stocke les données dans PostgreSQL
- **Base de données** : PostgreSQL (patients, encounters, observations FHIR)

### 7. Audit Fairness (Port 8086)

- **Technologie** : Python FastAPI
- **Rôle** : Audit de biais et équité du modèle
- **Communication** :
  - Analyse les prédictions du modèle
  - Vérifie l'équité selon différents groupes démographiques
  - Retourne des rapports d'audit

### 8. HAPI FHIR (Port 8090)

- **Technologie** : Java (HAPI FHIR Server)
- **Rôle** : Serveur FHIR standard pour stocker les données médicales
- **Communication** :
  - Reçoit les requêtes de `proxy-fhir`
  - Stocke les ressources FHIR (Patient, Encounter, Observation)
- **Base de données** : Base de données interne HAPI FHIR

### 9. PostgreSQL (Port 5432)

- **Technologie** : PostgreSQL 15
- **Rôle** : Base de données centrale
- **Tables principales** :
  - `users` : Utilisateurs de l'application
  - `fhir_patients` : Patients synchronisés depuis FHIR
  - `fhir_encounters` : Rencontres médicales
  - `fhir_observations` : Observations cliniques
  - `deid_patients` : Patients anonymisés
  - Et autres tables pour l'audit et le mapping

## Flux de Données

### Création d'un Patient

```
Frontend → Score API → Proxy FHIR → HAPI FHIR
                ↓
         PostgreSQL (stockage)
```

### Prédiction de Risque

```
Frontend → Score API → DeID Service → Featurizer → Model Risque
                ↓              ↓
         PostgreSQL      PostgreSQL
```

### Workflow Complet

1. **Création** : Frontend crée un patient → Proxy FHIR → HAPI FHIR → PostgreSQL
2. **Anonymisation** : Frontend demande anonymisation → Score API → DeID Service → PostgreSQL
3. **Extraction** : Score API → Featurizer (analyse NLP des notes cliniques)
4. **Prédiction** : Score API → Model Risque (calcul du score XGBoost)
5. **Audit** : Score API → Audit Fairness (vérification de l'équité)
6. **Affichage** : Score API retourne tout au Frontend

## Communication entre Services

### Dans Docker

Les services communiquent via le **nom du conteneur** :

- `http://score-api:8085` (pas `localhost`)
- `http://postgres:5432`
- `http://proxy-fhir:8081`

### Depuis le Navigateur

Le frontend utilise `localhost` car il s'exécute dans le navigateur :

- `http://localhost:8085` (Score API)
- `http://localhost:8082` (DeID)
- `http://localhost:8081` (Proxy FHIR)

## Ce qu'on peut Ajouter au Projet

### 1. Monitoring et Observabilité

- **Prometheus** : Collecte de métriques
- **Grafana** : Tableaux de bord de monitoring
- **ELK Stack** : Centralisation des logs
- **Jaeger** : Traçage distribué des requêtes

### 2. Sécurité

- **OAuth2/OpenID Connect** : Authentification moderne
- **API Gateway** : Point d'entrée unique avec rate limiting
- **Vault** : Gestion sécurisée des secrets
- **HTTPS/TLS** : Chiffrement des communications

### 3. Performance

- **Redis** : Cache pour améliorer les performances
- **RabbitMQ/Kafka** : File d'attente pour traitement asynchrone
- **CDN** : Distribution du frontend
- **Load Balancer** : Répartition de charge

### 4. Développement

- **CI/CD** : GitHub Actions, GitLab CI
- **Tests automatisés** : Unit tests, integration tests
- **Documentation API** : Swagger/OpenAPI amélioré
- **Environnements** : Dev, Staging, Production

### 5. Fonctionnalités Métier

- **Notifications** : Alertes par email/SMS pour risques élevés
- **Rapports** : Génération de rapports PDF
- **Export de données** : CSV, Excel pour analyses
- **Historique** : Suivi des prédictions dans le temps
- **Multi-tenant** : Support de plusieurs hôpitaux

### 6. Machine Learning

- **Réentraînement automatique** : Mise à jour périodique du modèle
- **A/B Testing** : Comparaison de différents modèles
- **Feature Store** : Gestion centralisée des caractéristiques
- **MLflow** : Suivi des expériences ML

### 7. Infrastructure

- **Kubernetes** : Orchestration avancée (au lieu de Docker Compose)
- **Terraform** : Infrastructure as Code
- **Backup automatique** : Sauvegarde de la base de données
- **Disaster Recovery** : Plan de reprise après sinistre

## Commandes Utiles

### Démarrer tous les services

```bash
docker-compose up -d
```

### Voir les logs d'un service

```bash
docker logs healthflow-score-api
docker logs healthflow-deid
```

### Redémarrer un service

```bash
docker-compose restart deid
```

### Arrêter tous les services

```bash
docker-compose down
```

### Reconstruire un service après modification

```bash
docker-compose up -d --build deid
```

## Conclusion

Cette architecture de microservices permet :

- **Scalabilité** : Chaque service peut être mis à l'échelle indépendamment
- **Maintenabilité** : Code modulaire et facile à maintenir
- **Flexibilité** : Facile d'ajouter ou modifier un service
- **Résilience** : Si un service tombe, les autres continuent de fonctionner

Docker simplifie grandement le déploiement et la gestion de cette architecture complexe.
