import base64
import html
import json
import logging
import os
import re
from typing import Any
from urllib.parse import quote, unquote, urlparse

import azure.functions as func
import requests
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from pydantic import BaseModel, ConfigDict, Field, ValidationError

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
logger = logging.getLogger(__name__)

WIKI_URL_PATTERN = re.compile(r"/_wiki/wikis/([^/]+)(?:/([^?#]+))?", re.IGNORECASE)


class Finding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str | None = None
    severity: str
    category: str
    description: str
    impact: str
    recommendation: str
    evidence: list[str] = Field(default_factory=list)


class ReviewResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewId: str
    sourceRevision: str
    summary: str | None = None
    overallRisk: str
    recommendation: str
    findings: list[Finding] = Field(default_factory=list)
    missingInformation: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    event_id: str
    work_item_id: int
    wiki_url: str


class WikiDocument(BaseModel):
    content: str
    revision: str
    url: str


class WikiReference(BaseModel):
    project: str
    wiki_id: str
    page_id: int | None = None
    path: str | None = None


@app.function_name(name="architecture_review")
@app.route(route="architecture-review", methods=["POST"])
def architecture_review(req: func.HttpRequest) -> func.HttpResponse:
    correlation_id = req.headers.get("x-correlation-id") or req.headers.get("x-ms-invocation-id") or "unknown"
    logger.info("Architecture review started correlation_id=%s", correlation_id)

    try:
        payload = req.get_json()
        request = parse_review_request(payload)
        logger.info("Parsed request: work_item_id=%s wiki_url=%s", request.work_item_id, request.wiki_url)
        wiki = get_wiki_document(request.wiki_url)
        logger.info("Wiki document fetched: revision=%s length=%d", wiki.revision, len(wiki.content))
        guidance = search_guidance(wiki.content)
        logger.info("Guidance search returned %d results", len(guidance))
        package = build_review_package(request, wiki, guidance)
        save_snapshot(request.event_id, "input.json", package)
        result = invoke_foundry(package)
        save_snapshot(request.event_id, "result.json", result.model_dump())
        update_board(request.work_item_id, result)
    except (ValueError, ValidationError) as error:
        logger.warning("Invalid architecture review request correlation_id=%s error=%s", correlation_id, error)
        return json_response({"error": str(error)}, status_code=400)
    except requests.RequestException as error:
        logger.exception("External service failure correlation_id=%s error=%s", correlation_id, error)
        return json_response({"error": f"External service failure: {error}", "correlationId": correlation_id}, status_code=502)
    except Exception:
        logger.exception("Architecture review failed correlation_id=%s", correlation_id)
        return json_response({"error": "Architecture review failed", "correlationId": correlation_id}, status_code=500)

    logger.info("Architecture review completed correlation_id=%s review_id=%s", correlation_id, result.reviewId)
    return json_response({"status": "completed", "reviewId": result.reviewId, "workItemId": request.work_item_id})


def extract_wiki_url(text: str | None) -> str | None:
    """Extract a wiki URL from HTML or mixed text that may include a description snippet."""
    if not text:
        return None

    if text.strip().startswith("https://") and "<" not in text:
        cleaned = text.strip().rstrip(".,)")
        if WIKI_URL_PATTERN.search(cleaned):
            return cleaned

    # Exclude '&' too: HTML-encoded quotes (e.g. &quot;) never appear as a literal
    # boundary char, so without this the match bleeds into the next URL/text.
    match = re.search(r"https?://[^\s<>\"'&]+/_wiki/wikis/[^\s<>\"'&]*", text)
    if match:
        url = match.group(0).rstrip(".,)>")
        url = re.sub(r"<.*$", "", url).rstrip("/")
        return url

    return None


def parse_review_request(payload: dict[str, Any]) -> ReviewRequest:
    resource = payload.get("resource") or {}
    revision = resource.get("revision") or {}
    revision_fields = revision.get("fields") or {}
    change_fields = resource.get("fields") or {}

    work_item_id = (
        resource.get("workItemId")
        or revision.get("id")
        or payload.get("workItemId")
        or payload.get("resourceId")
    )

    raw_wiki = (
        payload.get("wikiUrl")
        or revision_fields.get("Custom.WikiUrl")
        or revision_fields.get("System.Description")
        or change_fields.get("Custom.WikiUrl", {}).get("newValue")
        or change_fields.get("System.Description", {}).get("newValue")
    )
    wiki_url = extract_wiki_url(raw_wiki) if isinstance(raw_wiki, str) else None

    if not payload.get("id"):
        raise ValueError("The event must include an event id")
    if not work_item_id:
        raise ValueError("The event must include a Board work item id")
    if not wiki_url or not WIKI_URL_PATTERN.search(wiki_url):
        raise ValueError(f"The event must include a valid Azure DevOps Wiki URL (got: {raw_wiki[:200] if raw_wiki else 'None'})")

    return ReviewRequest(event_id=str(payload["id"]), work_item_id=int(work_item_id), wiki_url=wiki_url)


