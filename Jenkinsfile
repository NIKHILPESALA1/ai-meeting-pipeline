pipeline {
    agent any

    environment {
        DATA_DIR = "/root/.jenkins/workspace/MYPROJECT1/data"
        DOCKER_IMAGE = "nikhilpesala/ai_meeting_pipeline:latest"
        CONTAINER_NAME = "ai_meeting_pipeline"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Check for Video Changes') {
            steps {
                script {
                    // Properly declare NEW_VIDEOS
                    def NEW_VIDEOS = sh(
                        script: "git diff-tree --no-commit-id --name-only -r HEAD | grep .mp4 || true",
                        returnStdout: true
                    ).trim()

                    if (NEW_VIDEOS) {
                        echo "📌 New video(s) detected:\n${NEW_VIDEOS}"
                    } else {
                        echo "✅ No new videos detected."
                        NEW_VIDEOS = ""
                    }

                    // Store for later stages
                    env.NEW_VIDEOS = NEW_VIDEOS
                }
            }
        }

        stage('Pull Docker Image') {
            steps {
                script {
                    sh "docker pull ${DOCKER_IMAGE}"
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    echo "🚀 Starting Docker container ${CONTAINER_NAME}..."

                    // Remove old container only if it exists
                    sh """
                    if [ \$(docker ps -a -q -f name=${CONTAINER_NAME}) ]; then
                        docker rm -f ${CONTAINER_NAME}
                    fi
                    """

                    // Run new container
                    sh """
                    docker run -d \
                        --name ${CONTAINER_NAME} \
                        -v ${DATA_DIR}:/app/data \
                        --memory=4g \
                        ${DOCKER_IMAGE} \
                        bash -c "mkdir -p /app/data/meetings && tail -f /dev/null"
                    """
                }
            }
        }

        stage('Copy Videos into Container') {
            when {
                expression { return env.NEW_VIDEOS?.trim() }
            }
            steps {
                script {
                    echo "📁 Copying detected videos into the container..."
                    env.NEW_VIDEOS.split('\n').each { file ->
                        sh "docker cp ${file} ${CONTAINER_NAME}:/app/data/meetings/"
                    }
                }
            }
        }

        stage('Process New Videos') {
            when {
                expression { return env.NEW_VIDEOS?.trim() }
            }
            steps {
                script {
                    echo "🎬 Processing videos inside container..."
                    sh "docker exec ${CONTAINER_NAME} python3 scripts/process_new_videos.py"
                }
            }
        }

        stage('Push Summarized Output to Salesforce') {
            when {
                expression { return env.NEW_VIDEOS?.trim() }
            }
            steps {
                script {
                    echo "📤 Pushing summarized output to Salesforce..."
                    // Add your Salesforce push commands here
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Docker container..."
            sh """
            docker stop ${CONTAINER_NAME} || true
            docker rm ${CONTAINER_NAME} || true
            docker system prune -f
            """
        }
    }
}
