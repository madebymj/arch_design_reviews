[[_TOC_]]

# Introduction
This architecture document describes the Solution Design for ...

## In-scope of this document

| Nr. |Description |
|--|--|
| IS001 | All IT components needed for running this solution in the organizations IT environment. |

## Out of Scope of this document

| Nr. | Description |
|--|--|
| OOS001 | Identity and Access Management for the solution. |
| OOS002 | All other topic not described in the in-scope section of this page. |

# Business Drivers and Success Factors

| Business Driver(s) | Description |
|--|--|
|  |  |

| Critical Success Factor(s) | Description |
|--|--|
|  |  |

# Requirements

## Business Requirements
Business requirements represent business objectives stated by the customer. Statements of goals, objectives, and outcomes that describe why a change has been initiated. They can apply to the whole of an enterprise, a business area, or a specific initiative.

| Reference ID | Statement | Rationale| HLD Reference |
|--|--|--|--|
| BSRQ001 |  |  |  |

## Stakeholder Requirements
Stakeholder requirements represent the requirements of individual stakeholders. Describe the needs of stakeholders that must be met in order to achieve the business requirements.

| Reference ID | Statement | Rationale| HLD Reference |
|--|--|--|--|
| STRQ001 |  |  |  |

## Solution Requirements
Features and characteristics expected of developed software application represent solution requirements. Describe the capabilities and qualities of a solution that meets the stakeholder requirements. They provide the appropriate level of detail to allow for the development and implementation of the solution.

### Functional Requirements
Functional requirements are the expected features of the system. 

| Reference ID | Statement | Rationale| HLD Reference |
|--|--|--|--|
| FNRQ001 |  |  |  |

### Non-Functional Requirements
Non-functional requirements are related to the behavior of the system. 

| Reference ID | Statement | Rationale| HLD Reference |
|--|--|--|--|
| NFRQ001 | Confidentiality Integrity Availability (CIA) Rating: <br/> - C = x <br/> - I = x <br/> - A = x | This is a core input for designing solutions based on business criticality. | N/A. |
| NFRQ002 | Return Point Objective: <br/> - RPO = xx hours | Core metric that defines the amount of data change loss acceptable to the business | N/A. |
| NFRQ003 | Return Time Objective: <br/> - RTO = xx hours | Core Metric that defines the maximum allow time that the service is not available to the business outside of regular maintenance. | N/A. |
| NFRQ004 | Solution must be aligned with the Cloud Principles: <br/> - [Link.](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/323/Principles) | Solutions must be aligned with core principles on how they are to be designed and deployed on the Cloud Platform | N/A. |
| NFRQ005 |  |  |  |

## Transition Requirements
The transition requirements are the requirements needed to implement the software application successfully. Describe the capabilities that the solution must have and the conditions the solution must meet to facilitate transition from the current state to the future state, but which are not needed once the change is complete. They are differentiated from other requirements types because they are of a temporary nature.

| Reference ID | Statement | Rationale| HLD Reference |
|--|--|--|--|
| TRRQ001 |  |  |  | 

# Design Decisions

| Reference ID | Statement | Rationale| Implications |
|--|--|--|--|
| SOLDEC001 |  |  |  |

# Design Assumptions

| Reference ID | Statement | Rationale| Implications |
|--|--|--|--|
| SOLASS001 |  |  |  |

# Solution Architecture

## Application Architecture
:::mermaid
graph LR;
    A[Firewall] --> B[WebApp] --> C[Middleware] --> D[Database]

:::

## Integration Architecture
:::mermaid
graph LR;
    A[Solution X] 
A -->|LogicApp| B[Solution 1] 
A --> |SFTP| C[Solution 2] 
A --> |RESTAPI| D[Solution n]

:::

## Technology Architecture
Insert Visio Diagrams


## Security Architecture
:::mermaid
graph LR;
    A[Solution X] 
A --> | solution| B[Identity and Access] 
A --> | solution| C[Network Security] 
A --> | solution| D[Encryption]

:::


## Solution Sizing
The following prices are provided in per month consumption increments and are rough estimations based on average usage.

| Resource Type | Quantity / Size* | Price** |
|--|--|--|
|  |  |  |

*These are initial sizing requirements to be used at time of deployment and may change after deployment based on changing performance requirements.

**Prices have been captured xx/xx/xxxx and are subject to change in the future.

## Solution Naming

| Subscription | Resource Groups | Resources |
|--|--|--|
| alz-nl-hq-p-app | rg-euw-nl-hq-p-app | vnet-euw-nl-hq-p-app​ <br/> asg-euw-nl-hq-p-app​ <br/> vm- euw-nl-hq-p-app001​ <br/> vm-euw-nl-hq-p-app002​ <br/> kv-euw-nl-hq-p-app​ <br/> sqlmi-euw-nl-hq-p-app​ <br/> rsv-euw-nl-hq-p-app |
|  | rg-euw-nl-hq-p-avd| avd-euw-nl-hq-p-app001 |
| alz-nl-hq-p-app |  | vnet-euw-nl-hq-d-app​ <br/> asg-euw-nl-hq-d-app​ <br/> vm- euw-nl-hq-d-app001​ <br/> vm-euw-nl-hq-d-app002​ <br/> kv-euw-nl-hq-d-app​ <br/> sqlmi-euw-nl-hq-d-app​ <br/> rsv-euw-nl-hq-d-app |
|  | rg-euw-nl-hq-d-avd | avd-euw-nl-hq-d-app001 |

