from pathlib import Path

import pytest

from app.composition import (
    audit_cover_letter_composition,
)
from app.models import (
    ContactInformation,
    CoverLetterDocument,
    GeneratedApplication,
    RecipientInformation,
)


def valid_letter():
    return CoverLetterDocument(
        candidate_name="Alex Morgan",
        candidate_contact=ContactInformation(),
        recipient=RecipientInformation(
            name="Hiring Manager",
            employer="Northstar Manufacturing",
        ),
        subject_line=(
            "RE: Senior Operations Transformation Manager"
        ),
        salutation="Dear Hiring Manager,",
        paragraph_1=(
            "This opportunity is compelling because it "
            "brings together areas central to my verified "
            "professional background."
        ),
        paragraph_2=(
            "The advertised role requires multi-site "
            "transformation leadership, an area aligned "
            "with my verified experience."
        ),
        paragraph_3=(
            "I would bring verified experience in "
            "automation, governance, and change adoption."
        ),
        paragraph_4=(
            "I would welcome a conversation about the "
            "role and appreciate your consideration."
        ),
    )


def test_four_substantive_paragraphs_pass():
    audit = audit_cover_letter_composition(
        valid_letter()
    )

    assert audit.passed is True
    assert audit.substantive_paragraph_count == 4


def test_missing_body_paragraph_fails():
    letter = valid_letter()
    letter.paragraph_3 = ""

    audit = audit_cover_letter_composition(
        letter
    )

    assert audit.passed is False
    assert audit.substantive_paragraph_count == 3


def test_current_employer_context_is_job_posting():
    audit = audit_cover_letter_composition(
        valid_letter()
    )

    assert audit.employer_context_sources == [
        "JOB_POSTING"
    ]


def test_inferred_motivation_is_recorded():
    audit = audit_cover_letter_composition(
        valid_letter()
    )

    assert audit.motivation_basis == (
        "INFERRED_FROM_EVIDENCE"
    )

    assert any(
        "inferred from verified candidate evidence"
        in item
        for item in audit.warnings
    )


def test_explicit_candidate_motivation_supported():
    audit = audit_cover_letter_composition(
        valid_letter(),
        motivation_basis="EXPLICIT_CANDIDATE",
    )

    assert audit.motivation_basis == (
        "EXPLICIT_CANDIDATE"
    )


def test_unknown_motivation_basis_rejected():
    with pytest.raises(ValueError):
        audit_cover_letter_composition(
            valid_letter(),
            motivation_basis="MADE_UP",
        )


def test_existing_application_fixture_remains_compatible():
    application = (
        GeneratedApplication.model_validate_json(
            Path(
                "benchmarks/fixtures/"
                "generated_application.json"
            ).read_text()
        )
    )

    assert (
        application.cover_letter_composition.passed
        is True
    )


def test_writer_prompt_contains_phase11_rules():
    from app.prompts import WRITER_PROMPT

    required = [
        "PARAGRAPH 1 — PERSONAL MOTIVATION",
        "Evidence-grounded professional inference",
        "Persuasive synthesis is encouraged.",
        "Current employer context comes from the JOB POSTING.",
        "reasonable role-level interpretations",
        "Do not turn a job requirement into candidate experience.",
        "PARAGRAPH 4 — SUMMARY AND CLOSE",
    ]

    for value in required:
        assert value in WRITER_PROMPT


def test_generation_pipeline_applies_cover_letter_audit():
    text = Path("app/ai.py").read_text()

    start = text.index(
        "def generate_application("
    )

    block = text[start:]

    assert (
        "audit_cover_letter_composition("
        in block
    )

    assert (
        'employer_context_sources=['
        in block
    )

    assert (
        '"JOB_POSTING"'
        in block
    )

    assert (
        '"INFERRED_FROM_EVIDENCE"'
        in block
    )
