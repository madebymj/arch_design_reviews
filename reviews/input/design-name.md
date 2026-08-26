[[_TOC_]]

# Introduction
This document outlines the high-level architecture of the AI-Enabled Robotic Process Automation (RPA) application hosted on Microsoft Azure. The solution leverages Azure App Service deployed within a private network to enhance security, Azure Virtual Machines to host the Playwright MCP Server, and Azure AI Foundry with the Claude Sonnet model to provide advanced AI capabilities. The application is exposed externally through a centralized Azure API Management solution, ensuring secure, controlled, and governed access to the platform and its services.

## In-scope of this document
| Nr. | Description |
| --- | --- |
| IS001 | Design of the infrastructure architecture for **AI Enabled Robotics Process Automation** in the SHVE Azure environment, covering onlye Development environment for now. |
| IS002 | All IT components required to run this solution within the organization’s IT environment. |
| IS003 | Deploy new dedicated Subscription with new Azure Landing Zone for the Development environment following SHV global standards, security policies, and governance controls. |
| IS004 | Deployment of Azure resources such as Azure Virtual Networks, Subnets, Azure App Service, Azure Virtual Machine and Private Endpoints within the new landing zones. |
| IS005 | Creation and configuration of Private Endpoints and supporting network resources for all Azure resources. |
| IS006 | Configuration of Virtual Network integration for Azure App Service to enable secure internal communication. |

## Out of Scope of this document
| Nr. | Description |
| --- | --- |
| OOS001 | Code Deployment, operation, and lifecycle management of Azure App Service. |
| OOS002 | Integration and configuration of third-party tools. |
| OOS003 | APIM integration will be handled by the Integration team. |
| OOS004 | MCP deployment will be carried out by the application team. The CCoE team will only provide the Windows-based virtual machine. |
| OOS005 | Security and compliance activities related to application data at the business layer, beyond the Azure platform and services deployed by the CCoE team. |
| OOS006 | Enterprise-wide Identity and Access Management beyond the defined RBAC scope. |
| OOS007 | Any topics not explicitly defined in the _In Scope_ section of this document. |

# Business Drivers and Success Factors

| Business Driver(s) | Description |
| --- | --- |
| Intelligent Process Automation and Operational Efficiency | Enable the automation of complex, repetitive business processes using AI-driven decision-making and robotic process automation, reducing manual effort, improving productivity, and accelerating process execution across the organization. |

| Critical Success Factor(s) | Description |
| --- | --- |
| Secure, Reliable, and Scalable AI Platform | Ensure the solution delivers enterprise-grade security through private network deployment, provides high availability and scalability on Azure, and enables accurate AI-powered automation through seamless integration with Azure AI Foundry, Claude Sonnet, and the Playwright MCP Server. |

# Requirements

## Business Requirements
Business requirements represent business objectives stated by the customer. Statements of goals, objectives, and outcomes that describe why a change has been initiated. They can apply to the whole of an enterprise, a business area, or a specific initiative.

| Reference ID | Statement | Rationale | HLD Reference |
| --- | --- | --- | --- |
| BSRQ001 | Provide secure external exposure of AI Enabled Robotics Process Automation via APIM & Application Gateway. | Ensures controlled, secure, and centralized access to the application by acting as a single entry point, enabling traffic filtering, SSL termination, and protection of backend services from direct internet exposure. | N/A |
| BSRQ001 | Deploy the Azure infrastructure to host the **AI Enabled Robotics Process Automation** application and all dependent services within the new subscription, using a dedicated new Resource Group and Landing Zone. | Ensures the application and its dependencies are hosted in a secure environment with proper resource isolation and platform support for reliable operation. | N/A |
| BSRQ003 | Ensure network connectivity, isolation, and compliance for all deployed resources. | Maintain enterprise security standards, enforce private endpoints, NSG/UDR policies. | N/A |

