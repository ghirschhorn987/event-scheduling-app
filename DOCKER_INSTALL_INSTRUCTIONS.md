# Manual Docker Installation and Deployment Instructions

## Step 1: Install Docker

Open a NEW terminal window (not the one I'm using) and run these commands:

```bash
# Download Docker installation script
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh

# Install Docker (will prompt for password)
sudo sh /tmp/get-docker.sh

# Add yourself to docker group
sudo usermod -aG docker $USER

# Activate docker group (so you don't need to log out)
newgrp docker
```

## Step 2: Deploy with Local Build

After Docker is installed and you've run `newgrp docker`, navigate to your project directory and run:

```bash
cd /home/ghirschhorn/dev/antigravity-projects/event-scheduling-app
./deploy_local.sh
```

This will:
1. Build the Docker image locally using your exact source code
2. Push it to Google Container Registry
3. Deploy it to Cloud Run

## Troubleshooting

If you get "permission denied" errors when running docker commands:
- Make sure you ran `newgrp docker`
- Or log out and log back in
- Or run commands with `sudo docker ...` (not recommended)

If the build fails, check:
- Docker is running: `docker ps`
- You're authenticated to GCP: `gcloud auth list`
