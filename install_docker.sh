#!/bin/bash
set -e

echo "Installing Docker..."

# Download Docker installation script
curl -fsSL https://get.docker.com -o /tmp/get-docker.sh

# Run the installation script
sudo sh /tmp/get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER

echo ""
echo "Docker installation complete!"
echo ""
echo "IMPORTANT: You need to log out and log back in for group changes to take effect."
echo "After logging back in, run: ./deploy_local.sh"
echo ""
echo "Alternatively, you can run this command to start a new shell with docker group:"
echo "  newgrp docker"
echo "  ./deploy_local.sh"
