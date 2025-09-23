pipeline {
    agent any

    environment {
        IMAGE = "ai_meeting_pipeline:latest"
        DATA_DIR = "${WORKSPACE}/data"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t $IMAGE .
                '''
            }
        }

        stage('Run Pipeline in Container') {
            steps {
                sh '''
                docker run --rm \
                  -v $DATA_DIR:/app/data \
                  $IMAGE bash -c "
                    python scripts/extract_audio.py &&
                    python scripts/transcribe.py &&
                    python scripts/summarize_extract.py
                  "
                '''
            }
        }

        stage('Archive Results') {
            steps {
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
