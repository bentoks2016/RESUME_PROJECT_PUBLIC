import pytest

from fastapi import HTTPException
from google.genai import errors

from app.provider_errors import (
    raise_ai_service_http_error,
)


def call_helper(error):
    with pytest.raises(HTTPException) as caught:
        raise_ai_service_http_error(
            error,
            "Fallback failure."
        )

    return caught.value


def test_gemini_429_becomes_http_429():
    error = errors.ClientError(
        429,
        {
            "error": {
                "code": 429,
                "status": "RESOURCE_EXHAUSTED",
                "message": "Quota exceeded.",
            }
        },
    )

    result = call_helper(error)

    assert result.status_code == 429
    assert "quota" in result.detail.lower()
    assert "preserved" in result.detail.lower()


def test_gemini_503_becomes_http_503():
    error = errors.ServerError(
        503,
        {
            "error": {
                "code": 503,
                "status": "UNAVAILABLE",
                "message": "High demand.",
            }
        },
    )

    result = call_helper(error)

    assert result.status_code == 503
    assert "temporarily busy" in result.detail.lower()
    assert "preserved" in result.detail.lower()


def test_unknown_exception_becomes_http_500():
    result = call_helper(
        RuntimeError("Unexpected internal failure.")
    )

    assert result.status_code == 500
    assert result.detail == "Fallback failure."


def test_all_ai_endpoints_use_provider_error_translation():
    from pathlib import Path

    text = Path("app/main.py").read_text()

    endpoint_markers = [
        '@app.post("/api/analyze")',
        '@app.post("/api/verify-gaps")',
        '@app.post("/api/analyze-achievements")',
        '@app.post("/api/verify-achievements")',
        '@app.post("/api/generate")',
        '@app.post("/api/check-integrity")',
        '@app.post("/api/recruiter-review")',
        '@app.post("/api/interview-preparation")',
    ]

    positions = []

    for marker in endpoint_markers:
        position = text.find(marker)
        assert position != -1, (
            f"Missing AI endpoint: {marker}"
        )
        positions.append(position)

    for index, marker in enumerate(endpoint_markers):
        start = positions[index]

        if index + 1 < len(positions):
            end = positions[index + 1]
        else:
            end = len(text)

        block = text[start:end]

        assert "raise_ai_service_http_error(" in block, (
            f"{marker} does not use shared "
            "provider-error translation."
        )
