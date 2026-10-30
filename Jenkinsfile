
pipeline {

    agent any

    environment {
        DOCKER_IMAGE = 'YOUR_DOCKERHUB_USERNAME/campuscare'
        DOCKER_CREDENTIALS = 'dockerhub-credentials'
        K8S_NAMESPACE = 'default'
    }

    stages {

        // Stage 1: Get latest source code
        stage('Checkout') {
            steps {
                echo 'Pulling latest source code from GitHub...'
                checkout scm
            }
        }

        // Stage 2: Install Python dependencies
        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh 'python3 -m pip install -r requirements.txt'
            }
        }

        // Stage 3: Build Docker Image
        stage('Build Docker Image') {
            steps {
                echo 'Building CampusCare Docker image...'
                script {
                    docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                }
            }
        }

        // Stage 4: Push Image to Docker Hub
        stage('Push Docker Image') {
            steps {
                echo 'Pushing image to Docker Hub...'

                script {
                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        DOCKER_CREDENTIALS
                    ) {
                        docker.image(
                            "${DOCKER_IMAGE}:${BUILD_NUMBER}"
                        ).push()

                        docker.image(
                            "${DOCKER_IMAGE}:${BUILD_NUMBER}"
                        ).push('latest')
                    }
                }
            }
        }

        // Stage 5: Deploy to Kubernetes
        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying CampusCare to Kubernetes...'

                sh """
                    kubectl set image deployment/campuscare \
                    campuscare=${DOCKER_IMAGE}:${BUILD_NUMBER} \
                    -n ${K8S_NAMESPACE}

                    kubectl rollout status deployment/campuscare \
                    -n ${K8S_NAMESPACE}
                """
            }
        }
    }

    post {
        success {
            echo 'CampusCare deployed successfully!'
        }

        failure {
            echo 'CI/CD Pipeline failed. Check the Jenkins logs.'
        }
    }
}
