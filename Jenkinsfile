pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        TF_IN_AUTOMATION   = 'true'
        TF_DIR             = 'terraform'
        ECR_REGISTRY       = '759530261212.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPOSITORY     = 'lumora-ecommerce-flask'
        IMAGE_TAG          = "${env.BUILD_NUMBER ?: 'latest'}"
        INFRACOST_CLI_ORG  = 'thiagarajan-b'
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
                            sh '''
                                export INFRACOST_NO_COLOR=true
                                export INFRACOST_SKIP_UPDATE_CHECK=true
                                export CI=true
                                export INFRACOST_CI=true
                                
                                if [ -n "${INFRACOST_API_KEY}" ] && [ "${INFRACOST_API_KEY}" != "dummy" ]; then
                                    echo "Injecting Infracost v2 authentication tokens..."
                                    export INFRACOST_API_KEY="${INFRACOST_API_KEY}"
                                    export INFRACOST_CLI_AUTHENTICATION_TOKEN="${INFRACOST_API_KEY}"
                                    export INFRACOST_CLI_ORG="${INFRACOST_CLI_ORG:-thiagarajan-b}"
                                    
                                    echo "Running Infracost v2 multi-project scan (Terraform + Kubernetes)..."
                                    timeout 60s infracost scan --org "${INFRACOST_CLI_ORG}" > infracost-report.txt 2>&1 || \
                                    echo "Notice: Infracost scan timed out or key invalid, proceeding."
                                    
                                    # Append filtered resource cost breakdown (> $0.5 only)
                                    infracost inspect --group-by resource --min-cost 0.5 >> infracost-report.txt 2>&1 || true
                                    
                                    if [ -f infracost-report.txt ]; then
                                        cat infracost-report.txt
                                    fi
                                else
                                    echo "Notice: Valid INFRACOST_API_KEY not configured. Skipping."
                                fi
                            '''

                            if (fileExists('infracost-report.txt')) {
                                archiveArtifacts artifacts: 'infracost-report.txt',
                                                 allowEmptyArchive: true
                            }
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

        stage('Ansible Configuration Check') {
            steps {
                echo 'Running Ansible syntax verification...'
                dir('ansible') {
                    sh '''
                        if command -v ansible-playbook >/dev/null 2>&1; then
                            echo "Ansible detected. Validating playbook syntax using ansible.cfg..."
                            ansible-playbook -i inventory/hosts.ini --syntax-check playbooks/setup_jenkins.yml
                        else
                            echo "Ansible not present on this runner, skipping syntax check."
                        fi
                    '''
                }
            }
        }

        stage('Application Test (Pytest)') {
            steps {
                echo 'Executing automated unit tests...'
                sh '''
                    # Create and activate an isolated virtual environment
                    if [ ! -d ".venv" ]; then
                        python3 -m venv .venv || virtualenv .venv || true
                    fi

                    if [ -f .venv/bin/activate ]; then
                        . .venv/bin/activate
                        pip install --no-cache-dir -r requirements.txt
                        pytest tests/ -v
                    else
                        # Fallback if venv is unavailable
                        pip3 install --user --break-system-packages -r requirements.txt || true
                        export PATH="$HOME/.local/bin:$PATH"
                        pytest tests/ -v || python3 -m unittest discover -s tests -p "test_*.py" -v
                    fi
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image: ${env.ECR_REPOSITORY}:${env.IMAGE_TAG}..."
                sh '''
                    docker build \
                        -t ${ECR_REPOSITORY}:${IMAGE_TAG} \
                        -t ${ECR_REPOSITORY}:latest \
                        .
                    docker images | grep ${ECR_REPOSITORY}
                '''
            }
        }

        stage('Trivy Container Security Scan') {
            steps {
                echo 'Scanning container image for vulnerabilities using Trivy...'
                sh '''
                    if command -v trivy >/dev/null 2>&1; then
                        trivy image \
                            --severity HIGH,CRITICAL \
                            --exit-code 0 \
                            --format table \
                            ${ECR_REPOSITORY}:${IMAGE_TAG}
                    else
                        echo "Notice: Trivy is not installed on this runner. Skipping image vulnerability scan."
                    fi
                '''
            }
        }

        stage('Push Docker Image to AWS ECR') {
            steps {
                echo "Authenticating Docker to ECR and pushing image to ${env.ECR_REGISTRY}..."
                sh '''
                    aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
                        docker login --username AWS --password-stdin ${ECR_REGISTRY}

                    docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                    docker tag ${ECR_REPOSITORY}:latest ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest

                    docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                    docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                '''
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
    }

    success {
        echo 'Jenkins pipeline completed successfully!'

        emailext(
            to: '${DEFAULT_RECIPIENTS}',
            subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            mimeType: 'text/html',
            body: """
                <h2>Deployment Successful</h2>
                <p><b>Job Name:</b> ${env.JOB_NAME}</p>
                <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                <p><b>Status:</b> SUCCESS</p>
                <p><b>Pipeline URL:</b>
                    <a href="${env.BUILD_URL}">${env.BUILD_URL}</a>
                </p>
            """
        )
    }

    failure {
        echo 'Jenkins pipeline failed!'

        emailext(
            to: '${DEFAULT_RECIPIENTS}',
            subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
            mimeType: 'text/html',
            body: """
                <h2>Deployment Failed</h2>
                <p><b>Job Name:</b> ${env.JOB_NAME}</p>
                <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                <p><b>Status:</b> FAILURE</p>
                <p><b>Pipeline URL:</b>
                    <a href="${env.BUILD_URL}">${env.BUILD_URL}</a>
                </p>
                <p>Please check Jenkins console output.</p>
            """
        )
    }

    cleanup {
        deleteDir()
    }
}

}