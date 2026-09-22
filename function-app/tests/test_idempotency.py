import hashlib
import json
import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import azure.functions as func
import requests
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from function_app import ReviewResult, WikiDocument, architecture_review


class FakeBlob:
    def __init__(self, blobs: dict[str, str], etags: dict[str, int], name: str):
        self.blobs = blobs
        self.etags = etags
        self.name = name

    def upload_blob(
        self,
        value: str,
        overwrite: bool = False,
        etag: str | None = None,
        match_condition: object | None = None,
    ) -> None:
        if etag is not None and etag != str(self.etags.get(self.name)):
            raise ResourceModifiedError("Blob was modified")
        if self.name in self.blobs and not overwrite:
            raise ResourceExistsError("Blob already exists")
        self.blobs[self.name] = value
        self.etags[self.name] = self.etags.get(self.name, 0) + 1

    def delete_blob(self, etag: str | None = None, match_condition: object | None = None) -> None:
        if self.name not in self.blobs:
            raise ResourceNotFoundError("Blob does not exist")
        if etag is not None and etag != str(self.etags.get(self.name)):
            raise ResourceModifiedError("Blob was modified")
        del self.blobs[self.name]
        del self.etags[self.name]

    def download_blob(self) -> "FakeBlob":
        return self

    def readall(self) -> bytes:
        return self.blobs[self.name].encode()

    def get_blob_properties(self) -> SimpleNamespace:
        return SimpleNamespace(etag=str(self.etags[self.name]))


class FakeContainer:
    def __init__(self, blobs: dict[str, str], etags: dict[str, int]):
        self.blobs = blobs
        self.etags = etags
        self.created = False

    def create_container(self) -> None:
        if self.created:
            raise ResourceExistsError("Container already exists")
        self.created = True

    def get_blob_client(self, name: str) -> FakeBlob:
        return FakeBlob(self.blobs, self.etags, name)


class FakeBlobService:
    def __init__(self):
        self.blobs: dict[str, str] = {}
        self.etags: dict[str, int] = {}
        self.container = FakeContainer(self.blobs, self.etags)

    def get_container_client(self, _name: str) -> FakeContainer:
        return self.container

    def get_blob_client(self, container: str, blob: str) -> FakeBlob:
        return FakeBlob(self.blobs, self.etags, blob)


class IdempotencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.environment = patch.dict(
            os.environ,
            {
                "AzureWebJobsStorage": "test-connection-string",
                "AZURE_DEVOPS_ALLOWED_PROJECTS": "NL_HQ_T_Cloud_CoE",
                "REVIEW_TRIGGER_TAG": "design review",
                "AZURE_STORAGE_BLOB_ENDPOINT": "",
                "REVIEW_SNAPSHOT_CONTAINER": "",
            },
            clear=False,
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_duplicate_event_invokes_review_and_writeback_once(self) -> None:
        payload = {
            "id": "duplicate-event",
            "resource": {
                "workItemId": 189466,
                "fields": {
                    "System.Tags": {
                        "oldValue": "cloud",
                        "newValue": "cloud; design review",
                    }
                },
                "revision": {
                    "id": 189466,
                    "fields": {
                        "System.Description": (
                            "https://shv-energy.visualstudio.com/NL_HQ_T_Cloud_CoE/"
                            "_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/7521/design"
                        )
                    },
                },
            },
        }
        request = func.HttpRequest(
            method="POST",
            url="http://localhost/api/architecture-review",
            body=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        service = FakeBlobService()
        result = ReviewResult(
            reviewId="board-189466-duplicate-event",
            sourceRevision="revision-1",
            overallRisk="Low",
            recommendation="Proceed",
        )

        with (
            patch("function_app.BlobServiceClient.from_connection_string", return_value=service),
            patch(
                "function_app.get_wiki_document",
                return_value=WikiDocument(content="complete design", revision="revision-1", url="wiki"),
            ),
            patch("function_app.invoke_foundry", return_value=result) as invoke_foundry,
            patch("function_app.update_board") as update_board,
        ):
            first = architecture_review(request)
            second = architecture_review(request)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(json.loads(first.get_body())["status"], "completed")
        self.assertEqual(second.status_code, 200)
        self.assertEqual(json.loads(second.get_body())["status"], "ignored")
        self.assertIn("already accepted", json.loads(second.get_body())["reason"])
        invoke_foundry.assert_called_once()
        update_board.assert_called_once()

    def test_failed_review_releases_event_for_retry(self) -> None:
        payload = {
            "id": "retryable-event",
            "resource": {
                "workItemId": 189466,
                "fields": {
                    "System.Tags": {
                        "oldValue": "cloud",
                        "newValue": "cloud; design review",
                    }
                },
                "revision": {
                    "id": 189466,
                    "fields": {
                        "System.Description": (
                            "https://shv-energy.visualstudio.com/NL_HQ_T_Cloud_CoE/"
                            "_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/7521/design"
                        )
                    },
                },
            },
        }
        request = func.HttpRequest(
            method="POST",
            url="http://localhost/api/architecture-review",
            body=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        service = FakeBlobService()

        with (
            patch("function_app.BlobServiceClient.from_connection_string", return_value=service),
            patch(
                "function_app.get_wiki_document",
                return_value=WikiDocument(content="complete design", revision="revision-1", url="wiki"),
            ),
            patch("function_app.invoke_foundry", side_effect=RuntimeError("temporary failure")),
        ):
            first = architecture_review(request)
            second = architecture_review(request)

        self.assertEqual(first.status_code, 500)
        self.assertEqual(second.status_code, 500)
        self.assertEqual(service.blobs, {})

    def test_stale_processing_claim_is_recovered(self) -> None:
        payload = self._event_payload("stale-event")
        request = self._request(payload)
        service = FakeBlobService()
        name = f"events/{hashlib.sha256(b'stale-event').hexdigest()}.json"
        service.blobs[name] = json.dumps(
            {
                "eventId": "stale-event",
                "status": "processing",
                "claimedAt": (datetime.now(timezone.utc) - timedelta(minutes=11)).isoformat(),
                "claimToken": "abandoned",
            }
        )
        service.etags[name] = 1
        result = ReviewResult(
            reviewId="board-189466-stale-event",
            sourceRevision="revision-1",
            overallRisk="Low",
            recommendation="Proceed",
        )

        with (
            patch("function_app.BlobServiceClient.from_connection_string", return_value=service),
            patch(
                "function_app.get_wiki_document",
                return_value=WikiDocument(content="complete design", revision="revision-1", url="wiki"),
            ),
            patch("function_app.invoke_foundry", return_value=result),
            patch("function_app.update_board"),
        ):
            response = architecture_review(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_body())["status"], "completed")
        self.assertEqual(json.loads(service.blobs[name])["status"], "completed")

    def test_uncertain_board_write_is_not_retried(self) -> None:
        payload = self._event_payload("uncertain-board-event")
        request = self._request(payload)
        service = FakeBlobService()
        result = ReviewResult(
            reviewId="board-189466-uncertain-board-event",
            sourceRevision="revision-1",
            overallRisk="Low",
            recommendation="Proceed",
        )

        with (
            patch("function_app.BlobServiceClient.from_connection_string", return_value=service),
            patch(
                "function_app.get_wiki_document",
                return_value=WikiDocument(content="complete design", revision="revision-1", url="wiki"),
            ),
            patch("function_app.invoke_foundry", return_value=result),
            patch("function_app.update_board", side_effect=requests.Timeout("uncertain write")) as update_board,
        ):
            first = architecture_review(request)
            second = architecture_review(request)

        self.assertEqual(first.status_code, 502)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(json.loads(second.get_body())["status"], "ignored")
        update_board.assert_called_once()

    @staticmethod
    def _event_payload(event_id: str) -> dict[str, object]:
        return {
            "id": event_id,
            "resource": {
                "workItemId": 189466,
                "fields": {
                    "System.Tags": {
                        "oldValue": "cloud",
                        "newValue": "cloud; design review",
                    }
                },
                "revision": {
                    "id": 189466,
                    "fields": {
                        "System.Description": (
                            "https://shv-energy.visualstudio.com/NL_HQ_T_Cloud_CoE/"
                            "_wiki/wikis/NL_HQ_T_Cloud_CoE.wiki/7521/design"
                        )
                    },
                },
            },
        }

    @staticmethod
    def _request(payload: dict[str, object]) -> func.HttpRequest:
        return func.HttpRequest(
            method="POST",
            url="http://localhost/api/architecture-review",
            body=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )


if __name__ == "__main__":
    unittest.main()
