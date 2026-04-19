# GCP Billing Kill Switch

An automated, serverless kill switch to immediately disable billing on your Google Cloud Project if your spend exceeds a hard limit, preventing surprise bills.

## Architecture
- **Google Cloud Budget**: Monitors project spend.
- **Pub/Sub Topic**: Receives alerts from the Budget when thresholds are crossed.
- **Cloud Function**: Subscribed to the topic. Compares cost vs budget and unlinks the billing account if the hard cap is reached.

## Setup Instructions
1. Run `./setup.sh` to deploy the Cloud Function, enable necessary APIs, and set up the Pub/Sub topic.
2. **Crucial Step**: Go to Google Cloud Console -> Billing -> Account Management. Add the Compute Engine default service account (e.g. `123456789-compute@developer.gserviceaccount.com`) as a **Billing Account Administrator**. The function *cannot* disable billing without this permission!

## Testing the Kill Switch
You can manually test the system by publishing dummy messages to the Pub/Sub topic via the CLI.

### Testing Soft Limits (Warnings)
Simulate hitting the 50% or 90% soft limits. The Cloud Function should wake up, but ignore the message because the cost is below the budget.
*(Example: if your `BUDGET_AMOUNT` is `20.00`, test with `10.00` and `18.00`)*
```zsh
gcloud pubsub topics publish budget-alerts --message='{"costAmount": [50_PERCENT_OF_BUDGET], "budgetAmount": [YOUR_BUDGET_AMOUNT]}'
```
Check the logs:
```zsh
gcloud functions logs read stop-billing-fn --region=us-central1 --limit=5
```
*Expected output:* `Budget threshold not yet reached. No action taken.`

### Testing the Hard Cap (Kill Switch)
Simulate hitting the 100%+ hard limit.
*(Example: if your `BUDGET_AMOUNT` is `20.00`, test with `21.00`)*
```zsh
gcloud pubsub topics publish budget-alerts --message='{"costAmount": [OVER_100_PERCENT_OF_BUDGET], "budgetAmount": [YOUR_BUDGET_AMOUNT]}'
```
Wait 15 seconds, then verify the project billing is disconnected:
```zsh
gcloud billing projects describe YOUR_PROJECT_ID
```
*Expected output:* `billingEnabled: false` and no billing account listed.

## Recovery & Repair
If the kill switch trips (or you tested it), all billable services will be paused. To turn your project back on, you must re-link your billing account.
```zsh
gcloud billing projects link YOUR_PROJECT_ID --billing-account=YOUR_ACCOUNT_ID
```
*Note: If your actual spend is still at or above the hard cap, Google will send another alert shortly after you re-link, and the kill switch will trip again. To prevent an endless loop, either increase your budget amount or wait until the next calendar month for your spend to reset.*