## Stakeholder Requirements
Stakeholder requirements represent the requirements of individual stakeholders. Describe the needs of stakeholders that must be met in order to achieve the business requirements.

| Reference ID | Statement | Rationale | HLD Reference |
| --- | --- | --- | --- |
| STRQ001 | The CCoE must provision new dedicated Subscription, Landing Zones, Azure App Service along with all supporting resources for the Development environment. | Ensures compliance with SHV Energy’s landing zone architecture and governance framework. | N/A |

## Solution Requirements
Features and characteristics expected of developed software application represent solution requirements. Describe the capabilities and qualities of a solution that meets the stakeholder requirements. They provide the appropriate level of detail to allow for the development and implementation of the solution.

### Functional Requirements
Functional requirements are requirements are the expected features of the system. 

| Reference ID | Statement | Rationale | HLD Reference |
| --- | --- | --- | --- |
| FNRQ001 | Provision the AI Enabled Robotics Process Automation application in the new Azure subscription. | Ensures the application is deployed using a standardized, scalable, and cloud-native App Service platform aligned with organizational architecture standards. | N/A |
| FNRQ002 | Deploy an Azure Apps Service along with all required network components in the new dedicated Subscription and Landing zone. | Establishes a secure, isolated, and governed runtime environment aligned with SHV Energy landing zone standards, enabling controlled networking, scalability, and operational consistency. | N/A |
| FNRQ003 | Apply centralized governance, policies, and guardrails defined by the CCoE for all environments. | Ensures consistent compliance, security posture, cost control, and operational discipline across all environments. | N/A |
| FNRQ005 | Use the centralized APIM and Application Gateway to expose Azure App Service to external reciever. | Provides a secure and scalable entry point for external traffic, enabling features such as SSL termination, request routing, and web application firewall protection while preventing direct exposure of the App Service to the internet. | N/A |

### Non-Functional Requirements
Non-Functional requirements: Non-functional requirements are the requirements which are related to the behavior of the system. 

| Reference ID | Statement | Rationale | HLD Reference |
| --- | --- | --- | --- |
| NFRQ001 | Confidentiality Integrity Availability (CIA) Rating: <br/> - C = 3 <br/> - I = 3 <br/> - A = 3 | This is a core input for designing solutions based on business criticality. | N/A. |
| NFRQ002 | Return Point Objective: <br/> - RPO = 24 Hours <br/><br/>  | Core metric that defines the amount of data change loss acceptable to the business | N/A. |
| NFRQ003 | Return Time Objective:<br/>- RTO = 24 hours | Core Metric that defines the maximum allow time that the service is not available to the business outside of regular maintenance. | N/A. |
| NFRQ004 | Solution must be aligned with the Cloud Principles: <br/> - [Link.](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles) | Solutions must be aligned with core principles on how they are to be designed and deployed on the Cloud Platform | N/A. |
| NFRQ005 | Single Azure region needed | Geo-redundancy not required | N/A |

## Transition Requirements
The transition requirements are the requirements needed to implement the software application successfully. Describe the capabilities that the solution must have and the conditions the solution must meet to facilitate transition from the current state to the future state, but which are not needed once the change is complete. They are differentiated from other requirements types because they are of a temporary nature.

| Reference ID | Statement | Rationale| HLD Reference |
|--|--|--|--|
| TRRQ001 | N/A. | N/A. | N/A. |

### Design Decisions

