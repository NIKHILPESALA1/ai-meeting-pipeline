pipeline {
    agent any

    environment {
        CONTAINER_NAME = "ai_meeting_pipeline"
        DATA_DIR = "${env.WORKSPACE}/data"
        DOCKER_IMAGE = "nikhilpesala/ai_meeting_pipeline:latest"
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
                    echo "📹 Checking for new or modified video files (.mp4)..."
                    NEW_VIDEOS = sh(script: "git diff-tree --no-commit-id --name-only -r HEAD | grep .mp4 || true", returnStdout: true).trim()
                    if (NEW_VIDEOS) {
                        echo "📌 New video(s) detected:\n${NEW_VIDEOS}"
                    } else {
                        echo "✅ No new videos detected."
                        NEW_VIDEOS = ""
                    }
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
                    // Remove old container safely
                    sh "docker rm -f ${CONTAINER_NAME} || true"

                    // Run container with memory limit
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
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                script {
                    echo "📁 Copying detected videos into the container..."
                    for (video in NEW_VIDEOS.split("\n")) {
                        sh "docker cp ${video} ${CONTAINER_NAME}:/app/data/meetings/"
                    }
                }
            }
        }

        stage('Process New Videos') {
            when {
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                script {
                    echo "⚙️ Processing videos inside container..."
                    sh "docker exec ${CONTAINER_NAME} python3 scripts/process_new_videos.py"
                }
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Docker container..."
            sh "docker stop ${CONTAINER_NAME} || true"
            sh "docker rm ${CONTAINER_NAME} || true"
            sh "docker system prune -f"
        }
    }
}
