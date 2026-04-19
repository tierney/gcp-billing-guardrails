#!/bin/bash
# test-hard-limit.sh — Simulate an over-budget billing alert (WILL disable billing)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
GCLOUD="$REPO_ROOT/gcloud-agent.sh"

source "$REPO_ROOT/.env" 2>/dev/null || source ~/.env

# Calculate 101% of the budget amount to trigger the kill switch
OVER_LIMIT=$(echo "$BUDGET_AMOUNT * 1.01" | bc)

echo "⚠️  WARNING: This will disable billing for $PROJECT_ID!"
echo "Simulating hard cap: costAmount=$OVER_LIMIT, budgetAmount=$BUDGET_AMOUNT"
"$GCLOUD" pubsub topics publish budget-alerts \
  --message="{\"costAmount\": $OVER_LIMIT, \"budgetAmount\": $BUDGET_AMOUNT}"

echo "Message published. Waiting 15 seconds for function to process..."
sleep 15

echo "Reading logs..."
"$GCLOUD" functions logs read stop-billing-fn --region=us-central1 --limit=5

echo ""
echo "Verifying billing is now disabled..."
"$GCLOUD" billing projects describe "$PROJECT_ID"

echo ""
echo "⚠️  Run scripts/repair-billing.sh in billing-admin to re-enable billing."
