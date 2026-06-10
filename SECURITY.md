# Security Policy

## Reporting

Do not open a public issue for a suspected vulnerability. Report it privately through the GitHub repository's **Security > Advisories > New draft security advisory** flow.

## Data Handling

This public repository contains synthetic data only. Never commit production invoices, contracts, emails, personal data, access tokens, connection strings, or exported traces containing document content.

Production deployments must use Microsoft Entra ID, Azure RBAC, managed identities, private networking where required by policy, and least-privilege access to the Agent Application, Search, and Storage resources.
