# Billing Setup Verification

Run these commands to confirm the kill switch is fully wired up.

## 1. Verify Budget Exists and is Linked to Pub/Sub
```bash
source .env
./gcloud-agent.sh billing budgets list --billing-account=$ACCOUNT_ID
```
**Look for:**
- `notificationsRule.pubsubTopic` pointing to `projects/$PROJECT_ID/topics/budget-alerts`
- Three `thresholdRules` at 0.5, 0.9, and 1.0

## 2. Verify Cloud Function is Deployed and Active
```bash
./gcloud-agent.sh functions describe stop-billing-fn --region=us-central1
```
**Look for:** `state: ACTIVE` and `GOOGLE_CLOUD_PROJECT` set in `environmentVariables`.

## 3. Verify Project Billing is Enabled
```bash
./gcloud-agent.sh billing projects describe $PROJECT_ID
```
**Look for:** `billingEnabled: true`