| Reference ID | Statement | Rationale | Implications |
| --- | --- | --- | --- |
| SOLDEC001 | Use Windows based Azure App Service as the primary hosting platform for the AI Enabled Robotics Process Automation application. | Provides a fully managed, scalable, and container-native platform with reduced operational overhead. | Requires containerization of the application and adherence to Azure Container Apps platform constraints. |
| SOLDEC002 | Deploy the application within a new subscription. | Isolates the AI Enabled Robotics Process Automation solution from the corporate environment, providing independent governance, billing, and security boundaries, reducing risk of accidental impact on other resources. | Requires separate management of subscription-level policies, access controls, and monitoring; may increase operational overhead for cross-subscription integration and reporting. |
| SOLDEC003 | Provision dedicated Resource Groups and Landing Zones. | Ensures application and environment isolation and alignment with organizational governance and security standards. | Increases infrastructure footprint while improving separation of concerns and risk mitigation. |
| SOLDEC004 | Centralized APIM `NL-HQ-SHVE-APIM-DEV` and Application Gateway will be used to expose the Azure App Service. | Provides a unified, secure entry point for integrations and enables controlled access to Azure App Service. | Depends on proper routing, SSL configuration, and firewall rules; centralizes traffic management and monitoring. |
| SOLDEC005 | Apply centralized governance, policies, and guardrails defined by the CCoE across the environment. | Ensures consistent configuration, compliance, and lifecycle control across Azure deployments. | Requires continuous governance updates and alignment with enterprise policy frameworks; may affect deployment timelines if policy exceptions are needed. |
| SOLDEC006 | Ensure Azure App Service use private endpoints and remain inaccessible over the public internet. | Protects data-in-transit and aligns with SHV Energy’s network security standards. | Depends on DNS and Private Link configuration supported by the hub-spoke network. |
| SOLDEC007 | Deployment region will be Sweden Central. | Aligns with NL-HQ and corporate requirements and ensures optimal latency for target users. | No geographical redundancy. |
| SOLDEC009 | Assign subscriptions to the mg-online management group. | Based on the Landing Zone design decision tree and connectivity requirements. | Landing zone creation must comply with mg-online enforced policies. |
| SOLDEC010 | All PaaS services will be created with a private endpoints. | Ensures secure service-to-service communication and alignment with enterprise security standards. | Requires DNS, Private Link, and network design considerations. |
| SOLDEC011 | Access between all PaaS resources will be granted using Managed Identities. | Eliminates stored credentials and enforces identity-based access control. | Requires correct RBAC and Azure AD configuration. |
| SOLDEC012 | Private endpoints will be deployed in a dedicated Private Endpoint subnet, using Private DNS zones hosted in the same subscription. | Ensures consistent network segmentation and DNS governance. | Requires careful management of subnet capacity, DNS configuration, and potential cross-service connectivity considerations. |
| SOLDEC013 | Azure App Service plan will be deployed with zone redundancy disabled. | Simplifies deployment and reduces cost by not requiring multi-zone replication. | May increase risk of downtime during a regional outage since the service is not resilient across availability zones. |
| SOLDEC014 | Azure App Service will be deployed using the P0V3 pricing plan with an initial instance count of 1, scalable later based on demand. | Provides a cost-effective starting point while allowing future scaling as demand increases. | Initial single instance may limit performance and availability under high load until scaled. |
| SOLDEC015 | A new virtual machine running Windows Server 2025 with a Standard D2s_v5 size will be deployed to host the Playwright MCP server. | Provides a dedicated and supported environment for Playwright MCP deployment and execution. | Additional virtual machine resources, operating system licensing, monitoring, patching, and maintenance activities will be required. |
| SOLDEC016 | For the Development environment, the solution will leverage the existing shared Microsoft Foundry instance, `aif-sdc-nl-hq-d-genai`, hosted in the `alz-nl-hq-d-genai` subscription. A dedicated AI model deployment will be provisioned within this Foundry instance specifically for the AI-Enabled RPA solution. | Reusing the existing shared Microsoft Foundry instance avoids unnecessary duplication of platform resources while providing a dedicated model deployment for the solution. | The solution will depend on the availability and governance of the shared Foundry instance. The dedicated model deployment must be managed independently to ensure appropriate configuration, access control, capacity, and lifecycle management for the AI-Enabled RPA solution. |
| SOLDEC017 | A dedicated Claude Sonnet 4.6 model deployment will be provisioned for the AI-Enabled RPA application within the existing Microsoft Foundry instance, `aif-sdc-nl-hq-d-genai`. | A dedicated model deployment provides the AI-Enabled RPA application with an isolated and explicitly managed model endpoint, supporting consistent model configuration, access control, capacity management, and application-specific governance. | The application will depend on the availability and supported configuration of Claude Sonnet 4.6 within Microsoft Foundry. The dedicated deployment will require appropriate access controls, capacity allocation, monitoring, and lifecycle management. |
| SOLDEC018 | A private endpoint will be created for the App Service within the virtual network associated with the `NL-HQ-SHVE-APIM-DEV` APIM service. This will enable the APIM service to access the App Service over the private network, allowing the App Service to be securely exposed to the n8n service through APIM. | Using a private endpoint ensures that communication between APIM and the App Service remains within the private network, reducing exposure to the public internet while providing a secure integration path for the n8n service. | The App Service will require appropriate private DNS configuration and network connectivity to ensure APIM can resolve and reach the private endpoint. APIM will act as the controlled exposure layer for n8n, and the App Service should be configured to restrict or disable direct public access where appropriate. |


