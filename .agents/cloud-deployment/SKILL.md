---
name: Cloud Deployment & Containerization
description: Use these commands to containerize the application and deploy services to the cloud infrastructure.
---

**Allowed Commands:**
- `gcloud run deploy [SERVICE_NAME] --source . --region us-central1`: Deploy the current directory as a new revision to Google Cloud Run.
- `docker build -t [IMAGE_NAME] .`: Build the application container for local testing before deployment.
**Guardrails:** Always output the build logs to a temporary artifact file for review before initiating a cloud deployment.
