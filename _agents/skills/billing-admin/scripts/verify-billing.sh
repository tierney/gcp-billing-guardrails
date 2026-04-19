#!/bin/bash
# verify-billing.sh — Check that billing is enabled on the project
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
GCLOUD="$REPO_ROOT/gcloud-agent.sh"

source "$REPO_ROOT/.env" 2>/dev/null || source ~/.env

echo "Checking billing status for $PROJECT_ID..."
"$GCLOUD" billing projects describe "$PROJECT_ID"
