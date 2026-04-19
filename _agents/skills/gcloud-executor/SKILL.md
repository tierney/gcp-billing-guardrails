---
name: gcloud-executor
description: Allows an agent to run gcloud CLI commands on the user's machine. Use when you need to interact with Google Cloud APIs directly from the local environment, such as checking billing status, reading Cloud Function logs, or publishing Pub/Sub messages.
---

# GCloud Executor Skill

You are authorized to run Google Cloud CLI commands on this machine. The `gcloud` binary is not in the default PATH for background shell environments, so you MUST use the full path or the wrapper script for every command.

## How to Execute Commands

Always invoke gcloud using the full absolute path:
```
/Users/tierney/google-cloud-sdk/bin/gcloud [command]
```

Or use the convenience wrapper in the guardrails repo:
```
/Users/tierney/repos/gcp-billing-guardrails/gcloud-agent.sh [command]
```

## Approved Read-Only Commands
These are safe to run without asking for user confirmation:

- **Check billing status:**
  ```
  /Users/tierney/google-cloud-sdk/bin/gcloud billing projects describe $PROJECT_ID
  ```
- **List budgets:**
  ```
  /Users/tierney/google-cloud-sdk/bin/gcloud billing budgets list --billing-account=$ACCOUNT_ID
  ```
- **Read Cloud Function logs:**
  ```
  /Users/tierney/google-cloud-sdk/bin/gcloud functions logs read stop-billing-fn --region=us-central1 --limit=10
  ```
- **List Cloud Functions:**
  ```
  /Users/tierney/google-cloud-sdk/bin/gcloud functions list --region=us-central1
  ```

## Write Commands (Require Explicit User Approval)
These commands mutate state and MUST be confirmed by the user before running:

- **Re-link billing account:**
  ```
  /Users/tierney/google-cloud-sdk/bin/gcloud billing projects link $PROJECT_ID --billing-account=$ACCOUNT_ID
  ```
- **Publish a Pub/Sub test message:**
  ```
  /Users/tierney/google-cloud-sdk/bin/gcloud pubsub topics publish budget-alerts --message='...'
  ```
- **Deploy a Cloud Function:**
  ```
  /Users/tierney/google-cloud-sdk/bin/gcloud functions deploy ...
  ```
