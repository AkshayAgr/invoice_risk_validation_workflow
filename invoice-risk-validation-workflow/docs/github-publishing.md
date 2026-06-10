# Publish to GitHub

Before the first push, confirm the secret scan and tests pass and review every synthetic document. Do not include a local `.env`, Azure export containing credentials, production traces, or real business evidence.

Recommended repository settings:

1. Start with a private enterprise repository while security and legal reviews are pending.
2. Protect `main`; require pull requests, CI, CodeQL, resolved conversations, and at least one owner approval.
3. Enable secret scanning, push protection, Dependabot alerts, and private vulnerability reporting.
4. Restrict GitHub Actions permissions to read-only by default and approve third-party actions.
5. Store deployment configuration in GitHub Environments and authenticate Actions to Azure using OIDC, never a long-lived client secret.
6. Add named code owners for the API, infrastructure, workflow prompts, and financial policy.
7. Publish only after the synthetic-data and licensing review is complete.

Foundry portal state is not automatically reproduced from this repository. Treat the versioned agent instructions, mappings, guardrails, schemas, and evaluation evidence as the reviewable source, and record the published agent version in each release.
