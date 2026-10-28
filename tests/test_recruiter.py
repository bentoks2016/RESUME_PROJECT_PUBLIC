import pytest
from pydantic import ValidationError

from app.models import (
    RecruiterConcern,
    RecruiterInterviewQuestion,
    RecruiterReviewResult,
)


def valid_review():
    return RecruiterReviewResult(
        interview_recommendation="YES",
        first_impression=(
            "Relevant experience with several areas "
            "requiring clarification."
        ),
        strongest_signals=[
            "Relevant leadership experience",
        ],
        concerns=[
            RecruiterConcern(
                severity="CLARIFICATION",
                category="Scope",
                observation=(
                    "Ownership of a major project "
                    "is not completely clear."
                ),
                why_it_matters=(
                    "The hiring manager may need to "
                    "understand personal responsibility."
                ),
                evidence="Project description",
                suggested_fix=(
                    "Clarify personal responsibility "
                    "using truthful source evidence."
                ),
            ),
        ],
        unclear_points=[
            "Individual project ownership",
        ],
        missing_signals=[
            (
                "The submitted resume does not clearly "
                "demonstrate one requested capability."
            ),
        ],
        buzzword_risks=[],
        likely_interview_questions=[
            RecruiterInterviewQuestion(
                question=(
                    "What was your personal responsibility "
                    "for this project?"
                ),
                why_asked=(
                    "Individual ownership is unclear."
                ),
                evidence_to_prepare=(
                    "Specific responsibilities and examples."
                ),
            ),
        ],
        bottom_line=(
            "Worth interviewing, with clarification "
            "needed in several areas."
        ),
    )


def test_recruiter_review_contract_accepts_valid_result():
    review = valid_review()

    assert review.interview_recommendation == "YES"
    assert len(review.concerns) == 1
    assert len(review.likely_interview_questions) == 1


def test_recruiter_review_serializes():
    review = valid_review()

    data = review.model_dump()

    assert data["concerns"][0]["severity"] == (
        "CLARIFICATION"
    )
    assert (
        data["likely_interview_questions"][0]["question"]
    )


def test_recruiter_review_requires_bottom_line():
    data = valid_review().model_dump()
    del data["bottom_line"]

    with pytest.raises(ValidationError):
        RecruiterReviewResult.model_validate(
            data
        )
