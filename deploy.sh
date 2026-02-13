#!/bin/bash
set -e

# 1. Load Environment Variables
# Safely load variables into environment
if [ -f backend/.env ]; then
    echo "Loading backend/.env..."
    set -o allexport
    source backend/.env
    set +o allexport
fi

if [ -f frontend/.env.production ]; then
    echo "Loading frontend/.env.production..."
    set -o allexport
    source frontend/.env.production
    set +o allexport
fi

# 2. Verify Critical Variables
REQUIRED_VARS=("SUPABASE_URL" "SUPABASE_SERVICE_ROLE_KEY" "VITE_SUPABASE_URL" "VITE_SUPABASE_ANON_KEY" "CRON_SECRET")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set. Please check your .env files."
        exit 1
    fi
done

PROJECT_ID="event-scheduler-app-486106"
REGION="us-central1"
SERVICE_NAME="event-scheduler"

echo "Deploying to Project: $PROJECT_ID"

# 3. Build & Submit to Container Registry (Cloud Build)
echo "Submitting build to Cloud Build..."
gcloud builds submit --config cloudbuild.yaml \
    --project $PROJECT_ID \
    --substitutions _VITE_SUPABASE_URL="$VITE_SUPABASE_URL",_VITE_SUPABASE_ANON_KEY="$VITE_SUPABASE_ANON_KEY",_VITE_USE_MOCK_AUTH="${VITE_USE_MOCK_AUTH:-false}",_SERVICE_NAME="$SERVICE_NAME" .

# 4. Deploy to Cloud Run
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --project $PROJECT_ID \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars SUPABASE_URL="$SUPABASE_URL" \
    --set-env-vars SUPABASE_SERVICE_ROLE_KEY="$SUPABASE_SERVICE_ROLE_KEY" \
    --set-env-vars USE_MOCK_AUTH="${USE_MOCK_AUTH:-false}" \
    --set-env-vars RESEND_API_KEY="$RESEND_API_KEY" \
    --set-env-vars CRON_SECRET="$CRON_SECRET"

echo "Deployment Complete!"
