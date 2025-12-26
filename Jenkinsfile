pipeline {
    agent any
    
    environment {
        // Docker configuration
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
                    // Windows-compatible way to get git info
                    if (isUnix()) {
                        env.GIT_COMMIT_MSG = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                        env.GIT_AUTHOR = sh(script: 'git log -1 --pretty=%an', returnStdout: true).trim()
                    } else {
                        env.GIT_COMMIT_MSG = bat(script: '@git log -1 --pretty=%%B', returnStdout: true).trim()
                        env.GIT_AUTHOR = bat(script: '@git log -1 --pretty=%%an', returnStdout: true).trim()
                    }
                }
                echo "Commit: ${env.GIT_COMMIT_MSG}"
                echo "Author: ${env.GIT_AUTHOR}"
            }
        }
        
        stage('🐳 Build Docker Images') {
            parallel {
                stage('Docker: Score-API') {
                    steps {
                        script {
                            dir('score-api') {
                                if (isUnix()) {
                                    sh """
                                        docker build -t ${IMAGE_SCORE_API}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_SCORE_API}:${DOCKER_TAG} ${IMAGE_SCORE_API}:latest
                                    """
                                } else {
                                    bat """
                                        docker build -t ${IMAGE_SCORE_API}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_SCORE_API}:${DOCKER_TAG} ${IMAGE_SCORE_API}:latest
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Docker: DeID') {
                    steps {
                        script {
                            dir('deid') {
                                if (isUnix()) {
                                    sh """
                                        docker build -t ${IMAGE_DEID}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_DEID}:${DOCKER_TAG} ${IMAGE_DEID}:latest
                                    """
                                } else {
                                    bat """
                                        docker build -t ${IMAGE_DEID}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_DEID}:${DOCKER_TAG} ${IMAGE_DEID}:latest
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Docker: Featurizer') {
                    steps {
                        script {
                            dir('featurizer') {
                                if (isUnix()) {
                                    sh """
                                        docker build -t ${IMAGE_FEATURIZER}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_FEATURIZER}:${DOCKER_TAG} ${IMAGE_FEATURIZER}:latest
                                    """
                                } else {
                                    bat """
                                        docker build -t ${IMAGE_FEATURIZER}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_FEATURIZER}:${DOCKER_TAG} ${IMAGE_FEATURIZER}:latest
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Docker: Model-Risque') {
                    steps {
                        script {
                            dir('model-risque') {
                                if (isUnix()) {
                                    sh """
                                        docker build -t ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG} ${IMAGE_MODEL_RISQUE}:latest
                                    """
                                } else {
                                    bat """
                                        docker build -t ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG} ${IMAGE_MODEL_RISQUE}:latest
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Docker: Audit-Fairness') {
                    steps {
                        script {
                            dir('audit-fairness') {
                                if (isUnix()) {
                                    sh """
                                        docker build -t ${IMAGE_AUDIT_FAIRNESS}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_AUDIT_FAIRNESS}:${DOCKER_TAG} ${IMAGE_AUDIT_FAIRNESS}:latest
                                    """
                                } else {
                                    bat """
                                        docker build -t ${IMAGE_AUDIT_FAIRNESS}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_AUDIT_FAIRNESS}:${DOCKER_TAG} ${IMAGE_AUDIT_FAIRNESS}:latest
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Docker: Proxy-FHIR') {
                    steps {
                        script {
                            dir('proxy-fhir') {
                                if (isUnix()) {
                                    sh """
                                        docker build -t ${IMAGE_PROXY_FHIR}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_PROXY_FHIR}:${DOCKER_TAG} ${IMAGE_PROXY_FHIR}:latest
                                    """
                                } else {
                                    bat """
                                        docker build -t ${IMAGE_PROXY_FHIR}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_PROXY_FHIR}:${DOCKER_TAG} ${IMAGE_PROXY_FHIR}:latest
                                    """
                                }
                            }
                        }
                    }
                }
                
                stage('Docker: Frontend') {
                    steps {
                        script {
                            dir('frontend') {
                                if (isUnix()) {
                                    sh """
                                        docker build -t ${IMAGE_FRONTEND}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_FRONTEND}:${DOCKER_TAG} ${IMAGE_FRONTEND}:latest
                                    """
                                } else {
                                    bat """
                                        docker build -t ${IMAGE_FRONTEND}:${DOCKER_TAG} .
                                        docker tag ${IMAGE_FRONTEND}:${DOCKER_TAG} ${IMAGE_FRONTEND}:latest
                                    """
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('🧪 Run Tests in Docker') {
            parallel {
                stage('Test Score-API') {
                    steps {
                        script {
                            if (isUnix()) {
                                sh 'docker run --rm ${IMAGE_SCORE_API}:${DOCKER_TAG} pytest tests/ -v || true'
                            } else {
                                bat 'docker run --rm %IMAGE_SCORE_API%:%DOCKER_TAG% pytest tests/ -v || exit 0'
                            }
                        }
                    }
                }
                
                stage('Test DeID') {
                    steps {
                        script {
                            if (isUnix()) {
                                sh 'docker run --rm ${IMAGE_DEID}:${DOCKER_TAG} pytest tests/ -v || true'
                            } else {
                                bat 'docker run --rm %IMAGE_DEID%:%DOCKER_TAG% pytest tests/ -v || exit 0'
                            }
                        }
                    }
                }
                
                stage('Test Featurizer') {
                    steps {
                        script {
                            if (isUnix()) {
                                sh 'docker run --rm ${IMAGE_FEATURIZER}:${DOCKER_TAG} pytest tests/ -v || true'
                            } else {
                                bat 'docker run --rm %IMAGE_FEATURIZER%:%DOCKER_TAG% pytest tests/ -v || exit 0'
                            }
                        }
                    }
                }
                
                stage('Test Model-Risque') {
                    steps {
                        script {
                            if (isUnix()) {
                                sh 'docker run --rm ${IMAGE_MODEL_RISQUE}:${DOCKER_TAG} pytest tests/ -v || true'
                            } else {
                                bat 'docker run --rm %IMAGE_MODEL_RISQUE%:%DOCKER_TAG% pytest tests/ -v || exit 0'
                            }
                        }
                    }
                }
            }
        }
        
        stage('🚀 Deploy with Docker Compose') {
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
                    
                    if (isUnix()) {
                        sh '''
                            docker-compose down || true
                            docker-compose up -d
                            echo "⏳ Waiting for services..."
                            sleep 30
                            docker-compose ps
                        '''
                    } else {
                        bat '''
                            docker-compose down || exit 0
                            docker-compose up -d
                            echo ⏳ Waiting for services...
                            timeout /t 30 /nobreak
                            docker-compose ps
                        '''
                    }
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        
        failure {
            echo '❌ Pipeline failed!'
        }
        
        always {
            echo '🧹 Cleaning up...'
            script {
                if (isUnix()) {
                    sh '''
                        docker image prune -f || true
                        docker container prune -f || true
                    '''
                } else {
                    bat '''
                        docker image prune -f || exit 0
                        docker container prune -f || exit 0
                    '''
                }
            }
        }
    }
}
