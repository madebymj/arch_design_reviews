# Architecture Review Function

This Azure Functions app receives an authenticated Azure Boards event, reads the complete linked Azure DevOps Wiki revision, and sends that design to the architecture-review agent in Microsoft Foundry. The agent retrieves targeted guidance through its configured Azure AI Search knowledge tool and returns findings and recommendations. The Function validates the JSON response and writes readable findings to the Board item only.

The Function never edits the Wiki design page.

## Local setup

1. Copy `local.settings.example.json` to `local.settings.json`.
2. Provide local-only values. Do not commit `local.settings.json`.
3. Create a Python virtual environment and install `requirements.txt`.
4. Start the Function host with Azure Functions Core Tools.

## Expected Board event

The handler accepts a `workitem.updated` payload containing a work-item ID, a Wiki URL, and a newly added tag matching `REVIEW_TRIGGER_TAG`. The parser ignores other tag changes and rejects Wiki projects that are not listed in `AZURE_DEVOPS_ALLOWED_PROJECTS`.

Example:

```json
{
  "id": "event-123",
  "resource": {
  "workItemId": 185148,
  "fields": {
    "System.Tags": {
      "oldValue": "cloud",
      "newValue": "cloud; design review"
    }
  },
  "revision": {
    "id": 185148,
    "fields": {
      "System.Description": "Review design: https://dev.azure.com/org/project/_wiki/wikis/wiki/design"
    }
  }
}
```

## Azure configuration

For multiple projects, set `AZURE_DEVOPS_ALLOWED_PROJECTS` to a comma-separated allowlist, for example `test-project,NL_HQ_T_Cloud_CoE`. The Wiki URL determines which approved project is used for both Wiki retrieval and Board writeback. Set `REVIEW_TRIGGER_TAG=design review`.

In each approved Azure DevOps project, create a **Work item updated** service hook with **Tag = design review** and **Field = Tags**. The Function processes only an event where `design review` is absent from `oldValue` and present in `newValue`. Tag removals and unrelated tag edits return HTTP `200` with `status: ignored`, so Azure DevOps records a successful webhook delivery rather than an error.

Use the Function managed identity in Azure. Store Azure DevOps credentials in Key Vault if the chosen Azure DevOps integration cannot use Entra authentication. The Azure DevOps PAT or service identity must have Wiki read and work-item read/write permissions in every approved project. Grant the Function identity only the required permissions for writing configured snapshots and invoking the Foundry agent. Grant Search permissions to the Foundry project identity used by the agent's configured knowledge tool.
