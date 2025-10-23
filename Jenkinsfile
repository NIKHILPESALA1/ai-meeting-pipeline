pipeline {
    agent any

    environment {
        IMAGE_NAME = "ai_meeting_pipeline"
        IMAGE_TAG = "latest"
        REGISTRY = "nikhilpesala"
        FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        SF_INSTANCE_URL = "https://login.salesforce.com"
        CONTAINER_NAME = "ai_meeting_pipeline_${env.BUILD_ID}" // Dynamic container name per build
    }

    triggers {
        githubPush() // Trigger on GitHub push event
    }

    stages {

        stage('Checkout') {
            steps {
                git url: 'https://github.com/NIKHILPESALA1/ai-meeting-pipeline.git', branch: 'main'
            }
        }

        stage('Pull Docker Image') {
            steps {
                script {
                    sh """
                        docker pull ${FULL_IMAGE} || echo "No existing image found, skipping pull"
                    """
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    sh """
                        docker run -d --name ${CONTAINER_NAME} \
                        -v \$(pwd)/data:/app/data \
                        ${FULL_IMAGE} bash -c "mkdir -p /app/data/meetings && tail -f /dev/null"
                    """
                }
            }
        }

        stage('Process New Videos') {
            steps {
                sh """
                    docker exec ${CONTAINER_NAME} python3 scripts/process_new_videos.py
                """
            }
        }

        stage('Push Summarized Output to Salesforce') {
            environment {
                SF_CLIENT_ID     = credentials('SF_CLIENT_ID')
                SF_CLIENT_SECRET = credentials('SF_CLIENT_SECRET')
                SF_USERNAME      = credentials('SF_USERNAME')
                SF_PASSWORD      = credentials('SF_PASSWORD')
            }
            steps {
                sh """
                    docker exec ${CONTAINER_NAME} python3 scripts/push_to_salesforce.py
                """
            }
        }
    }

    post {
        always {
            echo "Cleaning up Docker container..."
            sh "docker stop ${CONTAINER_NAME} || true"
            sh "docker rm ${CONTAINER_NAME} || true"
            sh "docker system prune -f"
        }
    }
}