### Design Assumptions
| Reference ID | Statement | Rationale | Implications |
| --- | --- | --- | --- |
| SOLASS001 | Regulatory, compliance, and data-residency requirements for BU workloads are confirmed to allow deployment within Sweden Central. | Prevents non-compliance and data-movement issues after go-live. | Changes in regulatory interpretation could require re-validation or environment adjustment. |
| SOLASS002 | All runtime identities will use managed identities, and all secrets (DB passwords, Sensedia keys, storage keys) will be stored only in Azure Key Vault, not in code or configuration files. | Aligns with security best practices and minimizes credential‑leak risk.| Requires Key Vault availability and RBAC configuration; application startup and pipelines must be able to resolve and access Key Vault, and any manual secret sharing is prohibited. |

# Solution Architecture

## Development Environment

![image.png](/.attachments/image-5457315f-3501-41d2-ab07-70b9efdc443a.png)

## Security Architecture
:::mermaid
graph LR;
    A[Azure Solution] 
A --> | Entra ID| B[Identity and Access] 
A --> | HTTPS | C[Network Security] 
A --> | Encryption at rest, in transit | D[Encryption]

:::

## Solution Sizing
The following prices are provided in per month consumption increments and are rough estimations based on average usage. The estimations for the compute below include the Azure Hybrid Benefit licensing model and 3 years reserved instances. 

| Resource Type | Quantity / Size* | Price** |
|--|--|--|
| Azure App Service | x 1 P0V3 (1 vCPU(s), 4 GB RAM, 250 GB Storage) | €55.05 per month |
| Virtual Machines | x 1 B2als v2 (2 vCPUs, 4 GB RAM), Hybrid Enabled | €24.06 per month |
| Storage Account | 2 x Standard, LRS | 2 x €0.02 per GB per month |
| Key Vault | 1 x Standard | NA |

**Prices have been captured 21/08/2026 for Sweden Central region and are subject to change in the future.

## Solution Naming

| Subscription | Environment | Resource Groups | Resources |
| --- | --- | --- | --- |
| alz-nl-hq-d-airpa | Development | `rg-sdc-nl-hq-d-airpa` | Virtual Network: `vnet-sdc-nl-hq-d-airpa` <br/> Subnets: <br> `snet-sdc-nl-hq-d-airpaagent`, <br> `snet-sdc-nl-hq-d-airpamcp`, <br> `snet-sdc-nl-hq-d-airpaprivep` <br> App Service: `app-sdc-nl-hq-d-airpa` <br> App Service Plan: `asp-sdc-nl-hq-d-airpa` <br> Virtual Machine: `NL-HQ-D-AP014` <br> Key Vault: `kv-sdc-nl-hq-d-airpa` <br> Storage Account: `alzsdcnlhqdstdairpa` |

