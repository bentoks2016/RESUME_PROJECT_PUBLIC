from app.ats import (
    audit_resume_keywords,
    build_authorized_keywords,
    validate_ats_structure,
)
from app.models import (
    CareerPosition,
    ContactInformation,
    EducationItem,
    GapVerificationItem,
    GapVerificationResult,
    KeywordAnalysis,
    ResumeDocument,
    SkillGroup,
)


def gap_item(
    result,
    status,
    keywords,
):
    return GapVerificationItem(
        gap_id="gap-1",
        requirement="Test requirement",
        original_status="MISSING",
        verified_status=status,
        verification_result=result,
        evidence_summary="Test",
        supported_keywords=keywords,
        caution="",
    )


def empty_verification():
    return GapVerificationResult(
        items=[]
    )


def test_supported_source_keyword_is_authorized():
    analysis = [
        KeywordAnalysis(
            keyword="Python",
            importance="required",
            status="SUPPORTED",
            evidence="Source resume",
            currently_in_resume=True,
            use_in_tailored_resume=True,
        )
    ]

    result = build_authorized_keywords(
        analysis,
        empty_verification(),
    )

    assert [item.keyword for item in result] == [
        "Python"
    ]


def test_missing_source_keyword_is_not_authorized():
    analysis = [
        KeywordAnalysis(
            keyword="Kubernetes",
            importance="required",
            status="MISSING",
            evidence="",
            currently_in_resume=False,
            use_in_tailored_resume=False,
        )
    ]

    result = build_authorized_keywords(
        analysis,
        empty_verification(),
    )

    assert result == []


def test_verified_supported_gap_can_authorize_keyword():
    verification = GapVerificationResult(
        items=[
            gap_item(
                "VERIFIED",
                "SUPPORTED",
                ["Kubernetes"],
            )
        ]
    )

    result = build_authorized_keywords(
        [],
        verification,
    )

    assert [item.keyword for item in result] == [
        "Kubernetes"
    ]


def test_not_verified_gap_cannot_authorize_keyword():
    verification = GapVerificationResult(
        items=[
            gap_item(
                "NOT_VERIFIED",
                "SUPPORTED",
                ["Kubernetes"],
            )
        ]
    )

    result = build_authorized_keywords(
        [],
        verification,
    )

    assert result == []


def test_verified_but_non_supported_gap_cannot_authorize_keyword():
    verification = GapVerificationResult(
        items=[
            gap_item(
                "VERIFIED",
                "TRANSFERABLE",
                ["Kubernetes"],
            )
        ]
    )

    result = build_authorized_keywords(
        [],
        verification,
    )

    assert result == []


def valid_resume():
    return ResumeDocument(
        name="Test Candidate",
        contact=ContactInformation(
            email="candidate@example.com",
        ),
        profile=["Professional profile"],
        career_positions=[
            CareerPosition(
                job_title="Manager",
                employer="Example Ltd",
                dates="2020-2024",
            )
        ],
        skill_groups=[
            SkillGroup(
                name="Technology",
                accomplishments=[
                    "Used Python for data analysis."
                ],
            )
        ],
        education=[
            EducationItem(
                program_name="Degree",
                school_name="Example University",
            )
        ],
    )


def test_valid_resume_structure_passes():
    result = validate_ats_structure(
        valid_resume()
    )

    assert result["passed"] is True
    assert result["issues"] == []


def test_missing_email_is_reported():
    resume = valid_resume()
    resume.contact.email = ""

    result = validate_ats_structure(
        resume
    )

    assert result["passed"] is False
    assert "Candidate email is missing." in (
        result["issues"]
    )


def test_authorized_keyword_audit_uses_actual_resume():
    resume = valid_resume()

    verification = GapVerificationResult(
        items=[]
    )

    analysis = [
        KeywordAnalysis(
            keyword="Python",
            importance="required",
            status="SUPPORTED",
            evidence="Source",
            currently_in_resume=True,
            use_in_tailored_resume=True,
        )
    ]

    authorized = build_authorized_keywords(
        analysis,
        verification,
    )

    result = audit_resume_keywords(
        resume,
        authorized,
    )

    assert result["score"] == 100
    assert "Python" in result["found"]
