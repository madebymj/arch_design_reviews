# Azure Deployment Plan

> **Status:** Deployed

Generated: 2026-09-21

## Pending experiment: Free Azure AI Search compatibility (2026-10-05)

**Status:** Free Search is selected by the live Function; live review completed for work item 191291. Basic is retained but application access was revoked on 2026-10-05. Earlier evidence below describes the staged migration chronologically.

**Goal:** Test a new Free Search service with the existing complete architecture-review workflow without replacing or deleting the working Basic service.

**Preparation:** Inspect the existing index, knowledge sources/base, authentication, storage/vector usage, and agent tool configuration. Check Free-tier quota, regional availability and supported features before provisioning.

**Isolation:** Use a separate Free service and test agent/connection. Do not redirect the live Function or service hooks without explicit approval. Confirm how to exercise the Function and a designated test Board work item without affecting normal reviews.

**Validation:** Verify indexed guidance, retrieval and citations, full written design and all PNG assessments, structured-response validation and actual Azure Boards writeback. A successful Search query alone does not prove end-to-end compatibility.

**Stop conditions:** Unsupported managed-identity/model connection, Free-tier limits, unavailable regional capacity, denied access or required unsafe changes. Report the exact blocker; do not silently change retrieval behavior.

**Costs and cleanup:** Free Search capacity has no service charge; model/tool test invocations remain billable. Preserve Basic and do not delete test resources without approval.

### Read-only preflight results

- User confirmed subscription `f565124f-a0f3-4bde-b0e8-dcadc036868b` and West Europe.
- Actual Basic Search location is West Europe; do not reuse the historical Canada Central location for Search.
- Subscription resource listing returned one Search service (`archdesignreview`, Basic), with no existing Free service.
- Current Search contains one index (`search-1789141789651`), 21 documents, 214,359 bytes of storage and zero vector-index bytes.
- Existing knowledge source is `searchIndex`; knowledge base is `architecture-review-knowledge`, with `minimal` retrieval reasoning effort and a GPT-4.1 model connection.
- Free compatibility is not yet proven. Index schema, semantic settings, source configuration and actual Free service retrieval must be tested.
- Proposed sequence: provision isolated Free Search in West Europe; copy index schema/documents and compatible knowledge source/base; verify retrieval; create isolated test agent connection; exercise orchestrator with designated test Board item; verify citations, all diagram assessments and Board writeback.
- Do not migrate the existing Blob indexer/skillset blindly: these are ingestion infrastructure, and Free outbound identity restrictions may require a different approved ingestion approach.
- User approved the isolated sequence. Recipe: Azure CLI/REST, no changes to live Function or webhook. Test Search resource name: `archdesignreview-free-test`, resource group `rg-euw-nl-hq-s-sandbox`, subscription and region as confirmed above.
- Pending: designated test work item / isolated Function execution method. No Azure resources have been created or modified.

### Experiment validation checklist

- All validation checks pass:
  - Core validation: CLI authentication, AVM Bicep compilation, ARM validation and what-if for `infra/free-search-test.bicep`.
  - Docker build: not applicable (no container or Function code deployment).
  - Azure Policy validation: inspect inherited assignments and ARM validation result.
  - Static role verification: template creates no RBAC assignments; Free uses no outbound managed identity.
- Provision only the isolated Free resource; no live infrastructure changes.

### Experiment validation proof (supplement to Section 7)

- Shared `validate-deployment.ps1` completed with `OVERALL: PASS`: Azure CLI, authentication, AVM Bicep build, ARM validate and what-if.
- What-if: two creates including nested deployment; actual service create is only `archdesignreview-free-test`, Free SKU, no identity. Zero modifications/deletions; existing Basic and Foundry resources are ignored.
- Inherited policy enumeration returned 62 assignments; ARM validation passed applicable enforcement checks.
- Editor Bicep diagnostics: no errors.
- No application code changed; no Docker build required. Static template review: no role assignments, no managed identity, no secrets in template.

### Experiment results (2026-10-05)

