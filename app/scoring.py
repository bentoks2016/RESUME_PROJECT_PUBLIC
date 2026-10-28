from dataclasses import dataclass

from app.models import (
    KeywordAnalysis,
    ScoreBreakdown,
)


# =========================================================
# MATCH SCORE WEIGHTS
# =========================================================

# Qualification Match measures candidate evidence only.
#
# ATS keyword coverage is deliberately excluded. The
# original relative evidence weights are preserved and
# normalized by their total (0.80) during calculation.
QUALIFICATION_WEIGHTS = {
    "required_skills": 0.30,
    "experience_alignment": 0.25,
    "leadership_seniority": 0.10,
    "education": 0.05,
    "preferred_qualifications": 0.05,
    "industry_alignment": 0.05,
}

QUALIFICATION_WEIGHT_TOTAL = sum(
    QUALIFICATION_WEIGHTS.values()
)


# =========================================================
# KEYWORD IMPORTANCE WEIGHTS
# =========================================================

KEYWORD_IMPORTANCE_WEIGHTS = {
    "critical": 4.0,
    "required": 3.0,
    "high": 3.0,
    "preferred": 2.0,
    "medium": 2.0,
    "low": 1.0,
}


# =========================================================
# KEYWORD STATUS SCORES
# =========================================================

# Current ATS:
# Keyword must actually occur in the current resume.

CURRENT_STATUS_VALUES = {
    "SUPPORTED": 1.0,
    "TRANSFERABLE": 0.65,
    "MISSING": 0.0,
}


# Tailored ATS:
# Supported keywords can be fully incorporated.
# Transferable keywords receive partial credit.
# Missing qualifications receive no credit.

TAILORED_STATUS_VALUES = {
    "SUPPORTED": 1.0,
    "TRANSFERABLE": 0.70,
    "MISSING": 0.0,
}


@dataclass
class ScoringResult:
    match_score: int
    ats_score: int


def clamp(
    value: float,
    minimum: float = 0,
    maximum: float = 100
) -> float:
    """
    Keep all scores between 0 and 100.
    """

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


def normalize_importance(
    importance: str
) -> float:
    """
    Convert Gemini's importance label into a
    deterministic numerical weight.
    """

    value = (
        importance
        or ""
    ).strip().lower()

    return KEYWORD_IMPORTANCE_WEIGHTS.get(
        value,
        1.0
    )


def normalize_status(
    status: str
) -> str:
    """
    Normalize status labels returned by the AI.
    """

    value = (
        status
        or ""
    ).strip().upper()

    if value not in {
        "SUPPORTED",
        "TRANSFERABLE",
        "MISSING",
    }:
        return "MISSING"

    return value


# =========================================================
# ATS SCORING
# =========================================================

def calculate_current_ats_score(
    keywords: list[KeywordAnalysis]
) -> int:
    """
    Calculate ATS coverage for the CURRENT resume.

    A keyword contributes only when it is actually
    present in the uploaded resume.

    Keyword importance controls how much each keyword
    contributes to the final ATS score.
    """

    if not keywords:
        return 0

    earned = 0.0
    possible = 0.0

    for keyword in keywords:

        importance = normalize_importance(
            keyword.importance
        )

        possible += importance

        if not keyword.currently_in_resume:
            continue

        status = normalize_status(
            keyword.status
        )

        status_value = CURRENT_STATUS_VALUES.get(
            status,
            0.0
        )

        earned += (
            importance
            * status_value
        )

    if possible == 0:
        return 0

    score = (
        earned / possible
    ) * 100

    return round(
        clamp(score)
    )


def calculate_tailored_ats_score(
    keywords: list[KeywordAnalysis]
) -> int:
    """
    Calculate potential ATS coverage after truthful
    optimization.

    Only keywords Gemini identifies as legitimately
    usable in the tailored resume receive credit.

    Unsupported/MISSING qualifications receive no credit.
    """

    if not keywords:
        return 0

    earned = 0.0
    possible = 0.0

    for keyword in keywords:

        importance = normalize_importance(
            keyword.importance
        )

        possible += importance

        if not keyword.use_in_tailored_resume:
            continue

        status = normalize_status(
            keyword.status
        )

        status_value = TAILORED_STATUS_VALUES.get(
            status,
            0.0
        )

        earned += (
            importance
            * status_value
        )

    if possible == 0:
        return 0

    score = (
        earned / possible
    ) * 100

    return round(
        clamp(score)
    )


# =========================================================
# MATCH SCORING
# =========================================================

def calculate_match_score(
    breakdown: ScoreBreakdown,
    ats_score: int | None = None,
) -> int:
    """
    Calculate candidate Qualification Match.

    Qualification Match measures evidence alignment with
    the target role. ATS keyword coverage is intentionally
    excluded.

    ats_score is retained temporarily for compatibility
    with existing callers, but does not affect this score.
    """

    values = {
        "required_skills":
            breakdown.required_skills,

        "experience_alignment":
            breakdown.experience_alignment,

        "leadership_seniority":
            breakdown.leadership_seniority,

        "education":
            breakdown.education,

        "preferred_qualifications":
            breakdown.preferred_qualifications,

        "industry_alignment":
            breakdown.industry_alignment,
    }

    weighted = 0.0

    for category, weight in (
        QUALIFICATION_WEIGHTS.items()
    ):
        weighted += (
            clamp(values[category])
            * weight
        )

    if QUALIFICATION_WEIGHT_TOTAL == 0:
        return 0

    score = (
        weighted
        / QUALIFICATION_WEIGHT_TOTAL
    )

    return round(
        clamp(score)
    )


# =========================================================
# ANALYSIS SCORING
# =========================================================

def calculate_analysis_scores(
    breakdown: ScoreBreakdown,
    keywords: list[KeywordAnalysis]
) -> dict:
    """
    Calculate all deterministic scores used during
    initial job/resume analysis.
    """

    current_ats = (
        calculate_current_ats_score(
            keywords
        )
    )

    potential_ats = (
        calculate_tailored_ats_score(
            keywords
        )
    )

    # Qualification Match is evidence-based. Merely
    # tailoring wording or increasing ATS keyword coverage
    # does not increase the candidate's qualifications.
    current_match = (
        calculate_match_score(
            breakdown
        )
    )

    potential_match = current_match

    return {
        "current_match_score":
            current_match,

        "estimated_tailored_score":
            potential_match,

        "current_ats_score":
            current_ats,

        "estimated_tailored_ats_score":
            potential_ats,
    }


def calculate_final_match_score(
    breakdown,
    final_ats_score: int | None = None,
) -> int:
    """
    Calculate final evidence-based Qualification Match.

    ATS coverage is measured and reported independently.
    It cannot increase qualification alignment merely
    because supported terminology was added to the resume.
    """

    values = {
        "required_skills":
            breakdown.required_skills,
        "experience_alignment":
            breakdown.experience_alignment,
        "leadership_seniority":
            breakdown.leadership_seniority,
        "education":
            breakdown.education,
        "preferred_qualifications":
            breakdown.preferred_qualifications,
        "industry_alignment":
            breakdown.industry_alignment,
    }

    weighted = sum(
        clamp(values[category]) * weight
        for category, weight
        in QUALIFICATION_WEIGHTS.items()
    )

    if QUALIFICATION_WEIGHT_TOTAL == 0:
        return 0

    return round(
        clamp(
            weighted
            / QUALIFICATION_WEIGHT_TOTAL
        )
    )
