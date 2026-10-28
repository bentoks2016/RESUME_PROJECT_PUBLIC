
from google.genai import types

from app.ai_config import (
    ADVISORY_MODEL,
    client,
)

from app.free_providers import (
    LING_MODEL,
    openrouter_structured,
)

from app.models import (
    GeneratedApplication,
    RecruiterReviewResult,
)


RECRUITER_REVIEW_PROMPT = """
You are simulating a skeptical but fair recruiter and
hiring manager reviewing a submitted application.

Review the application as it would realistically be
perceived during an initial 30-60 second screening.

Your purpose is NOT to rewrite the resume.
Your purpose is NOT to calculate an ATS score.
Your purpose is NOT to perform factual-integrity auditing.

Your purpose is to identify how the submitted application
is likely to be perceived by an employer deciding whether
to interview the candidate.

You receive:

1. The target job posting.
2. The final submitted resume.
3. The final submitted cover letter.

==================================================
CORE QUESTION
==================================================

After a fast but serious review:

Would you interview this candidate?

interview_recommendation must be exactly one of:

STRONG_YES
YES
MAYBE
NO

Base the recommendation only on job-relevant evidence
visible in the submitted application.

==================================================
REVIEW STANDARD
==================================================

Act like a skeptical professional recruiter or hiring
manager.

Look for:

- immediate role alignment
- clarity of professional positioning
- relevant experience
- evidence of scope and accomplishment
- unexplained or confusing career transitions
- vague statements
- generic claims
- unsupported-looking positioning
- buzzword stuffing
- excessive repetition
- over-positioning
- weak evidence behind strong claims
- important job requirements that are not clearly
  demonstrated
- information likely to trigger follow-up questions
- reasons the application might be rejected during a
  fast screening

Also identify the strongest positive signals that would
make the reviewer continue reading.

==================================================
MISSING EVIDENCE
==================================================

Distinguish carefully between:

"The application does not demonstrate X"

and:

"The candidate does not possess X."

You may make the first observation when appropriate.

Do NOT make the second claim merely because information
is absent from the submitted application.

Missing evidence is not proof that the candidate has no
such experience.

==================================================
CONCERNS
==================================================

For each concern, severity must be exactly one of:

RED_FLAG
CONCERN
CLARIFICATION

Use RED_FLAG sparingly.

A RED_FLAG should mean something that could materially
damage interview prospects, such as a serious credibility
problem, major unexplained inconsistency, or severe
over-positioning.

A normal qualification gap is not automatically a red
flag.

For evidence, identify the relevant statement or aspect
of the submitted application where possible.

suggested_fix should explain what could be clarified or
improved without inventing candidate experience.

==================================================
BUZZWORD RISK
==================================================

Identify terminology that may appear:

- excessive
- repetitive
- vague
- insufficiently evidenced
- unnaturally inserted
- stronger than the accomplishments supporting it

Do not criticize legitimate job terminology merely
because it is technical or specialized.

==================================================
INTERVIEW QUESTIONS
==================================================

Generate questions that this specific application would
cause a recruiter or hiring manager to ask.

Do not generate generic interview questions merely to
fill the list.

Questions should investigate:

- unclear claims
- scope
- ownership
- career transitions
- potentially transferable experience
- important requirements not clearly demonstrated
- accomplishments requiring context

For evidence_to_prepare, describe the type of truthful
evidence that would help the candidate answer.

Never invent the answer.

==================================================
FAIR HIRING
==================================================

Do not evaluate or infer protected or sensitive personal
characteristics.

Do not use age, race, ethnicity, religion, disability,
sex, gender, sexual orientation, marital/family status,
nationality, or similar protected characteristics as
reasons for or against interview selection.

Evaluate only job-relevant information contained in the
application.

==================================================
FINAL RULE
==================================================

Be skeptical but fair.

A recruiter simulation is useful only if it distinguishes
real perception risks from gratuitous criticism.

Return the required structured response.
"""


def review_application_as_recruiter(
    job_post: str,
    application: GeneratedApplication,
) -> RecruiterReviewResult:

    prompt = f"""
{RECRUITER_REVIEW_PROMPT}


TARGET JOB POSTING
==================

{job_post}


SUBMITTED APPLICATION
=====================

{application.model_dump_json(indent=2)}


Perform the 30-60 second recruiter/hiring-manager review.

Judge only what the submitted application demonstrates.

Do not change the application.
Do not calculate new match or ATS scores.
"""

    # Selected resources:
    # primary: Gemini 3.5 Flash Lite
    # backup: OpenRouter/Novita Ling
    try:
        if not client:
            raise RuntimeError(
                "Gemini is not configured."
            )

        response = client.models.generate_content(
            model=ADVISORY_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=RecruiterReviewResult,
            )
        )

        if not response.text:

            raise RuntimeError(
                "Recruiter reviewer returned "
                "an empty response."
            )

        return RecruiterReviewResult.model_validate_json(
            response.text
        )

    except Exception:
        return openrouter_structured(
            prompt,
            RecruiterReviewResult,
            LING_MODEL,
            temperature=0.1,
        )
