"""
Deterministic role-to-candidate opportunity mapping.

Phase 8A:
Map job-posting requirements already classified by
ResumeAnalysis to DIRECT / TRANSFERABLE / NONE.

Phase 9A:
Derive candidate verification questions from
TRANSFERABLE / NONE role mappings.

This module performs no AI calls and cannot upgrade
candidate evidence.
"""

import re

from app.models import (
    GapQuestion,
    Requirement,
    ResumeAnalysis,
    RoleOpportunityMapping,
    RoleOpportunityMappingResult,
)


STATUS_TO_CONNECTION = {
    "SUPPORTED": "DIRECT",
    "TRANSFERABLE": "TRANSFERABLE",
    "MISSING": "NONE",
}


def normalize_status(value: str) -> str:
    return (value or "").strip().upper()


def normalize_requirement(value: str) -> str:
    """
    Normalize superficial requirement wording differences
    without performing semantic inference.
    """
    value = (value or "").casefold()

    value = re.sub(
        r"[^a-z0-9]+",
        " ",
        value,
    )

    return " ".join(
        value.split()
    )


REQUIREMENT_CONNECTORS = {
    "a",
    "an",
    "and",
    "or",
    "the",
    "to",
    "of",
    "for",
    "in",
    "with",
}


def requirement_tokens(value: str) -> set[str]:
    return {
        token
        for token in normalize_requirement(
            value
        ).split()
        if token not in REQUIREMENT_CONNECTORS
    }


def question_covers_requirement(
    question: str,
    requirement: str,
) -> bool:
    """
    Determine whether an existing question conservatively
    covers an analyzed requirement.

    Exact normalized matches pass. A question containing
    every meaningful requirement token also passes, allowing
    harmless qualifiers such as "or advanced analytics".

    Partial overlap alone is not sufficient.
    """
    normalized_question = normalize_requirement(
        question
    )
    normalized_requirement = normalize_requirement(
        requirement
    )

    if (
        normalized_question
        == normalized_requirement
    ):
        return True

    required = requirement_tokens(
        requirement
    )
    questioned = requirement_tokens(
        question
    )

    return bool(
        required
        and required.issubset(
            questioned
        )
    )


def map_requirement(
    requirement: Requirement,
) -> RoleOpportunityMapping:
    """
    Convert an existing evidence classification to its
    Phase 8A connection.

    This function deliberately does not infer a stronger
    candidate status than ResumeAnalysis established.
    """

    status = normalize_status(
        requirement.status
    )

    if status not in STATUS_TO_CONNECTION:
        raise ValueError(
            "Unsupported requirement status for "
            f"opportunity mapping: {requirement.status!r}"
        )

    connection = STATUS_TO_CONNECTION[status]

    if connection == "DIRECT":
        rationale = (
            "Existing candidate analysis provides direct "
            "evidence for this job-posting requirement."
        )
        should_ask = False

    elif connection == "TRANSFERABLE":
        rationale = (
            "Related candidate evidence exists, but direct "
            "experience is not established."
        )
        should_ask = True

    else:
        rationale = (
            "The job posting establishes this role "
            "requirement, but current candidate evidence "
            "does not establish the capability."
        )
        should_ask = True

    # Requirement.evidence already follows the application's
    # evidence semantics. For MISSING requirements it contains
    # no positive candidate evidence.
    candidate_evidence = (
        requirement.evidence
        if connection != "NONE"
        else ""
    )

    return RoleOpportunityMapping(
        requirement=requirement.requirement,
        importance=requirement.importance,
        connection=connection,
        signal_source="JOB_POSTING",
        role_evidence=requirement.requirement,
        candidate_evidence=candidate_evidence,
        keywords=list(
            requirement.keywords or []
        ),
        rationale=rationale,
        should_ask_gap_question=should_ask,
    )


def build_role_opportunity_mapping(
    analysis: ResumeAnalysis,
) -> RoleOpportunityMappingResult:
    mappings = [
        map_requirement(requirement)
        for requirement in analysis.requirements
    ]

    direct_count = sum(
        item.connection == "DIRECT"
        for item in mappings
    )

    transferable_count = sum(
        item.connection == "TRANSFERABLE"
        for item in mappings
    )

    none_count = sum(
        item.connection == "NONE"
        for item in mappings
    )

    return RoleOpportunityMappingResult(
        mappings=mappings,
        direct_count=direct_count,
        transferable_count=transferable_count,
        none_count=none_count,
        source="JOB_POSTING",
        summary=(
            f"{direct_count} direct, "
            f"{transferable_count} transferable, "
            f"{none_count} unsupported job-posting "
            "connections."
        ),
    )


def build_job_posting_gap_questions(
    analysis: ResumeAnalysis,
) -> list[GapQuestion]:
    """
    Build Phase 9A gap questions.

    Preserve existing analysis-generated gap questions where
    possible. Add deterministic fallback questions only for
    TRANSFERABLE or MISSING requirements that do not already
    have one.

    A question requests candidate evidence. It never creates
    candidate evidence.
    """

    mapping = build_role_opportunity_mapping(
        analysis
    )

    existing = list(
        analysis.gap_questions or []
    )

    existing_requirement_texts = [
        question.requirement
        for question in existing
    ]

    generated = []

    for index, item in enumerate(
        mapping.mappings,
        1,
    ):
        if not item.should_ask_gap_question:
            continue

        if any(
            question_covers_requirement(
                question_requirement,
                item.requirement,
            )
            for question_requirement
            in existing_requirement_texts
        ):
            continue

        if item.connection == "TRANSFERABLE":
            reason = (
                "Related candidate evidence exists, but "
                "direct experience is not established. "
                "Additional factual information may clarify "
                "the level of experience."
            )
        else:
            reason = (
                "This job-posting requirement is not "
                "established by the candidate's current "
                "evidence. Additional factual information "
                "is required before it can be claimed."
            )

        generated.append(
            GapQuestion(
                id=f"job-gap-{index}",
                requirement=item.requirement,
                reason=reason,
                suggested_examples=[],
            )
        )

    return existing + generated
