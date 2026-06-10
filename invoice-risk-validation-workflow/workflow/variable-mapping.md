# Workflow Variable Mapping

| Node | Output Variable |
|---|---|
| Ask Invoice Number | invoice_input |
| Input Guardrail Agent | input_guardrail_result |
| Invoice Intake Agent | invoice_intake_result |
| Contract Matching Agent | contract_matching_result |
| Amendment Resolution Agent | amendment_resolution_result |
| Purchase Order Matching Agent | purchase_order_matching_result |
| Approval Email Verification Agent | approval_verification_result |
| SLA & Service Credit Agent | sla_service_credit_result |
| Duplicate Invoice Detection Agent | duplicate_detection_result |
| Final Invoice Risk & Decision Agent | final_invoice_decision_result |
| Executive Invoice Summary Agent | executive_summary_result |
| Output Guardrail Agent | safe_final_summary |

## Passing Multiple Inputs to a Node

Example for Amendment Resolution Agent:

```text
Invoice Intake Result:
{Text(Local.invoice_intake_result)}

Contract Matching Result:
{Text(Local.contract_matching_result)}
```

Example for Purchase Order Matching Agent:

```text
Invoice Intake Result:
{Text(Local.invoice_intake_result)}

Contract Matching Result:
{Text(Local.contract_matching_result)}

Amendment Resolution Result:
{Text(Local.amendment_resolution_result)}
```
