#!/bin/bash
set -e
set -x

# Configuration
SERVICE_NAME="event-scheduler"
REGION="us-central1"
JOB_NAME="trigger-event-scheduling"
SCHEDULE="*/5 * * * *"  # Every 5 minutes
URI="https://event-scheduler-113221755789.us-central1.run.app/api/schedule" # Check URL after deployment

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
if gcloud scheduler jobs describe $JOB_NAME --location $REGION --quiet > /dev/null 2>&1; then
    echo "Updating existing job..."
    gcloud scheduler jobs update http $JOB_NAME \
        --location $REGION \
        --schedule "$SCHEDULE" \
        --uri "$URI" \
        --http-method POST \
        --update-headers "X-Cron-Secret=$CRON_SECRET" \
        --attempt-deadline 30s \
        --quiet
else
    echo "Creating new job..."
    gcloud scheduler jobs create http $JOB_NAME \
        --location $REGION \
        --schedule "$SCHEDULE" \
        --uri "$URI" \
        --http-method POST \
        --headers "X-Cron-Secret=$CRON_SECRET" \
        --attempt-deadline 30s \
        --quiet
fi

echo "Scheduler Job Configured Successfully!"
