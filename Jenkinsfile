pipeline {
  agent any
  environment {
    IMAGE_NAME = 'hv-ecommerce'
    IMAGE_TAG = "${BUILD_NUMBER}"
    K8S_NAMESPACE = 'hv-ecommerce'
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Test') {
      steps {
        sh 'python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt && pytest -q'
      }
    }
    stage('Build Image') {
      steps { sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .' }
    }
    stage('Scan Image') {
      steps { sh 'trivy image --exit-code 0 --severity HIGH,CRITICAL $IMAGE_NAME:$IMAGE_TAG' }
    }
    stage('Push Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
          sh 'docker tag $IMAGE_NAME:$IMAGE_TAG $DOCKER_USER/$IMAGE_NAME:$IMAGE_TAG'
          sh 'docker push $DOCKER_USER/$IMAGE_NAME:$IMAGE_TAG'
        }
      }
    }
    stage('Deploy to Kubernetes') {
      steps {
        withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
          sh 'kubectl apply -f k8s/namespace.yaml'
          sh 'kubectl apply -f k8s/mongo.yaml'
          sh 'sed "s|IMAGE_PLACEHOLDER|$DOCKER_USER/$IMAGE_NAME:$IMAGE_TAG|g" k8s/app.yaml | kubectl apply -f -'
          sh 'kubectl apply -f k8s/hpa.yaml'
          sh 'kubectl rollout status deployment/hv-ecommerce -n $K8S_NAMESPACE --timeout=180s'
        }
      }
    }
  }
  post { always { junit allowEmptyResults: true, testResults: 'reports/*.xml' } }
}
