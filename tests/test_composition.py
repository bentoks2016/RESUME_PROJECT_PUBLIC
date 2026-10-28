from app.composition import (
    audit_resume_composition,
)
from app.models import (
    ContactInformation,
    EducationItem,
    ResumeDocument,
    SkillGroup,
    TrainingItem,
)


def valid_resume():
    return ResumeDocument(
        name="Alex Morgan",
        contact=ContactInformation(),
        profile=[
            (
                "Operations transformation professional "
                "with 11 years of manufacturing experience "
                "specializing in multi-site transformation, "
                "automation, and governance."
            ),
            (
                "Led cross-functional operational "
                "improvement across four manufacturing "
                "sites."
            ),
            (
                "Introduced automated production reporting, "
                "reducing weekly manual reporting effort "
                "by 18 hours."
            ),
            (
                "Bachelor of Business Administration with "
                "Lean Six Sigma Green Belt training."
            ),
        ],
        career_positions=[],
        skill_groups=[
            SkillGroup(
                name="Transformation & Delivery",
                accomplishments=[
                    "Led multi-site improvement.",
                    "Managed program risks.",
                    "Coordinated stakeholders.",
                    "Led adoption workshops.",
                ],
            ),
            SkillGroup(
                name="Automation & Performance",
                accomplishments=[
                    "Introduced automated reporting.",
                    "Used Power BI dashboards.",
                    "Developed performance reporting.",
                    "Facilitated problem-solving sessions.",
                ],
            ),
        ],
        education=[
            EducationItem(
                program_name=(
                    "Bachelor of Business Administration"
                ),
                school_name="Fictional University",
            )
        ],
        additional_training=[
            TrainingItem(
                course_name=(
                    "Lean Six Sigma Green Belt"
                ),
                provider="Fictional Provider",
            )
        ],
    )


def test_valid_resume_passes_composition_audit():
    audit = audit_resume_composition(
        valid_resume()
    )

    assert audit.passed is True
    assert audit.profile_first_bullet_present is True
    assert (
        audit.profile_final_education_bullet_present
        is True
    )
    assert audit.principal_skill_group_count == 2
    assert audit.skill_group_accomplishment_counts == [
        4,
        4,
    ]


def test_missing_profile_fails_audit():
    resume = valid_resume()
    resume.profile = []

    audit = audit_resume_composition(
        resume
    )

    assert audit.passed is False
    assert audit.profile_first_bullet_present is False


def test_education_must_be_in_final_profile_bullet():
    resume = valid_resume()

    resume.profile = [
        resume.profile[0],
        (
            "Bachelor of Business Administration with "
            "Lean Six Sigma Green Belt training."
        ),
        "Led multi-site operational improvement.",
    ]

    audit = audit_resume_composition(
        resume
    )

    assert audit.passed is False
    assert (
        audit.profile_final_education_bullet_present
        is False
    )


def test_three_accomplishments_warns_but_does_not_fail():
    resume = valid_resume()

    resume.skill_groups[0].accomplishments.pop()

    audit = audit_resume_composition(
        resume
    )

    assert audit.passed is True

    assert any(
        "approximately four" in warning
        for warning in audit.warnings
    )


def test_missing_source_education_does_not_force_invention():
    resume = valid_resume()

    resume.education = []
    resume.additional_training = []

    resume.profile[-1] = (
        "Additional verified operational experience."
    )

    audit = audit_resume_composition(
        resume
    )

    assert audit.passed is True
    assert any(
        "No source education or training" in warning
        for warning in audit.warnings
    )


def test_writer_prompt_contains_phase10_evidence_rules():
    from app.prompts import WRITER_PROMPT

    required = [
        "approximately three highly relevant supported skills",
        "final PROFILE bullet",
        "Create two principal functional skill groups",
        "VERB + DETAILS + SUPPORTED RESULT",
        "Use Verb + Details only",
        "Never infer or manufacture success",
    ]

    for text in required:
        assert text in WRITER_PROMPT


def test_generated_application_composition_audit_defaults():
    from pathlib import Path
    from app.models import GeneratedApplication

    application = GeneratedApplication.model_validate_json(
        Path(
            "benchmarks/fixtures/"
            "generated_application.json"
        ).read_text()
    )

    assert application.resume_composition.passed is True


def test_composition_audit_serializes_with_application():
    from pathlib import Path
    from app.composition import (
        audit_resume_composition,
    )
    from app.models import GeneratedApplication

    application = GeneratedApplication.model_validate_json(
        Path(
            "benchmarks/fixtures/"
            "generated_application.json"
        ).read_text()
    )

    application.resume_composition = (
        audit_resume_composition(
            application.resume
        )
    )

    data = application.model_dump()

    assert "resume_composition" in data
    assert (
        "structure_issues"
        in data["resume_composition"]
    )
    assert (
        "warnings"
        in data["resume_composition"]
    )


def test_generation_pipeline_applies_composition_audit():
    from pathlib import Path

    text = Path("app/ai.py").read_text()

    start = text.index(
        "def generate_application("
    )

    block = text[start:]

    assert (
        "audit_resume_composition("
        in block
    )

    assert (
        "application.resume_composition"
        in block
    )
