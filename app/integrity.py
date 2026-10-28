import json

from google.genai import types

from app.ai_config import (
    CRITICAL_MODEL,
    client,
)

from app.free_providers import (
    LING_MODEL,
    groq_structured,
    openrouter_structured,
)

from app.models import (
    FactualIntegrityResult,
    GeneratedApplication,
    GapVerificationResult,
)


INTEGRITY_PROMPT = """
You are a strict factual-integrity auditor for resumes
and cover letters.

Your purpose is NOT to improve the candidate's application.

Your purpose is to identify claims in generated application
documents that cannot be supported by the candidate's
source information.

You receive:

1. Original resume
2. Candidate-supplied gap answers
3. Independent verification of those gap answers
4. Generated resume
5. Generated cover letter

==================================================
EVIDENCE CATEGORIES
==================================================

You must keep candidate evidence and employer evidence
strictly separate.

CANDIDATE EVIDENCE
------------------

Candidate claims may be supported only by:

SOURCE A:
Original resume.

SOURCE B:
Candidate-provided gap information independently verified
as VERIFIED / SUPPORTED.

SOURCE C:
Verified achievement information.

PARTIAL or TRANSFERABLE evidence may support carefully
qualified transferable statements but must NOT be treated
as proof of direct experience.

NEEDS_DETAIL and NOT_VERIFIED information must not support
new candidate factual claims.

The job posting is NEVER evidence that the candidate has
a skill, qualification, accomplishment, technology, or
experience.

EMPLOYER / ROLE EVIDENCE
------------------------

The target JOB POSTING may support factual statements
about:

- the advertised role
- stated responsibilities
- required qualifications
- preferred qualifications
- objectives explicitly described in the posting
- employer facts explicitly stated in the posting

Reasonable role-level interpretation is permitted.

For example, if the posting repeatedly requires
multi-site delivery, stakeholder coordination, and
organizational change, it is reasonable to characterize
the role as requiring cross-functional transformation
leadership.

However, role-level inference must not be upgraded into
unsupported company fact.

Without grounded company research, do not treat claims
about the employer's broader:

- corporate strategy
- investments
- recent initiatives
- transformation programs
- financial position
- market direction
- future plans
- organizational challenges

as supported unless those facts are explicitly stated in
the job posting.

GROUNDED COMPANY RESEARCH
-------------------------

Grounded company research is a reserved evidence category
for the deferred Company Intelligence capability.

No grounded company research is supplied to this integrity
check at present.

Therefore do not classify a company claim as supported by
GROUNDED_COMPANY_RESEARCH.

REASONABLE INFERENCE
--------------------

Persuasive synthesis and reasonable interpretation are
allowed when their factual premises are supported.

A rhetorical inference does not become a fabrication
merely because the exact wording does not occur in a
source.

Examples:

Candidate evidence:
The candidate has led multi-site manufacturing
transformation.

Job posting:
The role leads transformation across multiple sites.

Generated:
"This opportunity is a natural next step in a career
focused on multi-site operational transformation."

This may be a REASONABLE_REFRAME because it synthesizes
supported facts without creating a new factual premise.

But:

"I have admired this company for years."

is UNSUPPORTED unless candidate evidence establishes that
personal history.

Likewise:

"The company is undertaking an enterprise-wide digital
transformation."

is UNSUPPORTED unless the job posting explicitly
establishes that fact or future grounded research supports
it.

CLAIM PROVENANCE
----------------

For every material claim, set evidence_source to exactly
one of:

CANDIDATE_EVIDENCE
JOB_POSTING
GROUNDED_COMPANY_RESEARCH
REASONABLE_INFERENCE
UNSUPPORTED

Use REASONABLE_INFERENCE only when the underlying factual
premises are themselves supported.

Use UNSUPPORTED when no permitted evidence establishes the
material factual premise.

==================================================
CLAIMS TO CHECK
==================================================

Audit material factual claims involving:

EMPLOYMENT

- employer names
- job titles
- employment dates
- locations

EDUCATION

- degrees
- institutions
- graduation dates
- certifications
- professional training

METRICS

- percentages
- dollar amounts
- revenue
- savings
- growth
- team sizes
- numbers of clients
- numbers of users
- geographic scope
- performance improvements

TECHNOLOGY

- programming languages
- AI systems
- platforms
- cloud technologies
- frameworks
- databases
- enterprise applications
- methodologies

RESPONSIBILITIES

- leadership scope
- strategic ownership
- implementation responsibility
- executive advisory responsibility
- budget ownership
- hiring responsibility
- client responsibility
- product ownership
- technical architecture responsibility

ACCOMPLISHMENTS

- projects
- implementations
- transformations
- launches
- improvements
- commercial outcomes
- research outcomes

==================================================
STATUS
==================================================

Every material claim must be classified as exactly one:

SUPPORTED

Directly supported by the original resume or verified
candidate information.

REASONABLE_REFRAME

The wording differs from the source, but remains a fair,
non-misleading characterization of supported experience.

UNSUPPORTED

The generated document asserts information that cannot be
substantiated by the permitted evidence.

CONTRADICTION

The generated claim conflicts with source information.

==================================================
SEVERITY
==================================================

Use exactly:

LOW

Minor wording concern with little risk of misleading.

MEDIUM

Meaningful overstatement that should be corrected.

HIGH

Material unsupported professional claim.

CRITICAL

Potentially serious fabrication involving matters such as:

- employer
- title
- degree
- certification
- employment date
- significant metric
- major technology experience
- major client relationship
- substantial responsibility

==================================================
IMPORTANT DISTINCTIONS
==================================================

Do not flag ordinary writing improvements simply because
they use different words.

For example:

SOURCE:
"Led strategic planning and market analysis."

GENERATED:
"Led strategic planning and competitive market analysis."

This can be a REASONABLE_REFRAME if the meaning remains
accurate.

But:

SOURCE:
"Conducted market analysis."

GENERATED:
"Advised Fortune 100 CEOs on enterprise transformation."

This is UNSUPPORTED unless separate verified evidence
supports it.

==================================================
METRICS
==================================================

Be especially strict with numbers.

Never infer a metric.

If the generated resume says:

"Increased productivity by 35%"

the exact or substantively equivalent result must exist in
the approved evidence.

Otherwise flag it.

==================================================
TECHNOLOGY
==================================================

Do not assume that related technologies are equivalent.

Examples:

Transformers does not automatically prove RAG.

Python does not automatically prove production ML
engineering.

REST APIs do not automatically prove AWS experience.

Cybersecurity does not automatically prove enterprise
model-risk governance.

==================================================
JOB-DESCRIPTION CONTAMINATION
==================================================

Watch carefully for job requirements that have been copied
into the candidate's resume without evidence.

If the job requires "SAP S/4HANA" but the candidate source
does not demonstrate it, any generated claim of SAP
S/4HANA experience must be flagged.

==================================================
COVER LETTER
==================================================

Apply the same factual standard to the cover letter.

Marketing language is acceptable only when it remains
consistent with candidate evidence.

Do not allow the cover letter to introduce unsupported
skills simply because they are required by the employer.

==================================================
EMPLOYER CLAIMS IN THE COVER LETTER
==================================================

Audit employer-side claims separately from candidate
claims.

A statement about what the advertised role requires may
use JOB_POSTING evidence.

A reasonable interpretation of several advertised
responsibilities may use REASONABLE_INFERENCE when it
introduces no unsupported factual premise.

Do not confuse:

"The role requires..."
with:
"The company is currently..."

The first may be established by the job posting.

The second is a company factual claim and requires either
explicit support in the posting or, in the future,
GROUNDED_COMPANY_RESEARCH.

Do not flag persuasive professional motivation merely
because it uses interpretive language such as:

- compelling opportunity
- particularly drawn to
- natural next step

provided the explanation is grounded in established
candidate evidence and advertised role characteristics.

Flag invented personal history or employer facts.

==================================================
SCORING
==================================================

Return an integrity_score from 0-100.

Use approximately:

100:
No material factual concerns.

95-99:
Only minor reasonable-reframe concerns.

85-94:
Some wording or evidence concerns requiring review.

70-84:
One or more meaningful unsupported claims.

Below 70:
Serious factual reliability problems.

Any CRITICAL contradiction or fabrication should cause:

passed = false

Any HIGH unsupported claim should normally cause:

passed = false

The goal is accuracy, not generosity.

==================================================
CORRECTIONS
==================================================

For every unsupported or contradictory claim, provide a
suggested_correction.

The correction must either:

1. return to supported source wording,
2. qualify the claim appropriately, or
3. recommend removing it.

Never solve an unsupported claim by inventing different
information.
"""


