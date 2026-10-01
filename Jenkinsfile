pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        TF_IN_AUTOMATION   = 'true'
        TF_DIR             = 'terraform'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('Checkout SCM') {
            steps {
                echo 'Checking out source code from GitHub...'
                checkout scm
            }
        }

        stage('Validate Prerequisites') {
            steps {
                echo 'Validating CLI tools (Terraform & AWS CLI)...'
                sh 'terraform version'
                sh 'aws --version'
                sh 'infracost --version || true' 
                sh 'aws sts get-caller-identity'
            }
        }

        stage('Terraform Init') {
            steps {
                echo 'Initializing Terraform S3 Remote State Backend...'
                dir("${env.TF_DIR}") {
                    sh 'terraform init -no-color'
                }
            }
        }

        stage('Terraform Validate & Format Check') {
            steps {
                echo 'Validating Terraform code structure...'
                dir("${env.TF_DIR}") {
                    sh 'terraform validate -no-color'
                    sh 'terraform fmt -check -no-color || true'
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                echo 'Generating Terraform Execution Plan...'
                dir("${env.TF_DIR}") {
                    sh 'terraform plan -no-color -out=tfplan'
                }
            }
        }

                stage('FinOps: Cost Estimation') {
            steps {
                echo 'Estimating AWS Infrastructure Cost via Infracost...'
                script {
                    try {
                        withCredentials([string(credentialsId: 'infracost-api-key', variable: 'INFRACOST_API_KEY')]) {
                            dir("${env.TF_DIR}") {
                                sh '''
                                    infracost breakdown --path . --format table --out-file ../infracost-report.txt
                                    cat ../infracost-report.txt
                                '''
                            }
                            archiveArtifacts artifacts: 'infracost-report.txt', allowEmptyArchive: true
                        }
                    } catch (Exception e) {
                        echo "Notice: Infracost cost estimation skipped or failed: ${e.getMessage()}. Ensure 'infracost-api-key' is configured in Jenkins Credentials."
                    }
                }
            }
        }

        stage('Terraform Apply') {
            when {
                branch 'main'
            }
            steps {
                echo 'Applying Infrastructure Changes via Terraform...'
                dir("${env.TF_DIR}") {
                    sh 'terraform apply -no-color -auto-approve tfplan'
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline execution completed.'
            cleanWs(deleteDirs: true, notFailBuild: true)
        }
        success {
            echo 'Terraform Jenkins Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check build logs for diagnostic details.'
        }
    }
}
