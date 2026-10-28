import re
from dataclasses import dataclass

from app.models import (
    GapVerificationResult,
    KeywordAnalysis,
    ResumeDocument,
)


@dataclass
class ATSKeyword:
    keyword: str
    importance: str
    source: str


IMPORTANCE_WEIGHT = {
    "critical": 4,
    "required": 3,
    "high": 3,
    "preferred": 2,
    "medium": 2,
    "low": 1,
}


def normalize_text(
    value: str
) -> str:

    value = (
        value
        or ""
    ).lower()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


def keyword_present(
    keyword: str,
    text: str
) -> bool:

    keyword = normalize_text(
        keyword
    )

    text = normalize_text(
        text
    )

    if not keyword:
        return False

    return keyword in text


def build_authorized_keywords(
    keyword_analysis: list[KeywordAnalysis],
    verification: GapVerificationResult
) -> list[ATSKeyword]:
    """
    Build the ATS keyword whitelist.

    Only terminology supported by the original resume,
    transferable evidence, or newly verified candidate
    evidence may enter the whitelist.
    """

    allowed = {}


    # -----------------------------------------
    # Original resume evidence
    # -----------------------------------------

    for item in keyword_analysis:

        status = (
            item.status
            or ""
        ).strip().upper()


        if status not in {
            "SUPPORTED",
            "TRANSFERABLE"
        }:

            continue


        if not item.use_in_tailored_resume:

            continue


        key = normalize_text(
            item.keyword
        )


        if not key:

            continue


        allowed[key] = ATSKeyword(
            keyword=item.keyword,
            importance=item.importance,
            source=status
        )


    # -----------------------------------------
    # Candidate-verified gap evidence
    # -----------------------------------------

    for item in verification.items:

        verification_result = (
            item.verification_result
            or ""
        ).strip().upper()


        verified_status = (
            item.verified_status
            or ""
        ).strip().upper()


        if (
            verification_result != "VERIFIED"
            or verified_status != "SUPPORTED"
        ):

            continue


        for keyword in item.supported_keywords:

            key = normalize_text(
                keyword
            )


            if not key:

                continue


            if key not in allowed:

                allowed[key] = ATSKeyword(
                    keyword=keyword,
                    importance="required",
                    source="VERIFIED_GAP"
                )


    return list(
        allowed.values()
    )


def resume_to_searchable_text(
    resume: ResumeDocument
) -> str:
    """
    Flatten the structured resume into searchable
    text for deterministic ATS auditing.
    """

    pieces = []


    # Profile
    pieces.extend(
        resume.profile
    )


    # Career history
    for position in resume.career_positions:

        pieces.extend([
            position.job_title,
            position.employer,
            position.location,
            position.dates,
        ])


    # Functional achievement groups
    for group in resume.skill_groups:

        pieces.append(
            group.name
        )

        pieces.extend(
            group.accomplishments
        )


    # Education
    for item in resume.education:

        pieces.extend([
            item.program_name,
            item.school_name,
            item.location,
            item.dates,
        ])


    # Additional training
    for item in resume.additional_training:

        pieces.extend([
            item.course_name,
            item.provider,
            item.location,
            item.date,
        ])


    return "\n".join(
        value
        for value in pieces
        if value
    )


def audit_resume_keywords(
    resume: ResumeDocument,
    authorized_keywords: list[ATSKeyword]
) -> dict:
    """
    Measure the actual occurrence of authorized ATS
    keywords in the generated resume.

    Important keywords carry more weight.
    """

    text = resume_to_searchable_text(
        resume
    )


    found = []

    missing = []


    earned_weight = 0

    possible_weight = 0


    for item in authorized_keywords:

        importance = (
            item.importance
            or ""
        ).strip().lower()


        weight = IMPORTANCE_WEIGHT.get(
            importance,
            1
        )


        possible_weight += weight


        if keyword_present(
            item.keyword,
            text
        ):

            found.append(
                item.keyword
            )

            earned_weight += weight

        else:

            missing.append(
                item.keyword
            )


    if possible_weight > 0:

        score = round(
            (
                earned_weight
                / possible_weight
            )
            * 100
        )

    else:

        score = 0


    return {
        "score": score,

        "found": found,

        "missing": missing,

        "authorized_count":
            len(authorized_keywords),
    }


def validate_ats_structure(
    resume: ResumeDocument
) -> dict:
    """
    Validate the minimum structural requirements
    of the generated ATS resume.
    """

    issues = []


    if not resume.name.strip():

        issues.append(
            "Candidate name is missing."
        )


    if not resume.profile:

        issues.append(
            "Profile section is missing."
        )


    if not resume.career_positions:

        issues.append(
            "Experience section is missing."
        )


    if not resume.skill_groups:

        issues.append(
            "Skill groups are missing."
        )


    if not resume.education:

        issues.append(
            "Education section is missing."
        )


    if not resume.contact.email:

        issues.append(
            "Candidate email is missing."
        )


    return {
        "passed":
            len(issues) == 0,

        "issues":
            issues,
    }
