pipeline {
    agent any

    environment {
        IMAGE_NAME = "ai_meeting_pipeline"
        IMAGE_TAG = "latest"
        REGISTRY = "nikhilpesala" // change this to your registry
        FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/NIKHILPESALA1/ai-meeting-pipeline.git', branch: 'main'
            }
        }

        stage('Pull Existing Image') {
            steps {
                script {
                    // Try to pull existing image to use as cache
                    sh """
                        docker pull ${FULL_IMAGE} || echo "No existing image found, will build"
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh """
                        docker build \
                        --cache-from ${FULL_IMAGE} \
                        -t ${FULL_IMAGE} .
                    """
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    sh """
                        docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASS}
                        docker push ${FULL_IMAGE}
                    """
                }
            }
        }

        stage('Run Container') {
            steps {
                sh """
                    docker run -d --name ai_meeting_app -p 5000:5000 ${FULL_IMAGE}
                """
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f'
        }
    }
}
