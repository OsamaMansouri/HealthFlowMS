pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_AUDIT = "healthflowms/audit-fairness"
        DOCKER_IMAGE_SCORE = "healthflowms/score-api"
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        DOCKER_REGISTRY = "docker.io"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Source code already checked out by SCM'
            }
        }
        
        stage('Build Audit-Fairness') {
            steps {
                echo 'Building audit-fairness service...'
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
        
        stage('Build Score-API') {
            steps {
                echo 'Building score-api service...'
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
        
        stage('Test Audit-Fairness') {
            steps {
                echo 'Testing audit-fairness...'
                dir('audit-fairness') {
                    sh '''
                        . venv/bin/activate
                        pytest tests/ || true
                    '''
                }
            }
        }
        
        stage('Test Score-API') {
            steps {
                echo 'Testing score-api...'
                dir('score-api') {
                    sh '''
                        . venv/bin/activate
                        pytest tests/ || true
                    '''
                }
            }
        }
        
        stage('Docker Build') {
            parallel {
                stage('Build Audit-Fairness Image') {
                    steps {
                        dir('audit-fairness') {
                            sh """
                                docker build -t ${DOCKER_IMAGE_AUDIT}:${DOCKER_TAG} .
                                docker tag ${DOCKER_IMAGE_AUDIT}:${DOCKER_TAG} ${DOCKER_IMAGE_AUDIT}:latest
                            """
                        }
                    }
                }
                stage('Build Score-API Image') {
                    steps {
                        dir('score-api') {
                            sh """
                                docker build -t ${DOCKER_IMAGE_SCORE}:${DOCKER_TAG} .
                                docker tag ${DOCKER_IMAGE_SCORE}:${DOCKER_TAG} ${DOCKER_IMAGE_SCORE}:latest
                            """
                        }
                    }
                }
            }
        }
        
        stage('Docker Push') {
            when {
                branch 'main'
            }
            parallel {
                stage('Push Audit-Fairness') {
                    steps {
                        withCredentials([usernamePassword(credentialsId: 'docker-registry', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh """
                                echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin ${DOCKER_REGISTRY}
                                docker push ${DOCKER_IMAGE_AUDIT}:${DOCKER_TAG}
                                docker push ${DOCKER_IMAGE_AUDIT}:latest
                            """
                        }
                    }
                }
                stage('Push Score-API') {
                    steps {
                        withCredentials([usernamePassword(credentialsId: 'docker-registry', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh """
                                echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin ${DOCKER_REGISTRY}
                                docker push ${DOCKER_IMAGE_SCORE}:${DOCKER_TAG}
                                docker push ${DOCKER_IMAGE_SCORE}:latest
                            """
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production...'
                input message: 'Deploy to production?', ok: 'Deploy'
                sh '''
                    docker-compose -f docker-compose.prod.yml up -d audit-fairness score-api
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            deleteDir()
        }
    }
}
