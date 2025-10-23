pipeline {
    agent any

    // Global environment variables
    environment {
        IMAGE_NAME = "ai_meeting_pipeline"
        IMAGE_TAG = "latest"
        REGISTRY = "nikhilpesala"
        FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        SF_INSTANCE_URL = "https://login.salesforce.com"
        SF_APP_DESCRIPTION = "External Client App for Automated Meeting Summarizer"
    }

    // Trigger pipeline on GitHub push
    triggers {
        githubPush()
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
                sh """
                    docker run -d --name ai_meeting_app -p 5000:5000 ${FULL_IMAGE}
                """
            }
        }

        stage('Process New Videos') {
            steps {
                // This assumes your container automatically picks up new videos in /app/meetings
                sh """
                docker exec ai_meeting_app python3 scripts/transcribe_and_summarize.py
                """
            }
        }

        stage('Push to Salesforce') {
            environment {
                SF_CLIENT_ID     = credentials('SF_CLIENT_ID')
                SF_CLIENT_SECRET = credentials('SF_CLIENT_SECRET')
                SF_USERNAME      = credentials('SF_USERNAME')
                SF_PASSWORD      = credentials('SF_PASSWORD')
            }
            steps {
                sh """
                docker exec ai_meeting_app python3 scripts/push_to_salesforce.py
                """
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f'
            // Optional: stop and remove the container to free resources
            sh 'docker stop ai_meeting_app || true'
            sh 'docker rm ai_meeting_app || true'
        }
    }
}
