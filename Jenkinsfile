pipeline {
    agent any

    triggers {
        githubPush()   // Still trigger on push — we’ll filter inside the pipeline
    }

    environment {
        DATA_DIR = "${WORKSPACE}/data"
        CONTAINER_NAME = "ai_meeting_pipeline_6"
        IMAGE_NAME = "nikhilpesala/ai_meeting_pipeline:latest"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/NIKHILPESALA1/ai-meeting-pipeline.git'
            }
        }

        stage('Check for Video Changes') {
            steps {
                script {
                    echo "🔍 Checking for new or modified video files (.mp4)..."
                    def changed = sh(
                        script: "git diff-tree --no-commit-id --name-only -r HEAD | grep '.mp4' || true",
                        returnStdout: true
                    ).trim()

                    if (!changed) {
                        echo "🟡 No new or updated video files detected. Skipping the rest of the pipeline."
                        currentBuild.result = 'SUCCESS'
                        error("No .mp4 files found in latest commit.")
                    } else {
                        echo "🎥 New video(s) detected:\n${changed}"
                        env.NEW_VIDEOS = changed
                    }
                }
            }
        }

        stage('Pull Docker Image') {
            steps {
                script {
                    sh "docker pull ${IMAGE_NAME}"
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    echo "🚀 Starting Docker container ${CONTAINER_NAME}..."
                    sh """
                        docker rm -f ${CONTAINER_NAME} || true
                        docker run -d --name ${CONTAINER_NAME} \
                        -v ${DATA_DIR}:/app/data \
                        ${IMAGE_NAME} \
                        bash -c "mkdir -p /app/data/meetings && tail -f /dev/null"
                    """
                }
            }
        }

        stage('Copy Videos into Container') {
            steps {
                script {
                    echo "📂 Copying detected videos into the container..."
                    def videoFiles = env.NEW_VIDEOS.split()
                    for (file in videoFiles) {
                        sh "docker cp ${file} ${CONTAINER_NAME}:/app/data/meetings/"
                    }
                }
            }
        }

        stage('Process New Videos') {
            steps {
                script {
                    echo "🧠 Processing videos inside container..."
                    sh "docker exec ${CONTAINER_NAME} python3 scripts/process_new_videos.py"
                }
            }
        }

        stage('Push Summarized Output to Salesforce') {
            steps {
                script {
                    echo "☁️ Uploading summarized data to Salesforce..."
                    // You can later add integration here
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
                docker system prune -f || true
            """
        }
    }
}
