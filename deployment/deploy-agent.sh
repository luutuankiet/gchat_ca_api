#!/bin/bash
# Deploy CA API Agent to Vertex AI Agent Engine

set -e  # Exit on error

echo "======================================================"
echo "Deploying CA API Agent to Vertex AI Agent Engine"
echo "======================================================"

# Check required environment variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "Error: GOOGLE_CLOUD_PROJECT not set"
    echo "Run: export GOOGLE_CLOUD_PROJECT=your-project-id"
    exit 1
fi

if [ -z "$GOOGLE_CLOUD_LOCATION" ]; then
    echo "Warning: GOOGLE_CLOUD_LOCATION not set, using default: us-central1"
    export GOOGLE_CLOUD_LOCATION="us-central1"
fi

if [ -z "$CA_AGENT_ID" ]; then
    echo "Error: CA_AGENT_ID not set"
    echo "This is your Conversational Analytics agent ID from BigQuery/Looker"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  Project: $GOOGLE_CLOUD_PROJECT"
echo "  Location: $GOOGLE_CLOUD_LOCATION"
echo "  CA Agent ID: $CA_AGENT_ID"
echo ""

# Navigate to agent directory
cd "$(dirname "$0")/../ca_api_agent"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Authenticate
echo "Authenticating with Google Cloud..."
gcloud auth application-default login

# Set project
gcloud config set project "$GOOGLE_CLOUD_PROJECT"

# Enable required APIs
echo ""
echo "Enabling required APIs..."
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

# Deploy the agent
echo ""
echo "Deploying agent to Vertex AI..."
echo "This may take 5-10 minutes..."

gcloud vertex-ai reasoning-engines create \
  --agent-file=agent.py \
  --requirements-file=requirements.txt \
  --region="$GOOGLE_CLOUD_LOCATION" \
  --display-name="ca-api-agent" \
  --env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,CA_AGENT_ID=$CA_AGENT_ID"

echo ""
echo "======================================================"
echo "Deployment Complete!"
echo "======================================================"
echo ""
echo "IMPORTANT: Copy the Reasoning Engine ID from above"
echo "Format: projects/.../locations/.../reasoningEngines/[ID]"
echo "                                                     ^^^^"
echo ""
echo "You'll need this ID for deploying the gchat_connector."
echo "Save it as: export REASONING_ENGINE_ID=<ID>"
echo ""
