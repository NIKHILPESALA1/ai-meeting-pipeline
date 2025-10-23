pipeline {
    agent any

    environment {
        CONTAINER_NAME = "ai_meeting_pipeline"
        VIDEO_DIR = "data/meetings"
        PROCESSED_DIR = "/app/data/processed"
        NEW_VIDEOS = ""   // ✅ Make it global
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
            echo "Checking for new or modified .mp4 files in ${VIDEO_DIR}..."

            def prevCommit = env.GIT_PREVIOUS_SUCCESSFUL_COMMIT ?: 'HEAD~1'
            def currentCommit = env.GIT_COMMIT

            // Debug info
            echo "Previous commit: ${prevCommit}"
            echo "Current commit:  ${currentCommit}"

            def diffOutput = sh(
                script: "git diff --name-only ${prevCommit} ${currentCommit} | grep '\\.mp4\$' || true",
                returnStdout: true
            ).trim()

            echo "Raw git diff output:\n${diffOutput}"

            env.NEW_VIDEOS = diffOutput
            echo "DEBUG → env.NEW_VIDEOS = '${env.NEW_VIDEOS}'"

            if (!env.NEW_VIDEOS?.trim()) {
                echo "No new videos detected. Skipping next stages."
            } else {
                echo "Detected new video files: ${env.NEW_VIDEOS}"
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
                        sh "docker cp ${video} ${CONTAINER_NAME}:/app/data/meetings/"
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
                    echo "Transcribing and summarizing new videos..."
                    env.NEW_VIDEOS.split('\n').findAll { it?.trim() }.each { video ->
                        def parts = video.tokenize('/')
                        def filename = parts[-1]
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
            echo "Cleaning up Docker container..."
            sh "docker stop ${CONTAINER_NAME} || true"
            sh "docker rm ${CONTAINER_NAME} || true"
        }
    }
}
