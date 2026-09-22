import base64
import hashlib
import html
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote, unquote, urlparse
from uuid import uuid4

import azure.functions as func
import requests
from azure.ai.projects import AIProjectClient
from azure.core import MatchConditions
from azure.core.exceptions import AzureError, ResourceExistsError, ResourceModifiedError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from pydantic import BaseModel, ConfigDict, Field, ValidationError

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
logger = logging.getLogger(__name__)

WIKI_URL_PATTERN = re.compile(r"/_wiki/wikis/([^/]+)(?:/([^?#]+))?", re.IGNORECASE)
EVENT_CLAIM_STALE_AFTER = timedelta(minutes=10)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_WIKI_IMAGES = 10
MAX_WIKI_IMAGE_BYTES = 15 * 1024 * 1024
MAX_WIKI_IMAGES_TOTAL_BYTES = 50 * 1024 * 1024


class IgnoredEvent(Exception):
    pass


@dataclass(frozen=True)
class ReviewEventClaim:
    event_id: str
    token: str
    blob: Any
    etag: str


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


class DiagramAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    imageName: str
    summary: str
    issues: list[str] = Field(default_factory=list)


class ReviewResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reviewId: str
    sourceRevision: str
    summary: str | None = None
    overallRisk: str
    recommendation: str
    findings: list[Finding] = Field(default_factory=list)
    diagramAssessments: list[DiagramAssessment] = Field(default_factory=list)
    missingInformation: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    event_id: str
    work_item_id: int
    wiki_url: str
    devops_project: str
    trigger_tag: str


class WikiImage(BaseModel):
    name: str
    source_path: str
    media_type: str
    content: bytes


class WikiImageReference(BaseModel):
    display_name: str
    source_path: str


class WikiDocument(BaseModel):
    content: str
    revision: str
    url: str
    images: list[WikiImage] = Field(default_factory=list)


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
    request: ReviewRequest | None = None
    event_claim: ReviewEventClaim | None = None
    review_completed = False
    board_update_started = False

    try:
        payload = req.get_json()
        request = parse_review_request(payload)
        event_claim = claim_review_event(request.event_id)
        logger.info(
            "Parsed request: work_item_id=%s project=%s trigger_tag=%s wiki_url=%s",
            request.work_item_id,
            request.devops_project,
            request.trigger_tag,
            request.wiki_url,
        )
        wiki = get_wiki_document(request.wiki_url)
        logger.info(
            "Wiki document fetched: revision=%s length=%d images=%d image_bytes=%d",
            wiki.revision,
            len(wiki.content),
            len(wiki.images),
            sum(len(image.content) for image in wiki.images),
        )
        package = build_review_package(request, wiki)
        save_snapshot(request.event_id, "input.json", package)
        result = invoke_foundry(package, wiki.images)
        logger.info(
            "Foundry review returned: review_id=%s findings=%d diagram_assessments=%d",
            result.reviewId,
            len(result.findings),
            len(result.diagramAssessments),
        )
        save_snapshot(request.event_id, "result.json", result.model_dump())
        board_update_started = True
        update_board(request.devops_project, request.work_item_id, result)
        complete_review_event(event_claim)
        review_completed = True
    except IgnoredEvent as event:
        logger.info("Architecture review event ignored correlation_id=%s reason=%s", correlation_id, event)
        return json_response({"status": "ignored", "reason": str(event)})
    except (ValueError, ValidationError) as error:
        logger.warning("Invalid architecture review request correlation_id=%s error=%s", correlation_id, error)
        return json_response({"error": str(error)}, status_code=400)
    except requests.RequestException as error:
        logger.exception("External service failure correlation_id=%s error=%s", correlation_id, error)
        return json_response({"error": f"External service failure: {error}", "correlationId": correlation_id}, status_code=502)
    except Exception:
        logger.exception("Architecture review failed correlation_id=%s", correlation_id)
        return json_response({"error": "Architecture review failed", "correlationId": correlation_id}, status_code=500)
    finally:
        if event_claim and not review_completed:
            if board_update_started:
                mark_review_event_failed_after_write(event_claim)
            else:
                release_review_event(event_claim)

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
    trigger_tag = os.environ.get("REVIEW_TRIGGER_TAG", "design review").strip()
    tag_change = change_fields.get("System.Tags") or {}
    new_tags = parse_tags(tag_change.get("newValue"))
    old_tags = parse_tags(tag_change.get("oldValue"))

    if not payload.get("id"):
        raise ValueError("The event must include an event id")
    if not work_item_id:
        raise ValueError("The event must include a Board work item id")
    if not wiki_url or not WIKI_URL_PATTERN.search(wiki_url):
        raise ValueError(f"The event must include a valid Azure DevOps Wiki URL (got: {raw_wiki[:200] if raw_wiki else 'None'})")
    if not trigger_tag:
        raise ValueError("REVIEW_TRIGGER_TAG must not be empty")
    normalized_trigger_tag = trigger_tag.casefold()
    if normalized_trigger_tag not in new_tags:
        raise IgnoredEvent(f"The '{trigger_tag}' tag was not added")
    if normalized_trigger_tag in old_tags:
        raise IgnoredEvent(f"The work item already had the '{trigger_tag}' tag")

    wiki = parse_wiki_reference(wiki_url)
    validate_allowed_project(wiki.project)
    return ReviewRequest(
        event_id=str(payload["id"]),
        work_item_id=int(work_item_id),
        wiki_url=wiki_url,
        devops_project=wiki.project,
        trigger_tag=trigger_tag,
    )


