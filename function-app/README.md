# Architecture Review Function

This Azure Functions app receives an authenticated Azure Boards event, reads the linked Azure DevOps Wiki revision, retrieves stable guidance from Azure AI Search, invokes the architecture-review agent in Microsoft Foundry, validates the JSON response, and writes findings to the Board item only.

The Function never edits the Wiki design page.

## Local setup

1. Copy `local.settings.example.json` to `local.settings.json`.
2. Provide local-only values. Do not commit `local.settings.json`.
3. Create a Python virtual environment and install `requirements.txt`.
4. Start the Function host with Azure Functions Core Tools.

## Expected Board event

The handler accepts a JSON payload containing a work-item ID and a Wiki URL. The exact Azure DevOps service-hook payload varies by event version, so the parser accepts common field names and rejects requests without both values.

Example:

```json
{
  "id": "event-123",
  "resource": {
    "id": 185148,
    "fields": {
      "System.Description": "Review design: https://dev.azure.com/org/project/_wiki/wikis/wiki/design"
    }
  }
}
```

## Azure configuration

Use the Function managed identity in Azure. Store Azure DevOps credentials in Key Vault if the chosen Azure DevOps integration cannot use Entra authentication. Grant the identity only the required permissions for reading the Wiki, reading/updating the Board item, querying Search, and invoking the Foundry agent.
