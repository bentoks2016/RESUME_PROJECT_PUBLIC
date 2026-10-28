from app.models import KeywordAnalysis, ScoreBreakdown
from app.scoring import (
    calculate_analysis_scores,
    calculate_current_ats_score,
    calculate_final_match_score,
    calculate_match_score,
    calculate_tailored_ats_score,
    clamp,
    normalize_status,
)


def keyword(
    name,
    status="SUPPORTED",
    importance="required",
    current=True,
    tailored=True,
):
    return KeywordAnalysis(
        keyword=name,
        importance=importance,
        status=status,
        evidence="test evidence",
        currently_in_resume=current,
        use_in_tailored_resume=tailored,
    )


def test_clamp_enforces_score_boundaries():
    assert clamp(-50) == 0
    assert clamp(50) == 50
    assert clamp(150) == 100


def test_unknown_status_becomes_missing():
    assert normalize_status("something-else") == "MISSING"


def test_current_ats_requires_keyword_to_be_present():
    keywords = [
        keyword(
            "Python",
            status="SUPPORTED",
            current=False,
        )
    ]

    assert calculate_current_ats_score(keywords) == 0


def test_missing_keyword_receives_no_tailored_credit():
    keywords = [
        keyword(
            "Kubernetes",
            status="MISSING",
            tailored=True,
        )
    ]

    assert calculate_tailored_ats_score(keywords) == 0


def test_supported_keyword_receives_full_tailored_credit():
    keywords = [
        keyword(
            "Python",
            status="SUPPORTED",
            tailored=True,
        )
    ]

    assert calculate_tailored_ats_score(keywords) == 100


def test_transferable_keyword_receives_partial_tailored_credit():
    keywords = [
        keyword(
            "Cloud",
            status="TRANSFERABLE",
            tailored=True,
        )
    ]

    assert calculate_tailored_ats_score(keywords) == 70


def test_match_score_is_bounded():
    breakdown = ScoreBreakdown(
        required_skills=100,
        experience_alignment=100,
        ats_keyword_coverage=100,
        leadership_seniority=100,
        education=100,
        preferred_qualifications=100,
        industry_alignment=100,
    )

    assert calculate_match_score(
        breakdown,
        100,
    ) == 100


def test_analysis_scores_are_python_calculated():
    breakdown = ScoreBreakdown(
        required_skills=50,
        experience_alignment=50,
        ats_keyword_coverage=99,
        leadership_seniority=50,
        education=50,
        preferred_qualifications=50,
        industry_alignment=50,
    )

    keywords = [
        keyword(
            "Python",
            status="SUPPORTED",
            current=False,
            tailored=True,
        )
    ]

    result = calculate_analysis_scores(
        breakdown,
        keywords,
    )

    assert result["current_ats_score"] == 0
    assert result["estimated_tailored_ats_score"] == 100

    # ATS optimization is independent of Qualification
    # Match. Better keyword coverage does not create new
    # candidate qualifications.
    assert result["estimated_tailored_score"] == (
        result["current_match_score"]
    )


def test_ats_score_does_not_change_qualification_match():
    breakdown = ScoreBreakdown(
        required_skills=70,
        experience_alignment=70,
        ats_keyword_coverage=0,
        leadership_seniority=70,
        education=70,
        preferred_qualifications=70,
        industry_alignment=70,
    )

    low_ats = calculate_match_score(
        breakdown,
        0,
    )

    high_ats = calculate_match_score(
        breakdown,
        100,
    )

    assert low_ats == high_ats == 70


def test_tailoring_alone_does_not_improve_qualification_match():
    breakdown = ScoreBreakdown(
        required_skills=80,
        experience_alignment=75,
        ats_keyword_coverage=10,
        leadership_seniority=80,
        education=70,
        preferred_qualifications=50,
        industry_alignment=85,
    )

    keywords = [
        keyword(
            "Operational transformation",
            status="SUPPORTED",
            current=False,
            tailored=True,
        )
    ]

    result = calculate_analysis_scores(
        breakdown,
        keywords,
    )

    assert result["current_ats_score"] == 0
    assert (
        result["estimated_tailored_ats_score"]
        == 100
    )

    assert (
        result["estimated_tailored_score"]
        == result["current_match_score"]
    )


def test_final_ats_does_not_change_qualification_match():
    breakdown = ScoreBreakdown(
        required_skills=60,
        experience_alignment=60,
        ats_keyword_coverage=0,
        leadership_seniority=60,
        education=60,
        preferred_qualifications=60,
        industry_alignment=60,
    )

    assert calculate_final_match_score(
        breakdown,
        0,
    ) == calculate_final_match_score(
        breakdown,
        100,
    )


def test_generation_protects_final_evidence_breakdown():
    from pathlib import Path

    text = Path("app/ai.py").read_text()
    start = text.index(
        "def generate_application("
    )
    block = text[start:]

    assert (
        "application.final_score_breakdown = "
        "FinalScoreBreakdown("
        in block
    )
    assert (
        "analysis.score_breakdown.required_skills"
        in block
    )
    assert (
        "analysis.score_breakdown.experience_alignment"
        in block
    )


def test_methodology_separates_qualification_and_ats():
    from pathlib import Path

    text = Path("app/main.py").read_text()
    start = text.index(
        '@app.get("/api/scoring-methodology")'
    )
    block = text[start:]

    assert '"qualification_match_weights"' in block
    assert (
        '"independent_from_qualification_match": True'
        in block
    )
    assert (
        '"ats_keyword_coverage": 20'
        not in block
    )


def test_score_labels_distinguish_qualification_and_ats():
    from pathlib import Path

    text = Path(
        "app/templates/index.html"
    ).read_text()

    assert "Qualification Match" in text
    assert "Evidence-Based Match Potential" in text
    assert "Current ATS Coverage" in text
    assert "Estimated ATS Coverage" in text
    assert "Final Qualification Match" in text
    assert "Final ATS Coverage" in text
