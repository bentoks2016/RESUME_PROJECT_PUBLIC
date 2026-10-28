from app.models import (
    EmployerInterviewQuestion,
    GapInterviewPreparation,
    InterviewPreparationResult,
    LikelyInterviewQuestion,
    STARStory,
)


def test_interview_preparation_contract():
    result = InterviewPreparationResult(
        preparation_summary=(
            "Prepare evidence around leadership "
            "and transferable experience."
        ),
        likely_questions=[
            LikelyInterviewQuestion(
                question=(
                    "Describe a relevant project."
                ),
                category="Experience",
                likelihood="HIGH",
                why_likely=(
                    "The role emphasizes delivery."
                ),
                interviewer_is_testing=(
                    "Ownership and execution."
                ),
            ),
        ],
        star_stories=[
            STARStory(
                title="Verified delivery example",
                evidence_strength="READY",
                situation="Known source context.",
                task="Known responsibility.",
                action="Known candidate action.",
                result="Known source result.",
                source_evidence="Original resume",
                useful_for_questions=[
                    "Project delivery"
                ],
                missing_details=[],
            ),
        ],
        gap_preparation=[
            GapInterviewPreparation(
                requirement="Example requirement",
                likely_question=(
                    "What experience do you have here?"
                ),
                gap_type="TRANSFERABLE",
                truthful_answer_strategy=(
                    "Acknowledge the distinction and "
                    "bridge to verified related work."
                ),
                transferable_evidence=[
                    "Related source experience"
                ],
                bridge_to_strength=(
                    "Connect related delivery experience."
                ),
                do_not_claim=[
                    "Direct experience not in evidence"
                ],
            ),
        ],
        questions_for_employer=[
            EmployerInterviewQuestion(
                question=(
                    "What outcomes define success "
                    "in the first six months?"
                ),
                audience="HIRING_MANAGER",
                why_ask=(
                    "Clarifies role priorities."
                ),
            ),
        ],
        final_advice=[
            "Keep answers evidence-based."
        ],
    )

    assert len(result.likely_questions) == 1
    assert len(result.star_stories) == 1
    assert len(result.gap_preparation) == 1
    assert len(result.questions_for_employer) == 1


def test_star_story_supports_missing_details():
    story = STARStory(
        title="Incomplete but useful example",
        evidence_strength="NEEDS_DETAIL",
        situation="Known context",
        task="Known task",
        action="Known action",
        result="Result not established.",
        source_evidence="Original resume",
        missing_details=[
            "Specific outcome",
            "Scope",
        ],
    )

    assert story.evidence_strength == "NEEDS_DETAIL"
    assert "Specific outcome" in story.missing_details


def test_gap_preparation_can_forbid_unsupported_claim():
    preparation = GapInterviewPreparation(
        requirement="Direct platform experience",
        likely_question=(
            "Tell me about your direct experience."
        ),
        gap_type="MISSING",
        truthful_answer_strategy=(
            "Acknowledge no demonstrated direct "
            "experience and bridge to related evidence."
        ),
        transferable_evidence=[
            "Related verified experience"
        ],
        bridge_to_strength=(
            "Discuss adjacent capability."
        ),
        do_not_claim=[
            "Direct platform implementation"
        ],
    )

    assert preparation.do_not_claim == [
        "Direct platform implementation"
    ]
