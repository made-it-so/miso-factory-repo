#!/bin/bash
set -e

# Authenticate and set keys
docker-credential-gcr configure-docker --registries=us-east4-docker.pkg.dev
export GEMINI_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
export JWT_SECRET_KEY="PASTE_YOUR_JWT_SECRET_KEY_HERE"

# Stop, remove, pull all images
sudo docker stop miso-orchestrator miso-python-agent miso-frontend || true
sudo docker rm -f miso-orchestrator miso-python-agent miso-frontend || true
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

# Launch containers with corrected ports
# Orchestrator no longer needs a public port
sudo docker run -d --name miso-orchestrator --restart always --network miso-net -v /var/run/docker.sock:/var/run/docker.sock -e JWT_SECRET_KEY=$JWT_SECRET_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
# Agent is unchanged
sudo docker run -d --name miso-python-agent --restart always --network miso-net -v /var/run/docker.sock:/var/run/docker.sock -e GEMINI_API_KEY=$GEMINI_API_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
# Frontend now uses the standard port 80
sudo docker run -d --name miso-frontend --restart always --network miso-net -p 80:80 us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo "MISO Factory deployment complete on standard port. ✅"
