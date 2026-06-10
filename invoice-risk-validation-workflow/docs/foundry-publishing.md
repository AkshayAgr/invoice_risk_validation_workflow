# Publish the Foundry Workflow

1. Recreate or update each workflow node from the versioned instructions in `agents/`, `workflow/variable-mapping.md`, and `workflow/guardrails.md`.
2. Attach Azure AI Search and other tools using managed identity. Grant the published agent identity the same least-privilege data-plane roles needed by the workflow.
3. Test the workflow against synthetic scenarios and the JSON schemas in `workflow/json-schemas/`.
4. Publish it as an **Agent Application** using the **Responses** protocol.
5. Copy the stable application endpoint ending in `/protocols/openai` into `FOUNDRY_AGENT_ENDPOINT`.
6. Grant the API's managed identity **Azure AI User** at the Agent Application scope.

The published Agent Application currently exposes a stateless Responses API. This service sends only the invoice number per request, which avoids sharing conversation state between enterprise users.

Treat portal changes as controlled releases: update the matching prompt/schema files in GitHub, review them through a pull request, publish a new agent version, evaluate it, and then promote it. Keep screenshots only as supporting evidence; they are not a reproducible workflow definition.

Microsoft references:

- [Publish agents in Microsoft Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-agent?view=foundry)
- [Invoke an Agent Application with the Responses API](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/publish-responses)