def parse_tags(value: Any) -> set[str]:
    if not isinstance(value, str):
        return set()
    return {tag.strip().casefold() for tag in value.split(";") if tag.strip()}


def validate_allowed_project(project: str) -> None:
    configured_projects = os.environ.get("AZURE_DEVOPS_ALLOWED_PROJECTS") or os.environ.get("AZURE_DEVOPS_PROJECT")
    if not configured_projects:
        raise ValueError("AZURE_DEVOPS_ALLOWED_PROJECTS is not configured")

    allowed_projects = {value.strip().casefold() for value in configured_projects.split(",") if value.strip()}
    if project.casefold() not in allowed_projects:
        raise ValueError(f"Azure DevOps project '{project}' is not approved for architecture reviews")


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

    project = unquote(raw_project)
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
        f"{os.environ['AZURE_DEVOPS_ORG_URL'].rstrip('/')}/{quote(wiki.project, safe='')}"
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
    images = get_wiki_images(wiki, content)
    return WikiDocument(content=content, revision=revision, url=wiki_url, images=images)


def get_wiki_images(wiki: WikiReference, content: str) -> list[WikiImage]:
    image_references = extract_wiki_png_references(content)
    if len(image_references) > MAX_WIKI_IMAGES:
        raise ValueError(
            f"The Wiki page contains {len(image_references)} PNG images; the maximum is {MAX_WIKI_IMAGES}"
        )

    images: list[WikiImage] = []
    total_bytes = 0
    for reference in image_references:
        image = download_wiki_png(wiki, reference.source_path, reference.display_name)
        total_bytes += len(image.content)
        if total_bytes > MAX_WIKI_IMAGES_TOTAL_BYTES:
            raise ValueError(
                f"The Wiki PNG images exceed the {MAX_WIKI_IMAGES_TOTAL_BYTES // (1024 * 1024)} MB total limit"
            )
        images.append(image)
    return images


def extract_wiki_png_paths(content: str) -> list[str]:
    return [reference.source_path for reference in extract_wiki_png_references(content)]


