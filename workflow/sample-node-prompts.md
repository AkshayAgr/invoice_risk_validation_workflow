# Sample Node Prompts

## Start / Ask Question Message

```text
Please enter the invoice number you want to validate.
```

Save response as:

```text
invoice_input
```

## Invoice Intake Agent Node

```text
Find and extract this invoice from the knowledge base.

Invoice identifier:
{Text(Local.invoice_input)}

Return only a compact valid JSON object.
Do not return markdown.
Do not validate against contract, PO, amendment, SLA, approval emails, or duplicates.
```

## Contract Matching Agent Node

```text
You are running Step 2 of the invoice validation workflow.

Use this invoice intake result:

{Text(Local.invoice_intake_result)}

Find the governing contract from the connected knowledge base.

Return only a compact valid JSON object.
Do not return markdown.
```

## Amendment Resolution Agent Node

```text
You are running Step 3 of the invoice validation workflow.

Invoice Intake Result:
{Text(Local.invoice_intake_result)}

Contract Matching Result:
{Text(Local.contract_matching_result)}

Find applicable amendments from the connected knowledge base.

Return only a compact valid JSON object.
Do not return markdown.
```

## Purchase Order Matching Agent Node

```text
You are running Step 4 of the invoice validation workflow.

Invoice Intake Result:
{Text(Local.invoice_intake_result)}

Contract Matching Result:
{Text(Local.contract_matching_result)}

Amendment Resolution Result:
{Text(Local.amendment_resolution_result)}

Find and compare the matching purchase order.

Return only a compact valid JSON object.
Do not return markdown.
```

## Final Decision Agent Node

```text
Make the final invoice decision using these upstream outputs.

Invoice Intake Result:
{Text(Local.invoice_intake_result)}

Contract Result:
{Text(Local.contract_matching_result)}

Amendment Result:
{Text(Local.amendment_resolution_result)}

PO Result:
{Text(Local.purchase_order_matching_result)}

Approval Result:
{Text(Local.approval_verification_result)}

SLA Result:
{Text(Local.sla_service_credit_result)}

Duplicate Result:
{Text(Local.duplicate_detection_result)}

Return only valid JSON.
```

## Executive Summary Agent Node

```text
Create an executive business summary from this decision output:

{Text(Local.final_invoice_decision_result)}

Return concise markdown bullet points.
Do not change the decision, risk score, payable amount, or deduction.
```
