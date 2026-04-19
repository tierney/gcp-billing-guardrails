---
name: gcloud-executor
description: Allows an agent to run gcloud CLI commands on the user's machine. Use when you need to interact with Google Cloud APIs directly from the local environment, such as checking billing status, reading Cloud Function logs, or publishing Pub/Sub messages.
---

# GCloud Executor Skill

You are authorized to run Google Cloud CLI commands on this machine.

## How to Execute Commands

Always use the portable wrapper script at the root of this repository. It automatically discovers the `gcloud` binary on any machine, regardless of where the SDK is installed or who the user is:

```
./gcloud-agent.sh [command]
```

If you need an absolute path to the wrapper, resolve it relative to the repository root (e.g. find the repo with `git rev-parse --show-toplevel`).

## Approved Read-Only Commands
These are safe to run without asking for user confirmation:

- **Check billing status:**
  ```
  ./gcloud-agent.sh billing projects describe $PROJECT_ID
  ```
- **List budgets:**
  ```
  ./gcloud-agent.sh billing budgets list --billing-account=$ACCOUNT_ID
  ```
- **Read Cloud Function logs:**
  ```
  ./gcloud-agent.sh functions logs read stop-billing-fn --region=us-central1 --limit=10
  ```
- **List Cloud Functions:**
  ```
  ./gcloud-agent.sh functions list --region=us-central1
  ```

## Write Commands (Require Explicit User Approval)
These commands mutate state and MUST be confirmed by the user before running:

- **Re-link billing account:**
  ```
  ./gcloud-agent.sh billing projects link $PROJECT_ID --billing-account=$ACCOUNT_ID
  ```
- **Publish a Pub/Sub test message:**
  ```
  ./gcloud-agent.sh pubsub topics publish budget-alerts --message='...'
  ```
- **Deploy a Cloud Function:**
  ```
  ./gcloud-agent.sh functions deploy ...
  ```

## Loading Project Variables
Before running any command, source the project `.env` to populate `$PROJECT_ID`, `$ACCOUNT_ID`, and `$BUDGET_AMOUNT`:
```
source .env
```
