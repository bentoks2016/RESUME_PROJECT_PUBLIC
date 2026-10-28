import json

from google.genai import types

from app.ai_config import (
    CRITICAL_MODEL,
    DISCOVERY_MODEL,
    client,
)

from app.free_providers import (
    LING_MODEL,
    UNION_MODEL,
    groq_structured,
    openrouter_structured,
)

from app.models import (
    AchievementAnalysis,
    AchievementVerificationResult,
    ResumeAnalysis,
)


ACHIEVEMENT_ANALYSIS_PROMPT = """
You are an executive resume achievement analyst.

Analyze the candidate's original resume and identify
statements that are relevant to the target job but are
too vague, responsibility-focused, or insufficiently
quantified to be persuasive.

==================================================
OBJECTIVE
==================================================

Find statements that could potentially become stronger
accomplishments if the candidate supplies more factual
information.

Examples of weak statements:

"Responsible for operations and strategy."

"Managed a team."

"Worked with clients."

"Developed AI models."

"Led business development."

"Improved processes."

"Conducted market research."

Do NOT rewrite these by inventing outcomes.

Instead, identify what additional information would make
them stronger.

==================================================
ACHIEVEMENT FRAMEWORK
==================================================

Strong accomplishment statements usually contain:

ACTION
What did the candidate actually do?

CONTEXT
Where, why, or under what circumstances?

SCOPE
How large was the responsibility?

RESULT
What changed because of the work?

METRIC
Can the result or scope be quantified?

A strong statement often follows:

ACTION + CONTEXT/SCOPE + RESULT

Metrics are valuable but NOT mandatory.

A strong qualitative business result is preferable to an
invented number.

==================================================
METRIC DISCOVERY
==================================================

When appropriate, consider asking about:

- team size
- number of clients
- number of users
- geographic coverage
- number of states/countries
- revenue
- revenue growth
- contracts
- account growth
- cost savings
- time savings
- productivity
- processing time
- error reduction
- forecast accuracy
- model performance
- project duration
- data volume
- number of partnerships
- workforce size
- customer satisfaction
- operational capacity
- adoption
- turnaround time

Only ask metrics relevant to the actual statement.

Do not ask for revenue metrics for academic research
unless the context supports such a question.

==================================================
JOB RELEVANCE
==================================================

Prioritize weak statements that relate to important target
job requirements.

For each opportunity identify relevant:

- job requirements
- ATS terminology

Do not invent candidate evidence merely because a keyword
appears in the job posting.

==================================================
PRIORITY
==================================================

Use:

HIGH
MEDIUM
LOW

HIGH:
Improving the statement could materially strengthen fit
for an important job requirement.

MEDIUM:
Useful improvement but not central.

LOW:
Minor resume-quality improvement.

Return at most 10 opportunities.

Prefer quality over quantity.

==================================================
FACTUAL INTEGRITY
==================================================

Do not propose a metric as if it already exists.

Do not infer outcomes.

Do not infer team size.

Do not infer revenue.

Do not infer improvements.

The purpose is to ASK the candidate, not answer for them.
"""


ACHIEVEMENT_VERIFICATION_PROMPT = """
You are an evidence-controlled resume achievement writer.

You receive:

1. The candidate's original resume statement
2. Candidate-supplied additional accomplishment details
3. The target job requirements

Your objective is to convert legitimate evidence into a
strong accomplishment statement.

==================================================
RULES
==================================================

Never invent:

- numbers
- percentages
- revenue
- savings
- team sizes
- clients
- users
- technologies
- employers
- responsibilities
- outcomes

Use only information explicitly present in:

1. original source statement, OR
2. candidate-supplied achievement answer.

==================================================
OUTPUT STATUS
==================================================

verification_status must be exactly one of:

VERIFIED

Candidate provided sufficient factual detail to create
a stronger accomplishment statement.

PARTIAL

Some useful new detail exists, but the statement should
remain conservative.

SKIPPED

Candidate did not provide meaningful additional
information.

==================================================
OPTIMIZED STATEMENT
==================================================

When evidence supports it, use:

STRONG ACTION VERB
+
CONTEXT OR SCOPE
+
RESULT / BUSINESS RELEVANCE

Example:

SOURCE:
"Led business development."

CANDIDATE:
"Developed partnerships with solar contractors in
Massachusetts, Texas and Florida."

GOOD:
"Developed commercial partnerships with solar contractors
across Massachusetts, Texas, and Florida to expand the
company's multi-state delivery network."

Do NOT invent revenue or growth percentages.

==================================================
METRICS
==================================================

Use numbers only when the candidate explicitly supplies
them or they already exist in the original resume.

Preserve approximate language when supplied.

Example:

Candidate says:
"about 40 employees"

Do not rewrite as:
"43 employees"

Use:
"approximately 40 employees"

==================================================
ATS TERMINOLOGY
==================================================

Relevant job terminology can be incorporated only when the
candidate's evidence actually supports it.

Do not convert a general accomplishment into specialized
experience merely to obtain a keyword.
"""


def analyze_achievements(
    job_post: str,
    resume: str,
    analysis: ResumeAnalysis,
) -> AchievementAnalysis:

    prompt = f"""
{ACHIEVEMENT_ANALYSIS_PROMPT}


TARGET JOB
==========

{job_post}


ORIGINAL RESUME
===============

{resume}


JOB ANALYSIS
============

{analysis.model_dump_json(indent=2)}


Identify the highest-value achievement opportunities.

Focus particularly on statements that are relevant to
the target role but currently describe responsibility
rather than impact.
"""


    # Selected resources:
    # primary: Gemini 3.1 Flash Lite
    # backup: OpenRouter/Stealth Union Alpha
    try:
        if not client:
            raise RuntimeError(
                "Gemini is not configured."
            )

        response = client.models.generate_content(
            model=DISCOVERY_MODEL,

            contents=prompt,

            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=AchievementAnalysis,
            )
        )

        if not response.text:

            raise RuntimeError(
                "Achievement analysis returned "
                "an empty response."
            )

        return AchievementAnalysis.model_validate_json(
            response.text
        )

    except Exception:
        return openrouter_structured(
            prompt,
            AchievementAnalysis,
            UNION_MODEL,
            temperature=0.1,
        )


def verify_achievements(
    job_post: str,
    answers: list,
) -> AchievementVerificationResult:

    answer_json = json.dumps(
        answers,
        indent=2,
        ensure_ascii=False
    )


    prompt = f"""
{ACHIEVEMENT_VERIFICATION_PROMPT}


TARGET JOB
==========

{job_post}


CANDIDATE ACHIEVEMENT ANSWERS
=============================

{answer_json}


Create a verified optimized statement for each candidate
answer containing meaningful additional information.

Never invent missing metrics or results.
"""


    # Selected $0 resources:
    # primary: Groq GPT-OSS 120B
    # backup: OpenRouter/Novita Ling
    try:
        return groq_structured(
            prompt,
            AchievementVerificationResult,
            temperature=0.1,
        )

    except Exception:
        return openrouter_structured(
            prompt,
            AchievementVerificationResult,
            LING_MODEL,
            temperature=0.1,
        )
