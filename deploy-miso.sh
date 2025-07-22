#!/bin/bash
set -e

docker-credential-gcr configure-docker --registries=us-east4-docker.pkg.dev
docker network create miso-net || true

export GEMINI_API_KEY="PASTE_YOUR_GEMINI_API_KEY_HERE"
export JWT_SECRET_KEY="PASTE_YOUR_JWT_SECRET_KEY_HERE"

docker stop miso-orchestrator miso-python-agent miso-frontend miso-memory miso-redis || true
docker rm -f miso-orchestrator miso-python-agent miso-frontend miso-memory miso-redis || true

docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest
docker pull us-east4-docker.pkg.dev/miso-final-1234/miso-factory/memory-service:latest
docker pull redis:7.2-alpine

docker run -d --name miso-redis --restart always --network miso-net redis:7.2-alpine
docker run -d --name miso-memory --restart always --network miso-net us-east4-docker.pkg.dev/miso-final-1234/miso-factory/memory-service:latest
docker run -d --name miso-orchestrator --restart always --network miso-net -p 80:5001 -v /var/run/docker.sock:/var/run/docker.sock -e JWT_SECRET_KEY=$JWT_SECRET_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
docker run -d --name miso-python-agent --restart always --network miso-net -e GEMINI_API_KEY=$GEMINI_API_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
docker run -d --name miso-frontend --restart always --network miso-net -p 8080:80 us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo "MISO Factory 5-service deployment complete. ✅"
