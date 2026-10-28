from app.models import GapVerificationResult


NO_EVIDENCE_SUMMARY = (
    "The candidate did not confirm additional "
    "experience sufficient to close this requirement."
)

NO_EVIDENCE_CAUTION = (
    "No new evidence was supplied. This result "
    "must not negate or contradict evidence in "
    "the original resume."
)


def normalize_no_answers(
    verification: GapVerificationResult,
    gap_answers: list,
) -> GapVerificationResult:
    """
    Deterministically normalize explicit NO gap answers.

    A NO answer means that no additional evidence was
    supplied for the specific gap.

    It must never:
    - create verified evidence
    - authorize new ATS keywords
    - negate evidence from the original resume

    verified_status is deliberately not changed here.
    The current data model does not yet provide a
    deterministic relationship between GapQuestion and
    its originating Requirement.
    """

    no_answer_ids = {
        str(answer.get("gap_id", ""))
        for answer in gap_answers
        if not answer.get("has_experience", False)
    }

    for item in verification.items:

        if str(item.gap_id) not in no_answer_ids:
            continue

        item.verification_result = "NOT_VERIFIED"
        item.supported_keywords = []
        item.evidence_summary = NO_EVIDENCE_SUMMARY
        item.caution = NO_EVIDENCE_CAUTION

    return verification
