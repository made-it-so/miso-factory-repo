#!/bin/bash
set -e

docker-credential-gcr configure-docker --registries=us-east4-docker.pkg.dev
docker network create miso-net || true

export GEMINI_API_KEY=AIzaSyD3APrdkS5zmdrpNgV0TEoWPn5iKoHhD5A
export JWT_SECRET_KEY=98ce897618b7199fc7c06727c6b6259a3ed3a2b7dfd39fdc

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
