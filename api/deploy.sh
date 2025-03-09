#!/bin/bash

# Set variables
PROJECT_ID="tylers-platform"
REGION="us-central1"
REPO_NAME="flask-api-repo"
IMAGE_NAME="flask-api"
IMAGE_URI="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"
LOCAL_IMAGE="$IMAGE_NAME:local"   # local-only image tag
SERVICE_NAME="flask-api"

COMMAND=$1

function run_locally() {
  echo "🐳 Building Docker image for local use..."
  docker build -t $LOCAL_IMAGE .

  echo "🏠 Running container locally on port 8080..."
  docker run --rm -p 8080:8080 $LOCAL_IMAGE

  # Optional cleanup: remove local image after exit
  # docker rmi $LOCAL_IMAGE
}

function deploy_to_cloudrun() {
  echo "🚀 Starting Deployment Process for Cloud Run..."

  # 1️⃣ Authenticate Docker with GCP
  echo "🔑 Authenticating with Google Artifact Registry..."
  gcloud auth configure-docker $REGION-docker.pkg.dev

  # 2️⃣ Build the Docker Image (linux/amd64 for cloud run)
  echo "🐳 Building Docker image for Cloud Run..."
  docker build --platform linux/amd64 -t $IMAGE_URI .

  # 3️⃣ Push the Image to Google Artifact Registry
  echo "📤 Pushing Docker image to Artifact Registry..."
  docker push $IMAGE_URI

  # 4️⃣ Deploy to Cloud Run
  echo "🚀 Deploying Cloud Run service..."
  gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_URI \
    --region=$REGION \
    --platform=managed \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1

  # 5️⃣ Get the Cloud Run Service URL
  SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
    --region=$REGION --format='value(status.url)')

  echo "✅ Deployment Complete! 🚀"
  echo "🌍 Cloud Run Service is live at: $SERVICE_URL"

  # Cleanup: remove amd64 image from local system
  docker rmi $IMAGE_URI
}

case "$COMMAND" in
  local)
    run_locally
    ;;
  deploy)
    deploy_to_cloudrun
    ;;
  *)
    echo "Usage: $0 [local|deploy]"
    exit 1
    ;;
esac