# Azure Deployment Plan

> **Status:** Deployed

Generated: 2026-09-21

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
