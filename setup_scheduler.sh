#!/bin/bash
set -e

# Configuration
SERVICE_NAME="event-scheduler"
REGION="us-central1"
JOB_NAME="trigger-event-scheduling"
SCHEDULE="*/15 * * * *"  # Every 15 minutes
URI="https://event-scheduler-486106.run.app/api/schedule" # Check URL after deployment

# Ensure CRON_SECRET is available
if [ -z "$CRON_SECRET" ]; then
    if [ -f backend/.env ]; then
        export $(grep -v '^#' backend/.env | xargs)
    fi
fi

if [ -z "$CRON_SECRET" ]; then
    echo "Error: CRON_SECRET is not set."
    exit 1
fi

echo "Creating/Updating Cloud Scheduler Job: $JOB_NAME"

# Check if job exists
if gcloud scheduler jobs describe $JOB_NAME --location $REGION > /dev/null 2>&1; then
    echo "Updating existing job..."
    gcloud scheduler jobs update http $JOB_NAME \
        --location $REGION \
        --schedule "$SCHEDULE" \
        --uri "$URI" \
        --http-method POST \
        --headers "X-Cron-Secret=$CRON_SECRET" \
        --attempt-deadline 30s
else
    echo "Creating new job..."
    gcloud scheduler jobs create http $JOB_NAME \
        --location $REGION \
        --schedule "$SCHEDULE" \
        --uri "$URI" \
        --http-method POST \
        --headers "X-Cron-Secret=$CRON_SECRET" \
        --attempt-deadline 30s
fi

echo "Scheduler Job Configured Successfully!"
