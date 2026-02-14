#!/bin/bash
set -e

# Load environment variables
echo "Loading environment variables..."
set -o allexport
source backend/.env
source frontend/.env.production
set +o allexport

PROJECT_ID="event-scheduler-app-486106"
SERVICE_NAME="event-scheduler"
REGION="us-central1"

echo "Deploying to Project: ${PROJECT_ID}"
echo "Using fresh Cloud Build configuration..."

# Submit build using the new configuration file
gcloud builds submit \
  --config=cloudbuild-fresh.yaml \
  --substitutions=_VITE_SUPABASE_URL="${VITE_SUPABASE_URL}",_VITE_SUPABASE_ANON_KEY="${VITE_SUPABASE_ANON_KEY}",_VITE_USE_MOCK_AUTH="${VITE_USE_MOCK_AUTH:-false}",_SERVICE_NAME="${SERVICE_NAME}",_REGION="${REGION}" \
  --project=${PROJECT_ID}

echo "Deployment Complete!"
echo "Service URL: https://event-scheduler-113221755789.us-central1.run.app"
