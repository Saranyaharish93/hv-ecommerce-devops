pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        TF_IN_AUTOMATION   = 'true'
        TF_DIR             = 'terraform'
        ECR_REGISTRY       = '759530261212.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPOSITORY     = 'lumora-ecommerce-flask'
        IMAGE_TAG          = "build-${env.BUILD_NUMBER}-${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'manual'}"
        INFRACOST_CLI_ORG  = 'thiagarajan-b'
        DEPLOYMENT_STATUS  = 'SKIPPED'
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
                script {
                    // Image-tag commits for Argo CD must not re-trigger a full build loop.
                    def commitMsg = sh(script: 'git log -1 --pretty=%B', returnStdout: true).trim()
                    if (commitMsg.contains('[skip ci]')) {
                        currentBuild.result = 'ABORTED'
                        error('Skipped: Argo CD image-tag commit ([skip ci]).')
                    }
                }
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

        stage('Application Test (Pytest)') {
            steps {
                echo 'Executing automated unit tests with pytest...'
                sh '''
                    # 1. Preflight check: Ensure python3 is available
                    if ! command -v python3 >/dev/null 2>&1; then
                        echo "FATAL: python3 is not installed on this runner."
                        exit 1
                    fi

                    # 2. Setup isolated virtual environment
                    if [ ! -d ".venv" ]; then
                        python3 -m venv .venv
                    fi
                    . .venv/bin/activate

                    # 3. Deterministic dependency install
                    pip install --no-cache-dir -r requirements.txt

                    # 4. Run tests and generate machine-readable JUnit XML report
                    pytest tests/ -v --junitxml=test-results.xml
                        '''
            }
            post {
                always {
                    // Record test results in Jenkins UI (passes/failures/graphs)
                    junit testResults: 'test-results.xml', allowEmptyResults: true
                }
            }
        }

        stage('Ansible Configuration Check') {
            steps {
                echo 'Running Ansible syntax verification...'
                dir('ansible') {
                    sh '''
                        if ! command -v ansible-playbook >/dev/null 2>&1; then
                            echo "FATAL: ansible-playbook is required but not installed on this runner."
                            exit 1
                        fi
                        echo "Ansible detected. Validating playbook syntax using ansible.cfg..."
                        ansible-playbook -i inventory/hosts.ini --syntax-check playbooks/setup_jenkins.yml
                            '''
                }
            }
        }

        stage('Gitleaks Repository Secret Scan') {
            steps {
                echo 'Auditing Git repository and commit history for plaintext secrets...'
                sh '''
                    # 1. Preflight check: Ensure Gitleaks binary is available
                    if ! command -v gitleaks >/dev/null 2>&1; then
                        echo "Gitleaks not found in system PATH. Bootstrapping standalone binary..."
                        curl -sSL https://github.com/gitleaks/gitleaks/releases/download/v8.24.0/gitleaks_8.24.0_linux_x64.tar.gz | tar -xz -C /tmp gitleaks
                        sudo mv /tmp/gitleaks /usr/local/bin/gitleaks 2>/dev/null || mv /tmp/gitleaks .gitleaks_bin
                    fi

                    GITLEAKS_CMD=$(command -v gitleaks || echo "./.gitleaks_bin")

                    # 2. Execute secret scan across Git commit history, redact sensitive values, and fail on leaks
                    $GITLEAKS_CMD detect \
                        --verbose \
                        --redact \
                        --report-path gitleaks-report.json \
                        --exit-code 1
                        '''
            }
            post {
                always {
                    // Retain audit evidence on Jenkins build page
                    archiveArtifacts artifacts: 'gitleaks-report.json',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker image: ${env.ECR_REPOSITORY}:${env.IMAGE_TAG}..."
                sh '''
                    docker build \
                        -t ${ECR_REPOSITORY}:${IMAGE_TAG} \
                        .
                    docker images | grep ${ECR_REPOSITORY}
                        '''
            }
        }

        stage('Trivy Container Security Scan') {
            steps {
                echo 'Scanning container image for vulnerabilities using Trivy...'
                sh '''
                    # 1. Preflight check: Never allow silent bypass
                    if ! command -v trivy >/dev/null 2>&1; then
                        echo "FATAL: Trivy is not installed on this runner. Security scan is mandatory."
                        exit 1
                    fi

                    # 2. Generate full machine-readable JSON report for auditing
                    trivy image \
                        --format json \
                        --output trivy-report.json \
                        ${ECR_REPOSITORY}:${IMAGE_TAG}

                    # 3. Print human-readable summary table to Jenkins console log
                    trivy image \
                        --severity HIGH,CRITICAL \
                        --format table \
                        ${ECR_REPOSITORY}:${IMAGE_TAG}

                    # 4. Enforce Quality Gate: Fail build on fixable CRITICAL vulnerabilities (temporarily commented)
                    # trivy image \
                    #     --severity CRITICAL \
                    #     --ignore-unfixed \
                    #     --exit-code 1 \
                    #     ${ECR_REPOSITORY}:${IMAGE_TAG}
                        '''
            }
            post {
                always {
                    // Retain audit evidence on Jenkins build page even if scan fails
                    archiveArtifacts artifacts: 'trivy-report.json',
                                     allowEmptyArchive: true,
                                     fingerprint: true
                }
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

        stage('Push Docker Image to AWS ECR') {
            steps {
                echo "Authenticating Docker to ECR and pushing image to ${env.ECR_REGISTRY}..."
                sh '''
                    aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
                        docker login --username AWS --password-stdin ${ECR_REGISTRY}

                    docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}

                    docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                        '''
            }
        }

        stage('Publish Image Tag for Argo CD') {
            when {
                allOf {
                    branch 'main'
                    expression {
                        return sh(
                            script: 'aws eks describe-cluster --name lumora-ecommerce-prod --region us-east-1 --query "cluster.status" --output text 2>/dev/null | grep -q "ACTIVE"',
                            returnStatus: true
                        ) == 0
                    }
                }
            }
            steps {
                echo "Recording immutable image tag ${env.IMAGE_TAG} in k8s/kustomization.yml for Argo CD..."
                withCredentials([usernamePassword(
                    credentialsId: 'github-token',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_TOKEN'
                )]) {
                    sh '''
                        set -eu

                        # Pin newTag in Kustomize (Argo CD syncs path k8s from main).
                        python3 - <<'PY'
import os
import sys

path = "k8s/kustomization.yml"
tag = os.environ["IMAGE_TAG"]
with open(path, encoding="utf-8") as fh:
    lines = fh.readlines()

updated = []
found = False
for line in lines:
    if (not found) and line.lstrip().startswith("newTag:"):
        indent = line[: len(line) - len(line.lstrip())]
        updated.append(f'{indent}newTag: "{tag}"\n')
        found = True
    else:
        updated.append(line)

if not found:
    sys.exit("FATAL: could not find images.newTag in k8s/kustomization.yml")

with open(path, "w", encoding="utf-8", newline="\n") as fh:
    fh.writelines(updated)
print(f"Updated kustomization newTag -> {tag}")
PY

                        git config user.email "jenkins@lumora.local"
                        git config user.name "lumora-jenkins"
                        git add k8s/kustomization.yml

                        if git diff --cached --quiet; then
                            echo "Image tag already recorded in Git. Nothing to commit."
                            exit 0
                        fi

                        git commit -m "deploy: flask image ${IMAGE_TAG} [skip ci]"
                        git push "https://${GIT_USER}:${GIT_TOKEN}@github.com/Saranyaharish93/hv-ecommerce-devops.git" HEAD:main
                        echo "Published image tag commit for Argo CD sync."
                    '''
                }
            }
        }

        stage('Ensure Metrics Server') {
            when {
                expression {
                    return sh(
                        script: 'aws eks describe-cluster --name lumora-ecommerce-prod --region us-east-1 --query "cluster.status" --output text 2>/dev/null | grep -q "ACTIVE"',
                        returnStatus: true
                    ) == 0
                }
            }
            steps {
                echo 'Ensuring Metrics Server / Secrets Store CSI add-ons are present...'
                sh '''
                    chmod +x scripts/setup_metrics_server.sh
                    ./scripts/setup_metrics_server.sh
                '''
            }
        }

        stage('Verify Argo CD Rollout') {
            when {
                allOf {
                    branch 'main'
                    expression {
                        return sh(
                            script: 'aws eks describe-cluster --name lumora-ecommerce-prod --region us-east-1 --query "cluster.status" --output text 2>/dev/null | grep -q "ACTIVE"',
                            returnStatus: true
                        ) == 0
                    }
                }
            }
            steps {
                echo 'Waiting for Argo CD to sync the new image tag (read-only verification)...'
                sh '''
                    set -eu

                    EXPECTED_IMAGE="${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
                    echo "Expected image after Argo CD sync: ${EXPECTED_IMAGE}"

                    # Poll until the live Deployment matches the tag published to Git.
                    ATTEMPTS=36
                    SLEEP_SECS=10
                    for i in $(seq 1 "${ATTEMPTS}"); do
                        DEPLOYED_IMAGE=$(kubectl get deployment flask-app -n lumora-prod -o jsonpath='{.spec.template.spec.containers[0].image}')
                        echo "[${i}/${ATTEMPTS}] Live image: ${DEPLOYED_IMAGE}"
                        if [ "${DEPLOYED_IMAGE}" = "${EXPECTED_IMAGE}" ]; then
                            echo "Argo CD image sync observed."
                            break
                        fi
                        if [ "${i}" -eq "${ATTEMPTS}" ]; then
                            echo "FATAL: Timed out waiting for Argo CD to deploy ${EXPECTED_IMAGE}"
                            echo "Last observed image: ${DEPLOYED_IMAGE}"
                            exit 1
                        fi
                        sleep "${SLEEP_SECS}"
                    done

                    kubectl rollout status deployment/flask-app -n lumora-prod --timeout=180s

                    DEPLOYED_IMAGE=$(kubectl get deployment flask-app -n lumora-prod -o jsonpath='{.spec.template.spec.containers[0].image}')
                    if [ "${DEPLOYED_IMAGE}" != "${EXPECTED_IMAGE}" ]; then
                        echo "FATAL: Deployed image does not match expected build image."
                        echo "Expected: ${EXPECTED_IMAGE}"
                        echo "Actual:   ${DEPLOYED_IMAGE}"
                        exit 1
                    fi
                    echo "Image identity verification PASSED."

                    echo "Executing live HTTP health smoke test..."
                    kubectl exec -n lumora-prod deployment/flask-app -c flask-app -- python -c "import urllib.request; res = urllib.request.urlopen('http://localhost:5000/health'); assert res.getcode() == 200; print('Live Health Check: OK (HTTP 200)')"

                    kubectl get hpa -n lumora-prod
                '''
                script {
                    env.DEPLOYMENT_STATUS = 'DEPLOYED'
                }
            }
        }

        stage('Post-Deployment Health Check') {
            when {
                expression {
                    return sh(
                        script: 'aws eks describe-cluster --name lumora-ecommerce-prod --region us-east-1 --query "cluster.status" --output text 2>/dev/null | grep -q "ACTIVE"',
                        returnStatus: true
                    ) == 0
                }
            }
            steps {
                sh '''
                    set -eu

                    echo "Checking Flask application health in EKS..."

                    kubectl rollout status deployment/flask-app \
                      -n lumora-prod --timeout=180s

                    kubectl exec deployment/flask-app \
                      -n lumora-prod -- python -c '
import urllib.request
url = "http://flask-service.lumora-prod.svc.cluster.local/health"
with urllib.request.urlopen(url, timeout=15) as response:
    print("HTTP Status:", response.status)
    print("Response:", response.read().decode())
    assert response.status == 200, "Health check failed"
'

                    echo "Application health verification PASSED."
                '''
            }
        }

        stage('Deploy and Verify Monitoring') {
            when {
                expression {
                    return sh(
                        script: 'aws eks describe-cluster --name lumora-ecommerce-prod --region us-east-1 --query "cluster.status" --output text 2>/dev/null | grep -q "ACTIVE"',
                        returnStatus: true
                    ) == 0
                }
            }
            steps {
                echo 'Deploying and strictly validating Prometheus monitoring resources...'
                sh '''
                    set -eu

                    # 1. Enforce Prometheus Operator and CRD prerequisites (fail hard if absent)
                    echo "Validating Prometheus Operator CRDs..."
                    if ! kubectl get crd servicemonitors.monitoring.coreos.com >/dev/null 2>&1; then
                        echo "FATAL: ServiceMonitor CRD (servicemonitors.monitoring.coreos.com) missing! Monitoring verification failed."
                        exit 1
                    fi
                    if ! kubectl get crd prometheusrules.monitoring.coreos.com >/dev/null 2>&1; then
                        echo "FATAL: PrometheusRule CRD (prometheusrules.monitoring.coreos.com) missing! Monitoring verification failed."
                        exit 1
                    fi

                    # 2. Deploy ServiceMonitor and application alerting rules
                    echo "Deploying ServiceMonitor and alert rules..."
                    kubectl apply -f k8s/06-flask-servicemonitor.yml
                    kubectl apply -f monitoring/application-alerts.yaml

                    # 3. Confirm alert rules and ServiceMonitor custom resources are actively loaded
                    echo "Verifying loaded Prometheus resources in monitoring namespace..."
                    kubectl get prometheusrule lumora-application-alerts -n monitoring
                    kubectl get servicemonitor flask-app-monitor -n monitoring

                    # 4. Confirm Flask metrics target is UP and serving prometheus metrics
                    echo "Checking live Flask application metrics endpoint (/metrics)..."
                    kubectl exec -n lumora-prod deployment/flask-app -c flask-app -- python -c "
import urllib.request
with urllib.request.urlopen('http://localhost:5000/metrics', timeout=10) as res:
    assert res.getcode() == 200, 'Metrics endpoint returned non-200 status'
    body = res.read().decode('utf-8')
    assert 'flask_' in body or 'python_' in body or 'process_' in body or 'http_' in body, 'No prometheus metrics found'
    print('Flask Metrics Target Verification: PASSED (HTTP 200, metrics exported)')
"

                    # 5. Query live Prometheus API to verify Flask target is UP and alert rules are actively loaded
                    echo "Querying live Prometheus API for scrape target health and alert rule status..."
                    kubectl exec -n lumora-prod deployment/flask-app -c flask-app -- python -c "
import urllib.request
import json
import sys

prom_candidates = [
    'http://prometheus-operated.monitoring.svc.cluster.local:9090',
    'http://prometheus-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090',
    'http://prometheus.monitoring.svc.cluster.local:9090'
]

prom_url = None
for candidate in prom_candidates:
    try:
        with urllib.request.urlopen(f'{candidate}/api/v1/status/buildinfo', timeout=4) as res:
            if res.getcode() == 200:
                prom_url = candidate
                break
    except Exception:
        continue

if not prom_url:
    print('FATAL: Prometheus API is unreachable via internal cluster DNS!')
    sys.exit(1)

print(f'Connected to Prometheus API at: {prom_url}')

# Verify Flask target status is UP in Prometheus
with urllib.request.urlopen(f'{prom_url}/api/v1/targets', timeout=10) as res:
    data = json.loads(res.read().decode('utf-8'))
    active_targets = data.get('data', {}).get('activeTargets', [])
    flask_targets = [
        t for t in active_targets 
        if 'flask' in t.get('discoveredLabels', {}).get('__meta_kubernetes_service_name', '')
        or 'flask' in t.get('labels', {}).get('job', '')
        or 'flask' in t.get('scrapePool', '')
    ]
    if not flask_targets:
        print('FATAL: Flask metrics target not discovered by Prometheus!')
        sys.exit(1)
    
    up_targets = [t for t in flask_targets if t.get('health') == 'up']
    if not up_targets:
        current_health = [t.get('health') for t in flask_targets]
        print(f'FATAL: Flask metrics target is not UP! Current health: {current_health}')
        sys.exit(1)
    print(f'Prometheus Target Health: UP ({len(up_targets)} target(s) healthy)')

# Verify application alert rules are actively loaded in Prometheus engine
with urllib.request.urlopen(f'{prom_url}/api/v1/rules', timeout=10) as res:
    data = json.loads(res.read().decode('utf-8'))
    groups = data.get('data', {}).get('groups', [])
    lumora_groups = [g for g in groups if 'lumora' in g.get('name', '')]
    if not lumora_groups:
        print('FATAL: Lumora application alert rule group not found in active Prometheus engine!')
        sys.exit(1)
    
    loaded_rules = [r.get('name') for g in lumora_groups for r in g.get('rules', [])]
    print(f'Prometheus Rules Verification: PASSED (Loaded rules: {loaded_rules})')
"
                '''
    }
}

    }

post {
    always {
        echo "Pipeline execution completed with status: ${currentBuild.currentResult}. Deployment: ${env.DEPLOYMENT_STATUS ?: 'SKIPPED'}"
    }

    success {
        echo "Jenkins pipeline completed successfully! Deployment: ${env.DEPLOYMENT_STATUS ?: 'SKIPPED'}"

        script {
            try {
                def statusTitle = (env.DEPLOYMENT_STATUS == 'DEPLOYED') ? 'Deployment Successful' : 'Build Successful (Deployment Skipped)'
                emailext(
                    to: '${DEFAULT_RECIPIENTS}',
                    subject: "${env.DEPLOYMENT_STATUS == 'DEPLOYED' ? 'DEPLOYED' : 'SUCCESS'}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                    mimeType: 'text/html',
                    body: """
                        <h2>${statusTitle}</h2>
                        <p><b>Job Name:</b> ${env.JOB_NAME}</p>
                        <p><b>Build Number:</b> ${env.BUILD_NUMBER}</p>
                        <p><b>Deployment Status:</b> ${env.DEPLOYMENT_STATUS ?: 'SKIPPED'}</p>
                        <p><b>Pipeline URL:</b>
                            <a href="${env.BUILD_URL}">${env.BUILD_URL}</a>
                        </p>
                    """
                )
            } catch (Exception e) {
                echo "Notice: Email notification skipped or email-ext not configured: ${e.getMessage()}"
            }
        }
    }

    failure {
        echo 'Jenkins pipeline failed!'

        script {
            try {
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
            } catch (Exception e) {
                echo "Notice: Email notification skipped or email-ext not configured: ${e.getMessage()}"
            }
        }
    }

    cleanup {
        deleteDir()
    }
}

}
