"""
Deterministic integration checks for the application workflow.

AI/domain functions are mocked at the HTTP boundary. These tests
verify endpoint serialization and hand-offs, not model quality.
"""

import json
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models import (
    GeneratedApplication,
    GapVerificationResult,
    ResumeAnalysis,
)

from benchmarks.cases import (
    JOB_TEXT,
    RESUME_TEXT,
)


client = TestClient(app)


def fixture(model_class, filename):
    return model_class.model_validate_json(
        Path(
            "benchmarks/fixtures",
            filename,
        ).read_text()
    )


def test_analysis_to_generation_workflow_contract():
    analysis = fixture(
        ResumeAnalysis,
        "analysis.json",
    )
    verification = fixture(
        GapVerificationResult,
        "gap_verification.json",
    )
    application = fixture(
        GeneratedApplication,
        "generated_application.json",
    )

    with patch(
        "app.main.analyze_resume",
        return_value=analysis,
    ):
        response = client.post(
            "/api/analyze",
            data={
                "job_text": JOB_TEXT,
                "resume_text": RESUME_TEXT,
            },
        )

    assert response.status_code == 200

    analysis_payload = response.json()

    assert "analysis" in analysis_payload
    assert "role_opportunity_mapping" in analysis_payload
    assert (
        analysis_payload["analysis"]["job_title"]
        == analysis.job_title
    )

    gap_answers = [
        {
            "gap_id": question.id,
            "requirement": question.requirement,
            "has_experience": False,
            "description": "",
            "context": "",
            "results": "",
            "technologies": "",
        }
        for question in analysis.gap_questions
    ]

    with patch(
        "app.main.verify_gap_answers",
        return_value=verification,
    ):
        response = client.post(
            "/api/verify-gaps",
            data={
                "job_text": JOB_TEXT,
                "resume_text": RESUME_TEXT,
                "analysis_json": json.dumps(
                    analysis_payload["analysis"]
                ),
                "gap_answers_json": json.dumps(
                    gap_answers
                ),
            },
        )

    assert response.status_code == 200

    verification_payload = response.json()

    assert "items" in verification_payload

    with patch(
        "app.main.generate_application",
        return_value=application,
    ):
        response = client.post(
            "/api/generate",
            data={
                "job_text": JOB_TEXT,
                "resume_text": RESUME_TEXT,
                "analysis_json": json.dumps(
                    analysis_payload["analysis"]
                ),
                "gap_answers_json": json.dumps(
                    gap_answers
                ),
                "verification_json": json.dumps(
                    verification_payload
                ),
                "achievement_verification_json": "{}",
            },
        )

    assert response.status_code == 200

    generated = response.json()

    assert "resume" in generated
    assert "cover_letter" in generated
    assert "final_match_score" in generated
    assert "final_ats_score" in generated
    assert "resume_composition" in generated
    assert "cover_letter_composition" in generated


def test_generated_application_downloads_through_api():
    application = fixture(
        GeneratedApplication,
        "generated_application.json",
    )

    resume_response = client.post(
        "/api/download/resume",
        data={
            "resume_json": (
                application.resume.model_dump_json()
            ),
            "filename": "Workflow Resume",
        },
    )

    assert resume_response.status_code == 200
    assert resume_response.content.startswith(
        b"PK"
    )

    letter_response = client.post(
        "/api/download/cover-letter",
        data={
            "cover_letter_json": (
                application.cover_letter.model_dump_json()
            ),
            "filename": "Workflow Cover Letter",
        },
    )

    assert letter_response.status_code == 200
    assert letter_response.content.startswith(
        b"PK"
    )


def test_scoring_methodology_exposes_separate_dimensions():
    response = client.get(
        "/api/scoring-methodology"
    )

    assert response.status_code == 200

    result = response.json()

    assert "qualification_match_weights" in result
    assert "ats_coverage" in result
    assert (
        result["ats_coverage"][
            "independent_from_qualification_match"
        ]
        is True
    )


def test_health_endpoint_is_release_ready():
    response = client.get("/health")

    assert response.status_code == 200

    result = response.json()

    assert result["status"] == "ok"
    assert result["application"] == "RESUME_PROJECT"


def test_analysis_rejects_obviously_short_job_posting():
    response = client.post(
        "/api/analyze",
        data={
            "job_text": "Too short",
            "resume_text": RESUME_TEXT,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Job posting appears too short."
    )


def test_analysis_rejects_obviously_short_resume():
    response = client.post(
        "/api/analyze",
        data={
            "job_text": JOB_TEXT,
            "resume_text": "Too short",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Resume appears too short."
    )
