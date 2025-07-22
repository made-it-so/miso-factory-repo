#!/bin/bash
set -e

# Read keys from command-line arguments
export GEMINI_API_KEY="$1"
export JWT_SECRET_KEY="$2"

# Authenticate and run services
docker-credential-gcr configure-docker --registries=us-east4-docker.pkg.dev
sudo docker network create miso-net || true
sudo docker stop miso-orchestrator miso-python-agent miso-frontend || true
sudo docker rm -f miso-orchestrator miso-python-agent miso-frontend || true
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest
sudo docker run -d --name miso-orchestrator --restart always --network miso-net -p 80:5001 -v /var/run/docker.sock:/var/run/docker.sock -e JWT_SECRET_KEY=$JWT_SECRET_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker run -d --name miso-python-agent --restart always --network miso-net -v /var/run/docker.sock:/var/run/docker.sock -e GEMINI_API_KEY=$GEMINI_API_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker run -d --name miso-frontend --restart always --network miso-net -p 8080:80 us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo "MISO Factory deployment with injected secrets is complete. ✅"
