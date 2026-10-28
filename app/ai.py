import json

from google.genai import types

from app.ai_config import (
    ADVISORY_MODEL,
    CRITICAL_MODEL,
    check_ai_configuration,
    client,
)

from app.composition import (
    audit_cover_letter_composition,
    audit_resume_composition,
)

from app.ats import (
    audit_resume_keywords,
    build_authorized_keywords,
    validate_ats_structure,
)

from app.free_providers import (
    LING_MODEL,
    UNION_MODEL,
    groq_structured,
    openrouter_structured,
)

from app.models import (
    FinalScoreBreakdown,
    GeneratedApplication,
    GapVerificationResult,
    ResumeAnalysis,
)

from app.scoring import (
    calculate_analysis_scores,
    calculate_final_match_score,
)

from app.parser import extract_contact_information
from app.gaps import normalize_no_answers
from app.prompts import (
    ANALYSIS_PROMPT,
    GAP_VERIFICATION_PROMPT,
    WRITER_PROMPT,
)

# =========================================================
# ANALYSIS PROMPT
# =========================================================



# =========================================================
# WRITER PROMPT
# =========================================================



def analyze_resume(
    job_post: str,
    resume: str
) -> ResumeAnalysis:

    prompt = f"""
{ANALYSIS_PROMPT}


JOB POSTING
===========

{job_post}


ORIGINAL RESUME
===============

{resume}


Perform the complete job-match and ATS analysis.

Create gap questions for important requirements that
could reasonably represent experience missing from the
candidate's existing resume.
"""

    # Selected resources:
    # primary: Gemini 3.5 Flash Lite
    # backup: OpenRouter/Novita Ling
    try:
        check_ai_configuration()

        response = client.models.generate_content(
            model=ADVISORY_MODEL,

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=ResumeAnalysis,
            )
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty analysis."
            )

        analysis = ResumeAnalysis.model_validate_json(
            response.text
        )

    except Exception:
        analysis = openrouter_structured(
            prompt,
            ResumeAnalysis,
            LING_MODEL,
            temperature=0.1,
        )

    scores = calculate_analysis_scores(
        analysis.score_breakdown,
        analysis.keyword_analysis
    )

    analysis.current_match_score = (
        scores["current_match_score"]
    )

    analysis.estimated_tailored_score = (
        scores["estimated_tailored_score"]
    )

    analysis.current_ats_score = (
        scores["current_ats_score"]
    )

    analysis.estimated_tailored_ats_score = (
        scores[
            "estimated_tailored_ats_score"
        ]
    )

    return analysis