- Deployment `architecture-review-free-test` succeeded; correlation ID `f0dfaafc-7155-4e45-bbab-29b1b91d7ff0`.
- Free service `archdesignreview-free-test` in West Europe: provisioned successfully, semantic free enabled, dual API-key/Entra inbound auth.
- Copied the existing index schema, all 21 retrievable guidance documents, search-index knowledge source and knowledge base. Indexer/data-source/skillset migration and automated ingestion are NOT tested.
- Direct minimal-reasoning retrieval succeeded with five references; Search activity elapsed time 628 ms.
- User approved granting project identity `becd02ce-f483-4423-bf76-1da69d839c60` Search Index Data Reader on the Free service only. Assignment verified.
- Separate Foundry connection `architecture-review-free-test-v2` uses ProjectManagedIdentity with audience `https://search.azure.com`. An earlier test connection (`architecture-review-free-test`) remains; its initially missing audience caused failed invocations. No resources were deleted.
- Test agent `architecture-review-agent-free-test`, version 3, retains the live model/output schema and has an explicit test instruction requiring the Free knowledge tool. A prior response without actual MCP calls was rejected by test instrumentation before writeback.
- Designated Board item: 191251. Successful review ID: `board-191251-free-search-test-60d234e5-17e7-45f2-9913-bd956f13de92`.
- Wiki revision: `fc3454242e4d1bffdee44aaf806bf45f276465fa`.
- Verified result: seven findings, seven diagram assessments, overall risk High, valid structured response, successful `knowledge_base_retrieve` MCP call on `architecture-review-free-test-v2`, and Board history readback containing the review ID.
- Total test handler time: 45.7 seconds (not a 30-second benchmark).
- Execution boundary: local invocation of the unchanged Function handler with live configuration copied into process memory, only agent selection overridden locally, and a synthetic tag-added event. This is NOT a deployed HTTP webhook test; local caller identity differs from the deployed Function identity.
- Live app setting `FOUNDRY_AGENT_NAME` remains `architecture-review-agent`; Basic service and webhook were not redirected. Item 191251 did not require the actual trigger tag for this isolated test.
- Compatibility conclusion: Free can support the current small index and the tested design/retrieval/vision/validation/writeback path. Not yet proven: automatic content ingestion, sustained load, Free monthly semantic/retrieval quotas, or live webhook cutover. Retain Basic until any cutover is separately approved and verified.
- Missing local Foundry tooling was installed to satisfy prerequisite checks: Azure Developer CLI and its Foundry extension/dependencies.

### Requested live cutover preparation (2026-10-05)

- User requested ingestion parity, a real Board-triggered test, and eventual Basic deletion only after success.
- Copied Basic Blob datasource, language-detection/chunking skillset, and indexer into Free. Original indexer schedule is unset; Free also has no automatic schedule.
- Approved authentication deviation: Free datasource uses read/list HTTPS container SAS for `archdesignreview1`, expiring 2026-11-04 11:38 UTC. Credential exists only in Search datasource; no credential persisted in source files.
- Initial Free indexing reported success, no failures/warnings, 21 indexed chunks; full reset/run verification pending.
- Free imposes a 180-second interval between on-demand indexer invocations; immediate rerun was rejected, not an authentication failure.
- Live Function agent switch and Basic deletion still require explicit confirmation. No live cutover performed.
- Full Free re-ingestion verified after the required interval: success, eight Blob documents processed, zero failures, zero errors/warnings; execution 2026-10-05 11:44:23-11:44:38 UTC. This proves actual Blob reads and skillset/index-projection processing, not just copied index content.
- User explicitly approved live agent selection change. Function `FOUNDRY_AGENT_NAME` set to `architecture-review-agent-free-test` and verified by app-settings readback. Unauthenticated HTTP endpoint returned 401, confirming responsiveness and authentication enforcement.
- Pending real webhook-triggered Board review. Basic is retained for rollback. Rollback setting: `FOUNDRY_AGENT_NAME=architecture-review-agent`. SAS expiry renewal is required before 2026-11-04.

### Live review and Basic access isolation (2026-10-05)

- Deployed Function completed review `board-191291-bf8f5816-e16b-4cc7-821a-d04773539e29`, operation `ef96a67f8ab0c1404a6b32db49cc9a66`, with seven findings and seven diagram assessments. Parsed request to completed findings took approximately 46 seconds; user confirmed successful Boards feedback.
- User requested retaining Basic while cutting off access from Foundry and other resources, then explicitly approved disabling Basic API-key authentication in addition to RBAC removal.
- Live Function selects `architecture-review-agent-free-test`; all three versions of that agent have only Free Search MCP endpoints. Latest version 3 uses connection `architecture-review-free-test-v2` with project managed identity.
- Aligned the unused Function `AZURE_SEARCH_ENDPOINT` setting to `https://archdesignreview-free-test.search.windows.net`; the application code uses agent selection, not this endpoint setting.
- Removed eleven direct Basic Search assignments: three each for Function `archdesignreview`, Foundry account `mpalanisandbox`, and Foundry project `firstProject` (Search Index Data Reader, Search Index Data Contributor, Search Service Contributor); one reader each for older workspace identities `platformaihub` and `firstplatformproject`.
- Removed Basic Search identity's outbound Storage Blob Data Reader assignment on `rgeuwnlhqssandboxb86c`. Total removals: twelve. Non-sensitive assignment IDs, principals, role definitions and scopes are saved in the session artifact `basic-search-removed-roles-2026-10-05.json` for recovery.
- Basic is still provisioned with Basic SKU and its data/connections retained. Verified zero direct role assignments on Basic, zero direct outbound roles for its managed identity, and `disableLocalAuth=true`. A Basic API-key document-count request returned HTTP 401.
- Free project Search Index Data Reader assignment was preserved. Free document-count request returned HTTP 200 with 21 documents. Function endpoint remained responsive and rejected unauthenticated requests with HTTP 401.
- Inherited tenant/subscription/resource-group administration assignments were deliberately not changed; administrators may still manage Basic or restore permissions. This is application isolation, not a deny-all administrative boundary.
- Post-isolation live test succeeded for item 191302: review `board-191302-aa5e8542-5738-4c6a-9253-b6cdc73ee6ed`, operation `b8c8d06f4aad9bcf318bb512cd8ab59a`. Function ran 13:23:33-13:24:21 UTC (47.755 seconds), called the Free agent endpoint successfully, validated seven findings and seven diagram assessments, and completed Board writeback. Independent work-item readback confirmed High risk / Changes Required and the matching review ID in `System.History`.
- Item 191302 revision 2 changed State and added the tag together, matching the current hook. Item 191299 changed State and added the tag in separate revisions; no matching Function review or Board feedback was found.
- A duplicate delivery of the 191302 event was ignored while its first execution was processing, as intended. This run confirms end-to-end operation after Basic isolation with a Free-only agent configuration; Function traces do not separately expose the individual MCP retrieval calls, so no per-tool trace or managed-identity Basic denial is claimed for this run.
- Basic rollback now requires restoring the needed roles and Search endpoint/agent selection, not merely changing the agent name. API-key authentication need not be restored for managed-identity connections.
- Existing hook was last observed filtering `System.State`, not `System.Tags`; no hook configuration change was approved or made. A tag-only update might not invoke it. Inspect actual event delivery if a new trigger produces no Function telemetry.
- Retaining Basic continues its capacity charges. Free ingestion SAS renewal is still required before 2026-11-04.

