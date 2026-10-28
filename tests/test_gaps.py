from app.gaps import (
    NO_EVIDENCE_SUMMARY,
    normalize_no_answers,
)
from app.models import (
    GapVerificationItem,
    GapVerificationResult,
)


def verification_item(
    *,
    gap_id="gap-1",
    verification_result="VERIFIED",
    verified_status="SUPPORTED",
    keywords=None,
):
    return GapVerificationItem(
        gap_id=gap_id,
        requirement="Example requirement",
        original_status="TRANSFERABLE",
        verified_status=verified_status,
        verification_result=verification_result,
        evidence_summary="Model-generated interpretation",
        supported_keywords=keywords or ["Kubernetes"],
        caution="",
    )


def test_no_answer_overrides_false_model_verification():
    verification = GapVerificationResult(
        items=[
            verification_item()
        ]
    )

    answers = [
        {
            "gap_id": "gap-1",
            "has_experience": False,
        }
    ]

    result = normalize_no_answers(
        verification,
        answers,
    )

    item = result.items[0]

    assert item.verification_result == "NOT_VERIFIED"
    assert item.supported_keywords == []
    assert item.evidence_summary == NO_EVIDENCE_SUMMARY


def test_no_answer_does_not_downgrade_existing_status():
    verification = GapVerificationResult(
        items=[
            verification_item(
                verified_status="TRANSFERABLE",
            )
        ]
    )

    result = normalize_no_answers(
        verification,
        [
            {
                "gap_id": "gap-1",
                "has_experience": False,
            }
        ],
    )

    assert (
        result.items[0].verified_status
        == "TRANSFERABLE"
    )


def test_yes_answer_is_not_modified():
    verification = GapVerificationResult(
        items=[
            verification_item()
        ]
    )

    result = normalize_no_answers(
        verification,
        [
            {
                "gap_id": "gap-1",
                "has_experience": True,
            }
        ],
    )

    item = result.items[0]

    assert item.verification_result == "VERIFIED"
    assert item.verified_status == "SUPPORTED"
    assert item.supported_keywords == [
        "Kubernetes"
    ]


def test_only_matching_gap_is_normalized():
    verification = GapVerificationResult(
        items=[
            verification_item(
                gap_id="gap-1"
            ),
            verification_item(
                gap_id="gap-2"
            ),
        ]
    )

    result = normalize_no_answers(
        verification,
        [
            {
                "gap_id": "gap-1",
                "has_experience": False,
            },
            {
                "gap_id": "gap-2",
                "has_experience": True,
            },
        ],
    )

    assert (
        result.items[0].verification_result
        == "NOT_VERIFIED"
    )

    assert (
        result.items[1].verification_result
        == "VERIFIED"
    )
