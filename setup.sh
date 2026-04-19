#!/bin/zsh

# --- Configuration ---
# Load variables from global ~/.env or local .env file
if [ -f ~/.env ]; then
    source ~/.env
fi

if [ -f .env ]; then
    source .env
fi

if [[ -z "$PROJECT_ID" ]] || [[ -z "$ACCOUNT_ID" ]] || [[ -z "$BUDGET_AMOUNT" ]]; then
    echo "ERROR: PROJECT_ID, ACCOUNT_ID, and BUDGET_AMOUNT must be set in ~/.env or the local .env file."
    echo "Please copy .env.example to .env and fill in your details if you aren't using ~/.env."
    exit 1
fi
# ---------------------

echo "Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

echo "Enabling required APIs..."
gcloud services enable \
    billingbudgets.googleapis.com \
    cloudbilling.googleapis.com \
    pubsub.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    eventarc.googleapis.com

echo "Creating Pub/Sub topic..."
gcloud pubsub topics create budget-alerts

echo "Deploying Cloud Function..."
gcloud functions deploy stop-billing-fn \
    --runtime nodejs22 \
    --trigger-topic budget-alerts \
    --entry-point stopBilling \
    --region us-central1 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --source .

echo "Creating Budget..."
gcloud billing budgets create \
    --billing-account=$ACCOUNT_ID \
    --display-name="${BUDGET_AMOUNT}-USD-Hard-Cap" \
    --budget-amount=$BUDGET_AMOUNT \
    --threshold-rule=percent=0.5 \
    --threshold-rule=percent=0.9 \
    --threshold-rule=percent=1.0 \
    --notifications-rule-pubsub-topic=projects/$PROJECT_ID/topics/budget-alerts

echo ""
echo '========================================='
echo 'Deployment initiated!'
echo 'IMPORTANT: Don'"'"'t forget Step 5!'
echo "1. Find the service account email generated during deployment (e.g., $PROJECT_ID@appspot.gserviceaccount.com)."
echo '2. Go to Google Cloud Console > Billing > Account Management.'
echo '3. Add that email as a Billing Account Administrator.'
echo '========================================='
