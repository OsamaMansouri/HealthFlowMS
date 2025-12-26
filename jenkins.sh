#!/bin/bash

# HealthFlowMS Jenkins Helper Script
# This script provides convenient commands for Jenkins operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Jenkins configuration
JENKINS_URL="http://localhost:8088"
JENKINS_CONTAINER="healthflow-jenkins"

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Show usage
usage() {
    cat << EOF
🚀 HealthFlowMS Jenkins Helper

Usage: ./jenkins.sh [COMMAND]

Commands:
    start           Start Jenkins service
    stop            Stop Jenkins service
    restart         Restart Jenkins service
    status          Show Jenkins status
    logs            View Jenkins logs
    rebuild         Rebuild Jenkins Docker image
    password        Get initial admin password
    url             Show Jenkins URL
    health          Check Jenkins health
    plugins         List installed plugins
    backup          Backup Jenkins data
    restore         Restore Jenkins from backup
    help            Show this help message

Examples:
    ./jenkins.sh start
    ./jenkins.sh logs
    ./jenkins.sh status

EOF
}

# Start Jenkins
start_jenkins() {
    print_header "Starting Jenkins"
    docker-compose up -d jenkins
    print_success "Jenkins is starting..."
    echo "Waiting for Jenkins to be ready..."
    sleep 10
    check_jenkins_health
    print_success "Jenkins URL: ${JENKINS_URL}"
}

# Stop Jenkins
stop_jenkins() {
    print_header "Stopping Jenkins"
    docker-compose stop jenkins
    print_success "Jenkins stopped"
}

# Restart Jenkins
restart_jenkins() {
    print_header "Restarting Jenkins"
    docker-compose restart jenkins
    print_success "Jenkins restarted"
    echo "Waiting for Jenkins to be ready..."
    sleep 10
    check_jenkins_health
}

# Check Jenkins status
check_status() {
    print_header "Jenkins Status"
    docker-compose ps jenkins
    
    if docker ps | grep -q $JENKINS_CONTAINER; then
        print_success "Jenkins is running"
        echo ""
        echo "📊 Container Stats:"
        docker stats --no-stream $JENKINS_CONTAINER
    else
        print_error "Jenkins is not running"
    fi
}

# View Jenkins logs
view_logs() {
    print_header "Jenkins Logs (Ctrl+C to exit)"
    docker-compose logs -f jenkins
}

# Rebuild Jenkins image
rebuild_jenkins() {
    print_header "Rebuilding Jenkins Image"
    print_warning "This will stop Jenkins and rebuild the Docker image"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose build jenkins
        docker-compose up -d jenkins
        print_success "Jenkins image rebuilt and started"
    else
        print_warning "Rebuild cancelled"
    fi
}

# Get initial admin password
get_password() {
    print_header "Initial Admin Password"
    if docker ps | grep -q $JENKINS_CONTAINER; then
        PASSWORD=$(docker exec $JENKINS_CONTAINER cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || echo "Not found")
        if [ "$PASSWORD" != "Not found" ]; then
            print_success "Initial Admin Password: $PASSWORD"
        else
            print_warning "Password file not found (Jenkins may be configured via JCasC)"
            print_success "Default credentials: admin / admin123"
        fi
    else
        print_error "Jenkins container is not running"
    fi
}

# Show Jenkins URL
show_url() {
    print_header "Jenkins URL"
    echo "🌐 Jenkins UI: ${JENKINS_URL}"
    echo "🔧 Jenkins API: ${JENKINS_URL}/api"
    echo "📘 Blue Ocean: ${JENKINS_URL}/blue"
}

# Check Jenkins health
check_jenkins_health() {
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" ${JENKINS_URL}/login 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "Jenkins is healthy (HTTP ${HTTP_CODE})"
        return 0
    else
        print_error "Jenkins is not ready (HTTP ${HTTP_CODE})"
        return 1
    fi
}

# List installed plugins
list_plugins() {
    print_header "Installed Jenkins Plugins"
    if docker ps | grep -q $JENKINS_CONTAINER; then
        docker exec $JENKINS_CONTAINER jenkins-plugin-cli --list 2>/dev/null || \
        docker exec $JENKINS_CONTAINER ls /var/jenkins_home/plugins/ | sed 's/.jpi$//' | sort
    else
        print_error "Jenkins container is not running"
    fi
}

# Backup Jenkins data
backup_jenkins() {
    print_header "Backing up Jenkins Data"
    BACKUP_DIR="./jenkins_backup"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="jenkins_backup_${TIMESTAMP}.tar.gz"
    
    mkdir -p $BACKUP_DIR
    
    echo "Creating backup: ${BACKUP_FILE}"
    docker run --rm \
        -v healthflowms_jenkins_data:/data \
        -v $(pwd)/${BACKUP_DIR}:/backup \
        alpine tar czf /backup/${BACKUP_FILE} -C /data .
    
    print_success "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}"
    echo "Backup size: $(du -h ${BACKUP_DIR}/${BACKUP_FILE} | cut -f1)"
}

# Restore Jenkins from backup
restore_jenkins() {
    print_header "Restore Jenkins from Backup"
    BACKUP_DIR="./jenkins_backup"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "Backup directory not found: ${BACKUP_DIR}"
        exit 1
    fi
    
    echo "Available backups:"
    ls -lh ${BACKUP_DIR}/*.tar.gz 2>/dev/null || echo "No backups found"
    
    read -p "Enter backup filename (or 'cancel'): " BACKUP_FILE
    
    if [ "$BACKUP_FILE" = "cancel" ]; then
        print_warning "Restore cancelled"
        exit 0
    fi
    
    if [ ! -f "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
        print_error "Backup file not found: ${BACKUP_FILE}"
        exit 1
    fi
    
    print_warning "⚠️ This will overwrite current Jenkins data!"
    read -p "Continue? (yes/NO) " -r
    if [[ ! $REPLY =~ ^yes$ ]]; then
        print_warning "Restore cancelled"
        exit 0
    fi
    
    echo "Stopping Jenkins..."
    docker-compose stop jenkins
    
    echo "Restoring backup..."
    docker run --rm \
        -v healthflowms_jenkins_data:/data \
        -v $(pwd)/${BACKUP_DIR}:/backup \
        alpine sh -c "rm -rf /data/* && tar xzf /backup/${BACKUP_FILE} -C /data"
    
    echo "Starting Jenkins..."
    docker-compose up -d jenkins
    
    print_success "Jenkins restored from: ${BACKUP_FILE}"
}

# Main command handler
case "${1:-help}" in
    start)
        start_jenkins
        ;;
    stop)
        stop_jenkins
        ;;
    restart)
        restart_jenkins
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    rebuild)
        rebuild_jenkins
        ;;
    password)
        get_password
        ;;
    url)
        show_url
        ;;
    health)
        check_jenkins_health
        ;;
    plugins)
        list_plugins
        ;;
    backup)
        backup_jenkins
        ;;
    restore)
        restore_jenkins
        ;;
    help|*)
        usage
        ;;
esac
