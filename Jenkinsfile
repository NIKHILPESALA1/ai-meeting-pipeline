pipeline {
    agent any

    environment {
        IMAGE = "ai_meeting_pipeline:latest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE .'
            }
        }

        stage('Run Pipeline in Container') {
            steps {
                sh '''
                docker run --rm $IMAGE bash -c "
                    python /app/scripts/extract_audio.py &&
                    python /app/scripts/transcribe.py &&
                    python /app/scripts/summarize_extract.py
                "
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'data/transcripts/*.txt, data/summaries/*.json', fingerprint: true
            }
        }
    }

    post {
        always {
            echo "Pipeline finished. Results are archived in Jenkins and available inside the container."
        }
    }
}
