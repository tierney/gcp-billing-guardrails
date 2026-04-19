# Pub/Sub Testing Reference

Publishing a message to the `budget-alerts` topic simulates a billing alert.
The `costAmount` and `budgetAmount` fields are read by the Cloud Function to decide whether to disable billing.

## Message Format
```json
{
  "costAmount": 10.00,
  "budgetAmount": 20.00
}
```

## Publish Command
```bash
source .env
./gcloud-agent.sh pubsub topics publish budget-alerts \
  --message="{\"costAmount\": [VALUE], \"budgetAmount\": $BUDGET_AMOUNT}"
```

## Threshold Guide
Given `BUDGET_AMOUNT=20.00`:

| Test | costAmount | Expected Behavior |
|------|-----------|-------------------|
| 50% soft limit | 10.00 | No action taken |
| 90% soft limit | 18.00 | No action taken |
| 100%+ hard limit | 21.00 | Billing disabled |
