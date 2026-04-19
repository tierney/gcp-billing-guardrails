#!/bin/zsh
# gcloud wrapper for agent use
# Ensures gcloud is always found regardless of PATH environment

GCLOUD_BIN="/Users/tierney/google-cloud-sdk/bin/gcloud"

if [ ! -f "$GCLOUD_BIN" ]; then
  echo "ERROR: gcloud not found at $GCLOUD_BIN"
  exit 1
fi

exec "$GCLOUD_BIN" "$@"
