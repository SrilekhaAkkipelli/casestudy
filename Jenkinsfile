pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'srilekha0208/campuscare'
        K8S_NAMESPACE = 'default'
        DOCKER_EXE = 'C:\\Users\\akkip\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
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

                bat '''
                    "%DOCKER_EXE%" build -t "%DOCKER_IMAGE%:%BUILD_NUMBER%" .
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                echo 'Pushing image to Docker Hub...'

                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_TOKEN'
                )]) {
                    bat '''
                        powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$env:DOCKER_TOKEN | & $env:DOCKER_EXE login --username $env:DOCKER_USER --password-stdin"

                        if errorlevel 1 exit /b 1

                        "%DOCKER_EXE%" push "%DOCKER_IMAGE%:%BUILD_NUMBER%"

                        if errorlevel 1 exit /b 1

                        "%DOCKER_EXE%" tag "%DOCKER_IMAGE%:%BUILD_NUMBER%" "%DOCKER_IMAGE%:latest"

                        if errorlevel 1 exit /b 1

                        "%DOCKER_EXE%" push "%DOCKER_IMAGE%:latest"
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying CampusCare to Kubernetes...'

                bat '''
                    kubectl apply -f kubernetes\\deployment.yaml -n %K8S_NAMESPACE%

                    if errorlevel 1 exit /b 1

                    kubectl apply -f kubernetes\\service.yaml -n %K8S_NAMESPACE%

                    if errorlevel 1 exit /b 1

                    kubectl set image deployment/campuscare campuscare=%DOCKER_IMAGE%:%BUILD_NUMBER% -n %K8S_NAMESPACE%

                    if errorlevel 1 exit /b 1

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