def extract_wiki_png_references(content: str) -> list[WikiImageReference]:
    raw_references: list[tuple[int, str, str]] = [
        (match.start(), match.group(1), match.group(2))
        for match in re.finditer(
            r"!\[([^\]]*)\]\(\s*<?([^)\s>]+\.png(?:\?[^)\s>]*)?)>?(?:\s+[^)]*)?\)",
            content,
            re.IGNORECASE,
        )
    ]
    for match in re.finditer(r"<img\b[^>]*>", content, re.IGNORECASE):
        image_tag = match.group(0)
        source_match = re.search(r"\bsrc=[\"']([^\"']+\.png(?:\?[^\"']*)?)[\"']", image_tag, re.IGNORECASE)
        if not source_match:
            continue
        alt_match = re.search(r"\balt=[\"']([^\"']*)[\"']", image_tag, re.IGNORECASE)
        raw_references.append((match.start(), alt_match.group(1) if alt_match else "", source_match.group(1)))

    references: list[WikiImageReference] = []
    used_paths: set[str] = set()
    used_names: set[str] = set()
    for position, raw_display_name, raw_source in sorted(raw_references):
        parsed = urlparse(html.unescape(raw_source))
        source_path = unquote(parsed.path)
        if not source_path.startswith("/.attachments/"):
            raise ValueError(f"Unsupported PNG reference '{raw_source}'; use a Wiki attachment")
        if source_path in used_paths:
            continue

        fallback_name = source_path.rsplit("/", 1)[-1]
        base_display_name = get_wiki_image_display_name(content, position, raw_display_name, fallback_name)
        display_name = base_display_name
        suffix = 2
        while display_name.casefold() in used_names:
            display_name = f"{base_display_name} ({suffix})"
            suffix += 1

        references.append(WikiImageReference(display_name=display_name, source_path=source_path))
        used_paths.add(source_path)
        used_names.add(display_name.casefold())
    return references


def get_wiki_image_display_name(content: str, position: int, raw_display_name: str, fallback_name: str) -> str:
    display_name = html.unescape(raw_display_name).strip()
    if display_name.casefold() not in {"", "image", "image.png"}:
        return display_name

    preceding_lines = content[:position].splitlines()
    for line in reversed(preceding_lines):
        if not line.strip():
            continue
        heading = re.match(r"^\s{0,3}#{1,6}\s*_?\s*(.*?)\s*_?\s*$", line)
        if heading:
            heading_text = heading.group(1).strip().strip("_*").strip()
            if heading_text:
                return heading_text
        break
    return fallback_name


def download_wiki_png(wiki: WikiReference, source_path: str, display_name: str | None = None) -> WikiImage:
    api_url = (
        f"{os.environ['AZURE_DEVOPS_ORG_URL'].rstrip('/')}/{quote(wiki.project, safe='')}"
        f"/_apis/git/repositories/{quote(wiki.wiki_id, safe='')}/items"
    )
    response = requests.get(
        api_url,
        params={"path": source_path, "includeContent": "true", "api-version": "7.1"},
        headers=devops_headers(),
        timeout=30,
        stream=True,
    )
    response.raise_for_status()

    declared_length = response.headers.get("Content-Length")
    if declared_length and int(declared_length) > MAX_WIKI_IMAGE_BYTES:
        raise ValueError(f"Wiki image '{source_path}' exceeds the {MAX_WIKI_IMAGE_BYTES // (1024 * 1024)} MB limit")

    chunks: list[bytes] = []
    downloaded = 0
    for chunk in response.iter_content(chunk_size=64 * 1024):
        downloaded += len(chunk)
        if downloaded > MAX_WIKI_IMAGE_BYTES:
            raise ValueError(f"Wiki image '{source_path}' exceeds the {MAX_WIKI_IMAGE_BYTES // (1024 * 1024)} MB limit")
        chunks.append(chunk)

    image_content = b"".join(chunks)
    if not image_content.startswith(PNG_SIGNATURE):
        raise ValueError(f"Wiki image '{source_path}' is not a valid PNG")
    return WikiImage(
        name=display_name or source_path.rsplit("/", 1)[-1],
        source_path=source_path,
        media_type="image/png",
        content=image_content,
    )


