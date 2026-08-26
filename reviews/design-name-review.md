# Azure Architecture Review: AI-Enabled Robotics Process Automation

## 1. Executive Summary

**Scope:** PoC environment in Sweden Central, based on `reviews/input/design-name.md` and `reviews/input/design-diagram.png`. The source design labels the workload as Development; this review applies the requested PoC classification.

**Environment classification:** PoC  
**Business criticality:** Not specified  
**Availability requirement:** RTO not specified for the PoC review; source design states RTO 24 hours. RPO not specified for the PoC review; source design states RPO 24 hours.

**Overall assessment:** The design has a reasonable intended landing-zone shape: a dedicated workload subscription, VNet, centralized APIM/Application Gateway/WAF, private endpoints, managed identities, Azure Policy, Defender for Cloud, and Azure DevOps IaC. As a PoC, resilience, HA, DR, and multi-region gaps are informational and cost and simplicity are prioritized. The design is still not sufficiently complete or internally consistent for secure PoC implementation.

The material risks are incomplete identity and network-flow specifications, lack of a threat model and guardrails for an AI agent that can invoke Playwright MCP tools and reach Salesforce, and unresolved landing-zone, hosting, and sizing contradictions. The diagram also shows a Sweden Central workload depending on a Central India connectivity hub without explaining data residency, latency, or failure behavior.

**Risk rating:** High  
**Approval status:** **Rejected**. Critical security findings remain unresolved. The design should return for review after security boundaries, private connectivity, ownership, and sizing contradictions are resolved and tested. Resilience and recovery improvements are recommended but are not PoC approval blockers.

## 2. Template Compliance Matrix

Status values: **Compliant** means materially addressed; **Partial** means present but incomplete, contradictory, or unverified; **Missing** means absent or marked `N/A` without sufficient justification.

| SHV template area | Status | Evidence and observation |
|---|---|---|
| Introduction, scope, out of scope | Compliant | Scope and exclusions are documented, but exclusions remove controls needed for end-to-end validation. |
| Business drivers and success factors | Compliant | Automation and secure/scalable AI objectives are stated. |
| Business requirements | Partial | Requirements exist, but `BSRQ001` is duplicated and the APIM/Application Gateway ownership boundary is unclear. |
| Stakeholder requirements | Partial | CCoE responsibility is stated; application, integration, security, and operations ownership is incomplete. |
| Functional requirements | Partial | Runtime and exposure requirements exist; authentication, authorization, tool approval, and model fallback are unspecified. |
| Non-functional requirements | Partial | CIA, RPO, RTO, single-region, and cloud-principle requirements are stated without controls or acceptance tests. |
| Transition requirements | Missing | `TRRQ001` is `N/A`; cutover, rollback, onboarding, and handover are absent. |
| Design decisions | Partial | Decisions are detailed, but App Service/container-native/containerization statements conflict. |
| Design assumptions | Partial | Residency and secret assumptions exist; DNS, identity, quota, traffic, Salesforce, and MCP assumptions are absent. |
| Solution architecture and diagram | Partial | Major services are shown; protocols, trust boundaries, DNS, routes, subnet delegations, and failure paths are absent. |
| Sizing and pricing | Partial | Prices exist, but VM SKU differs between the decision and sizing table; shared and network costs are omitted. |
| Naming | Compliant | Subscription, resource groups, VNet, subnets, and resources are mostly named. |
| Subscription and landing zone | Partial | SOLDEC009 says `mg-online`; subscription details and diagram show `mg-corp`. Existing/new status is unclear. |
| RBAC assignments | Missing | Only a Reader entry exists; PIM, managed-identity roles, scope, access reviews, and break-glass access are absent. |
| Backup and disaster recovery | Informational gap | The table is `N/A` despite RPO/RTO values in the source design and a Recovery Services Vault in the diagram. For this PoC, a full DR implementation is optional, but data protection and teardown/recovery expectations should still be documented. |
| Licensing and reservations | Partial | Hybrid Benefit and reservations are mentioned without entitlement, term, SKU, or usage validation. |
| IP address space and subnets | Partial | A `/26` VNet and three `/28` subnets are stated; growth, delegation, routes, NSGs, and peering ranges are absent. |
| Firewall and egress | Missing | Only VM-to-Salesforce HTTPS is listed; complete flows, DNS, firewall path, and FQDN controls are absent. |
| OWASP/WAF rules | Missing | The section is `N/A`; managed rules, exclusions, tuning, logging, and exceptions are absent. |
| Governance and compliance | Partial | Policy, Defender, locks, IaC, and tags are described; assignments, exemptions, and evidence are absent. |
| Risks, issues, gaps | Missing | Risks and gaps are declared `NA`/none despite material unresolved issues. |
| Support model and work items | Partial | A three-line model and work item exist; SLAs, runbooks, escalation, and acceptance criteria are absent. |