## Subscription Details (Existing)
| Subscription Name | Environment | Type | Management Group |
| --- | --- | --- | --- |
| alz-nl-hq-d-airpa | Development | MSDNDevTest | mg-corp |

##RBAC Assignments
| RBAC Role | Environment | Scope (Resource Group) | Group Name | Source Domain |
| --- | --- | --- | --- | --- |
| Reader | Development | alz-nl-hq-d-airpa | adm-Priyam.Das@shvenergy.com | shvenergy.com domain |

## Backup and Disaster Recovery

| Backup Item | Schedule |
|--|--|
| N/A |  |

## Software Licensing

| Vendor | Product | License Type | Quantity |
|--|--|--|--|

_BU's are eligible to enable Hybrid Use Benefit on VM's when they enable the Azure Virtual Machine in the SoftwareOne portal. By enabling this, significant cost savings can be achieved._

### Reserved Instance
| Resource Type | ENV | SKU | Reserved Instance |
|--|--|--|--|
| N/A |  |  | NA |

## IP Address Space

### Virtual Network

The specific VNET IP Address assignments for each landing zone is provided below. 

| VNET | Environment | CIDR Block | IPAM Pool |
| --- | --- | --- | --- |
| vnet-sdc-nl-hq-d-airpa | Development | /26 | IAP-NL-HQ-AZ-001 |

The mentioned Tag is for IPAM to ensure the CIDR block is correctly identified once the VNET is created.

### Subnets
The specific Subnet IP Address assignments for resources. 

| Subnets | Environment | Virtual Network | CIDR |
|--|--|--|--|
| snet-sdc-nl-hq-d-airpaagent | Development | vnet-sdc-nl-hq-d-airpa | /28 |
| snet-sdc-nl-hq-d-airpamcp | Development | vnet-sdc-nl-hq-d-airpa | /28 |
| snet-sdc-nl-hq-d-airpaprivep | Development | vnet-sdc-nl-hq-d-airpa | /28 |

## Firewall Rules

| Source | Destination | Port | Protocol | Description |
|--|--|--|--|--|
| Azure VM | Salesforce | 443 | HTTPS | Outbound connectivity to Salesforce for MCP tools. |

## OWASP Rules

| Rule Group | Rule ID | Description / Purpose | Exception Approved Y/N? |
|--|--|--|--|
| N/A |  |  |  |
|  |  |  |  |
|  |  |  |  |

## Governance
Using Management Groups the delegation of control and scope of management through desired state configuration is provided.

##Baselines 
To ensure Microsoft Defender for Cloud can report over compliance states Baselines on the Azure landscape are enforced. These baselines are described in the [Management and Monitoring Design](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/391/DLD-Azure-Management-and-Monitoring) and will be enforced by Azure Policy.

## Resource Compliance enforcement
Resource compliance is a three step approach; Using Azure Policy the security and architecture compliance is ensured by the following methods:
- Deployment; CCoE will deploy only using Infrastructure as Code via Azure DevOps to ensure configurations are done in a controlled manner.
- Management Plane; on Azure Management Pane level, Azure Policy enforces configurations for security and architecture compliance on the resources.
- Data Plane; on Data Plane, the data or operational level of the resource is controlled by the business. The business or other IT departments control the way these levels are kept in security and architecture compliance. eg. OS team for Operating systems, DB Team or Application owner for Databases or SQL Server level.

As part of this enforcement Resource Delete locks are in place after a deployment is performed using IaC. This is done as a separate stage when the configuration is verified by the CCoE deployment quality check.

##Tagging Values
The following values should be used for the required tags specified in [DLD Azure Governance Security and Compliance](link).
 Tag Name | Description | Key| Value pattern | Required? |
