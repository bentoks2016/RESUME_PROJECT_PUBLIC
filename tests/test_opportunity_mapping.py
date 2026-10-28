from app.models import (
    GapQuestion,
    Requirement,
)
from app.opportunity_mapping import (
    map_requirement,
)


def requirement(
    status,
    evidence="",
):
    return Requirement(
        requirement="Example capability",
        importance="PREFERRED",
        status=status,
        evidence=evidence,
        keywords=["Example"],
    )


def test_supported_maps_to_direct():
    result = map_requirement(
        requirement(
            "SUPPORTED",
            "Verified direct candidate evidence.",
        )
    )

    assert result.connection == "DIRECT"
    assert result.candidate_evidence == (
        "Verified direct candidate evidence."
    )
    assert result.should_ask_gap_question is False


def test_transferable_remains_transferable():
    result = map_requirement(
        requirement(
            "TRANSFERABLE",
            "Related candidate evidence only.",
        )
    )

    assert result.connection == "TRANSFERABLE"
    assert result.candidate_evidence == (
        "Related candidate evidence only."
    )
    assert result.should_ask_gap_question is True


def test_missing_maps_to_none_without_candidate_evidence():
    result = map_requirement(
        requirement(
            "MISSING",
            "No direct evidence found in the "
            "candidate's current resume.",
        )
    )

    assert result.connection == "NONE"
    assert result.candidate_evidence == ""
    assert result.should_ask_gap_question is True


def test_mapping_source_is_job_posting():
    result = map_requirement(
        requirement("SUPPORTED", "Evidence")
    )

    assert result.signal_source == "JOB_POSTING"
    assert result.role_evidence == (
        "Example capability"
    )


def test_unknown_status_is_rejected():
    import pytest

    with pytest.raises(ValueError):
        map_requirement(
            requirement(
                "SOMETHING_ELSE"
            )
        )


def load_analysis_fixture():
    from pathlib import Path
    from app.models import ResumeAnalysis

    return ResumeAnalysis.model_validate_json(
        Path(
            "benchmarks/fixtures/analysis.json"
        ).read_text()
    )


def test_synthetic_case_preserves_all_three_boundaries():
    from app.opportunity_mapping import (
        build_role_opportunity_mapping,
    )

    result = build_role_opportunity_mapping(
        load_analysis_fixture()
    )

    by_requirement = {
        item.requirement: item
        for item in result.mappings
    }

    sap = by_requirement[
        "Direct SAP S/4HANA implementation experience"
    ]

    ai = by_requirement[
        "Experience applying AI to industrial operations"
    ]

    multisite = by_requirement[
        "Experience in multi-site manufacturing environments"
    ]

    assert sap.connection == "TRANSFERABLE"
    assert ai.connection == "NONE"
    assert ai.candidate_evidence == ""
    assert multisite.connection == "DIRECT"


def test_gap_discovery_preserves_existing_questions():
    from app.opportunity_mapping import (
        build_job_posting_gap_questions,
    )

    analysis = load_analysis_fixture()

    result = build_job_posting_gap_questions(
        analysis
    )

    ids = {
        question.id
        for question in result
    }

    assert "gap-sap" in ids
    assert "gap-ai" in ids


def test_gap_discovery_does_not_question_direct_evidence():
    from app.opportunity_mapping import (
        build_job_posting_gap_questions,
    )

    analysis = load_analysis_fixture()

    questions = build_job_posting_gap_questions(
        analysis
    )

    requirements = {
        item.requirement
        for item in questions
    }

    assert (
        "Experience in multi-site manufacturing environments"
        not in requirements
    )


def test_gap_discovery_is_idempotent():
    from app.opportunity_mapping import (
        build_job_posting_gap_questions,
    )

    analysis = load_analysis_fixture()

    first = build_job_posting_gap_questions(
        analysis
    )

    analysis.gap_questions = first

    second = build_job_posting_gap_questions(
        analysis
    )

    assert [
        item.model_dump()
        for item in second
    ] == [
        item.model_dump()
        for item in first
    ]


def test_every_non_direct_mapping_has_gap_question():
    from app.opportunity_mapping import (
        build_job_posting_gap_questions,
        build_role_opportunity_mapping,
    )

    analysis = load_analysis_fixture()

    questions = build_job_posting_gap_questions(
        analysis
    )

    questioned_requirements = {
        item.requirement.strip().casefold()
        for item in questions
    }

    mapping = build_role_opportunity_mapping(
        analysis
    )

    for item in mapping.mappings:
        if item.connection in {
            "TRANSFERABLE",
            "NONE",
        }:
            assert (
                item.requirement.strip().casefold()
                in questioned_requirements
            )


def test_analysis_endpoint_integrates_role_mapping():
    from pathlib import Path

    text = Path("app/main.py").read_text()

    start = text.index(
        '@app.post("/api/analyze")'
    )

    end = text.index(
        '@app.post("/api/verify-gaps")'
    )

    block = text[start:end]

    assert (
        "build_job_posting_gap_questions("
        in block
    )

    assert (
        "build_role_opportunity_mapping("
        in block
    )

    assert (
        '"role_opportunity_mapping"'
        in block
    )


def test_gap_discovery_deduplicates_live_requirement_variants():
    """
    Regression for Phase 15 live acceptance.

    Existing model-generated gap questions may contain
    punctuation or additional qualifying words while still
    covering the same analyzed requirement.
    """
    analysis = load_analysis_fixture()

    analysis.requirements = [
        Requirement(
            requirement=(
                "Direct SAP S/4HANA implementation "
                "experience."
            ),
            importance="PREFERRED",
            status="TRANSFERABLE",
            evidence=(
                "Related SAP/ERP exposure only."
            ),
            keywords=[
                "SAP S/4HANA",
            ],
        ),
        Requirement(
            requirement=(
                "Experience applying AI to industrial "
                "operations."
            ),
            importance="PREFERRED",
            status="MISSING",
            evidence=(
                "No direct evidence found in the "
                "candidate's current resume."
            ),
            keywords=[
                "AI",
                "industrial operations",
            ],
        ),
    ]

    analysis.gap_questions = [
        GapQuestion(
            id="q1",
            requirement=(
                "Direct SAP S/4HANA implementation "
                "experience"
            ),
            reason="Verify direct implementation.",
            suggested_examples=[],
        ),
        GapQuestion(
            id="q2",
            requirement=(
                "Experience applying AI or advanced "
                "analytics to industrial operations"
            ),
            reason="Verify industrial AI experience.",
            suggested_examples=[],
        ),
        GapQuestion(
            id="q3",
            requirement=(
                "Change management methodologies"
            ),
            reason="Additional useful evidence.",
            suggested_examples=[],
        ),
    ]

    from app.opportunity_mapping import (
        build_job_posting_gap_questions,
    )

    result = build_job_posting_gap_questions(
        analysis
    )

    assert [item.id for item in result] == [
        "q1",
        "q2",
        "q3",
    ]
