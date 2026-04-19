#!/bin/bash
# test-soft-limit.sh — Simulate a sub-threshold billing alert (no billing impact)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
GCLOUD="$REPO_ROOT/gcloud-agent.sh"

source "$REPO_ROOT/.env" 2>/dev/null || source ~/.env

# Calculate 50% of the budget amount
SOFT_LIMIT=$(echo "$BUDGET_AMOUNT * 0.5" | bc)

echo "Simulating 50% soft limit: costAmount=$SOFT_LIMIT, budgetAmount=$BUDGET_AMOUNT"
"$GCLOUD" pubsub topics publish budget-alerts \
  --message="{\"costAmount\": $SOFT_LIMIT, \"budgetAmount\": $BUDGET_AMOUNT}"

echo "Message published. Waiting 15 seconds for function to process..."
sleep 15

echo "Reading logs..."
"$GCLOUD" functions logs read stop-billing-fn --region=us-central1 --limit=5
