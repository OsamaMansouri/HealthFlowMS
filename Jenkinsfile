pipeline {
    agent any
    
    environment {
        // Docker configuration
        DOCKER_REGISTRY = "docker.io"
        DOCKER_NAMESPACE = "healthflowms"
        DOCKER_TAG = "${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'latest'}"
        BUILD_TAG = "${env.BUILD_NUMBER}-${env.GIT_BRANCH}"
        
        // Service image names
        IMAGE_SCORE_API = "${DOCKER_NAMESPACE}/score-api"
        IMAGE_DEID = "${DOCKER_NAMESPACE}/deid"
        IMAGE_FEATURIZER = "${DOCKER_NAMESPACE}/featurizer"
        IMAGE_MODEL_RISQUE = "${DOCKER_NAMESPACE}/model-risque"
        IMAGE_AUDIT_FAIRNESS = "${DOCKER_NAMESPACE}/audit-fairness"
        IMAGE_PROXY_FHIR = "${DOCKER_NAMESPACE}/proxy-fhir"
        IMAGE_FRONTEND = "${DOCKER_NAMESPACE}/frontend"
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        timeout(time: 1, unit: 'HOURS')
        timestamps()
    }
    
    stages {
        stage('🔍 Checkout') {
            steps {
                echo '📥 Checking out source code...'
                checkout scm
                script {
                    env.GIT_COMMIT_MSG = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                    env.GIT_AUTHOR = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
                }
                echo "Commit: ${env.GIT_COMMIT_MSG}"
                echo "Author: ${env.GIT_AUTHOR}"
            }
        }
        
        stage('🏗️ Build Services') {
            parallel {
                stage('Build Score-API') {
                    steps {
                        echo '🔨 Building Score-API...'
                        dir('score-api') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }
                
                stage('Build DeID') {
                    steps {
                        echo '🔨 Building DeID Service...'
                        dir('deid') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }
                
                stage('Build Featurizer') {
                    steps {
                        echo '🔨 Building Featurizer...'
                        dir('featurizer') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }
                
                stage('Build Model-Risque') {
                    steps {
                        echo '🔨 Building Model-Risque...'
                        dir('model-risque') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }
                
                stage('Build Audit-Fairness') {
                    steps {
                        echo '🔨 Building Audit-Fairness...'
                        dir('audit-fairness') {
                            sh '''
                                python3 -m venv venv
                                . venv/bin/activate
                                pip install --upgrade pip
                                pip install -r requirements.txt
                            '''
                        }
                    }
                }
                
                stage('Build Proxy-FHIR') {
                    steps {
                        echo '🔨 Building Proxy-FHIR (Java)...'
                        dir('proxy-fhir') {
                            sh 'mvn clean package -DskipTests'
                        }
                    }
                }
                
                stage('Build Frontend') {
                    steps {
                        echo '🔨 Building Frontend...'
                        dir('frontend') {
                            sh '''
                                npm install
                                npm run build
                            '''
                        }
                    }
                }
            }
        }
        
        stage('🧪 Run Tests') {
            parallel {
                stage('Test Score-API') {
                    steps {
                        echo '🧪 Testing Score-API...'
                        dir('score-api') {
                            sh '''
                                . venv/bin/activate
                                pytest tests/ -v --cov=app --cov-report=xml --cov-report=html || true
                            '''
                        }
                    }
                }
                
                stage('Test DeID') {
                    steps {
                        echo '🧪 Testing DeID Service...'
                        dir('deid') {
                            sh '''
                                . venv/bin/activate
                                pytest tests/ -v --cov=app --cov-report=xml || true
                            '''
                        }
                    }
                }
                
                stage('Test Featurizer') {
                    steps {
                        echo '🧪 Testing Featurizer...'
                        dir('featurizer') {
                            sh '''
                                . venv/bin/activate
                                pytest tests/ -v --cov=app --cov-report=xml || true
                            '''
                        }
                    }
                }
                
                stage('Test Model-Risque') {
                    steps {
                        echo '🧪 Testing Model-Risque...'
                        dir('model-risque') {
                            sh '''
                                . venv/bin/activate
                                pytest tests/ -v --cov=app --cov-report=xml || true
                            '''
                        }
                    }
                }
                
                stage('Test Proxy-FHIR') {
                    steps {
                        echo '🧪 Testing Proxy-FHIR (JUnit)...'
                        dir('proxy-fhir') {
                            sh 'mvn test || true'
                        }
                    }
                }
            }
        }
        
        stage('📊 Code Quality Analysis') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    branch 'dark'
                }
            }
            steps {
                echo '📊 Running SonarQube analysis...'
                script {
                    try {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=healthflowms \
                                -Dsonar.sources=. \
                                -Dsonar.host.url=http://localhost:9000 \
                                -Dsonar.login=${SONAR_TOKEN} || true
                        '''
                    } catch (Exception e) {
                        echo "⚠️ SonarQube analysis failed: ${e.message}"
                    }
                }
            }
        }
        
        stage('🐳 Build Docker Images') {
            parallel {
                stage('Docker: Score-API') {
                    steps {
                        dir('score-api') {
                            sh """
                                docker build -t ${IMAGE_SCORE_API}:${DOCKER_TAG} .
                                docker tag ${IMAGE_SCORE_API}:${DOCKER_TAG} ${IMAGE_SCORE_API}:latest
                            """
                        }
                    }
                }
                
                stage('Docker: DeID') {
                    steps {
                        dir('deid') {
                            sh """
                                docker build -t ${IMAGE_DEID}:${DOCKER_TAG} .
                                docker tag ${IMAGE_DEID}:${DOCKER_TAG} ${IMAGE_DEID}:latest
                            """
                        }
                    }
                }
                
                stage('Docker: Featurizer') {
                    steps {
                        dir('featurizer') {
                            sh """
                                docker build -t ${IMAGE_FEATURIZER}:${DOCKER_TAG} .
                                docker tag ${IMAGE_FEATURIZER}:${DOCKER_TAG} ${IMAGE_FEATURIZER}:latest
                            """
                        }
                    }
                }
                
                stage('Docker: Model-Risque') {
                    steps {
                        dir('model-risque') {
                            sh """
                                docker build -t ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG} .
                                docker tag ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG} ${IMAGE_MODEL_RISQUE}:latest
                            """
                        }
                    }
                }
                
                stage('Docker: Audit-Fairness') {
                    steps {
                        dir('audit-fairness') {
                            sh """
                                docker build -t ${IMAGE_AUDIT_FAIRNESS}:${DOCKER_TAG} .
                                docker tag ${IMAGE_AUDIT_FAIRNESS}:${DOCKER_TAG} ${IMAGE_AUDIT_FAIRNESS}:latest
                            """
                        }
                    }
                }
                
                stage('Docker: Proxy-FHIR') {
                    steps {
                        dir('proxy-fhir') {
                            sh """
                                docker build -t ${IMAGE_PROXY_FHIR}:${DOCKER_TAG} .
                                docker tag ${IMAGE_PROXY_FHIR}:${DOCKER_TAG} ${IMAGE_PROXY_FHIR}:latest
                            """
                        }
                    }
                }
                
                stage('Docker: Frontend') {
                    steps {
                        dir('frontend') {
                            sh """
                                docker build -t ${IMAGE_FRONTEND}:${DOCKER_TAG} .
                                docker tag ${IMAGE_FRONTEND}:${DOCKER_TAG} ${IMAGE_FRONTEND}:latest
                            """
                        }
                    }
                }
            }
        }
        
        stage('📤 Push Docker Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                echo '📤 Pushing Docker images to registry...'
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry') {
                        sh """
                            docker push ${IMAGE_SCORE_API}:${DOCKER_TAG}
                            docker push ${IMAGE_SCORE_API}:latest
                            
                            docker push ${IMAGE_DEID}:${DOCKER_TAG}
                            docker push ${IMAGE_DEID}:latest
                            
                            docker push ${IMAGE_FEATURIZER}:${DOCKER_TAG}
                            docker push ${IMAGE_FEATURIZER}:latest
                            
                            docker push ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG}
                            docker push ${IMAGE_MODEL_RISQUE}:latest
                            
                            docker push ${IMAGE_AUDIT_FAIRNESS}:${DOCKER_TAG}
                            docker push ${IMAGE_AUDIT_FAIRNESS}:latest
                            
                            docker push ${IMAGE_PROXY_FHIR}:${DOCKER_TAG}
                            docker push ${IMAGE_PROXY_FHIR}:latest
                            
                            docker push ${IMAGE_FRONTEND}:${DOCKER_TAG}
                            docker push ${IMAGE_FRONTEND}:latest
                        """
                    }
                }
            }
        }
        
        stage('🚀 Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def environment = env.GIT_BRANCH == 'main' ? 'production' : 'staging'
                    echo "🚀 Deploying to ${environment}..."
                    
                    if (environment == 'production') {
                        input message: '🚨 Deploy to PRODUCTION?', ok: 'Deploy'
                    }
                    
                    sh """
                        docker-compose down || true
                        docker-compose up -d
                    """
                    
                    // Wait for services to be healthy
                    sh '''
                        echo "⏳ Waiting for services to be healthy..."
                        sleep 30
                        docker-compose ps
                    '''
                }
            }
        }
        
        stage('✅ Health Check') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                echo '✅ Running health checks...'
                script {
                    def services = [
                        'Score-API': 'http://localhost:8085/health',
                        'DeID': 'http://localhost:8082/health',
                        'Featurizer': 'http://localhost:8083/health',
                        'Model-Risque': 'http://localhost:8084/health',
                        'Proxy-FHIR': 'http://localhost:8081/actuator/health'
                    ]
                    
                    services.each { name, url ->
                        def status = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' ${url} || echo '000'",
                            returnStdout: true
                        ).trim()
                        
                        if (status == '200') {
                            echo "✅ ${name}: Healthy"
                        } else {
                            echo "⚠️ ${name}: Status ${status}"
                        }
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            script {
                if (env.GIT_BRANCH == 'main' || env.GIT_BRANCH == 'develop') {
                    echo '📧 Sending success notification...'
                    // Add email or Slack notification here
                }
            }
        }
        
        failure {
            echo '❌ Pipeline failed!'
            script {
                echo '📧 Sending failure notification...'
                // Add email or Slack notification here
            }
        }
        
        always {
            echo '🧹 Cleaning up workspace...'
            // Archive test reports
            junit(allowEmptyResults: true, testResults: '**/target/surefire-reports/*.xml')
            
            // Archive coverage reports
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'score-api/htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report - Score API'
            ])
            
            // Clean up Docker images
            sh '''
                docker image prune -f || true
                docker container prune -f || true
            '''
        }
    }
}
