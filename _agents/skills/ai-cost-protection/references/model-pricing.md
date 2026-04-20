# AI Model Pricing Reference

> ⚠️ Pricing is approximate and subject to change.
> Always verify at: https://cloud.google.com/vertex-ai/pricing

## Video Generation

| Model | SKU | Cost/Second | 6s Video | 8s Video |
|---|---|---|---|---|
| Veo 2.0 | `Veo 2 Video Generation` | ~$0.35/s | ~$2.10 | ~$2.80 |
| Veo 3.1 Lite | `Veo 3.1 Lite Video Generation` | ~$0.25/s | ~$1.50 | ~$2.00 |

## VeoCallGuard Constants

Update `guardrails/veo_call_guard.py` when pricing changes:

```python
VEO2_COST_PER_SECOND_USD    = 0.35
VEO31_LITE_COST_PER_SECOND_USD = 0.25
```

## Safe Session Budgets

| Use Case | max_calls | max_cost_usd | Model |
|---|---|---|---|
| Local testing | 3 | $5.00 | Veo 3.1 Lite |
| Development iteration | 5 | $10.00 | Veo 2.0 |
| Staging review | 10 | $20.00 | Veo 2.0 |
| Production run | Set explicitly | Set from business budget | Either |

## API Quota Caps (GCP Console)

Set hard per-day request limits to complement VeoCallGuard:

1. Go to: https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/quotas
2. Filter: `Generate Video`
3. Set `Requests per day` to match your `max_calls` setting
