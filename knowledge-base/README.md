# Azure Architecture Review Knowledge Base

This folder contains curated, stable reference material for the Azure AI Foundry architecture-review agent and Azure AI Search index.

## Reference files

The `reference` folder contains individual Markdown files copied from the repository:

- `agent-review-instructions.md`: review rules and workflow boundaries.
- `azure-principles.md`: internal Azure design principles.
- `caf-validation-checklist.md`: Cloud Adoption Framework checklist.
- `waf-validation-checklist.md`: Azure Well-Architected Framework checklist.
- `architecture-review-template.md`: expected review sections.
- `shv-design-template.md`: solution-design structure.
- `workload-request-template.md`: workload request structure.
- `design-review-approval-flow.md`: Azure DevOps, Function, Search, Foundry, and approval flow.

## Upload guidance

Upload the contents of `reference` to the private Azure Blob Storage container used as the Azure AI Search data source.

Do not add the live Azure DevOps Wiki design here. The Wiki revision linked from the Azure Boards item is the authoritative current design and must be supplied directly by the Azure Function for each review.

Do not add secrets, access tokens, passwords, connection strings, `node_modules`, generated build output, or unapproved example designs.

When a source document changes, update its copy here before running the Azure AI Search indexer again.
