#!/bin/bash
set -e

echo "Authenticating Docker..."
sudo docker-credential-gcr configure-docker --registries=us-east4-docker.pkg.dev

echo "Setting API keys (REPLACE PLACEHOLDERS)..."
export GEMINI_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
export JWT_SECRET_KEY="PASTE_YOUR_JWT_SECRET_KEY_HERE"

echo "Creating Docker network..."
sudo docker network create miso-net || true

echo "Stopping and removing any old containers..."
sudo docker stop miso-orchestrator miso-python-agent miso-frontend || true
sudo docker rm -f miso-orchestrator miso-python-agent miso-frontend || true

echo "Pulling latest images..."
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo "Launching new containers..."
sudo docker run -d --name miso-orchestrator --restart always --network miso-net -p 80:5001 -v /var/run/docker.sock:/var/run/docker.sock -e JWT_SECRET_KEY=$JWT_SECRET_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker run -d --name miso-python-agent --restart always --network miso-net -v /var/run/docker.sock:/var/run/docker.sock -e GEMINI_API_KEY=$GEMINI_API_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker run -d --name miso-frontend --restart always --network miso-net -p 8080:80 us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo " "
echo "MISO Factory deployment complete. ✅"