---

## 1. Project Overview

**Goal:** Deploy the updated architecture-review Python code to the existing development Function App `archdesignreview`. The update allows the existing test project and `NL_HQ_T_Cloud_CoE`, routes Wiki reads and Board writeback to the project identified by the approved Wiki URL, and starts a review only when the `design review` tag is newly added.

**Path:** Modify an existing Azure application.

**Change type:** Code and application-settings update. Do not create, move, resize, or delete Azure resources.

---

## 2. Requirements

| Attribute | Value |
|-----------|-------|
| Classification | Development/internal demo |
| Scale | Small, fewer than 1,000 review users/events |
| Budget | Balanced; preserve existing resources and remove one unused Python dependency |
| Subscription | `alz-nl-hq-s-ccoeadm-mpalani` |
| Subscription ID | `f565124f-a0f3-4bde-b0e8-dcadc036868b` |
| Resource group | `rg-euw-nl-hq-s-sandbox` |
| Location | Canada Central |
| Existing target | Function App `archdesignreview` |
| Compliance boundary | Preserve existing tenant, subscription, resource group, identities, networking, monitoring, and Azure DevOps approval controls |

### Policy constraints

Validation successfully read 62 policy assignments applicable to the target resource-group scope. This deployment does not submit an ARM resource deployment or change resource configuration; it updates application files on the existing Function App. The deployment must:

- Preserve the existing Function App, hosting plan, identity, networking, TLS, tags, diagnostic settings, and application settings.
- Avoid resource creation, deletion, movement, SKU changes, or public-access changes.
- Preserve compliance with the 62 visible policy assignments by avoiding ARM configuration changes.
- Stop if the deployment command attempts to provision or mutate infrastructure.

---

## 3. Components Detected

| Component | Type | Technology | Path |
|-----------|------|------------|------|
| Architecture review orchestrator | HTTP-triggered Azure Function | Python 3.12, Azure Functions Python v2 programming model | `function-app/` |
| Review agent | Existing prompt agent | Microsoft Foundry Agent Service | Existing project `firstProject` |
| Guidance knowledge | Existing search knowledge tool | Azure AI Search | Existing Search service `archdesignreview` |
| Source and workflow | Existing work tracking | Azure DevOps Wiki, Boards, and service hooks | `Cloud Community of Practice (CoP)` and `NL_HQ_T_Cloud_CoE` |
| Monitoring | Existing APM | Application Insights | `archdesignreview202609131507` |

### Function dependencies

The Function uses:

- `azure-functions`
- `azure-identity`
- `azure-storage-blob`
- `azure-ai-projects`
- `openai`
- `requests`
- `pydantic>=2,<3`

`azure-search-documents` is removed because the Function no longer queries Azure AI Search directly.

### Existing infrastructure

| Item | Status |
|------|--------|
| Existing Function App | Reuse `archdesignreview` |
| Existing resource group | Reuse `rg-euw-nl-hq-s-sandbox` |
| Existing Foundry project and agent | Reuse |
| Existing Azure AI Search service and knowledge connection | Reuse |
| Existing Application Insights | Reuse |
| Existing managed identities and RBAC | Preserve; Function Search roles can be reviewed separately after runtime verification |
| `azure.yaml` | Not present |
| Infrastructure-as-code files | Not present |
| New infrastructure required | No |

---

## 4. Recipe Selection

**Selected:** Azure CLI, update-only Function App code deployment.

**Rationale:**

- The target Function App already exists.
- Previous successful deployments updated this same Function App.
- The repository does not use `azure.yaml`, Bicep, or Terraform.
- The requested change affects Function code, Python dependencies, and documentation only.
- A direct code deployment minimizes risk and preserves existing infrastructure.

**Intended command family:** Azure Functions/App Service zip deployment through Azure CLI, targeting:

```text
subscription: f565124f-a0f3-4bde-b0e8-dcadc036868b
resource group: rg-euw-nl-hq-s-sandbox
Function App: archdesignreview
```

The exact non-interactive deployment command must be resolved and verified during deployment. It must upload only the contents of `function-app/`.

