#!/bin/bash
set -e

# Load environment variables
echo "Loading environment variables..."
set -o allexport
source backend/.env
source frontend/.env.production
set +o allexport

# Configuration
PROJECT_ID="event-scheduler-app-486106"
SERVICE_NAME="event-scheduling-app"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
TIMESTAMP=$(date +%s)
IMAGE_TAG="${IMAGE_NAME}:${TIMESTAMP}"

echo "Building Docker image locally..."
echo "Image tag: ${IMAGE_TAG}"

# Build the Docker image locally with all necessary build args
docker build \
  --platform linux/amd64 \
  --build-arg CACHEBUST=${TIMESTAMP} \
  --build-arg VITE_SUPABASE_URL="${VITE_SUPABASE_URL}" \
  --build-arg VITE_SUPABASE_ANON_KEY="${VITE_SUPABASE_ANON_KEY}" \
  --build-arg VITE_USE_MOCK_AUTH="${VITE_USE_MOCK_AUTH:-false}" \
  -t ${IMAGE_TAG} \
  -t ${IMAGE_NAME}:latest \
  .

echo "Pushing image to Google Container Registry..."
docker push ${IMAGE_TAG}
docker push ${IMAGE_NAME}:latest

echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_TAG} \
  --platform managed \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --allow-unauthenticated

echo "Deployment Complete!"
echo "Service URL: https://event-scheduler-113221755789.us-central1.run.app"