def parse_wiki_reference(wiki_url: str) -> WikiReference:
    parsed = urlparse(wiki_url)
    match = WIKI_URL_PATTERN.search(parsed.path)
    if not match:
        raise ValueError("Unable to parse the Wiki URL")

    wiki_id = unquote(match.group(1))
    page_part = unquote(match.group(2) or "").strip("/")
    project_part = parsed.path.split("/_wiki/", 1)[0].strip("/").split("/")
    raw_project = project_part[-1] if project_part else ""
    if not raw_project:
        raise ValueError("Wiki URL does not contain a project")

    project = quote(unquote(raw_project), safe="")
    if page_part:
        first_segment, _, remaining_path = page_part.partition("/")
        if first_segment.isdigit():
            return WikiReference(
                project=project,
                wiki_id=wiki_id,
                page_id=int(first_segment),
                path=f"/{remaining_path}" if remaining_path else None,
            )
        return WikiReference(project=project, wiki_id=wiki_id, path=f"/{page_part}")

    return WikiReference(project=project, wiki_id=wiki_id, path="/")


def get_wiki_document(wiki_url: str) -> WikiDocument:
    wiki = parse_wiki_reference(wiki_url)
    encoded_wiki_id = quote(wiki.wiki_id, safe="")
    logger.info(
        "Fetching wiki: project=%s wiki_id=%s page_id=%s path=%s",
        wiki.project,
        wiki.wiki_id,
        wiki.page_id,
        wiki.path,
    )

    api_url = (
        f"{os.environ['AZURE_DEVOPS_ORG_URL'].rstrip('/')}/{wiki.project}"
        f"/_apis/wiki/wikis/{encoded_wiki_id}/pages"
    )
    params = {"includeContent": "true", "api-version": "7.1-preview.1"}
    if wiki.page_id is not None:
        api_url = f"{api_url}/{wiki.page_id}"
    elif wiki.path:
        params["path"] = wiki.path

    response = requests.get(
        api_url,
        params=params,
        headers=devops_headers(),
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    content = data.get("content")
    if not content:
        raise ValueError("The Wiki page has no content")
    revision = response.headers.get("ETag", data.get("eTag", "unknown")).strip('"')
    return WikiDocument(content=content, revision=revision, url=wiki_url)


def search_guidance(design_content: str) -> list[dict[str, str]]:
    endpoint = os.environ.get("AZURE_SEARCH_ENDPOINT")
    index_name = os.environ.get("AZURE_SEARCH_INDEX")
    if not endpoint or not index_name:
        return []

    terms = " ".join(design_content.split()[:120])
    client = SearchClient(endpoint=endpoint, index_name=index_name, credential=DefaultAzureCredential())
    results = client.search(
        search_text=terms,
        top=8,
        select=["title", "chunk", "metadata_storage_path"],
    )
    return [
        {
            "title": result.get("title", ""),
            "content": result.get("chunk", ""),
            "sourcePath": result.get("metadata_storage_path", ""),
        }
        for result in results
    ]


def build_review_package(request: ReviewRequest, wiki: WikiDocument, guidance: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "reviewId": f"board-{request.work_item_id}-{request.event_id}",
        "sourceRevision": wiki.revision,
        "wikiUrl": wiki.url,
        "boardItemId": request.work_item_id,
        "design": {"content": wiki.content, "attachments": []},
        "knowledgeContext": {"searchIndex": os.environ.get("AZURE_SEARCH_INDEX"), "results": guidance},
        "constraints": {
            "writeFindingsToBoardOnly": True,
            "doNotModifyWiki": True,
            "humanApprovalRequired": True,
        },
    }


def invoke_foundry(package: dict[str, Any]) -> ReviewResult:
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_AGENT_NAME"]
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential(), allow_preview=True)
    openai_client = project_client.get_openai_client(agent_name=agent_name)
    response = openai_client.responses.create(
        input=json.dumps(package),
    )
    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise ValueError("Foundry agent returned no text output")
    try:
        return ReviewResult.model_validate(json.loads(strip_code_fences(output_text)))
    except (json.JSONDecodeError, ValidationError) as error:
        raise ValueError(f"Foundry agent returned invalid review JSON: {error}") from error