---

## 5. Architecture

**Stack:** Existing serverless Azure Function with Microsoft Foundry Agent Service.

### Service mapping

| Component | Azure service | Deployment action |
|-----------|---------------|-------------------|
| Python orchestrator | Existing Azure Function App `archdesignreview` | Replace application package only |
| Review agent | Existing Foundry project `firstProject`, agent `architecture-review-agent` | No resource deployment; use its existing Search knowledge tool |
| Guidance | Existing Azure AI Search service `archdesignreview` | No deployment |
| Snapshots | Existing Blob Storage configuration | No deployment |
| Telemetry | Existing Application Insights `archdesignreview202609131507` | No deployment |

### Runtime responsibility after deployment

1. The Function receives the authenticated Azure Boards work-item update event.
2. The Function verifies that `design review` was newly added.
3. The Function derives the Azure DevOps project from the Wiki URL and verifies it against `AZURE_DEVOPS_ALLOWED_PROJECTS`.
4. The Function reads the complete linked Wiki page and source revision from that project.
5. The Function sends the complete design plus explicit retrieval requirements to the Foundry agent.
6. The agent retrieves targeted guidance for architecture, security, identity, networking, reliability, operations, governance, and cost.
7. The Function validates, formats, snapshots when configured, and writes the result to the work item in the same approved project.

### Supporting services

| Service | Purpose |
|---------|---------|
| Application Insights | Function requests, traces, dependencies, and exceptions |
| Managed Identity | Function-to-Foundry and Azure service authentication |
| Key Vault reference or protected app setting | Azure DevOps PAT protection |
| Azure AI Search | Agent-owned targeted guidance retrieval |

---

## 6. Provisioning Limit Checklist

No resources are provisioned and no SKU, instance count, compute capacity, IP address, storage account, Search service, or model deployment is added.

| Resource Type | Number to Deploy | Total After Deployment | Limit/Quota | Notes |
|---------------|------------------|------------------------|-------------|-------|
| `Microsoft.Web/sites` | 0 | Existing count unchanged | Not applicable | Code package update to existing `archdesignreview` |
| `Microsoft.Search/searchServices` | 0 | Existing count unchanged | Not applicable | Existing agent knowledge service |
| `Microsoft.CognitiveServices/accounts` | 0 | Existing count unchanged | Not applicable | Existing Foundry account/project |
| `Microsoft.Storage/storageAccounts` | 0 | Existing count unchanged | Not applicable | Existing Function/snapshot storage |
| `Microsoft.Insights/components` | 0 | Existing count unchanged | Not applicable | Existing Application Insights |

**Status:** All resource quantities are zero; quota and regional capacity are unchanged.

---

## 7. Execution Checklist

### Phase 1: Planning

- [x] Analyze workspace.
- [x] Confirm update of the existing Function App only.
- [x] Confirm subscription.
- [x] Confirm the live existing target is in Canada Central.
- [x] Record development classification, small scale, and balanced budget.
- [x] Scan codebase and dependencies.
- [x] Select Azure CLI code-only deployment recipe.
- [x] Confirm no new resources and no quota impact.
- [x] User approved this completed plan on 2026-09-21.

### Phase 2: Preparation

- [x] All validation checks pass.
  - [x] 1. Core validation: Azure CLI installed/authenticated, selected subscription correct, Python syntax/import/package checks pass, and existing Function target is verified. Bicep validate/what-if is not applicable because no infrastructure deployment exists.
  - [x] 2. Focused behavior validation: approved-project routing, case-insensitive tag addition, ignored non-trigger events, and unapproved-project rejection pass.
  - [x] 3. Build verification: production dependencies install into the deployable package and `function_app` imports successfully.
  - [x] 4. Docker build: not applicable because the Python Function is deployed as a zip/code package and has no Dockerfile.
  - [x] 5. Azure Policy validation: policy assignments are read at the target resource-group scope; the deployment does not change ARM resources.
  - [x] 6. Static RBAC verification: no IaC or role assignments change; existing Function identity access is preserved.
- [x] Remove Function-side Azure AI Search code.
- [x] Remove unused `azure-search-documents` dependency.
- [x] Remove obsolete Function Search settings from the local settings example.
- [x] Add agent-owned guidance retrieval requirements to the review package.
- [x] Update architecture and operational documentation.
- [x] Validate the full design is preserved in the package.
- [x] Validate all eight review domains are requested.
- [x] Validate Python syntax and Pylance diagnostics.
- [x] Run Azure validation workflow and populate validation proof.

### Phase 3: Deployment

- [x] Confirm Azure authentication and selected subscription.
- [x] Recheck the existing Function App state.
- [x] Set `AZURE_DEVOPS_ALLOWED_PROJECTS` to `Cloud Community of Practice (CoP),NL_HQ_T_Cloud_CoE`.
- [x] Set `REVIEW_TRIGGER_TAG` to `design review`.
- [x] Create a deployment package containing only the validated Function files.
- [x] Deploy the package to the existing `archdesignreview` Function App.
- [x] Confirm deployment status succeeds.
- [x] Confirm the Function is running and the endpoint remains available.
- [x] Run controlled endpoint tests for ignored and rejected events without Board writeback.
- [x] Verify Application Insights telemetry.
- [x] Preserve Board-only writeback behavior.

