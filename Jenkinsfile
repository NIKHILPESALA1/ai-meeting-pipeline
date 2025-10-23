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
                    def videoDir = "${WORKSPACE}/${VIDEO_DIR}"
                    def recordFile = "${WORKSPACE}/.last_videos.txt"

                    sh "mkdir -p ${videoDir}"

                    // List current .mp4 files
                    def currentList = sh(
                        script: "ls ${videoDir}/*.mp4 2>/dev/null || true",
                        returnStdout: true
                    ).trim()

                    // Read previous list
                    def previousList = fileExists(recordFile) ? readFile(recordFile).trim() : ""

                    // Find new videos
                    def newVideos = []
                    if (currentList) {
                        newVideos = currentList.split('\n').findAll { !previousList.contains(it) }
                    }

                    if (newVideos) {
                        env.NEW_VIDEOS = newVideos.join('\n')
                        echo "🎥 New video(s) detected:\n${env.NEW_VIDEOS}"
                        writeFile file: recordFile, text: currentList
                    } else {
                        env.NEW_VIDEOS = ""
                        echo "No new videos found in ${videoDir}."
                    }
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
                    if (containerExists == "") {
                        sh "docker run -d --name ${CONTAINER_NAME} -v \${WORKSPACE}/data:/app/data --memory=4g nikhilpesala/ai_meeting_pipeline:latest bash -c 'mkdir -p ${PROCESSED_DIR} && tail -f /dev/null'"
                    } else {
                        sh "docker start ${CONTAINER_NAME}"
                    }
                }
            }
        }

        stage('Copy Videos into Container') {
            when {
                expression { return env.NEW_VIDEOS?.trim() }
            }
            steps {
                script {
                    env.NEW_VIDEOS.split('\n').findAll { it?.trim() }.each { video ->
                        sh "docker cp '${video}' ${CONTAINER_NAME}:/app/data/meetings/"
                    }
                }
            }
        }

        stage('Transcribe and Summarize') {
            when {
                expression { return env.NEW_VIDEOS?.trim() }
            }
            steps {
                script {
                    echo "🧠 Transcribing and summarizing new videos..."
                    env.NEW_VIDEOS.split('\n').findAll { it?.trim() }.each { video ->
                        def filename = video.tokenize('/').last()
                        sh "docker exec ${CONTAINER_NAME} python /app/scripts/process_new_videos.py /app/data/meetings/${filename} /app/data/processed/${filename}.json"
                    }
                }
            }
        }

        stage('Push Summarized Output to Salesforce') {
            when {
                expression { return env.NEW_VIDEOS?.trim() }
            }
            steps {
                sh "docker exec ${CONTAINER_NAME} python /app/scripts/push_to_salesforce.py ${PROCESSED_DIR}"
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Docker container..."
            sh "docker stop ${CONTAINER_NAME} || true"
            sh "docker rm ${CONTAINER_NAME} || true"
        }
    }
}
