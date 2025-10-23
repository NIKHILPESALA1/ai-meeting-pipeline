pipeline {
    agent any

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Check for Video Changes') {
            steps {
                script {
                    echo "🔍 Checking for new or modified video files (.mp4) in data/meetings..."
                    // Use single quotes to avoid Groovy interpreting $
                    NEW_VIDEOS = sh(
                        script: 'git diff-tree --no-commit-id --name-only -r HEAD | grep ^data/meetings/.*\\.mp4$ || true',
                        returnStdout: true
                    ).trim()
                    
                    if (NEW_VIDEOS) {
                        echo "✅ New video(s) detected:\n${NEW_VIDEOS}"
                    } else {
                        echo "ℹ️ No new videos detected."
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
            steps {
                script {
                    echo "🚀 Starting Docker container ai_meeting_pipeline..."
                    sh '''
                        docker ps -a -q -f name=ai_meeting_pipeline | grep . && docker rm -f ai_meeting_pipeline || true
                        docker run -d --name ai_meeting_pipeline -v $PWD/data:/app/data --memory=4g nikhilpesala/ai_meeting_pipeline:latest bash -c "mkdir -p /app/data/meetings && tail -f /dev/null"
                    '''
                }
            }
        }

        stage('Copy Videos into Container') {
            when {
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                script {
                    echo "📂 Copying detected videos into the container..."
                    NEW_VIDEOS.split('\n').each { video ->
                        sh "docker cp ${video} ai_meeting_pipeline:/app/data/meetings/"
                    }
                }
            }
        }

        stage('Process New Videos') {
            when {
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                echo "🎬 Processing new videos..."
                // Your video processing commands here
            }
        }

        stage('Push Summarized Output to Salesforce') {
            when {
                expression { return NEW_VIDEOS != "" }
            }
            steps {
                echo "📤 Pushing summarized output..."
                // Your Salesforce push commands here
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up Docker container..."
            sh '''
                docker stop ai_meeting_pipeline || true
                docker rm ai_meeting_pipeline || true
                docker system prune -f
            '''
        }
    }
}
