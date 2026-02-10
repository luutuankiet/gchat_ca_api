#!/bin/bash
# Deploy Google Chat Connector to Cloud Run

set -e  # Exit on error

echo "======================================================"
echo "Deploying Google Chat Connector to Cloud Run"
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

if [ -z "$REASONING_ENGINE_ID" ]; then
    echo "Error: REASONING_ENGINE_ID not set"
    echo "This is the ID from the ca_api_agent deployment"
    echo "Run: export REASONING_ENGINE_ID=your-reasoning-engine-id"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  Project: $GOOGLE_CLOUD_PROJECT"
echo "  Location: $GOOGLE_CLOUD_LOCATION"
echo "  Reasoning Engine ID: $REASONING_ENGINE_ID"
echo ""

# Navigate to connector directory
cd "$(dirname "$0")/../gchat_connector"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI not found"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
gcloud config set project "$GOOGLE_CLOUD_PROJECT"

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable chat.googleapis.com

# Deploy to Cloud Run
echo ""
echo "Deploying connector to Cloud Run..."
echo "This may take 3-5 minutes..."

gcloud run deploy gchat-connector \
  --source . \
  --region="$GOOGLE_CLOUD_LOCATION" \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT" \
  --set-env-vars="GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION" \
  --set-env-vars="REASONING_ENGINE_ID=$REASONING_ENGINE_ID" \
  --max-instances=10 \
  --memory=512Mi \
  --timeout=300

echo ""
echo "======================================================"
echo "Deployment Complete!"
echo "======================================================"
echo ""
echo "IMPORTANT: Copy the Service URL from above"
echo "Example: https://gchat-connector-abc123-uc.a.run.app"
echo ""
echo "Next steps:"
echo "1. Go to Google Cloud Console > Google Chat API"
echo "2. Configure your Chat app with this URL"
echo "3. Publish the Chat app"
echo "4. Test in Google Chat!"
echo ""
