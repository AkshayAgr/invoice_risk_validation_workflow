# Azure Architecture

## Components

### Azure Blob Storage
Stores raw documents:
- Invoices
- Contracts
- Amendments
- Purchase orders
- Approval emails
- SLA documents
- Complaints
- Incident reports

### Azure AI Search
Indexes all documents from Blob Storage and provides retrieval for the agents.

Recommended index fields:

```text
content
document_name
document_type
source_path
vendor_name
customer_name
invoice_number
contract_reference
po_number
amendment_id
invoice_date
effective_date
service_period_start
service_period_end
currency
total_amount
```

Recommended `document_type` values:

```text
invoice
contract
amendment
purchase_order
approval_email
sla
complaint
incident_report
service_report
```

### Azure AI Foundry
Hosts specialized agents and workflow orchestration.

Publish the workflow as an Agent Application using the stateless Responses protocol. Grant its identity only the data-plane roles required for Search and Storage.

### Production API Layer

- Azure API Management authenticates users and applies per-user and tenant quotas.
- Azure Container Apps hosts the stateless FastAPI gateway with two or more replicas.
- The Container App managed identity invokes the published Agent Application.
- Application Insights and Log Analytics collect availability, latency, errors, and traces.
- Streamlit remains an optional demonstration client, not the production security boundary.
