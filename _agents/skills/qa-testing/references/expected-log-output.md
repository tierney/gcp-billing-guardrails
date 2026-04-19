# Expected Cloud Function Log Output

After publishing a Pub/Sub message, wait 10-15 seconds then read logs:
```bash
./gcloud-agent.sh functions logs read stop-billing-fn --region=us-central1 --limit=10
```

## Soft Limit Test (cost < budget)
```
Checking budget for [PROJECT_ID]: Current Cost $10 / Budget $20
Budget threshold not yet reached. No action taken.
```
✅ This is correct. No action was taken.

## Hard Limit Test (cost >= budget)
```
Checking budget for [PROJECT_ID]: Current Cost $21 / Budget $20
Budget exceeded: 21/20. Disabling billing for [PROJECT_ID]...
Success: Billing disabled and project capped.
```
✅ This is correct. Billing has been disabled.

## Error: PERMISSION_DENIED
```
Error: 7 PERMISSION_DENIED: User does not have permission on project to disable billing
```
❌ The service account hasn't been granted Billing Account Administrator.
**Fix**: Go to GCP Console → Billing → Account Management → Add the Compute Engine default service account as Billing Account Administrator.

## Error: costAmount is $0 / project is "undefined"
```
Checking budget for undefined: Current Cost $0 / Budget $20
```
❌ The `GOOGLE_CLOUD_PROJECT` environment variable was not set on the function.
**Fix**: Re-deploy the function: `./setup.sh`
