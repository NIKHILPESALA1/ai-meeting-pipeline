pipeline {
    agent any

    environment {
        IMAGE_NAME = "ai_meeting_pipeline"
        IMAGE_TAG = "latest"
        REGISTRY = "nikhilpesala"
        FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        DATA_DIR = "/root/.jenkins/workspace/${JOB_NAME}/data"
        SF_INSTANCE_URL = "https://login.salesforce.com"
    }

    triggers {
        githubPush() // Trigger on GitHub push event
    }

    stages {

        stage('Prepare Workspace') {
            steps {
                script {
                    sh "mkdir -p ${DATA_DIR}/meetings"
                }
            }
        }

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
                # Remove old container if exists
                docker rm -f ai_meeting_pipeline2 || true

                # Run new container and create meetings folder inside
                docker run -d --name ai_meeting_pipeline2 \
                -v ${DATA_DIR}:/app/data \
                ${FULL_IMAGE} bash -c "mkdir -p /app/data/meetings && tail -f /dev/null"
            """
        }
    }
}


        stage('Process New Videos') {
            steps {
                sh """
                    docker exec ai_meeting_pipeline2 python3 scripts/process_new_videos.py
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
                    docker exec ai_meeting_pipeline2 python3 scripts/push_to_salesforce.py
                """
            }
        }
    }

    post {
        always {
            echo "Cleaning up Docker container..."
            sh 'docker stop ai_meeting_pipeline2 || true'
            sh 'docker rm ai_meeting_pipeline2 || true'
            sh 'docker system prune -f'
        }
    }
}
