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
                echo 'Validating Terraform, AWS CLI and AWS authentication...'
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
                    sh 'terraform init -input=false -no-color'
                }
            }
        }

        stage('Terraform Format Check') {
            steps {
                echo 'Checking Terraform formatting...'
                dir("${env.TF_DIR}") {
                    sh 'terraform fmt -check -recursive -no-color'
                }
            }
        }

        stage('Terraform Validate') {
            steps {
                echo 'Validating Terraform configuration...'
                dir("${env.TF_DIR}") {
                    sh 'terraform validate -no-color'
                }
            }
        }

        stage('Terraform Plan') {
            steps {
                echo 'Generating Terraform execution plan...'
                dir("${env.TF_DIR}") {
                    sh '''
                        terraform plan \
                            -input=false \
                            -no-color \
                            -out=tfplan

                        terraform show \
                            -no-color \
                            tfplan > tfplan.txt
                    '''
                }
            }
        }

        stage('Archive Terraform Plan') {
            steps {
                echo 'Archiving Terraform plan for review...'
                archiveArtifacts artifacts: 'terraform/tfplan.txt',
                                 fingerprint: true
            }
        }

        stage('FinOps: Cost Estimation') {
            steps {
                echo 'Estimating AWS Infrastructure Cost via Infracost...'
                script {
                    try {
                        withCredentials([
                            string(
                                credentialsId: 'infracost-api-key',
                                variable: 'INFRACOST_API_KEY'
                            )
                        ]) {
                            dir("${env.TF_DIR}") {
                                sh '''
                                    infracost breakdown \
                                        --path . \
                                        --format table \
                                        --out-file ../infracost-report.txt

                                    cat ../infracost-report.txt
                                '''
                            }

                            archiveArtifacts artifacts: 'infracost-report.txt',
                                             allowEmptyArchive: true
                        }
                    } catch (Exception e) {
                        echo "Notice: Infracost cost estimation skipped or failed: ${e.getMessage()}. Ensure 'infracost-api-key' is configured in Jenkins Credentials."
                    }
                }
            }
        }

        stage('Terraform Apply Approval') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Review the archived Terraform plan. Apply infrastructure changes?',
                      ok: 'Apply'
            }
        }

        stage('Terraform Apply') {
            when {
                branch 'main'
            }
            steps {
                echo 'Applying approved Terraform infrastructure changes...'
                dir("${env.TF_DIR}") {
                    sh '''
                        terraform apply \
                            -input=false \
                            -no-color \
                            -auto-approve \
                            tfplan
                    '''
                }
            }
        }

        stage('Deploy to EKS & Setup Metrics Server') {
            when {
                // Guard: Only run if the EKS cluster is actively provisioned on AWS
                expression {
                    return sh(
                        script: 'aws eks describe-cluster --name lumora-ecommerce-prod --region us-east-1 --query "cluster.status" --output text 2>/dev/null | grep -q "ACTIVE"',
                        returnStatus: true
                    ) == 0
                }
            }
            steps {
                echo 'EKS Cluster is ACTIVE. Deploying Metrics Server and Workloads...'
                sh '''
                    # 1. Run automated Metrics Server check & installation
                    chmod +x scripts/setup_metrics_server.sh
                    ./scripts/setup_metrics_server.sh

                    # 2. Deploy application manifests and HPA via Kustomize
                    kubectl apply -k k8s/

                    # 3. Wait for Flask app rollout
                    kubectl rollout status deployment/flask-app -n lumora-prod --timeout=180s

                    # 4. Display live HPA status
                    kubectl get hpa -n lumora-prod
                '''
            }
        }
    }

   post {
    always {
        echo 'Pipeline execution completed.'
        deleteDir()
    }
    success {
        echo 'Terraform Jenkins Pipeline executed successfully!'
    }
    failure {
        echo 'Pipeline failed. Check build logs for diagnostic details.'
    }
}
}