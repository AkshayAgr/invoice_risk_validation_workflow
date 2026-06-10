# Demo Flow

## Demo Input

The user enters:

```text
INV-2026-014
```

## Workflow

1. Invoice Intake Agent extracts invoice fields.
2. Contract Matching Agent finds governing contract.
3. Amendment Resolution Agent applies latest amendment.
4. Purchase Order Matching Agent checks PO coverage.
5. Approval Email Verification Agent checks exception approvals.
6. SLA & Service Credit Agent calculates service credit.
7. Duplicate Invoice Detection Agent checks duplicate risk.
8. Final Decision Agent gives recommendation.
9. Executive Summary Agent converts JSON into business-friendly bullets.

## Best Demo Story

Use an invoice where:

- Invoice exists and is readable.
- Contract exists.
- Amendment reduced the service rate.
- PO matches but amount exceeds expected rate.
- Approval email allows a PO overage.
- SLA breach creates a credit.
- No duplicate is found.

Expected final decision:

```text
APPROVE_WITH_DEDUCTION
```
