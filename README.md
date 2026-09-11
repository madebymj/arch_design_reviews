# Azure Architecture Copilot

## Overview

The Azure Architecture Copilot is a comprehensive tool designed to assist architects in analyzing, designing, and implementing workloads on Microsoft Azure. This project aims to streamline the process of gathering requirements from business units and ensuring that all requests adhere to best practices outlined in the Cloud Adoption Framework (CAF) and the Azure Well-Architected Framework (WAF).

## Features

- **Request Validation**: Validate workload requests against CAF and WAF to ensure compliance with best practices.
- **Documentation**: Generate thorough documentation in both Markdown and HTML formats, including templates for requests and architecture reviews.
- **Architecture Diagrams**: Create visual representations of Azure workloads using Mermaid diagrams for better understanding and communication.

## Project Structure

The project is organized into several key directories:

- **.github**: Contains copilot instructions for using the tool effectively.
- **docs**: Houses documentation files in both HTML and Markdown formats, as well as architecture diagrams.
- **templates**: Includes various templates for validation checklists and workload requests.
- **src/styles**: Contains stylesheets, including Tailwind CSS configurations.

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

4. Use the templates in the `templates` directory to document your workload requests and architecture reviews.

5. Generate documentation by navigating to the `docs` directory and using the provided HTML and Markdown files.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.