---

## 8. Validation Plan

Validation must prove:

1. `function_app.py` has no syntax or Pylance errors.
2. A case-insensitive, whitespace-tolerant new `design review` tag is accepted.
3. Tag removal, unrelated tag changes, and events where the tag already existed return HTTP 200 with `status: ignored`.
4. A Wiki URL from either approved project is accepted and an unapproved project is rejected.
5. Wiki reads and Board writeback use the project parsed from the approved Wiki URL.
6. `build_review_package` includes the complete Wiki design and project.
7. Function host configuration remains valid.
8. The deployment package excludes local settings, virtual environments, cache files, tests, and documentation.
9. The target remains the existing Function App.
10. No infrastructure deployment is required.

---

## 9. Validation Proof

The table below records the preceding deployment. Validation proof for the multi-project tag-trigger update will be appended after the current Azure validation workflow completes.

| Check | Evidence | Result |
|-------|----------|--------|
| Azure authentication | `az account show`; subscription ID matched `f565124f-a0f3-4bde-b0e8-dcadc036868b` | PASS |
| Existing target | ARM GET for `Microsoft.Web/sites/archdesignreview` | PASS: Running, Linux Function App, Canada Central |
| Secure transport | Existing resource property `httpsOnly=true` | PASS |
| Managed identity | Existing system-assigned principal `761e98ac-6ff5-42b6-85c2-ebd397739c99` | PASS |
| Required settings | Read setting names only; all six required names present, 15 settings total | PASS |
| Python syntax | Python 3.12 `py_compile function_app.py` | PASS |
| Dependency resolution | `python -m pip install --dry-run -r requirements.txt` | PASS |
| Deployable build | Installed production dependencies into `.python_packages/lib/site-packages`; imported `function_app`; 4,079 package files built | PASS |
| Function configuration | Parsed `host.json`; Functions extension bundle remains `[4.*, 5.0.0)` | PASS |
| Runtime package behavior | 250-word design preserved; retrieval owner is `foundry-agent`; eight domains present; no `knowledgeContext` | PASS |
| Pylance | File diagnostics and VS Code Problems | PASS: no errors |
| Package contents | Staged only `function_app.py`, `host.json`, and `requirements.txt` | PASS |
| Removed direct Search use | No `SearchClient`, `search_guidance`, Function Search settings, or `azure-search-documents` dependency | PASS |
| Repository diff | `git diff --check` | PASS |
| Azure Policy visibility | Read 62 assignments at target resource-group scope | PASS |
| Docker | No Dockerfile; zip/code deployment | Not applicable |
| Bicep/ARM what-if | No infrastructure template or ARM configuration deployment | Not applicable |
| Static RBAC review | No Bicep/Terraform or role assignment changes. Code still requires existing Foundry invocation and optional Blob write access; direct Search access is removed | PASS |

Only the official Azure validation workflow may change the plan status to `Validated`.

### Multi-project tag-trigger validation - 2026-09-21

| Check | Evidence | Result |
|-------|----------|--------|
| Azure context | `az account show`; user confirmed subscription `f565124f-a0f3-4bde-b0e8-dcadc036868b` and Canada Central | PASS |
| Existing target | `az functionapp show` | PASS: Running Linux Function App, HTTPS only, Canada Central |
| Required settings | Read setting names only; 15 settings and all required names present | PASS |
| Python syntax | Pylance syntax check and Python 3.12 `py_compile` | PASS |
| Pylance diagnostics | `textDocument/diagnostic`, VS Code Problems | PASS: no errors |
| Dependencies | `pip install --dry-run -r requirements.txt` | PASS |
| Approved projects | Focused runtime test for `Cloud Community of Practice (CoP)` and `NL_HQ_T_Cloud_CoE` | PASS |
| Trigger semantics | Case-insensitive new tag accepted; removal, existing tag, and unrelated tag changes ignored | PASS |
| Project rejection | Unapproved Wiki project runtime test | PASS |
| Project-aware writeback | Mocked PATCH URL targeted `NL_HQ_T_Cloud_CoE` work-item API | PASS |
| Signature compatibility | Pylance checked `update_board`; all call sites compatible | PASS |
| Deployable build | Installed production dependencies, imported `function_app`, and staged only three root application files | PASS |
| Package | `archdesignreview-tag-trigger.zip`, 5,813 files, SHA-256 `0752FEC40BE776F7DEDAA4B7BB40B4EEAE716A285D2689D11EF2174416969ECF` | PASS |
| Function configuration | Parsed `host.json`; extension bundle `[4.*, 5.0.0)` | PASS |
| Repository diff | `git diff --check` | PASS |
| Azure Policy visibility | Read 62 assignments at target resource-group scope | PASS |
| Docker and IaC | No Dockerfile or infrastructure directory; code/settings-only update | Not applicable |
| Static RBAC | No IaC, managed identity, or role-assignment changes | PASS |

---

## 10. Deployment and Rollback

### Deployment

