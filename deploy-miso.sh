#!/bin/bash
set -e

# Tell all subsequent sudo commands to use the config file from the default user's home
export DOCKER_CONFIG=$HOME/.docker

# Set API keys (REPLACE PLACEHOLDERS)
echo "Setting API keys..."
export GEMINI_API_KEY=AIzaSyD3APrdkS5zmdrpNgV0TEoWPn5iKoHhD5A
export JWT_SECRET_KEY=98ce897618b7199fc7c06727c6b6259a3ed3a2b7dfd39fdc

echo "Pulling latest images..."
sudo -E docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo -E docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo -E docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo "Stopping and removing any old containers..."
sudo -E docker stop miso-orchestrator miso-python-agent miso-frontend || true
sudo -E docker rm -f miso-orchestrator miso-python-agent miso-frontend || true

echo "Launching new containers..."
sudo -E docker run -d --name miso-orchestrator --restart always --network miso-net -p 80:5001 -v /var/run/docker.sock:/var/run/docker.sock -e JWT_SECRET_KEY=$JWT_SECRET_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo -E docker run -d --name miso-python-agent --restart always --network miso-net -v /var/run/docker.sock:/var/run/docker.sock -e GEMINI_API_KEY=$GEMINI_API_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo -E docker run -d --name miso-frontend --restart always --network miso-net -p 8080:80 us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo " "
echo "MISO Factory deployment complete. ✅"
