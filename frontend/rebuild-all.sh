#!/bin/bash
set -e
echo "--- Building python-agent ---"
cd ~/miso-final-deployment/python-agent && gcloud builds submit .
echo "--- Building orchestrator ---"
cd ~/miso-final-deployment/orchestrator && gcloud builds submit .
echo "--- Building frontend ---"
cd ~/miso-final-deployment/frontend && gcloud builds submit .
echo "--- All builds complete ---"
