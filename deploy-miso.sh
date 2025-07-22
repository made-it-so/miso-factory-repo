#!/bin/bash
set -e

# Set API keys (REPLACE PLACEHOLDERS)
export GEMINI_API_KEY="AIzaSyD3APrdkS5zmdrpNgV0TEoWPn5iKoHhD5A"
export JWT_SECRET_KEY="98ce897618b7199fc7c06727c6b6259a3ed3a2b7dfd39fdc"

# Stop and remove any old containers
sudo docker stop miso-orchestrator miso-python-agent miso-frontend || true
sudo docker rm -f miso-orchestrator miso-python-agent miso-frontend || true

# Launch new containers from pre-pulled images
sudo docker run -d --name miso-orchestrator --restart always --network miso-net -p 80:5001 -v /var/run/docker.sock:/var/run/docker.sock -e JWT_SECRET_KEY=$JWT_SECRET_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/orchestrator:latest
sudo docker run -d --name miso-python-agent --restart always --network miso-net -v /var/run/docker.sock:/var/run/docker.sock -e GEMINI_API_KEY=$GEMINI_API_KEY us-east4-docker.pkg.dev/miso-final-1234/miso-factory/python-agent:latest
sudo docker run -d --name miso-frontend --restart always --network miso-net -p 80:80 us-east4-docker.pkg.dev/miso-final-1234/miso-factory/frontend:latest

echo " "
echo "MISO Factory deployment complete. ✅"
