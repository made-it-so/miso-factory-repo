#!/bin/bash
set -e

# --- 1. CONFIGURATION (EDIT THESE VALUES) ---
export BILLING_ACCOUNT_ID=01B9B4-651864-D4F774
export GITHUB_REPO_URL="https://github.com/made-it-so/miso-factory-repo.git"

# --- 2. PROJECT CREATION & SETUP ---
echo "## Creating new project..."
export NEW_PROJECT_ID="miso-factory-$(date +%s)"
gcloud projects create $NEW_PROJECT_ID
gcloud config set project $NEW_PROJECT_ID

echo "## Linking billing account..."
gcloud beta billing projects link $NEW_PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID

echo "## Enabling all necessary APIs..."
gcloud services enable compute.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com iam.googleapis.com

# --- 3. SOURCE CODE CREATION ---
echo "## Creating local source code..."
mkdir -p miso-factory/orchestrator/src miso-factory/python-agent/src miso-factory/frontend/public
cd miso-factory

# (The script will contain the 'cat' commands to create all source files here)

# --- 4. GIT & REPOSITORY SETUP ---
echo "## Initializing Git and pushing to your repository..."
git init
git config --global init.defaultBranch main
git branch -m main
git config --global user.email "miso@factory.com"
git config --global user.name "MISO"
git add .
git commit -m "Initial commit of MISO Factory"
git remote add origin $GITHUB_REPO_URL
git push -u origin main || true

# --- 5. INFRASTRUCTURE PROVISIONING ---
echo "## Creating new VPC network and firewall rules..."
gcloud compute networks create miso-vpc --subnet-mode=auto
gcloud compute firewall-rules create allow-miso-all --network=miso-vpc --allow=tcp:22,tcp:80

echo "## Creating new VM instance..."
gcloud compute instances create miso-vm --zone=us-east4-c --machine-type=e2-standard-4 --image-family=cos-stable --image-project=cos-cloud --network=miso-vpc

echo " "
echo "--- MISO GENESIS PROTOCOL: PHASE 1 COMPLETE ---"
echo "New Project ID: $NEW_PROJECT_ID"