- Package only `function-app/`.
- Use a non-interactive Azure CLI Function/App Service zip-deploy operation.
- Update only `AZURE_DEVOPS_ALLOWED_PROJECTS` and `REVIEW_TRIGGER_TAG`; preserve every other application setting.
- Do not delete the obsolete Azure Search setting values during this deployment; they can be cleaned up separately after successful runtime verification.

### Verification

- Confirm the deployment record reports success.
- Confirm the Function host starts without import errors.
- Confirm `architecture_review` is discoverable.
- Confirm a controlled invocation reaches the Foundry agent.
- Confirm Foundry traces show targeted Search knowledge retrieval.
- Confirm the Function writes a valid review to Azure Boards only.

### Rollback

If startup or smoke testing fails:

1. Stop further test events.
2. Redeploy the previous known-good package based on commit `56c62b5`.
3. Confirm the previous Function host starts.
4. Confirm Board event processing returns to the prior behavior.
5. Retain failed deployment logs and correlation IDs for diagnosis.

Rollback does not require resource deletion or infrastructure changes.

---

## 11. Deployment Verification

The table below records the preceding deployment.

| Check | Evidence | Result |
|-------|----------|--------|
| Deployment package | `archdesignreview-search-agent.zip`, SHA-256 `D142BC28ACF41D183125835E4FAB507313DA258BEF3F5EEFAB648285D27D7676` | PASS |
| Azure deployment | Deployment ID `2aa4352b-bec3-40c6-af06-36b7dc1af1c1`, deployer `az_cli_functions`, status `4`, complete `true` | PASS |
| Existing resource preserved | `archdesignreview`, Canada Central, Linux Function App, `httpsOnly=true` | PASS |
| Function discovery | `archdesignreview/architecture_review` returned by the management API | PASS |
| Function endpoint | Authenticated POST to `/api/architecture-review` returned expected HTTP `400` and `The event must include a Board work item id` | PASS |
| Application Insights | Correlation ID `deployment-smoke-20260921`, operation ID `83c11454ba14d092a861b7c27ea778c2` | PASS |
| Foundry agent | Synthetic non-writing request returned schema-valid review ID `deployment-agent-smoke-20260921` | PASS |
| Agent result | Overall risk `Critical`, recommendation `Changes Required`, five findings, ten evidence items | PASS |
| Board safety | Synthetic agent test bypassed Azure DevOps and no Board item was changed | PASS |
| Live Function identity | System-assigned principal `761e98ac-6ff5-42b6-85c2-ebd397739c99` retained six role assignments, including Foundry access | PASS |

### Multi-project tag-trigger deployment - 2026-09-22

| Check | Evidence | Result |
|-------|----------|--------|
| Live settings | `AZURE_DEVOPS_ALLOWED_PROJECTS=Cloud Community of Practice (CoP),NL_HQ_T_Cloud_CoE`; `REVIEW_TRIGGER_TAG=design review` | PASS |
| Deployment package | `archdesignreview-tag-trigger.zip`, SHA-256 `0752FEC40BE776F7DEDAA4B7BB40B4EEAE716A285D2689D11EF2174416969ECF` | PASS |
| Azure deployment | Deployment ID `053a9398-1034-4978-a312-78c25570c4d0`, deployer `az_cli_functions`, status `4`, complete `true` | PASS |
| Existing resource preserved | `archdesignreview`, Canada Central, Linux Function App, `httpsOnly=true`, state `Running` | PASS |
| Function discovery | `archdesignreview/architecture_review` returned by the management API | PASS |
| Ignored-event behavior | Authenticated event where `design review` already existed returned HTTP `200` and `status: ignored` | PASS |
| Project allowlist | Authenticated event for `Unapproved_Project` returned HTTP `400` with the expected rejection | PASS |
| Application Insights | Correlation IDs `deployment-ignored-smoke-20260922` and `deployment-rejected-smoke-20260922` captured with operation IDs | PASS |
| Board safety | Both smoke tests stopped before Wiki retrieval, Foundry invocation, and Board writeback | PASS |
| Live Function identity | Principal `761e98ac-6ff5-42b6-85c2-ebd397739c99` retained six existing role assignments | PASS |

### Live role verification

The Function managed identity retains:

- `Foundry User` on the Foundry account `mpalanisandbox`.
- `Foundry User` and `AzureML Data Scientist` on workspace `firstplatformproject`.
- `Search Index Data Reader`, `Search Index Data Contributor`, and `Search Service Contributor` on Search service `archdesignreview`.

The Function code no longer uses Search directly. The Search assignments were deliberately not removed during this code deployment. Remove or reduce them only after a separate least-privilege change is approved and the agent-only retrieval path has been observed during a real review.

### Deployed endpoint

`https://archdesignreview.azurewebsites.net/api/architecture-review`

---

## 12. Duplicate-event idempotency update

**Goal:** Prevent Azure DevOps webhook retries from invoking the Foundry agent and writing the same Board comment more than once.

**Observed evidence:** Work items `189445` and `189466` each received duplicate processing for one Azure DevOps event ID. The first request exceeded the service-hook response window, and a concurrent retry completed the same review a second time.

**Implementation:**

