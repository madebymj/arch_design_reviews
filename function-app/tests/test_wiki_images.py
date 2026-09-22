import json
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from function_app import (
    PNG_SIGNATURE,
    ReviewRequest,
    WikiDocument,
    WikiImage,
    WikiReference,
    build_review_package,
    download_wiki_png,
    extract_wiki_png_paths,
    extract_wiki_png_references,
    invoke_foundry,
)


class FakeImageResponse:
    headers = {"Content-Type": "image/png"}

    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self) -> None:
        pass

    def iter_content(self, chunk_size: int):
        yield self.content


class WikiImageTests(unittest.TestCase):
    def test_extracts_and_deduplicates_markdown_and_html_png_attachments(self) -> None:
        content = """
        ![Diagram](/.attachments/architecture.png)
        ![Diagram again](/.attachments/architecture.png)
        <img src="/.attachments/network%20flow.png" alt="Network">
        """

        self.assertEqual(
            extract_wiki_png_paths(content),
            ["/.attachments/architecture.png", "/.attachments/network flow.png"],
        )
        references = extract_wiki_png_references(content)
        self.assertEqual(references[0].display_name, "Diagram")
        self.assertEqual(references[1].display_name, "Network")

    def test_uses_wiki_caption_as_diagram_name(self) -> None:
        references = extract_wiki_png_references(
            "###_SAP Management Servers - Prod Environment_\n\n"
            "![image.png]"
            "(/.attachments/image-de9592e9-efaf-4fca-9265-a8442cf6e5fb.png)"
        )

        self.assertEqual(len(references), 1)
        self.assertEqual(references[0].display_name, "SAP Management Servers - Prod Environment")
        self.assertEqual(
            references[0].source_path,
            "/.attachments/image-de9592e9-efaf-4fca-9265-a8442cf6e5fb.png",
        )

    def test_rejects_external_png_reference(self) -> None:
        with self.assertRaisesRegex(ValueError, "use a Wiki attachment"):
            extract_wiki_png_paths("![Diagram](https://example.com/diagram.png)")

    @patch.dict(
        os.environ,
        {
            "AZURE_DEVOPS_ORG_URL": "https://shv-energy.visualstudio.com",
            "AZURE_DEVOPS_PAT": "test-only",
        },
        clear=False,
    )
    @patch("function_app.requests.get")
    def test_downloads_png_from_wiki_git_repository(self, get) -> None:
        image_content = PNG_SIGNATURE + b"image-data"
        get.return_value = FakeImageResponse(image_content)
        wiki = WikiReference(project="NL_HQ_T_Cloud_CoE", wiki_id="NL_HQ_T_Cloud_CoE.wiki")

        image = download_wiki_png(wiki, "/.attachments/architecture.png")

        self.assertEqual(image.content, image_content)
        self.assertEqual(image.media_type, "image/png")
        get.assert_called_once()
        self.assertIn("/_apis/git/repositories/NL_HQ_T_Cloud_CoE.wiki/items", get.call_args.args[0])
        self.assertEqual(get.call_args.kwargs["params"]["path"], "/.attachments/architecture.png")

    def test_review_package_describes_vision_attachment_without_embedding_bytes(self) -> None:
        request = ReviewRequest(
            event_id="event-1",
            work_item_id=189466,
            wiki_url="wiki-url",
            devops_project="NL_HQ_T_Cloud_CoE",
            trigger_tag="design review",
        )
        image = WikiImage(
            name="architecture.png",
            source_path="/.attachments/architecture.png",
            media_type="image/png",
            content=PNG_SIGNATURE + b"image-data",
        )
        wiki = WikiDocument(content="design", revision="revision-1", url="wiki-url", images=[image])

        package = build_review_package(request, wiki)

        self.assertEqual(package["design"]["attachments"][0]["name"], "architecture.png")
        self.assertTrue(package["design"]["attachments"][0]["includedAsVisionInput"])
        json.dumps(package)

    @patch.dict(
        os.environ,
        {
            "AZURE_AI_PROJECT_ENDPOINT": "https://example.test/project",
            "FOUNDRY_AGENT_NAME": "architecture-review-agent",
        },
        clear=False,
    )
    @patch("function_app.AIProjectClient")
    def test_invocation_sends_png_as_high_detail_vision_input(self, project_client_class) -> None:
        captured: dict[str, object] = {}

        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                output_text=json.dumps(
                    {
                        "reviewId": "review-1",
                        "sourceRevision": "revision-1",
                        "overallRisk": "Low",
                        "recommendation": "Approved",
                        "findings": [],
                        "diagramAssessments": [
                            {
                                "imageName": "architecture.png",
                                "summary": "The diagram is consistent with the written design.",
                                "issues": [],
                            }
                        ],
                        "missingInformation": [],
                        "assumptions": [],
                    }
                )
            )

        openai_client = SimpleNamespace(responses=SimpleNamespace(create=create))
        project_client_class.return_value.get_openai_client.return_value = openai_client
        image = WikiImage(
            name="architecture.png",
            source_path="/.attachments/architecture.png",
            media_type="image/png",
            content=PNG_SIGNATURE + b"image-data",
        )

        result = invoke_foundry({"reviewId": "review-1"}, [image])

        content = captured["input"][0]["content"]
        self.assertEqual(content[0]["type"], "input_text")
        self.assertEqual(content[1]["type"], "input_image")
        self.assertEqual(content[1]["detail"], "high")
        self.assertTrue(content[1]["image_url"].startswith("data:image/png;base64,"))
        self.assertEqual(result.reviewId, "review-1")
        self.assertEqual(result.diagramAssessments[0].imageName, "architecture.png")


if __name__ == "__main__":
    unittest.main()
