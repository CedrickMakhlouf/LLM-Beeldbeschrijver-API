"""Tests voor de LLM Beeldbeschrijver API."""

import base64

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_generator
from app.api.main import app

# Betrouwbaar Windows-applicatiescherm (VS Code docs, gehost door Microsoft)
VSCODE_SCREENSHOT_URL = "https://code.visualstudio.com/assets/docs/getstarted/userinterface/floating-editor.png"


class FakeGenerator:
    def generate(self, image_base64=None, image_url=None, image_id=None):
        return {
            "image_id": image_id,
            "description": "Een scherm met een knop en een tekstinvoerveld.",
            "processing_ms": 1,
        }


client = TestClient(app, raise_server_exceptions=False)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "LLM Beeldbeschrijver API"


def test_describe_success_base64():
    app.dependency_overrides[get_generator] = lambda: FakeGenerator()
    response = client.post(
        "/api/describe",
        json={"image_base64": "aGVsbG8=", "image_id": "001"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "description" in data
    assert data["image_id"] == "001"
    assert data["processing_ms"] >= 0
    app.dependency_overrides.clear()


def test_describe_success_url():
    app.dependency_overrides[get_generator] = lambda: FakeGenerator()
    response = client.post(
        "/api/describe",
        json={"image_url": "https://example.com/screen.png", "image_id": "002"},
    )
    assert response.status_code == 200
    app.dependency_overrides.clear()


def test_describe_missing_both_fields():
    app.dependency_overrides[get_generator] = lambda: FakeGenerator()
    response = client.post("/api/describe", json={})
    assert response.status_code == 422
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_describe_live_vscode_screenshot():
    """Roept de live API aan met een echte VS Code screenshot. Vereist geldige Azure-credentials."""
    img_bytes = httpx.get(VSCODE_SCREENSHOT_URL).content
    b64 = base64.b64encode(img_bytes).decode()
    response = httpx.post(
        "https://see-benchmark.ambitiousmoss-cd4cf8a8.eastus.azurecontainerapps.io/api/describe",
        json={"image_base64": b64, "image_id": "vscode-001"},
        timeout=30,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["description"]) > 50
    assert data["processing_ms"] > 0