- Atomically claim the SHA-256 hash of each Azure DevOps event ID in a dedicated Blob container.
- Use the existing `AzureWebJobsStorage` account; do not create or modify an Azure resource.
- Return HTTP `200` with `status: ignored` when the event claim already exists.
- Retain completed claims, recover processing claims older than ten minutes, and release claims after failures that occur before Board writeback.
- Retain a failure marker after an uncertain Board write so an automatic retry cannot create a second comment.
- Do not store design content, credentials, or access tokens in the claim.

**Validation checklist:**

- [x] Python and Pylance syntax checks pass.
- [x] The same event delivered twice invokes Foundry once and writes to Boards once.
- [x] A failed review releases its claim and can be retried.
- [x] A stale processing claim is recovered after ten minutes.
- [x] An uncertain Board write is not automatically retried.
- [x] Production dependencies install and the deployment package imports.
- [x] The package excludes tests, local settings, caches, and documentation.
- [x] Existing Function App configuration, identity, location, and HTTPS settings remain unchanged.

**Deployment checklist:**

- [x] Set `REVIEW_IDEMPOTENCY_CONTAINER=architecture-review-events`.
- [x] Deploy the validated code package to the existing `archdesignreview` Function App.
- [x] Confirm Function discovery and healthy state.
- [x] Seed a safe test event claim and verify a matching request returns HTTP `200` ignored without Wiki, Foundry, or Board calls.
- [x] Verify Application Insights records duplicate suppression.

### Validation proof

| Check | Evidence | Result |
|-------|----------|--------|
| Duplicate diagnosis | Event `c508fb3f-fcf0-4fe8-abb5-dcb895326f6a` completed twice for work item `189466` | CONFIRMED |
| Python syntax | Python 3.12 `py_compile` and Pylance file syntax checks | PASS |
| Duplicate regression | `test_duplicate_event_invokes_review_and_writeback_once` | PASS |
| Failure retry regression | `test_failed_review_releases_event_for_retry` | PASS |
| Worker recovery regression | `test_stale_processing_claim_is_recovered` | PASS |
| Uncertain write regression | `test_uncertain_board_write_is_not_retried` | PASS |
| Dependency resolution | `pip install --dry-run -r requirements.txt` | PASS |
| Deployable build | Production dependencies installed and `function_app` imported | PASS |
| Deployment package | `archdesignreview-idempotency-v2.zip`, 5,841 files, SHA-256 `4CFB9DD8519FE0BFFC90FAA7A1101296DE51ACF891F6958FCA806350907E12C1` | PASS |
| Package roots | `function_app.py`, `host.json`, and `requirements.txt` only | PASS |
| Function target | Existing `archdesignreview`, Running, Canada Central, HTTPS only | PASS |
| Repository diff | `git diff --check` | PASS |
| Function host configuration | Extension bundle `[4.*, 5.0.0)` | PASS |
| Azure Policy visibility | 62 assignments at target resource-group scope | PASS |
| Docker and IaC | No Dockerfile or infrastructure deployment | Not applicable |
| Static RBAC | Existing connection-string access to Function host storage; no role or IaC changes | PASS |

### Deployment proof

| Check | Evidence | Result |
|-------|----------|--------|
| App setting | `REVIEW_IDEMPOTENCY_CONTAINER=architecture-review-events` | PASS |
| Azure deployment | Deployment ID `93596420-3039-4c02-840f-30302628f6c5`, deployer `az_cli_functions`, status `4`, complete `true` | PASS |
| Existing resource preserved | `archdesignreview`, Running, Canada Central, HTTPS only | PASS |
| Function discovery | `archdesignreview/architecture_review` returned by the management API | PASS |
| Live duplicate suppression | Pre-claimed event returned HTTP `200` and `status: ignored` with reason `already accepted` | PASS |
| Side-effect prevention | Duplicate stopped before the parsed-request, Wiki-fetch, Foundry, and Board-write stages | PASS |
| Application Insights | Correlation ID `idempotency-v2-live-smoke-20260922`, operation ID `d3d6328e7eae79a8ca0a7ed0ad923e49` | PASS |
| Test cleanup | Synthetic event claim deleted after verification | PASS |
| Live Function identity | Principal `761e98ac-6ff5-42b6-85c2-ebd397739c99` retained six role assignments | PASS |

---

## 13. Wiki diagram vision review

**Goal:** Include embedded Azure DevOps Wiki PNG diagrams in the same architecture review as the written design.

**Implementation:**

- Extract embedded `/.attachments/*.png` references from Wiki Markdown and HTML.
- Download each PNG from the approved Wiki Git repository using the existing Azure DevOps credential.
- Reject external, missing, invalid, oversized, or excessive PNG inputs instead of silently skipping them.
- Send the complete design text and every PNG to the `gpt-4.1` Foundry agent as high-detail vision inputs.
- Require exactly one `diagramAssessments` entry for every supplied filename.
- Show diagram summaries and issues in the formatted Board result.

**Limits:** 10 PNGs, 15 MB per image, and 50 MB total.

**Foundry agent:** Version `7` is active with the existing `gpt-4.1` model and two existing tools. Its response contract now requires a named assessment for every supplied diagram.

**Validation checklist:**

