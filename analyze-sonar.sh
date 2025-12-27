#!/bin/bash

# HealthFlow-MS SonarQube Analysis Script
# This script analyzes all services using Docker-based SonarScanner

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  HealthFlow-MS SonarQube Analysis${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if SonarQube is running
echo -e "${YELLOW}Checking if SonarQube is running...${NC}"
if ! docker-compose ps sonarqube | grep -q "Up"; then
    echo -e "${RED}❌ SonarQube is not running!${NC}"
    echo -e "${YELLOW}Starting SonarQube...${NC}"
    docker-compose up -d sonarqube
    echo -e "${YELLOW}Waiting for SonarQube to start (this may take 2-3 minutes)...${NC}"
    sleep 120
fi

# Check SonarQube status
SONAR_STATUS=$(curl -s http://localhost:9000/api/system/status | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$SONAR_STATUS" != "UP" ]; then
    echo -e "${RED}❌ SonarQube is not ready yet. Please wait and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ SonarQube is running${NC}"
echo ""

# Prompt for SonarQube token
echo -e "${YELLOW}Enter your SonarQube token:${NC}"
echo -e "${YELLOW}(Generate at: http://localhost:9000 → My Account → Security → Tokens)${NC}"
read -r SONAR_TOKEN

if [ -z "$SONAR_TOKEN" ]; then
    echo -e "${RED}❌ Token is required!${NC}"
    exit 1
fi

# Function to analyze a Python service
analyze_python_service() {
    SERVICE_NAME=$1
    SERVICE_DIR=$2
    
    echo ""
    echo -e "${BLUE}🔍 Analyzing $SERVICE_NAME...${NC}"
    
    docker run --rm \
        --network="healthflowms_default" \
        -v "$(pwd)/$SERVICE_DIR:/usr/src" \
        sonarsource/sonar-scanner-cli \
        -Dsonar.login="$SONAR_TOKEN" \
        -Dsonar.host.url="http://sonarqube:9000"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $SERVICE_NAME analysis complete${NC}"
    else
        echo -e "${RED}❌ $SERVICE_NAME analysis failed${NC}"
    fi
}

# Function to analyze Java service
analyze_java_service() {
    echo ""
    echo -e "${BLUE}🔍 Analyzing Proxy FHIR (Java)...${NC}"
    
    cd proxy-fhir
    docker run --rm \
        --network="healthflowms_default" \
        -v "$(pwd):/usr/src" \
        -v "$HOME/.m2:/root/.m2" \
        maven:3.9-eclipse-temurin-17 \
        mvn clean verify sonar:sonar \
        -Dsonar.login="$SONAR_TOKEN" \
        -Dsonar.host.url="http://sonarqube:9000"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Proxy FHIR analysis complete${NC}"
    else
        echo -e "${RED}❌ Proxy FHIR analysis failed${NC}"
    fi
    cd ..
}

# Analyze all Python services
analyze_python_service "Score API" "score-api"
analyze_python_service "DeID Service" "deid"
analyze_python_service "Featurizer" "featurizer"
analyze_python_service "Model Risque" "model-risque"
analyze_python_service "Audit Fairness" "audit-fairness"

# Analyze Java service
analyze_java_service

# Analyze Frontend (optional, requires npm test coverage first)
# analyze_python_service "Frontend" "frontend"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  ✅ Analysis Complete!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${BLUE}View results at: ${YELLOW}http://localhost:9000${NC}"
echo ""