def build_review_package(request: ReviewRequest, wiki: WikiDocument) -> dict[str, Any]:
    return {
        "reviewId": f"board-{request.work_item_id}-{request.event_id}",
        "sourceRevision": wiki.revision,
        "wikiUrl": wiki.url,
        "boardItemId": request.work_item_id,
        "azureDevOpsProject": request.devops_project,
        "design": {
            "content": wiki.content,
            "attachments": [
                {
                    "name": image.name,
                    "sourcePath": image.source_path,
                    "mediaType": image.media_type,
                    "sizeBytes": len(image.content),
                    "includedAsVisionInput": True,
                }
                for image in wiki.images
            ],
        },
        "guidanceRetrieval": {
            "owner": "foundry-agent",
            "useConfiguredKnowledgeTool": True,
            "requiredDomains": [
                "architecture",
                "security",
                "identity",
                "networking",
                "reliability",
                "operations",
                "governance",
                "cost",
            ],
            "requirements": [
                "Review the complete design before choosing search queries.",
                "Review every supplied architecture diagram as a high-detail vision input.",
                "Compare each diagram with the written design and report omissions, contradictions, insecure flows, and architectural errors.",
                "Use focused searches for each applicable review domain.",
                "Ground every finding in retrieved guidance or explicit design evidence.",
                "Include the relevant source or design section in each finding's evidence.",
            ],
        },
        "diagramReview": {
            "required": bool(wiki.images),
            "requiredImages": [image.name for image in wiki.images],
            "requirements": [
                "Visually inspect every supplied image.",
                "Compare every diagram with the written design.",
                "Identify incorrect or missing components, trust boundaries, network flows, security controls, dependencies, and failure paths.",
                "Return exactly one diagramAssessments entry for every required image, using the exact imageName.",
                "Use an empty issues list only when no diagram issue is found.",
            ],
        },
        "constraints": {
            "writeFindingsToBoardOnly": True,
            "doNotModifyWiki": True,
            "humanApprovalRequired": True,
        },
    }


def invoke_foundry(package: dict[str, Any], images: list[WikiImage] | None = None) -> ReviewResult:
    endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_AGENT_NAME"]
    project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential(), allow_preview=True)
    openai_client = project_client.get_openai_client(agent_name=agent_name)
    content: list[dict[str, Any]] = [{"type": "input_text", "text": json.dumps(package)}]
    for image in images or []:
        encoded_image = base64.b64encode(image.content).decode("ascii")
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:{image.media_type};base64,{encoded_image}",
                "detail": "high",
            }
        )
    response = openai_client.responses.create(input=[{"role": "user", "content": content}])
    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise ValueError("Foundry agent returned no text output")
    try:
        result = ReviewResult.model_validate(json.loads(strip_code_fences(output_text)))
    except (json.JSONDecodeError, ValidationError) as error:
        raise ValueError(f"Foundry agent returned invalid review JSON: {error}") from error
    validate_diagram_assessments(result, images or [])
    return result


def validate_diagram_assessments(result: ReviewResult, images: list[WikiImage]) -> None:
    required_names = {image.name for image in images}
    returned_names = {assessment.imageName for assessment in result.diagramAssessments}
    if returned_names != required_names:
        missing = sorted(required_names - returned_names)
        unexpected = sorted(returned_names - required_names)
        raise ValueError(
            f"Foundry agent diagram assessments do not match the supplied images; "
            f"missing={missing}, unexpected={unexpected}"
        )


def save_snapshot(event_id: str, name: str, value: dict[str, Any]) -> None:
    endpoint = os.environ.get("AZURE_STORAGE_BLOB_ENDPOINT")
    container = os.environ.get("REVIEW_SNAPSHOT_CONTAINER")
    if not endpoint or not container:
        logger.info("Snapshot storage is not configured; skipping snapshot name=%s", name)
        return

    client = BlobServiceClient(account_url=endpoint, credential=DefaultAzureCredential())
    blob = client.get_blob_client(container=container, blob=f"{event_id}/{name}")
    blob.upload_blob(json.dumps(value, ensure_ascii=False), overwrite=True)


