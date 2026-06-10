# Azure Deployment

This Bicep template deploys the API to Azure Container Apps with:

- two warm replicas and autoscaling up to ten replicas
- a 20-request concurrency target per replica
- a user-assigned managed identity
- Log Analytics and Application Insights
- liveness and readiness probes

Build and push `app/Dockerfile` to your enterprise registry, then deploy:

```powershell
az deployment group create `
  --resource-group <resource-group> `
  --template-file infra/main.bicep `
  --parameters containerImage=<registry/image@sha256:digest> `
               containerRegistryName=<existing-acr-name> `
               foundryAgentEndpoint=<published-agent-application-endpoint> `
               entraClientId=<api-app-registration-client-id> `
               tenantId=<entra-tenant-id>
```

After deployment:

1. Grant the output managed identity **Azure AI User** on the published Agent Application.
2. Confirm the deployed Container Apps built-in Entra authentication accepts only the intended API audience.
3. Put Azure API Management or Front Door with WAF in front of the app for per-user quotas, tenant policy, and a stable enterprise hostname.
4. Run the load test and tune replica/concurrency limits against the actual model quota and observed workflow latency.

Do not treat `maxReplicas: 10` as a substitute for Foundry/model quota. Request quota before launch and set APIM throttling below the approved limit.

Microsoft references:

- [Container Apps authentication and authorization](https://learn.microsoft.com/en-us/azure/container-apps/authentication)
- [Managed identities in Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity)
- [Container Apps ARM/Bicep reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/2024-03-01/containerapps)
