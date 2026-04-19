#!/bin/bash
# repair-billing.sh — Re-link billing account to the project
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
GCLOUD="$REPO_ROOT/gcloud-agent.sh"

source "$REPO_ROOT/.env" 2>/dev/null || source ~/.env

echo "Re-linking billing account $ACCOUNT_ID to $PROJECT_ID..."
"$GCLOUD" billing projects link "$PROJECT_ID" --billing-account="$ACCOUNT_ID"

echo "Verifying..."
"$GCLOUD" billing projects describe "$PROJECT_ID"
