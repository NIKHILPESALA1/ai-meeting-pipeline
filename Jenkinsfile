pipeline {
    agent any

    environment {
        CONTAINER_NAME = "ai_meeting_pipeline"
        VIDEO_DIR = "data/meetings"
        PROCESSED_DIR = "/app/data/processed"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Check for New Videos') {
            steps {
                script {
                    echo "Checking for new or modified video files (.mp4) in ${VIDEO_DIR}..."
                    NEW_VIDEOS = sh(
                        script: "git diff-tree --no-commit-id --name-only -r HEAD | grep '^${VIDEO_DIR}/.*\\.mp4\$' || true",
                        returnStdout: true
                    ).trim()
                    echo "New video(s) detected:\n${NEW_VIDEOS}"
                }
            }
        }

        stage('Pull Docker Image') {
            steps {
                sh "docker pull nikhilpesala/ai_meeting_pipeline:latest"
            }
        }

        stage('Run Container') {
            steps {
                script {
                    def containerExists = sh(script: "docker ps -a -q -f name=${CONTAINER_NAME}", returnStdout: true).trim()
                    if (!containerExists) {
                        sh "docker run -d --name ${CONTAINER_NAME} -v \${WORKSPACE}/data:/app/data --memory=4g nikhilpesala/ai_meeting_pipeline:latest bash -c 'mkdir -p ${PROCESSED_DIR} && tail -f /dev/null'"
                    } else {
                        sh "docker start ${CONTAINER_NAME}"
                    }
                }
            }
        }

        stage('Copy Videos into Container') {
            when {
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                script {
                    NEW_VIDEOS.split('\n').each { video ->
                        sh "docker cp ${video} ${CONTAINER_NAME}:/app/data/meetings/"
                    }
                }
            }
        }

        stage('Transcribe and Summarize') {
            when {
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                script {
                    echo "Transcribing and summarizing new videos..."
                    NEW_VIDEOS.split('\n').each { video ->
                        def filename = video.split('/')[-1]
                        sh "docker exec ${CONTAINER_NAME} python /app/scripts/process_new_videos.py /app/data/meetings/${filename} /app/data/processed/${filename}.json"
                    }
                }
            }
        }

        stage('Push Summarized Output to Salesforce') {
            when {
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                sh "docker exec ${CONTAINER_NAME} python /app/scripts/push_to_salesforce.py ${PROCESSED_DIR}"
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
