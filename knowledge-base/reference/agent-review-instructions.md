# Copilot Instructions for Azure Architecture

## Overview
This document provides a set of instructions for utilizing the Copilot feature to analyze, design, and implement Azure workloads based on the requirements provided by business units. The process is guided by the Cloud Adoption Framework (CAF) and the Azure Well-Architected Framework (WAF).

## Steps to Follow

### 1. Requirement Gathering
- Collaborate with business units to gather detailed requirements for the Azure workload.
- Document the requirements clearly to ensure all aspects are covered.
- Use the existing Azure DevOps organization, project, and Wiki as the authoritative source. The designer updates the existing design page, then creates an Azure Boards architecture-review work item containing the Wiki link.

### 2. Validation Against Frameworks
- **Cloud Adoption Framework (CAF) Validation:**
  - Use the [CAF Validation Checklist](../templates/caf-validation-checklist.md) to ensure that the request aligns with the best practices outlined in the CAF.
  
- **Azure Well-Architected Framework (WAF) Validation:**
  - Refer to the [WAF Validation Checklist](../templates/waf-validation-checklist.md) to validate the request against the principles of the WAF.

### 3. Architecture Design
- Create a high-level architecture diagram using the Mermaid syntax. Refer to the [Architecture Template](../docs/diagrams/architecture-template.mmd) for guidance.
- Ensure that the architecture adheres to the principles of scalability, reliability, security, and cost optimization.
- Keep implementation behind the review and approval gate. Do not treat an agent recommendation as human approval.

### 4. Documentation
- Document the architecture and workload request using the provided templates:
  - Use the [Workload Request Template](../templates/workload-request-template.md) to format the request documentation.
  - Create a detailed architecture review using the [Architecture Review Template](../templates/architecture-review-template.md).

### 5. Automated Review Integration
- Azure DevOps Wiki and Boards are the source systems for the draft, review state, ownership, and approval evidence.
- An authenticated Azure Boards work-item event invokes the orchestration layer, currently modeled as an Azure Function. A Wiki edit alone does not trigger a review.
- The Function retrieves the exact Wiki revision, linked attachments, and Board work item; normalizes them into a bounded review package; and invokes the Azure AI Foundry review agent.
- The Azure AI Foundry project already exists; create the architecture-review agent inside that project.
- The Function validates the structured agent response and updates the Board with findings and links. It must not modify the Wiki design page.
- The architect manually updates the existing Wiki design in response to findings and resubmits a Board item with the new Wiki revision for re-review.
- Store review snapshots and non-sensitive audit metadata with correlation IDs. Never send secrets or access tokens to the agent.

### 6. Output Formats
- Generate documentation in both Markdown and HTML formats:
  - Markdown: Use the [Markdown Index](../docs/markdown/index.md) for the main documentation structure.
  - HTML: Use the [HTML Index](../docs/html/index.html) for web presentation.

### 7. Review and Approval
- Share the documented request and architecture with stakeholders for review.
- Incorporate feedback and finalize the documentation.
- Require an explicit human approval state in Azure Boards before implementation.
- Designs with Critical findings cannot be approved.

### 8. Implementation
- Once approved, proceed with the implementation of the Azure workload as per the documented architecture.

## Conclusion
Following these instructions will help ensure that Azure workloads are designed and implemented effectively, aligning with organizational requirements and best practices.