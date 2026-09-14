# Azure Architecture Copilot

## Overview

The Azure Architecture Copilot is a governed architecture-review workflow built around existing Azure DevOps and Microsoft Foundry resources. A designer updates the existing Azure DevOps Wiki design page, then creates an Azure Boards review item containing the Wiki link. That Board event triggers an Azure Function, which retrieves and normalizes the design and sends it to a new architecture-review agent in the existing Azure AI Foundry project. The Function publishes structured findings back to the Wiki and Board. A human architecture approver must approve the work item before implementation can start.

## Features

- **Request Validation**: Validate workload requests against CAF and WAF to ensure compliance with best practices.
- **Documentation**: Generate thorough documentation in both Markdown and HTML formats, including templates for requests and architecture reviews.
- **Architecture Diagrams**: Create visual representations of Azure workloads using Mermaid diagrams for better understanding and communication.
- **Automated Review Flow**: Connect the existing Azure DevOps Wiki and Boards to an Azure Function and a new review agent in the existing Azure AI Foundry project.

## Project Structure

The project is organized into several key directories:

- **.github**: Contains copilot instructions for using the tool effectively.
- **docs**: Houses documentation files in both HTML and Markdown formats, as well as architecture diagrams.
- **templates**: Includes various templates for validation checklists and workload requests.
- **src/styles**: Contains stylesheets, including Tailwind CSS configurations.
- **docs/markdown/design-review-approval-flow.md**: Defines the target Azure DevOps, Function, Foundry, approval, and implementation flow.
- **docs/diagrams/design-review-approval-flow.mmd**: Mermaid architecture diagram for the target flow.
- **function-app/**: Python Azure Function orchestrator for Board events, Wiki retrieval, Search grounding, Foundry invocation, and Board-only findings updates.

## Getting Started

To get started with the Azure Architecture Copilot, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd azure-architecture-copilot
   ```

2. Install the necessary dependencies:
   ```
   npm install
   ```

3. Review the copilot instructions located in `.github/copilot-instructions.md` for guidance on analyzing and implementing Azure workloads.

4. Use the templates in the `templates` directory to document workload requests and architecture reviews.

5. Read [docs/markdown/design-review-approval-flow.md](docs/markdown/design-review-approval-flow.md) for the target integration and approval lifecycle.

6. Generate documentation by navigating to the `docs` directory and using the provided HTML and Markdown files.

## Target review lifecycle

```text
Existing Azure DevOps Wiki page updated by designer
   -> Designer creates Azure Boards review item with Wiki link
   -> Board service-hook event
   -> Azure Function retrieves and normalizes the design
   -> Azure AI Foundry agent reviews CAF, WAF, security, cost, governance, and operations
   -> Function writes findings to the Board item only
   -> Architect manually updates the Wiki design
   -> Human approval or remediation
   -> Implementation gate
   -> Post-deployment validation
```

The agent recommends a decision; it does not approve designs or deploy Azure resources.

## Function orchestrator

The initial Function implementation is in [function-app/README.md](function-app/README.md). It expects an authenticated Azure Boards event containing a work-item ID and Wiki URL. It reads the exact Wiki revision, queries the stable Azure AI Search guidance index, invokes `architecture-review-agent`, validates the JSON response, and writes the findings to the Board item only. It never edits the Wiki.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.