def claim_review_event(event_id: str) -> ReviewEventClaim:
    connection_string = os.environ.get("AzureWebJobsStorage")
    if not connection_string:
        raise RuntimeError("AzureWebJobsStorage is required for review event idempotency")

    container_name = os.environ.get("REVIEW_IDEMPOTENCY_CONTAINER", "architecture-review-events")
    service = BlobServiceClient.from_connection_string(connection_string)
    container = service.get_container_client(container_name)
    try:
        container.create_container()
    except ResourceExistsError:
        pass

    event_hash = hashlib.sha256(event_id.encode("utf-8")).hexdigest()
    claim = container.get_blob_client(f"events/{event_hash}.json")
    token = str(uuid4())
    claimed_at = datetime.now(timezone.utc)
    value = {
        "eventId": event_id,
        "status": "processing",
        "claimedAt": claimed_at.isoformat(),
        "claimToken": token,
    }
    try:
        claim.upload_blob(json.dumps(value), overwrite=False)
    except ResourceExistsError:
        existing = json.loads(claim.download_blob().readall())
        status = existing.get("status")
        claimed_at_value = existing.get("claimedAt")
        if status != "processing":
            raise IgnoredEvent(f"Azure DevOps event '{event_id}' was already accepted")
        if not isinstance(claimed_at_value, str):
            raise RuntimeError(f"Azure DevOps event '{event_id}' has an invalid claim")
        existing_claimed_at = datetime.fromisoformat(claimed_at_value)
        if claimed_at - existing_claimed_at <= EVENT_CLAIM_STALE_AFTER:
            raise IgnoredEvent(f"Azure DevOps event '{event_id}' is already being processed")

        existing_etag = claim.get_blob_properties().etag
        try:
            claim.upload_blob(
                json.dumps(value),
                overwrite=True,
                etag=existing_etag,
                match_condition=MatchConditions.IfNotModified,
            )
        except ResourceModifiedError as error:
            raise IgnoredEvent(f"Azure DevOps event '{event_id}' is already being processed") from error
        logger.warning("Recovered stale review event claim event_id=%s", event_id)

    logger.info("Review event claimed event_id=%s", event_id)
    return ReviewEventClaim(event_id=event_id, token=token, blob=claim, etag=claim.get_blob_properties().etag)


def complete_review_event(claim: ReviewEventClaim) -> None:
    update_review_event_claim(claim, "completed")


def mark_review_event_failed_after_write(claim: ReviewEventClaim) -> None:
    try:
        update_review_event_claim(claim, "failed-after-board-write-attempt")
    except AzureError:
        logger.exception("Failed to mark uncertain Board write event_id=%s", claim.event_id)


def update_review_event_claim(claim: ReviewEventClaim, status: str) -> None:
    value = {
        "eventId": claim.event_id,
        "status": status,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "claimToken": claim.token,
    }
    claim.blob.upload_blob(
        json.dumps(value),
        overwrite=True,
        etag=claim.etag,
        match_condition=MatchConditions.IfNotModified,
    )


def release_review_event(claim: ReviewEventClaim) -> None:
    try:
        claim.blob.delete_blob(etag=claim.etag, match_condition=MatchConditions.IfNotModified)
        logger.info("Review event claim released after failure event_id=%s", claim.event_id)
    except AzureError:
        logger.exception("Failed to release review event claim event_id=%s", claim.event_id)


def update_board(project: str, work_item_id: int, result: ReviewResult) -> None:
    org_url = os.environ["AZURE_DEVOPS_ORG_URL"].rstrip("/")
    api_url = f"{org_url}/{quote(project, safe='')}/_apis/wit/workitems/{work_item_id}"
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
        "<h3>Diagram assessments</h3>"
        f"{format_diagram_assessments(result.diagramAssessments)}"
        "<h3>Assumptions</h3>"
        f"{format_html_list(result.assumptions, 'No assumptions returned.')}"
    )


def format_diagram_assessments(assessments: list[DiagramAssessment]) -> str:
    if not assessments:
        return "<p>No diagrams were supplied for review.</p>"
    return "".join(
        f"<h4>{html.escape(assessment.imageName)}</h4>"
        f"<p>{html.escape(assessment.summary)}</p>"
        f"{format_html_list(assessment.issues, 'No diagram-specific issues identified.')}"
        for assessment in assessments
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
