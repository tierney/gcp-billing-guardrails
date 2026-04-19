---
name: qa-testing
description: Tests the GCP billing kill switch by publishing Pub/Sub messages and reading Cloud Function logs to verify soft limit warnings and hard limit disconnections. Use when you need to verify the kill switch architecture is functioning.
---

# QA Tester Skill

You are responsible for validating that the automated Google Cloud billing kill switch is functioning correctly, ignoring safe thresholds, and successfully executing on critical thresholds.

## Core Capabilities

### 1. Test Soft Limits (Safe thresholds)
Publish a payload simulating a cost *below* the budget limit to ensure the function ignores it. 
First, determine the `BUDGET_AMOUNT` from the project's `.env` file, and calculate 50% and 90% of it. Then use those values in the `costAmount` and `budgetAmount` fields:
```zsh
gcloud pubsub topics publish budget-alerts --message='{"costAmount": [CALCULATED_50_PERCENT], "budgetAmount": [BUDGET_AMOUNT]}'
```
Then, verify the logs show the event was ignored:
```zsh
gcloud functions logs read stop-billing-fn --region=us-central1 --limit=10
```
Expected: `Budget threshold not yet reached. No action taken.`

### 2. Test Hard Limits (Kill Switch execution)
Publish a payload simulating a cost *above* the budget limit.
Calculate a value that is at least 100% of the `BUDGET_AMOUNT` and use it:
```zsh
gcloud pubsub topics publish budget-alerts --message='{"costAmount": [CALCULATED_101_PERCENT], "budgetAmount": [BUDGET_AMOUNT]}'
```
Then, verify the logs show the event was executed:
```zsh
gcloud functions logs read stop-billing-fn --region=us-central1 --limit=10
```
Expected: `Budget exceeded: 21/20. Disabling billing...` followed by a success message.

### 3. Verify Disconnection
After a hard limit test, always verify the project is actually disconnected from billing:
```zsh
gcloud billing projects describe $PROJECT_ID
```
Expected: `billingEnabled: false`.

*Important: Always inform the human or the `billing-admin` agent when you execute a Hard Limit test, as the project will need to be repaired/re-linked.*