## 3. Architecture Findings

### ARC-001: Unresolved landing-zone management-group contradiction

**Severity:** High  
**Category:** Governance / Architecture  
**Evidence:** SOLDEC009 assigns the subscription to `mg-online`; Subscription Details and the diagram place it under `mg-corp`.  
**Impact:** Different management groups can apply different policies, network controls, diagnostics, RBAC inheritance, and cost governance.  
**Recommendation:** Confirm the target management group through the landing-zone decision process. Record the subscription archetype, policy assignments, connectivity subscription, diagnostics, and approved exemptions as deployment prerequisites.  
**Reference:** [Cloud Adoption Framework landing zones](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/); [Azure landing-zone design areas](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/landing-zone/design-areas/).

### ARC-002: Architecture diagram does not establish a deployable end-to-end path

**Severity:** High  
**Category:** Architecture  
**Evidence:** The document describes APIM and Application Gateway exposure, while the diagram shows APIM, an Azure OpenAI private-endpoint label, WAF, App Service, VM, shared Foundry, and a Central India vWAN hub. DNS links, UDRs, NSGs, authentication, and the exact APIM-to-App Service path are not shown.  
**Impact:** The intended route cannot be implemented or tested unambiguously. Incorrect DNS or routing can cause public fallback, asymmetric routing, failed model calls, or a WAF/APIM bypass.  
**Recommendation:** Provide a deployment-level diagram showing subscriptions, regions, trust zones, subnet delegations, private endpoints, DNS zones and links, route tables, NSGs, ingress/egress flows, identities, and failure paths. Maintain one authoritative service inventory.

### ARC-003: App Service hosting decision is internally inconsistent

**Severity:** Medium  
**Category:** Architecture  
**Evidence:** SOLDEC001 selects Windows App Service but calls it container-native and states containerization is required; no image, registry, runtime, deployment, or rollback model is supplied.  
**Impact:** The implementation may use an unsupported or unintended runtime, with unclear image, patching, startup, and scaling ownership.  
**Recommendation:** Decide between native Windows App Service and Windows containers. Document runtime, image registry, deployment, health checks, supported features, and rollback.

### ARC-004: Cross-region connectivity and residency behavior are undocumented

**Severity:** High  
**Category:** Architecture / Governance  
**Evidence:** The workload is in Sweden Central, while the diagram shows peering to an SHV vWAN hub and Azure Firewall in Central India. The design states a single Azure region and assumes Sweden Central residency.  
**Impact:** Traffic may traverse or depend on another region, affecting latency, egress cost, availability, and residency obligations.  
**Recommendation:** Document route and data classes crossing the boundary. Validate vWAN topology, routing, firewall placement, failover, egress, and residency with landing-zone and compliance owners. Remove the path if unnecessary.

## 4. Security Findings

### SEC-001: AI agent and MCP tool boundary lacks threat modeling and least privilege

