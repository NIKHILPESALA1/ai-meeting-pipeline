pipeline {
    agent any

    environment {
        IMAGE = "ai_meeting_pipeline:latest"
        WORKSPACE_DIR = "${WORKSPACE}" // Jenkins workspace
    }

    stages {
        stage('Checkout Code') {
            steps {
                echo "Pulling latest code and videos from GitHub..."
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building the pipeline Docker image..."
                sh """
                docker build -t $IMAGE .
                """
            }
        }

        stage('Run Pipeline in Container') {
            steps {
                echo "Running AI pipeline inside container..."
                sh """
                docker run --rm \
                  -v $WORKSPACE_DIR:/app/data \
                  $IMAGE bash -c '
                      cd /app/data &&
                      git lfs pull &&
                      python /app/scripts/extract_audio.py &&
                      python /app/scripts/transcribe.py &&
                      python /app/scripts/summarize_extract.py
                  '
                """
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