def generate_application(
    job_post: str,
    resume: str,
    analysis: ResumeAnalysis,
    gap_answers: list,
    verification: GapVerificationResult,
    verified_achievements: dict | None = None
) -> GeneratedApplication:

    answers_json = json.dumps(
        gap_answers,
        indent=2,
        ensure_ascii=False
    )


    achievement_json = json.dumps(
        verified_achievements or {},
        indent=2,
        ensure_ascii=False
    )


    # Build an evidence-controlled ATS keyword whitelist.
    authorized_keywords = build_authorized_keywords(
        analysis.keyword_analysis,
        verification
    )


    authorized_keyword_list = [
        item.keyword
        for item in authorized_keywords
    ]


    authorized_keywords_json = json.dumps(
        authorized_keyword_list,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
{WRITER_PROMPT}


TARGET JOB
==========

{job_post}


ORIGINAL RESUME
===============

{resume}


ORIGINAL ANALYSIS
=================

{analysis.model_dump_json(indent=2)}


CANDIDATE-PROVIDED GAP ANSWERS
==============================

{answers_json}


INDEPENDENT GAP VERIFICATION
============================

{verification.model_dump_json(indent=2)}


VERIFIED ACHIEVEMENT ENHANCEMENTS
=================================

{achievement_json}


AUTHORIZED ATS KEYWORDS
=======================

{authorized_keywords_json}


ATS AUTHORIZATION RULE:

The list above contains job terminology that the
candidate's evidence permits you to use.

Prioritize these terms naturally when relevant in:

- Profile
- Skill Group headings
- Accomplishment statements
- Cover letter

Do not force every authorized keyword into the document.

Do not present job-description terminology outside this
authorized list as candidate experience unless it is
directly and unambiguously supported by the source
information.

Do not keyword-stuff.


ACHIEVEMENT RULE:

VERIFIED optimized achievement statements may be used
when creating the resume and cover letter.

PARTIAL statements may be used conservatively.

Never add a metric or result not contained in the verified
achievement evidence.

SKIPPED achievement opportunities must not be upgraded
using invented information.


IMPORTANT:

Only use new gap information according to the independent
verification result.

VERIFIED / SUPPORTED:
May be incorporated as supported experience.

PARTIAL / TRANSFERABLE:
May be incorporated only with accurate transferable
positioning.

NEEDS_DETAIL:
Do not present as established direct experience.

NOT_VERIFIED:
Do not use as candidate experience.


Create the strongest truthful targeted application.

Optimize supported ATS terminology.

Use additional gap information only where the candidate
explicitly confirmed that they possess the experience.

Return the required structured response.
"""

    # Selected $0 resources:
    # primary: OpenRouter/Stealth Union Alpha
    # backup: OpenRouter/Novita Ling
    # reserve: Gemini 3.6 Flash
    try:
        application = openrouter_structured(
            prompt,
            GeneratedApplication,
            UNION_MODEL,
            temperature=0.25,
        )

    except Exception:
        try:
            application = openrouter_structured(
                prompt,
                GeneratedApplication,
                LING_MODEL,
                temperature=0.25,
            )

        except Exception:
            check_ai_configuration()

            response = client.models.generate_content(
                model=CRITICAL_MODEL,

                contents=prompt,

                config=types.GenerateContentConfig(
                    temperature=0.25,
                    response_mime_type="application/json",
                    response_schema=GeneratedApplication,
                )
            )

            if not response.text:

                raise RuntimeError(
                    "Gemini returned an empty application."
                )

            application = (
                GeneratedApplication.model_validate_json(
                    response.text
                )
            )

    # -------------------------------------------------
    # DETERMINISTIC CONTACT PRESERVATION
    # -------------------------------------------------
    # Original-resume contact details are authoritative.
    # Restore them before deterministic ATS validation.
    source_contact = extract_contact_information(
        resume
    )

    application.resume.contact.email = (
        source_contact["email"]
    )
    application.resume.contact.phone = (
        source_contact["phone"]
    )
    application.resume.contact.linkedin = (
        source_contact["linkedin"]
    )

    application.cover_letter.candidate_contact.email = (
        source_contact["email"]
    )
    application.cover_letter.candidate_contact.phone = (
        source_contact["phone"]
    )
    application.cover_letter.candidate_contact.linkedin = (
        source_contact["linkedin"]
    )

    # =====================================================
    # DETERMINISTIC POST-GENERATION ATS AUDIT
    # =====================================================

    # Measure what actually appears in the generated resume.
    ats_result = audit_resume_keywords(
        application.resume,
        authorized_keywords
    )


    # Validate ATS-safe document structure.
    structure_result = validate_ats_structure(
        application.resume
    )


    # Python owns the final ATS score.
    application.final_ats_score = (
        ats_result["score"]
    )


    # Resume rewriting must not upgrade the candidate's
    # underlying qualification evidence. Until verified
    # evidence is deterministically rescored, preserve the
    # original analysis dimensions as the conservative
    # final qualification baseline.
    application.final_score_breakdown = FinalScoreBreakdown(
        required_skills=(
            analysis.score_breakdown.required_skills
        ),
        experience_alignment=(
            analysis.score_breakdown.experience_alignment
        ),
        leadership_seniority=(
            analysis.score_breakdown.leadership_seniority
        ),
        education=(
            analysis.score_breakdown.education
        ),
        preferred_qualifications=(
            analysis.score_breakdown.preferred_qualifications
        ),
        industry_alignment=(
            analysis.score_breakdown.industry_alignment
        ),
    )

    # Python owns final Qualification Match arithmetic.
    # ATS coverage is reported independently.
    application.final_match_score = (
        calculate_final_match_score(
            application.final_score_breakdown,
            application.final_ats_score
        )
    )


    # Preserve Gemini's explanatory placement audit while
    # overwriting deterministic measurement fields.
    application.ats_optimization.authorized_keywords = (
        authorized_keyword_list
    )

    application.ats_optimization.keywords_found = (
        ats_result["found"]
    )

    application.ats_optimization.keywords_missing = (
        ats_result["missing"]
    )

    application.ats_optimization.deterministic_ats_score = (
        ats_result["score"]
    )

    application.ats_optimization.structure_passed = (
        structure_result["passed"]
    )

    application.ats_optimization.structure_issues = (
        structure_result["issues"]
    )


    # keywords_added must represent terms actually found
    # in the generated resume, not terms Gemini says it used.
    application.keywords_added = (
        ats_result["found"]
    )


    application.resume_composition = (
        audit_resume_composition(
            application.resume
        )
    )

    application.cover_letter_composition = (
        audit_cover_letter_composition(
            application.cover_letter,
            employer_context_sources=[
                "JOB_POSTING"
            ],
            motivation_basis=(
                "INFERRED_FROM_EVIDENCE"
            ),
        )
    )

    return application


# =========================================================
# CANDIDATE GAP VERIFICATION
# =========================================================



def verify_gap_answers(
    job_post: str,
    resume: str,
    analysis: ResumeAnalysis,
    gap_answers: list
) -> GapVerificationResult:

    answers_json = json.dumps(
        gap_answers,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
{GAP_VERIFICATION_PROMPT}


TARGET JOB
==========

{job_post}


ORIGINAL RESUME
===============

{resume}


ORIGINAL REQUIREMENT ANALYSIS
=============================

{analysis.model_dump_json(indent=2)}


CANDIDATE GAP ANSWERS
=====================

{answers_json}


Evaluate every candidate gap answer.

Return a verification item for each gap answer.

Do not convert unsupported claims into verified
experience.
"""

    # Selected $0 resources:
    # primary: Groq GPT-OSS 120B
    # backup: OpenRouter/Stealth Union Alpha
    try:
        verification = groq_structured(
            prompt,
            GapVerificationResult,
            temperature=0.0,
        )

    except Exception:
        verification = openrouter_structured(
            prompt,
            GapVerificationResult,
            UNION_MODEL,
            temperature=0.0,
        )

    return normalize_no_answers(
        verification,
        gap_answers,
    )