**Severity:** Critical  
**Category:** Security  
**Evidence:** The design exposes an AI-enabled RPA application and Playwright MCP on a Windows VM, but defines no tool allow-list, user consent, prompt-injection defense, browser isolation, target-domain restriction, session handling, output validation, command/file restrictions, or audit events. The VM can reach Salesforce.  
**Impact:** A malicious prompt, compromised identity, poisoned page, or model error could cause unauthorized browser actions, data exfiltration, Salesforce changes, credential exposure, or lateral movement.  
**Recommendation:** Create an MCP-specific threat model. Isolate the MCP server, use a dedicated managed identity with only required permissions, enforce tool and destination allow-lists, disable arbitrary command/file access, isolate browser sessions, require approval for high-impact actions, redact sensitive outputs, and log tool invocations immutably. Test prompt injection and confused-deputy scenarios before approval.  
**Reference:** [Well-Architected security pillar](https://learn.microsoft.com/azure/well-architected/security/); [Azure AI Agent Service security](https://learn.microsoft.com/azure/ai-services/agents/concepts/what-is-agent-service); [Azure MCP Server guidance](https://learn.microsoft.com/azure/developer/azure-mcp-server/); [MCP security best practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices).

### SEC-002: External authentication and authorization are unspecified

**Severity:** Critical  
**Category:** Security  
**Evidence:** APIM/Application Gateway are the external entry point, but no client authentication, token validation, audience/issuer, authorization policy, rate limit, source restriction, or App Service access restriction is specified.  
**Impact:** Unauthorized clients may invoke the service, or an authenticated client may invoke actions beyond its business scope. Private backend access alone is not application authorization.  
**Recommendation:** Define Entra ID registrations, OAuth2 flow, APIM token validation, scopes/roles, certificate or workload identity requirements, client quotas, App Service access restrictions, and deny-by-default behavior. Verify no alternate public hostname or route bypasses APIM.

### SEC-003: RBAC and privileged access controls are insufficiently specified

**Severity:** High  
**Category:** Identity / Governance  
**Evidence:** The RBAC table contains only a Reader assignment. PIM, managed-identity role assignments, administrative roles, separation of duties, access reviews, and break-glass controls are absent.  
**Impact:** Operators may have excessive standing access while the application lacks required permissions for Key Vault, Foundry, storage, monitoring, or private DNS.  
**Recommendation:** Use group-based least-privilege RBAC, PIM for privileged roles, managed identities, access reviews, controlled break-glass accounts, and documented ownership. Include shared Foundry and DNS resources in the access model.

### SEC-004: VM, secrets, and outbound controls are not implementation-ready

**Severity:** High  
**Category:** Security  
**Evidence:** Key Vault is an assumption, but rotation, purge protection, diagnostics, private access, and recovery are unspecified. VM hardening, patching, endpoint protection, administrator access, JIT, and egress controls are absent. OWASP rules are `N/A`.  
**Impact:** Credentials, browser sessions, model/API tokens, or Salesforce data may be exposed; a compromised VM could become an outbound pivot.  
**Recommendation:** Define Key Vault RBAC, private access, soft-delete, purge protection, rotation, and diagnostics. Harden the VM with Defender for Servers, EDR, patching, JIT administration, no public IP, restricted management paths, disk encryption, and explicit firewall/FQDN egress. Define WAF managed rules and approved exceptions.

## 5. Networking Findings

### NET-001: Private endpoint and private DNS design is incomplete

**Severity:** High  
**Category:** Networking  
**Evidence:** The design mandates private endpoints for all PaaS services and a private DNS zone in the workload subscription, but does not list endpoint subresources, DNS zones, VNet links, forwarding, registration, or resolution from APIM, App Service, VM, and deployment agents.  
**Impact:** Services may fail to resolve, resolve publicly, or be inaccessible from required callers. DNS workarounds can undermine private access.  
**Recommendation:** Create a private-connectivity matrix for App Service, Foundry, Key Vault, Storage, monitoring, and other PaaS services. Specify endpoint policy, DNS ownership, hub/spoke links, forwarders, APIM resolution, and caller-by-caller validation.

### NET-002: Subnet and route controls are underspecified

**Severity:** High  
**Category:** Networking  
**Evidence:** Three `/28` subnets are named, but no delegation, NSG, UDR, firewall route, service endpoint decision, or growth calculation is supplied.  
**Impact:** Scaling, private endpoints, and future components may exhaust the `/26` or have unintended east-west and egress access.  
**Recommendation:** Produce an IP plan with growth reserve. Define subnet purposes/delegations, deny-by-default NSGs, UDR intent, forced tunneling, firewall inspection, and tested return paths. Evaluate a larger VNet.

### NET-003: Salesforce egress is not enforceable from the stated rule

**Severity:** High  
**Category:** Networking / Security  
**Evidence:** The only rule is `Azure VM -> Salesforce:443 HTTPS`; FQDN/IP ownership, DNS, proxy/firewall enforcement, source NAT, TLS decision, and App Service egress are unspecified.  
**Impact:** The MCP VM or App Service may reach unapproved destinations, or Salesforce access may fail as endpoints change.  
**Recommendation:** Define approved FQDNs and destination ownership, force egress through the approved firewall/proxy, restrict both VM and App Service outbound paths, log flows, and test TLS/certificate behavior.

## 6. Reliability Findings

### REL-001: PoC recovery expectations are undocumented

**Severity:** Informational  
**Category:** Reliability  
**Evidence:** RPO is listed as 24 hours and RTO as 24 hours in the source design, but Backup and Disaster Recovery is `N/A`. A Recovery Services Vault appears in the diagram without protected workloads, policy, retention, redundancy, access controls, restore dependencies, or test evidence.  
**Impact:** Recovery behavior is unknown after VM loss, deletion, corruption, secret loss, or regional disruption. This is acceptable as an explicitly accepted PoC limitation, but it must not be mistaken for production readiness.  
**Recommendation:** Document the PoC recovery boundary, disposable versus retained data, teardown/rebuild steps, and any minimum backup needed to avoid loss of valuable test data. Full restore testing against the 24-hour objectives is optional for this PoC.  
**Reference:** [Well-Architected reliability pillar](https://learn.microsoft.com/azure/well-architected/reliability/); [Azure Backup overview](https://learn.microsoft.com/azure/backup/backup-overview).

### REL-002: Single-instance compute is a PoC availability trade-off

**Severity:** Informational  
**Category:** Reliability  
**Evidence:** App Service is planned with one instance and zone redundancy disabled; MCP uses one VM.  
**Impact:** Host maintenance, platform faults, VM failure, or deployment errors can make the PoC workflow unavailable.  
**Recommendation:** Accept the single-instance design for the PoC, document expected downtime, and retain health checks and a simple rebuild/rollback procedure. Multi-instance and zone-resilient deployment are not required unless the workload moves beyond PoC.  

### REL-003: PoC regional failure and shared-service dependencies are not modeled

**Severity:** Informational  
**Category:** Reliability  
**Evidence:** The solution relies on single-region workload resources, shared Foundry in another subscription, centralized APIM, shared connectivity, and shared monitoring. No dependency SLA, quota, failover, or degraded-mode behavior is documented.  
**Impact:** An unrelated shared-service outage or quota event can stop the PoC workload.  
**Recommendation:** Record dependency owners, quota assumptions, and model-unavailable behavior. Multi-region redundancy and shared-service failover are optional for the PoC; reassess them before production use.  

## 7. Cost Findings

### COST-001: Sizing and price inputs are contradictory

**Severity:** High  
**Category:** Cost / Architecture  
**Evidence:** SOLDEC015 selects Standard `D2s_v5`; the sizing table prices `B2als v2`. App Service P0v3 pricing and storage assumptions also require validation.  
**Impact:** The estimate is not reproducible and may understate compute, licensing, or performance cost.  
**Recommendation:** Reconcile SKU, region, OS, instance count, hours, reservation/Hybrid Benefit eligibility, and currency. Attach a repeatable estimate and load-test evidence. Do not reserve capacity until usage is proven.

### COST-002: Shared and network-dependent costs are omitted

**Severity:** Medium  
**Category:** Cost  
**Evidence:** The estimate omits private endpoints/DNS, APIM, Application Gateway/WAF, firewall/vWAN, Log Analytics, Defender, Recovery Services Vault, bandwidth, Foundry/model usage, and support. Key Vault is `NA`.  
**Impact:** Total cost of ownership is understated and alternatives cannot be compared.  
**Recommendation:** Include shared-service allocation, token and browser volume, logs/retention, egress, backups, and non-production runtime hours. Add budget alerts and an owner.

### COST-003: Development shutdown and commitment assumptions are missing

**Severity:** Medium  
**Category:** Cost / Operations  
**Evidence:** Hybrid Benefit and three-year reservation language is present, but entitlement, opening hours, autoscale, and deallocation are not documented.  
**Impact:** Development capacity may be idle or commitments may be invalid.  
**Recommendation:** Define DevTest eligibility, VM start/stop automation, App Service scaling, reservation break-even, and budget alerts. Revisit commitments after measured usage.

## 8. Operational Findings

### OPS-001: Monitoring is shown but alerting and response are not defined

**Severity:** High  
**Category:** Operations  
**Evidence:** Application Insights, Log Analytics, Monitor, and Defender appear in the diagram, but diagnostic categories, retention, alerts, action groups, on-call ownership, runbooks, and MCP/model safety events are not defined.  
**Impact:** Operators may not detect unauthorized tool use, model failures, Salesforce errors, DNS failures, quota exhaustion, or recovery drift.  
**Recommendation:** Define platform/application diagnostics, correlation IDs, model/tool audit events, redaction, retention, Sentinel integration where applicable, actionable alerts, SLO dashboards, and runbooks with named owners.

### OPS-002: MCP VM ownership and lifecycle are excluded without an operating contract

**Severity:** High  
**Category:** Operations / Security  
**Evidence:** CCoE provides the Windows VM while the application team deploys MCP; deployment, operation, and lifecycle are out of scope. The support model has no SLAs or handoff criteria.  
**Impact:** Patching, browser updates, MCP versioning, vulnerability remediation, backup, incident response, and identity rotation can fall between teams.  
**Recommendation:** Define a RACI and acceptance checklist for baseline, patching, EDR, vulnerability SLAs, MCP release/rollback, monitoring, access, backup, and escalation.

### OPS-003: IaC and policy controls lack evidence and exception management

**Severity:** Medium  
**Category:** Governance / Operations  
**Evidence:** Azure DevOps IaC and delete locks are described, but repository, approvals, drift detection, policy exemptions, secret handling, test gates, and rollback are not identified.  
**Impact:** Infrastructure can drift from the reviewed design; delete locks can complicate controlled recovery or teardown.  
**Recommendation:** Link the IaC repository and pipeline, define validate/deploy/verify/lock stages, require approval for policy exceptions, scan IaC and images, and document lock removal and rollback.

## 9. Open Questions

1. Which management group is authoritative: `mg-online` or `mg-corp`, and is the subscription new or existing?
2. Does CIA 3 apply to Development, and what availability target is required for App Service and MCP?
3. What data is processed by the agent, browser, Salesforce, Foundry, logs, and storage, and what are classification, residency, retention, and deletion requirements?
4. How do external callers authenticate, and how are client, user, and tool permissions separated?
5. Which agent tools and Salesforce/browser destinations are allowed, and which actions require human approval?
6. How are prompt injection, malicious web content, session fixation, exfiltration, and confused-deputy attacks tested?
7. What are the exact APIM, Application Gateway, WAF, App Service, VM, Foundry, and Salesforce flows, including DNS and return paths?
8. Why does the diagram route through the Central India vWAN hub, and what data, latency, egress, and outage behavior results?
9. Which private endpoints, subresources, DNS zones, VNet links, and shared-subscription permissions are required?
10. What is the authoritative VM SKU and App Service runtime model, and what load test supports sizing?
11. What is backed up, how often, for how long, where, and when was the last restore test?
12. How are App Service, VM, Key Vault, Storage, Foundry configuration/model, DNS, and IaC recovered within 24 hours?
13. What are Foundry model availability, quota, throughput, safety, versioning, and fallback requirements?
14. What are operational SLAs, support hours, owners, alert routes, and escalation criteria across App team, CCoE, Integration, and Microsoft?
15. What request, token, browser-session, Salesforce, log, and backup volumes support the cost estimate?

## 10. Approval Recommendation

**Decision: REJECTED**

The design is not approved for implementation in its current form. `SEC-001` and `SEC-002` are Critical because the externally reachable AI/RPA capability and browser automation boundary lack a defined authorization and abuse-control model. PoC classification makes resilience findings informational, but it does not waive security, governance, or operational controls. This follows the repository rule that a design with Critical findings cannot be approved.

**Minimum conditions for resubmission:**

- Resolve management-group, hosting-model, VM-SKU, and diagram inconsistencies.
- Provide identity, authorization, MCP threat model, tool allow-list, human approval, logging, and egress controls.
- Provide tested private endpoint, DNS, routing, NSG, firewall, and Salesforce connectivity matrices.
- Document the PoC recovery boundary, disposable data, and rebuild procedure. Implement backups and restore testing before the design is promoted beyond PoC.
- Reconcile sizing and produce a complete cost model with DevTest scheduling and shared-service allocation.
- Assign operational ownership, SLAs, runbooks, monitoring, patching, vulnerability remediation, and model/MCP lifecycle responsibilities.

The next review should include the updated design, deployment-level diagram, policy/RBAC evidence, restore-test results, security-test results, and updated cost estimate.