|--|--|--|--|--|
| Application Name | Name of the application, service, or workload the resource is associated with. | ApplicationName | AI Enabled Robotics Process Automation | Yes |
| Approver Name | Person responsible for approving costs related to this resource. | Approver | priyam.das@shvenergy.com | Yes |
| Budget required/approved | Money allocated for this application, service or workload. | BudgetAmount | Numbered value in agreed currency {€} | No |
| Business Unit | Top-level division of your company that owns the subscription or workload the resource belongs to. In smaller organizations, this may represent a single corporate or shared top-level organizational element. | BusinessUnit | NL-HQ | Yes |
| Cost Center | Accounting cost center associated with this resource. | CostCenter | - | Yes |
| Disaster Recovery | Business criticality of this application, workload, or service. | DR | Business operational | Yes |
| End Date of the Project | Date when this application, workload, or service is planned to be retired. | EndDate | NA | No |
| Environment | Deployment environment of this application, workload, or service. | Env | Development | Yes |
| Owner Name | Owner of the application, workload, or service. | Owner | priyam.das@shvenergy.com | Yes |
| Requester Name | User that requested the creation of this application. | Requestor | - | No |
| Service Class | Service Level Agreement level of this application, workload, or service. | ServiceClass | Bronze | Yes |
| Start Date of the project | Date when this application, workload, or service was first deployed. | StartDate | NA | No |

All mandatory tags will be set with a default value by policy, which can be changed or extended when pattern is known (and enforceable by policy).

# Architecture Risks
| Risk nr. | Risk | Description |
|--|--|--|
| NA |

# Architecture Issues
| Issue nr. | Issue | Description |
|--|--|--|
| SAI001 | None identified |  |

# Architecture Gaps
| Gap nr. | Domain | Gap | Description |
|--|--|--|--|
| SAG001 | None identified   |  |  |

# Support Model
:::mermaid
graph TD;
A[First Line Team - App team] --> |SLA| B[Second Line Team - CCoE] --> |SLA| C[Third Line Team - Microsoft]
:::

# Work Items
#185148


# Applicable Principles

| Reference | Principle | Applicable? | In line | Reason for Deviation |
|--|--|--|--|--|
| CPP01 | [Subscription democratization](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=subscription-democratization) | Y | Y | N/A. |
| CPP02 | [Policy-driven governance](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=policy-driven-governance) | N/A. | N/A. | N/A. |
| CPP03 | [Single control and management plane](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=single-control-and-management-plane) | N/A. | N/A. | N/A. |
| CPP04 | [Application-centric and archetype-neutral](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=application-centric-and-archetype-neutral) | N/A. | N/A. | N/A. |
| CPP05 | [Align Azure-native design and roadmaps](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=align-azure-native-design-and-roadmaps) | N/A. | N/A. | N/A. |

| Reference | Principle | Applicable? | In line | Reason for Deviation |
|--|--|--|--|--|
| ADP01 | [Build for the needs of business.](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=build-for-the-needs-of-business) | Y | Y | N/A. |
| ADP02 | [Design for self-healing](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=design-for-self-healing) | N/A. | N/A. | N/A. |
| ADP03 | [Make all things redundant](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=make-all-things-redundant) | N/A. |N/A.| N/A. |
| ADP04 | [Minimize coordination](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=minimize-coordination) | N/A. |N/A.  | N/A. |
| ADP05 | [Design to scale out](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=design-to-scale-out) | Y | Y | N/A. |
| ADP06 | [Partition around limits](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=partition-around-limits) | N/A. | N/A. | N/A. |
| ADP07 | [Design for operations](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=design-for-operations) | Y | Y | N/A. |
| ADP08 | [Use managed services](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=use-managed-services) | Y | Y | N/A. |
| ADP09 | [Use the best data store for the job](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=use-the-best-data-store-for-the-job) | N/A. | N/A. | N/A. |
| ADP10 | [Design for evolution](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles?anchor=design-for-evolution) | N/A. | N/A. | N/A. |

