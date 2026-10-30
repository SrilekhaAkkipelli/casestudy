
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'srilekha0208/campuscare'
        DOCKER_CREDENTIALS = 'dockerhub-credentials'
        K8S_NAMESPACE = 'default'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out CampusCare source code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building CampusCare Docker image...'
                script {
                    docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing image to Docker Hub...'

                script {
                    docker.withRegistry(
                        'https://index.docker.io/v1/',
                        DOCKER_CREDENTIALS
                    ) {
                        docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").push()
                        docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}").push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Applying Kubernetes manifests...'

                bat '''
                    kubectl apply -f kubernetes\\deployment.yaml -n %K8S_NAMESPACE%
                    kubectl apply -f kubernetes\\service.yaml -n %K8S_NAMESPACE%

                    kubectl set image deployment/campuscare campuscare=%DOCKER_IMAGE%:%BUILD_NUMBER% -n %K8S_NAMESPACE%

                    kubectl rollout status deployment/campuscare -n %K8S_NAMESPACE%
                '''
            }
        }
    }

    post {
        success {
            echo 'CampusCare successfully built, pushed and deployed!'
        }

        failure {
            echo 'Pipeline failed. Check the Jenkins console output.'
        }
    }
}
