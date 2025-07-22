#!/bin/bash
set -e

export DOCKER_CONFIG=/home/kyle/.docker
docker-credential-gcr configure-docker --registries=us-east4-docker.pkg.dev

export GEMINI_API_KEY="$1"
export JWT_SECRET_KEY="$2"

sudo docker network create miso-net || true

sudo docker stop miso-orchestrator miso-python-agent miso-frontend miso-memory miso-redis || true
sudo docker rm -f miso-orchestrator miso-python-agent miso-frontend miso-memory miso-redis || true

sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest
sudo docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/memory-service:latest
sudo docker pull redis:7.2-alpine

sudo docker run -d --name miso-redis --restart always --network miso-net redis:7.2-alpine
sudo docker run -d --name miso-memory --restart always --network miso-net --name miso-memory us-east4-docker.pkg.dev/miso-final-1234/miso-factory/memory-service:latest
sudo docker run -d --name miso-orchestrator --restart always --network miso-net -p 80:5001 -v /var/run/docker.sock:/var/run/docker.sock -e JWT_SECRET_KEY=$JWT_SECRET_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker run -d --name miso-python-agent --restart always --network miso-net -e GEMINI_API_KEY=$GEMINI_API_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker run -d --name miso-frontend --restart always --network miso-net -p 8080:80 us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo "MISO Factory 5-service deployment complete. ✅"