- [x] Python and Pylance syntax checks pass.
- [x] PNG extraction, validation, download, request construction, and response validation tests pass.
- [x] Existing idempotency tests pass.
- [x] The live Wiki page yields four PNGs through the Azure DevOps Git Items API.
- [x] A non-writing Foundry test returns one assessment for each of the four exact filenames.
- [x] Production dependencies install and the deployment package imports.
- [x] The package excludes tests, local settings, caches, and documentation.

**Deployment checklist:**

- [x] Deploy the validated image-aware package to the existing `archdesignreview` Function App.
- [x] Confirm Function discovery, running state, HTTPS-only status, and unchanged identity.
- [x] Verify a Board-safe live request downloads four PNGs and completes the agent review.
- [x] Verify Application Insights records image count, total image bytes, and review completion.

### Validation proof

| Check | Evidence | Result |
|-------|----------|--------|
| Python syntax | Python 3.12 `py_compile` and Pylance file syntax checks | PASS |
| Unit tests | 9 tests covering idempotency and Wiki PNG handling | PASS |
| Live Wiki images | Page `7521` returned four `/.attachments/*.png` references | PASS |
| Image download | Azure DevOps Git Items API returned PNG content; live total 1,472,078 bytes | PASS |
| Foundry model | Agent version `7`, model `gpt-4.1`, two existing tools | PASS |
| Vision invocation | Four images sent as `input_image` with `detail=high` | PASS |
| Diagram contract | Four exact input filenames matched four returned `diagramAssessments` entries | PASS |
| Board safety | Live vision tests used work item `0` and bypassed Board writeback | PASS |
| Deployable build | Production dependencies installed and `function_app` imported | PASS |
| Deployment package | `archdesignreview-vision-v2.zip`, 5,841 files, SHA-256 `D67C5B92D34CDC5EBA30BFFCBAA57D413764EDD411CC55B2A3CD6188D0A41822` | PASS |
| Package roots | `function_app.py`, `host.json`, and `requirements.txt` only | PASS |
| Existing target | Running, Canada Central, HTTPS only, identity unchanged | PASS |
| Azure Policy visibility | 62 assignments at target resource-group scope | PASS |
| Infrastructure | No resource, role, dependency-manifest, or infrastructure changes | PASS |

### Deployment proof

| Check | Evidence | Result |
|-------|----------|--------|
| Azure deployment | Deployment ID `2badb5a1-faef-4c8b-98f5-16f665a496a5`, deployer `az_cli_functions`, status `4`, complete `true` | PASS |
| Existing resource preserved | `archdesignreview`, Running, HTTPS only, system-assigned identity unchanged | PASS |
| Function discovery | `archdesignreview/architecture_review` returned by the management API | PASS |
| Live Wiki retrieval | Revision `916dbadbd1e5f7f3e8a7e43c67ca444ea24a1c35`, 65,431 characters | PASS |
| Live diagram retrieval | Four PNGs downloaded, totaling 1,472,078 bytes | PASS |
| Foundry vision result | Eight findings and four diagram assessments returned | PASS |
| Application Insights | Correlation ID `vision-final-smoke-20260922-2028`, operation ID `12d942447c7a97194789f7555a9a12b4` | PASS |
| Board safety | Request used nonexistent work item `-1`; expected HTTP `502` occurred only at the final Board PATCH | PASS |
| Test cleanup | Both synthetic vision-test event claims were deleted | PASS |

---

## 14. Diagram display-name update

**Goal:** Show the Wiki image caption or HTML alt text in each diagram assessment instead of an Azure DevOps-generated attachment filename.

### Validation proof

| Check | Evidence | Result |
|-------|----------|--------|
| Caption parsing | Regression input `SAP Management Servers - Prod Environment` maps to the expected display name while retaining the original attachment path | PASS |
| PNG behavior | Markdown and HTML image extraction, deduplication, validation, download, and high-detail Foundry input tests | PASS |
| Unit tests | 10 tests covering idempotency, Wiki PNG handling, and human-readable diagram names | PASS |
| Pylance syntax | `function_app.py` and `test_wiki_images.py` | PASS |
| Build verification | Production `function_app` import | PASS |
| Repository diff | `git diff --check` | PASS |
| Static RBAC | No infrastructure, identity, role-assignment, or application-setting changes | PASS |

### Deployment proof

| Check | Evidence | Result |
|-------|----------|--------|
| Deployment package | `archdesignreview-diagram-names.zip`, SHA-256 `BC0CC271AB0D5BDD455A284E87C11CE2543340D19EF4A2363542A01384BD4871` | PASS |
| Azure deployment | Deployment ID `2e9b37a7-e955-4309-8235-2aab3da0d052`, status `4`, complete `true` | PASS |
| Live Wiki names | Four diagram headings resolved, including `SAP Management Servers - Prod Environment` | PASS |
| Foundry review | Six findings and four exact diagram assessments returned | PASS |
| Application Insights | Operation ID `8eefd8498cafe17fb9477656a8394676` | PASS |
| Board safety | Smoke test used nonexistent work item `-1`; expected failure occurred only at final Board write | PASS |
| Test cleanup | Both synthetic diagram-name event claims were deleted | PASS |
