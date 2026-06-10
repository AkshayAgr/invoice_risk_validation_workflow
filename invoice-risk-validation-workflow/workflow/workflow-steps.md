# Workflow Steps

## Full Sequential Flow

```text
Start
  ↓
Ask Invoice Number
  ↓
Input Guardrail Agent
  ↓
Invoice Intake Agent
  ↓
Contract Matching Agent
  ↓
Amendment Resolution Agent
  ↓
Purchase Order Matching Agent
  ↓
Approval Email Verification Agent
  ↓
SLA & Service Credit Agent
  ↓
Duplicate Invoice Detection Agent
  ↓
Final Invoice Risk & Decision Agent
  ↓
Executive Invoice Summary Agent
  ↓
Output Guardrail Agent
  ↓
End
```

## Recommended Build Order

1. Build Start → Invoice Intake Agent.
2. Add Contract Matching Agent.
3. Add Amendment Resolution Agent.
4. Add Purchase Order Matching Agent.
5. Add Approval Email Verification Agent.
6. Add SLA & Service Credit Agent.
7. Add Duplicate Invoice Detection Agent.
8. Add Final Decision Agent.
9. Add Executive Summary Agent.
10. Add guardrail nodes and if/else gates.
