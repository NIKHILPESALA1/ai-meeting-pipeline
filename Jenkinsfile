pipeline {
    agent any
    environment {
        NEW_VIDEOS = ''
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
                    // Detect new or modified mp4 files in data/meetings
                    NEW_VIDEOS = sh(
                        script: "git diff-tree --no-commit-id --name-only -r HEAD | grep ^data/meetings/.*\\.mp4$ || true",
                        returnStdout: true
                    ).trim()
                    
                    if (NEW_VIDEOS) {
                        echo "New video(s) detected:\n${NEW_VIDEOS}"
                    } else {
                        echo "No new videos detected."
                    }
                }
            }
        }

        stage('Pull Docker Image') {
            steps {
                script {
                    sh 'docker pull nikhilpesala/ai_meeting_pipeline:latest'
                }
            }
        }

        stage('Run Container') {
            when {
                expression { NEW_VIDEOS }
            }
            steps {
                script {
                    // Remove old container if exists
                    sh 'docker rm -f ai_meeting_pipeline || true'

                    // Start a fresh container
                    sh """
                    docker run -d --name ai_meeting_pipeline \
                    -v \${WORKSPACE}/data:/app/data \
                    --memory=4g nikhilpesala/ai_meeting_pipeline:latest \
                    bash -c "mkdir -p /app/data/meetings && tail -f /dev/null"
                    """
                }
            }
        }

        stage('Copy Videos into Container') {
            when {
                expression { NEW_VIDEOS }
            }
            steps {
                script {
                    NEW_VIDEOS.split("\\n").each { video ->
                        sh "docker cp ${video} ai_meeting_pipeline:/app/data/meetings/"
                    }
                }
            }
        }

        stage('Process New Videos') {
            when {
                expression { NEW_VIDEOS }
            }
            steps {
                script {
                    sh """
                    docker exec ai_meeting_pipeline bash -c 'for f in /app/data/meetings/*.mp4; do
                        echo "Processing \$f..."
                        # Place your processing command here
                    done'
                    """
                }
            }
        }

    }

    post {
        always {
            script {
                echo "Cleaning up Docker container..."
                sh 'docker stop ai_meeting_pipeline || true'
                sh 'docker rm ai_meeting_pipeline || true'
                sh 'docker system prune -f'
            }
        }
    }
}
