"""
Deterministic structural checks for the approved resume
composition specification.

This module does not generate or rewrite candidate facts.
Factual support remains the responsibility of the existing
evidence, verification, and integrity layers.
"""

import re

from app.models import (
    ResumeCompositionAudit,
    ResumeDocument,
)


EXPERIENCE_PATTERN = re.compile(
    r"\b\d+\+?\s+(?:years?|yrs?)\b",
    re.IGNORECASE,
)


def normalize(value: str) -> str:
    return " ".join(
        (value or "").split()
    ).casefold()


def education_training_terms(
    resume: ResumeDocument,
) -> list[str]:
    terms = []

    for item in resume.education:
        if item.program_name:
            terms.append(item.program_name)

        if item.school_name:
            terms.append(item.school_name)

    for item in resume.additional_training:
        if item.course_name:
            terms.append(item.course_name)

        if item.provider:
            terms.append(item.provider)

    return [
        normalize(term)
        for term in terms
        if normalize(term)
    ]


def audit_resume_composition(
    resume: ResumeDocument,
) -> ResumeCompositionAudit:
    issues = []
    warnings = []

    profile = [
        item.strip()
        for item in resume.profile
        if item and item.strip()
    ]

    first_present = bool(profile)

    if not first_present:
        issues.append(
            "PROFILE must contain a positioning "
            "first bullet."
        )

    elif not EXPERIENCE_PATTERN.search(
        profile[0]
    ):
        warnings.append(
            "PROFILE first bullet does not contain "
            "an explicit supported years-of-experience "
            "statement."
        )

    final_education_present = False

    terms = education_training_terms(
        resume
    )

    if profile and terms:
        final_profile = normalize(
            profile[-1]
        )

        final_education_present = any(
            term in final_profile
            for term in terms
        )

        if not final_education_present:
            issues.append(
                "PROFILE final bullet must reference "
                "supported education or training."
            )

    elif profile and not terms:
        # A candidate with no supplied education/training
        # must not have credentials invented merely to
        # satisfy the document structure.
        final_education_present = True

        warnings.append(
            "No source education or training is "
            "available for the PROFILE final bullet."
        )

    group_counts = [
        len(
            [
                item
                for item in group.accomplishments
                if item and item.strip()
            ]
        )
        for group in resume.skill_groups
    ]

    principal_group_count = len(
        resume.skill_groups
    )

    if principal_group_count < 2:
        issues.append(
            "Resume should contain two principal "
            "functional skill groups when sufficient "
            "supported evidence exists."
        )

    if principal_group_count > 2:
        warnings.append(
            "Resume contains more than the two "
            "principal functional skill groups in "
            "the approved target structure."
        )

    for index, count in enumerate(
        group_counts[:2],
        1,
    ):
        if count < 4:
            warnings.append(
                f"Skill Group {index} contains "
                f"{count} accomplishments; target "
                "is approximately four when supported "
                "evidence permits."
            )

        elif count > 4:
            warnings.append(
                f"Skill Group {index} contains "
                f"{count} accomplishments; target "
                "is approximately four."
            )

    return ResumeCompositionAudit(
        passed=not issues,
        profile_first_bullet_present=first_present,
        profile_final_education_bullet_present=(
            final_education_present
        ),
        principal_skill_group_count=(
            principal_group_count
        ),
        skill_group_accomplishment_counts=(
            group_counts
        ),
        structure_issues=issues,
        warnings=warnings,
    )


def audit_cover_letter_composition(
    letter,
    *,
    employer_context_sources=None,
    motivation_basis="INFERRED_FROM_EVIDENCE",
):
    """
    Deterministically audit the Phase 11 cover-letter
    structure and provenance state.

    This audit does not attempt to determine whether prose
    is persuasive or factually supported. Those remain
    semantic/evidence concerns.
    """
    from app.models import (
        CoverLetterCompositionAudit,
    )

    allowed_motivation_bases = {
        "EXPLICIT_CANDIDATE",
        "INFERRED_FROM_EVIDENCE",
    }

    if motivation_basis not in allowed_motivation_bases:
        raise ValueError(
            "Unsupported cover-letter motivation basis: "
            f"{motivation_basis!r}"
        )

    paragraphs = [
        letter.paragraph_1,
        letter.paragraph_2,
        letter.paragraph_3,
        letter.paragraph_4,
    ]

    substantive = [
        item.strip()
        for item in paragraphs
        if item and item.strip()
    ]

    issues = []
    warnings = []

    if len(substantive) != 4:
        issues.append(
            "Cover letter must contain exactly four "
            "substantive body paragraphs."
        )

    sources = list(
        employer_context_sources
        or ["JOB_POSTING"]
    )

    if not sources:
        issues.append(
            "Cover letter must identify at least one "
            "employer-context source."
        )

    if motivation_basis == "INFERRED_FROM_EVIDENCE":
        warnings.append(
            "Personal motivation was inferred from verified "
            "candidate evidence and the advertised role; "
            "no independent personal history is implied."
        )

    return CoverLetterCompositionAudit(
        passed=not issues,
        substantive_paragraph_count=len(
            substantive
        ),
        employer_context_sources=sources,
        motivation_basis=motivation_basis,
        structure_issues=issues,
        warnings=warnings,
    )
