pipeline {
    agent any

    environment {
        IMAGE = "ai_meeting_pipeline:latest"
        DATA_DIR = "${WORKSPACE}/data"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Pulling latest code and videos from GitHub..."
                checkout scm
            }
        }

        stage('Fetch LFS Videos') {
            steps {
                echo "Ensuring Git LFS videos are pulled..."
                sh '''
                git lfs install
                git lfs pull
                '''
            }
        }

        stage('Run Pipeline in Container') {
            steps {
                echo "Processing videos in Docker container..."
                sh '''
                docker run --rm -v $WORKSPACE:/app $IMAGE bash -c "
                    python /app/scripts/extract_audio.py &&
                    python /app/scripts/transcribe.py &&
                    python /app/scripts/summarize_extract.py
                "
                '''
            }
        }

        stage('Archive Results') {
            steps {
                echo "Archiving transcripts and summaries..."
                archiveArtifacts artifacts: 'data/summaries/*.json, data/transcripts/*.txt', fingerprint: true
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. Summaries & transcripts archived from container."
        }
    }
}
