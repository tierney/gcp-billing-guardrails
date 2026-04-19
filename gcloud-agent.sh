#!/bin/bash
# gcloud-agent.sh
# Portable gcloud wrapper for agent use.
# Discovers the gcloud binary across common installation locations
# so this works for any user on any machine.

# 1. Try the shell's PATH first (works in interactive shells)
GCLOUD_BIN=$(which gcloud 2>/dev/null)

# 2. If not in PATH, search common installation locations
if [ -z "$GCLOUD_BIN" ]; then
  for candidate in \
    "$HOME/google-cloud-sdk/bin/gcloud" \
    "/usr/local/google-cloud-sdk/bin/gcloud" \
    "/opt/homebrew/share/google-cloud-sdk/bin/gcloud" \
    "/usr/lib/google-cloud-sdk/bin/gcloud" \
    "/snap/google-cloud-sdk/current/bin/gcloud"; do
    if [ -f "$candidate" ]; then
      GCLOUD_BIN="$candidate"
      break
    fi
  done
fi

# 3. Fail clearly if still not found
if [ -z "$GCLOUD_BIN" ]; then
  echo "ERROR: gcloud CLI not found. Please install the Google Cloud SDK:"
  echo "  https://cloud.google.com/sdk/docs/install"
  exit 1
fi

exec "$GCLOUD_BIN" "$@"