## Subscription Details
| Subscription Name | Environment | Type | Management Group | 
|--|--|--|--|
| alz- | Production / Acceptance | EnterpriseAgreement | |
| alz- | Development / Test | MSDNDevTest | |

##RBAC Assignments
| RBAC Role | Group Name | Source Domain | 
|--|--|--|
| Azure Subscription Reader |  | _BU or shvenergy.corp_ | 
| VM Administrators |  | _BU or shvenergy.corp_ | 

## Backup and Disaster Recovery

| Backup Item | Schedule |
|--|--|
| Virtual Machines | - Daily Snapshot <BR/> - 7 day retention |
| Databases | - Point in time: every 10 minutes <br/> - 7 day retention |

## Software Licensing

| Vendor | Product | License Type | Quantity |
|--|--|--|--|
| Microsoft | Windows Server Datacenter | Hybrid / Pay as you go | TBD. |
| Microsoft | SQL Server Standard/Enterprise | Hybrid / Pay as you go | TBD. |
| Vendor | Product | TBD. | TBD. |'

_BU's are eligible to enable Hybrid Use Benefit on VM's when they enable the Azure Virtual Machine in the SoftwareOne portal. By enabling this, significant cost savings can be achieved._

### Reserved Instance
| Resource Type | ENV | SKU | Reserved Instance |
|--|--|--|--|
|  |  |  | 3 years <or 1year> |

_BU's commit for 3 years to this workload, allowing to have significant cost savings in place._

### Opening hours
To determine when resources like virtual machines need to be available, opening hours can be defined. Especially for non-production workloads, this can be another cost saver.   

_Ensure that any public holidays or specific days are mentioned._

| Resource Type | Env | Opening Hours | 
|--|--|--|
| Azure Virtual Machine | Production / DevTest | <hours>x<days per week>x<days per year> _for example 24x7x365_ |


## IP Address Space
The specific VNET IP Address assignments for each landing zone is provided below. 

| VNET | Environment | CIDR | Tag Name | Tag Value |
|--|--|--|--|--|
|  |  |  | X-IPAM-RES-ID |  |
|  |  |  | X-IPAM-RES-ID |  |

The mentioned Tag is for IPAM to ensure the CIDR block is correctly identified once the VNET is created.

## Firewall Rules

| Source | Destination | Port | Protocol | Description |
|--|--|--|--|--|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

## OWASP Rules

| Rule Group | Rule ID | Description / Purpose | Exception Approved Y/N? |
|--|--|--|--|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

##Tagging Values
The following values should be used for the required tags specified in [DLD Azure Governance Security and Compliance](link).
 Tag Name | Description | Key| Value pattern | Required? |
|--|--|--|--|--|
| Application Name | Name of the application, service, or workload the resource is associated with. | ApplicationName | minimal of 2 characters Vendor and Application separated by a dash (-) eg. SAP-Boost | Yes |
| Approver Name | Person responsible for approving costs related to this resource. | Approver | {email} eg. firstname.lastname@company.com | Yes |
| Budget required/approved | Money allocated for this application, service or workload. | BudgetAmount | Numbered value in agreed currency {€} | No |
| Business Unit | Top-level division of your company that owns the subscription or workload the resource belongs to. In smaller organizations, this may represent a single corporate or shared top-level organizational element. | BusinessUnit | <Country>-<BU> | Yes |
| Cost Center | Accounting cost center associated with this resource. | CostCenter | **{number}** | Yes |
| Disaster Recovery | Business criticality of this application, workload, or service. | DR | “Administrative service”, “Business operational”, “Business critical”, “Mission critical”, “None” | Yes |
| End Date of the Project | Date when this application, workload, or service is planned to be retired. | EndDate | {date} | No |
| Environment | Deployment environment of this application, workload, or service. | Env | Prod, Dev, Acc, Test, Sandbox, Decomissioned | Yes |
| Owner Name | Owner of the application, workload, or service. | Owner | {email} eg. firstname.lastname@company.com | Yes |
| Requester Name | User that requested the creation of this application. | Requestor | {email} eg. firstname.lastname@company.com  | No |
| Service Class | Service Level Agreement level of this application, workload, or service. | ServiceClass | DevTest, Bronze, Silver, Gold | Yes |
| Start Date of the project | Date when this application, workload, or service was first deployed. | StartDate | {date} | No |
| Maintenance Window | Time window for VM Patch Window (VMs and VM Scalesets only)| VMMaint | ms-<d/t/a/p/s>-<day(3char)>-set<#>-<w/l/a>-<r/nr> <br/>default: ms-manualbybu | No |
 

All mandatory tags will be set with a default value by policy, which can be changed or extended when pattern is known (and enforceable by policy).

# Architecture Risks
| Risk nr. | Risk | Description |
|--|--|--|
| SAR001 | Germany West Central paired region of Germany North limitations | If multi-region DR is required, there are limitations on the services and availability zones within the paired region. <br/><br/> [Decision - Region policy structure](https://dev.azure.com/SHV-Energy/NL_HQ_T_Cloud_CoE/_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/1958/Decision-Region-policy-structure?anchor=europe) |

# Architecture Issues
| Issue nr. | Issue | Description |
|--|--|--|
| SAI001 |  |  |

# Architecture Gaps
| Gap nr. | Domain | Gap | Description |
|--|--|--|--|
| SAG001 |  |  |  |

# Support Model
:::mermaid
graph TD;
A[First Line Team] --> |SLA| B[Second Line Team] --> |SLA| C[Third Line Team]

:::
# Solution Items
<list DevOps work Items>

# Dependent on Items
<list DevOps work Items>

# Approvals
_Design in Draft_

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