def check_factual_integrity(
    job_post: str,
    original_resume: str,
    gap_answers: list,
    verification: GapVerificationResult,
    application: GeneratedApplication,
    achievement_verification: dict | None = None,
) -> FactualIntegrityResult:

    source_json = json.dumps(
        gap_answers,
        indent=2,
        ensure_ascii=False
    )


    generated_json = (
        application.model_dump_json(
            indent=2
        )
    )


    prompt = f"""
{INTEGRITY_PROMPT}


TARGET JOB POSTING
==================

{job_post}


ORIGINAL RESUME
===============

{original_resume}


CANDIDATE GAP ANSWERS
=====================

{source_json}


GAP VERIFICATION
================

{verification.model_dump_json(indent=2)}


VERIFIED ACHIEVEMENT INFORMATION
================================

{json.dumps(
    achievement_verification or {},
    indent=2,
    ensure_ascii=False
)}


GENERATED APPLICATION
=====================

{generated_json}


Audit the generated resume and cover letter against
the permitted candidate evidence.

Check all material factual claims.

Be particularly strict about:

- metrics
- technologies
- employment
- credentials
- upgraded responsibilities
- job-description terminology appearing without evidence
"""

    # Selected $0 resources:
    # primary: Groq GPT-OSS 120B
    # backup: OpenRouter/Novita Ling
    try:
        return groq_structured(
            prompt,
            FactualIntegrityResult,
            temperature=0.0,
        )

    except Exception:
        return openrouter_structured(
            prompt,
            FactualIntegrityResult,
            LING_MODEL,
            temperature=0.0,
        )
