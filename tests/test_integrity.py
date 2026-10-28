from pathlib import Path

from app.models import (
    FactualClaim,
)


def test_factual_claim_records_candidate_provenance():
    claim = FactualClaim(
        claim="Led multi-site transformation.",
        document="RESUME",
        category="EXPERIENCE",
        status="SUPPORTED",
        source_evidence="Original resume.",
        evidence_source="CANDIDATE_EVIDENCE",
    )

    assert claim.evidence_source == (
        "CANDIDATE_EVIDENCE"
    )


def test_factual_claim_records_job_posting_provenance():
    claim = FactualClaim(
        claim=(
            "The advertised role requires "
            "multi-site transformation."
        ),
        document="COVER_LETTER",
        category="EMPLOYER_ROLE",
        status="SUPPORTED",
        source_evidence="Target job posting.",
        evidence_source="JOB_POSTING",
    )

    assert claim.evidence_source == "JOB_POSTING"


def test_old_factual_claim_data_remains_compatible():
    claim = FactualClaim(
        claim="Existing candidate claim.",
        document="RESUME",
        category="EXPERIENCE",
        status="SUPPORTED",
    )

    assert claim.evidence_source == (
        "CANDIDATE_EVIDENCE"
    )


def test_integrity_prompt_separates_evidence_categories():
    from app.integrity import INTEGRITY_PROMPT

    required = [
        "CANDIDATE EVIDENCE",
        "EMPLOYER / ROLE EVIDENCE",
        "GROUNDED COMPANY RESEARCH",
        "REASONABLE INFERENCE",
        "The job posting is NEVER evidence",
        "Do not confuse:",
    ]

    for value in required:
        assert value in INTEGRITY_PROMPT


def test_grounded_company_research_is_dormant():
    from app.integrity import INTEGRITY_PROMPT

    normalized = " ".join(
        INTEGRITY_PROMPT.split()
    )

    assert (
        "No grounded company research is supplied "
        "to this integrity check at present."
        in normalized
    )


def test_integrity_function_accepts_job_posting():
    import inspect

    from app.integrity import (
        check_factual_integrity,
    )

    parameters = list(
        inspect.signature(
            check_factual_integrity
        ).parameters
    )

    assert parameters[0] == "job_post"
    assert parameters[1] == "original_resume"


def test_integrity_endpoint_accepts_job_text():
    text = Path("app/main.py").read_text()

    start = text.index(
        '@app.post("/api/check-integrity")'
    )

    end = text.index(
        '@app.post("/api/download/resume")'
    )

    block = text[start:end]

    assert "job_text: str = Form(...)" in block
    assert (
        "check_factual_integrity(\n"
        "            job_text,"
        in block
    )


def test_integrity_frontend_sends_job_text():
    text = Path(
        "app/static/integrity-ui.js"
    ).read_text()

    assert '"job_text"' in text
    assert "storedJobText" in text
