# Production Readiness for 100 Concurrent Users

## Capacity Model

The supplied Container Apps template starts with two replicas, targets 20 active HTTP requests per replica, and can scale to ten replicas. This provides application-tier headroom for 100 concurrent users, but end-to-end capacity is controlled by workflow latency and the quotas of the Foundry model, Azure AI Search, and dependent services.

Before launch, run a staged load test at 25, 50, 75, and 100 concurrent users. Record p50/p95/p99 latency, error rate, throttling, token usage, model quota, Search latency, and replica count. The release gate should be based on your business SLO; a reasonable starting point is less than 1% server errors and no sustained 429 responses at the approved peak.

```powershell
pip install -r tests/load/requirements.txt
locust -f tests/load/locustfile.py --host https://<api-host> --users 100 --spawn-rate 5
```

## Required Launch Controls

- Publish the Foundry workflow as an Agent Application using the stateless Responses protocol.
- Grant the API managed identity **Azure AI User** only on that Agent Application.
- Require Entra authentication at Container Apps or API Management.
- Use API Management quotas/rate limits per user and tenant.
- Request sufficient model and Search quota before load testing.
- Use private endpoints and disable public network access where enterprise policy requires it.
- Keep at least two replicas across normal operation and use deployment revisions for rollback.
- Configure alerts for p95 latency, 5xx, 429, replica saturation, availability, and cost anomalies.
- Redact invoice content from logs and restrict access to traces because they may contain customer data.
- Create a human approval path for all payment recommendations. The workflow must never execute payment.

## Reliability and Recovery

The API is stateless and retries transient Foundry failures with jitter. Scale-out is bounded to avoid overwhelming Foundry. Configure an APIM timeout consistent with the measured workflow p99, and consider an asynchronous queue plus status endpoint if workflows regularly exceed interactive request limits.

Define RTO/RPO, deploy infrastructure from source, back up workflow configuration and Search index definitions, and test rollback plus regional recovery. The supplied template is single-region; regulated or mission-critical use requires a separately tested multi-region design.

## Release Checklist

- CI, CodeQL, dependency review, and container scanning pass.
- Agent prompts and schemas are reviewed and versioned.
- Synthetic evaluation set meets agreed accuracy and false-positive thresholds.
- Security threat model and privacy review are approved.
- Load test passes at 100 concurrent users with quota headroom.
- Runbooks, ownership, on-call alerts, and rollback are tested.
