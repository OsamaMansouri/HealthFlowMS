# Tests Automatisés - HealthFlow-MS

## Structure des Tests

Les tests sont organisés par service dans le dossier `tests/` de chaque microservice.

### Score API Tests

```bash
cd score-api
pytest tests/ -v
```

### Tests Disponibles

- **test_auth.py** : Tests d'authentification

  - Login avec credentials valides
  - Login avec credentials invalides
  - Récupération de l'utilisateur courant
  - Validation des tokens

- **test_health.py** : Tests des endpoints de santé
  - Health check basique

## Configuration

Les tests utilisent une base de données de test séparée (`healthflow_test`) pour éviter d'affecter les données de production.

## Exécution

### Option 1 : Dans Docker (Recommandé)

Les tests doivent être exécutés dans le conteneur Docker car pytest est installé là-bas.

**Windows PowerShell :**

```powershell
# Dans le dossier score-api
.\run_tests.ps1

# Ou directement
docker exec healthflow-score-api pytest tests/ -v
```

**Windows CMD :**

```cmd
run_tests.bat
```

**Linux/Mac :**

```bash
docker exec healthflow-score-api pytest tests/ -v
```

### Option 2 : Installation locale (Optionnel)

Si vous voulez exécuter pytest directement sur votre machine :

```bash
# Installer pytest localement
pip install pytest pytest-asyncio

# Puis exécuter
cd score-api
pytest tests/ -v
```

### Tests spécifiques

```bash
# Dans Docker
docker exec healthflow-score-api pytest tests/test_auth.py -v
docker exec healthflow-score-api pytest tests/test_health.py -v
```

### Avec couverture de code

```bash
docker exec healthflow-score-api pytest --cov=app --cov-report=html tests/
```