def save_snapshot(event_id: str, name: str, value: dict[str, Any]) -> None:
    endpoint = os.environ.get("AZURE_STORAGE_BLOB_ENDPOINT")
    container = os.environ.get("REVIEW_SNAPSHOT_CONTAINER")
    if not endpoint or not container:
        logger.info("Snapshot storage is not configured; skipping snapshot name=%s", name)
        return

    client = BlobServiceClient(account_url=endpoint, credential=DefaultAzureCredential())
    blob = client.get_blob_client(container=container, blob=f"{event_id}/{name}")
    blob.upload_blob(json.dumps(value, ensure_ascii=False), overwrite=True)


def update_board(work_item_id: int, result: ReviewResult) -> None:
    org_url = os.environ["AZURE_DEVOPS_ORG_URL"].rstrip("/")
    project = os.environ["AZURE_DEVOPS_PROJECT"]
    api_url = f"{org_url}/{project}/_apis/wit/workitems/{work_item_id}"
    history = format_review_history(result)
    patch = [{"op": "add", "path": "/fields/System.History", "value": history}]
    response = requests.patch(
        api_url,
        params={"api-version": "7.1"},
        headers={**devops_headers(), "Content-Type": "application/json-patch+json"},
        data=json.dumps(patch),
        timeout=30,
    )
    response.raise_for_status()


def format_review_history(result: ReviewResult) -> str:
    findings_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(finding.id)}</td>"
        f"<td>{html.escape(finding.severity)}</td>"
        f"<td>{html.escape(finding.category)}</td>"
        f"<td>{html.escape(finding.title or finding.description)}</td>"
        f"<td>{html.escape(finding.recommendation)}</td>"
        "</tr>"
        for finding in result.findings
    )
    findings_table = (
        "<table>"
        "<thead><tr><th>ID</th><th>Severity</th><th>Category</th><th>Finding</th><th>Recommendation</th></tr></thead>"
        f"<tbody>{findings_rows}</tbody>"
        "</table>"
        if result.findings
        else "<p>No findings returned.</p>"
    )

    details = "\n".join(format_finding_detail(finding) for finding in result.findings)
    summary = f"<p>{html.escape(result.summary)}</p>" if result.summary else ""

    return (
        "<h2>Architecture Review Result</h2>"
        f"<p><strong>Review ID:</strong> {html.escape(result.reviewId)}</p>"
        f"<p><strong>Source revision:</strong> {html.escape(result.sourceRevision)}</p>"
        f"<p><strong>Overall risk:</strong> {html.escape(result.overallRisk)}</p>"
        f"<p><strong>Recommendation:</strong> {html.escape(result.recommendation)}</p>"
        f"{summary}"
        "<h3>Findings summary</h3>"
        f"{findings_table}"
        "<h3>Detailed findings</h3>"
        f"{details if details else '<p>No detailed findings.</p>'}"
        "<h3>Missing information</h3>"
        f"{format_html_list(result.missingInformation, 'No missing information identified.')}"
        "<h3>Assumptions</h3>"
        f"{format_html_list(result.assumptions, 'No assumptions returned.')}"
    )


def format_finding_detail(finding: Finding) -> str:
    title = finding.title or finding.description
    return (
        f"<h4>{html.escape(finding.id)} - {html.escape(title)}</h4>"
        f"<p><strong>Severity:</strong> {html.escape(finding.severity)} | "
        f"<strong>Category:</strong> {html.escape(finding.category)}</p>"
        f"<p><strong>Description:</strong> {html.escape(finding.description)}</p>"
        f"<p><strong>Impact:</strong> {html.escape(finding.impact)}</p>"
        f"<p><strong>Recommendation:</strong> {html.escape(finding.recommendation)}</p>"
        "<p><strong>Evidence:</strong></p>"
        f"{format_html_list(finding.evidence, 'No evidence provided.')}"
    )


def format_html_list(items: list[str], empty_message: str) -> str:
    if not items:
        return f"<p>{html.escape(empty_message)}</p>"
    return "<ul>" + "".join(f"<li>{html.escape(item)}</li>" for item in items) + "</ul>"


def devops_headers() -> dict[str, str]:
    token = os.environ.get("AZURE_DEVOPS_PAT")
    if not token:
        raise ValueError("AZURE_DEVOPS_PAT is not configured")
    encoded = base64.b64encode(f":{token}".encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def strip_code_fences(value: str) -> str:
    value = value.strip()
    if value.startswith("```") and value.endswith("```"):
        value = value.split("\n", 1)[1].rsplit("```", 1)[0]
    return value.strip()


def json_response(body: dict[str, Any], status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(json.dumps(body), status_code=status_code, mimetype="application/json")
