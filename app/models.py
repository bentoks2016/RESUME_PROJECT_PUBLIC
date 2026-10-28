from typing import List

from pydantic import BaseModel, Field


# =========================================================
# ATS / JOB MATCH ANALYSIS
# =========================================================

class Requirement(BaseModel):
    requirement: str

    importance: str

    status: str

    evidence: str

    keywords: List[str] = []

    impact: str = ""

    recommendation: str = ""


class KeywordAnalysis(BaseModel):
    keyword: str
    importance: str
    status: str
    evidence: str = ""
    currently_in_resume: bool = False
    use_in_tailored_resume: bool = False


class GapQuestion(BaseModel):
    id: str
    requirement: str
    reason: str
    suggested_examples: List[str] = []


class ScoreBreakdown(BaseModel):

    required_skills: int = Field(
        ge=0,
        le=100
    )

    experience_alignment: int = Field(
        ge=0,
        le=100
    )

    ats_keyword_coverage: int = Field(
        ge=0,
        le=100
    )

    leadership_seniority: int = Field(
        ge=0,
        le=100
    )

    education: int = Field(
        ge=0,
        le=100
    )

    preferred_qualifications: int = Field(
        ge=0,
        le=100
    )

    industry_alignment: int = Field(
        ge=0,
        le=100
    )


class ResumeAnalysis(BaseModel):

    company: str
    job_title: str

    current_match_score: int = Field(
        ge=0,
        le=100
    )

    estimated_tailored_score: int = Field(
        ge=0,
        le=100
    )

    current_ats_score: int = Field(
        ge=0,
        le=100
    )

    estimated_tailored_ats_score: int = Field(
        ge=0,
        le=100
    )

    executive_summary: str

    requirements: List[Requirement]

    keyword_analysis: List[KeywordAnalysis]

    strengths: List[str]

    transferable_strengths: List[str]

    gaps: List[str]

    recommendations: List[str]

    gap_questions: List[GapQuestion]

    score_breakdown: ScoreBreakdown


class CandidateGapAnswer(BaseModel):
    gap_id: str

    requirement: str

    has_experience: bool

    description: str = ""

    context: str = ""

    results: str = ""

    technologies: str = ""


class GapVerificationItem(BaseModel):
    gap_id: str

    requirement: str

    original_status: str

    verified_status: str

    verification_result: str

    evidence_summary: str

    supported_keywords: List[str] = []

    caution: str = ""


class GapVerificationResult(BaseModel):
    items: List[GapVerificationItem]

    verified_experience_count: int = 0

    remaining_gap_count: int = 0

    summary: str = ""


# =========================================================
# SHARED CONTACT INFORMATION
# =========================================================

class ContactInformation(BaseModel):
    phone: str = ""
    email: str = ""
    linkedin: str = ""
    location: str = ""


# =========================================================
# COMBINATION RESUME
# =========================================================

class CareerPosition(BaseModel):
    job_title: str
    employer: str
    dates: str
    location: str = ""


class SkillGroup(BaseModel):
    name: str
    accomplishments: List[str]


class EducationItem(BaseModel):
    program_name: str
    school_name: str
    dates: str = ""
    location: str = ""


class TrainingItem(BaseModel):
    course_name: str
    provider: str
    date: str = ""
    location: str = ""


class ResumeDocument(BaseModel):

    name: str

    contact: ContactInformation

    profile: List[str]

    career_positions: List[CareerPosition]

    skill_groups: List[SkillGroup]

    education: List[EducationItem]

    additional_training: List[TrainingItem] = []


# =========================================================
# RESUME COMPOSITION AUDIT
# =========================================================

class ResumeCompositionAudit(BaseModel):

    passed: bool

    profile_first_bullet_present: bool = False

    profile_final_education_bullet_present: bool = False

    principal_skill_group_count: int = 0

    skill_group_accomplishment_counts: List[int] = []

    structure_issues: List[str] = []

    warnings: List[str] = []


# =========================================================
# COVER LETTER
# =========================================================

class RecipientInformation(BaseModel):
    name: str = ""
    position: str = ""
    employer: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""


class CoverLetterDocument(BaseModel):

    candidate_name: str

    candidate_contact: ContactInformation

    date_line: str = ""

    recipient: RecipientInformation

    subject_line: str

    salutation: str

    paragraph_1: str
    paragraph_2: str
    paragraph_3: str
    paragraph_4: str

    closing: str = "Sincerely"


# =========================================================
# COVER LETTER COMPOSITION AUDIT
# =========================================================

class CoverLetterCompositionAudit(BaseModel):

    passed: bool

    substantive_paragraph_count: int = 0

    # Current employer-side context comes from the job
    # posting. GROUNDED_COMPANY_RESEARCH can be added later.
    employer_context_sources: List[str] = []

    # EXPLICIT_CANDIDATE or INFERRED_FROM_EVIDENCE.
    motivation_basis: str = "INFERRED_FROM_EVIDENCE"

    structure_issues: List[str] = []

    warnings: List[str] = []


# =========================================================
# ATS OPTIMIZATION AUDIT
# =========================================================

class ATSKeywordPlacement(BaseModel):
    keyword: str
    importance: str
    evidence_status: str
    placement: List[str] = []
    included: bool = False
    rationale: str = ""


class ATSOptimizationAudit(BaseModel):
    headline_keywords: List[str] = []
    profile_keywords: List[str] = []
    skill_group_keywords: List[str] = []
    accomplishment_keywords: List[str] = []
    excluded_unsupported_keywords: List[str] = []
    keyword_placements: List[ATSKeywordPlacement] = []

    # Deterministic Python ATS audit
    authorized_keywords: List[str] = []
    keywords_found: List[str] = []
    keywords_missing: List[str] = []

    deterministic_ats_score: int = Field(
        default=0,
        ge=0,
        le=100
    )

    structure_passed: bool = True
    structure_issues: List[str] = []


# =========================================================
# FINAL GENERATED APPLICATION
# =========================================================

class FactualClaim(BaseModel):

    claim: str

    document: str

    category: str

    status: str

    source_evidence: str = ""

    # Provenance category for the claim's factual basis.
    # Current supported sources are candidate evidence and
    # the job posting. Grounded company research is reserved
    # for the deferred Company Intelligence path.
    evidence_source: str = "CANDIDATE_EVIDENCE"

    explanation: str = ""

    severity: str = "LOW"

    suggested_correction: str = ""


class FactualIntegrityResult(BaseModel):

    passed: bool

    integrity_score: int = Field(
        ge=0,
        le=100
    )

    total_claims_checked: int = 0

    supported_claims: int = 0

    reasonable_reframes: int = 0

    unsupported_claims: int = 0

    contradictions: int = 0

    critical_issues: int = 0

    claims: List[FactualClaim]

    summary: str


class AchievementOpportunity(BaseModel):

    id: str

    source_statement: str

    source_role: str = ""

    weakness: str

    opportunity_type: str

    suggested_questions: List[str]

    relevant_job_requirements: List[str] = []

    relevant_keywords: List[str] = []

    priority: str = "MEDIUM"


class AchievementAnalysis(BaseModel):

    opportunities: List[AchievementOpportunity]

    total_opportunities: int = 0

    high_priority_count: int = 0

    summary: str = ""


class AchievementAnswer(BaseModel):

    opportunity_id: str

    source_statement: str

    has_more_detail: bool

    action: str = ""

    scope: str = ""

    result: str = ""

    metrics: str = ""

    context: str = ""


class VerifiedAchievement(BaseModel):

    opportunity_id: str

    source_statement: str

    verification_status: str

    optimized_statement: str

    evidence_used: str

    keywords_supported: List[str] = []

    caution: str = ""


class AchievementVerificationResult(BaseModel):

    achievements: List[VerifiedAchievement]

    accepted_count: int = 0

    skipped_count: int = 0

    summary: str = ""


class FinalScoreBreakdown(BaseModel):

    required_skills: int = Field(
        ge=0,
        le=100
    )

    experience_alignment: int = Field(
        ge=0,
        le=100
    )

    leadership_seniority: int = Field(
        ge=0,
        le=100
    )

    education: int = Field(
        ge=0,
        le=100
    )

    preferred_qualifications: int = Field(
        ge=0,
        le=100
    )

    industry_alignment: int = Field(
        ge=0,
        le=100
    )


class GeneratedApplication(BaseModel):

    resume: ResumeDocument

    cover_letter: CoverLetterDocument

    final_score_breakdown: FinalScoreBreakdown

    final_match_score: int = Field(
        ge=0,
        le=100
    )

    final_ats_score: int = Field(
        ge=0,
        le=100
    )

    keywords_added: List[str]

    remaining_gaps: List[str]

    ats_optimization: ATSOptimizationAudit

    # Deterministic structural audit applied after generation.
    resume_composition: ResumeCompositionAudit = Field(
        default_factory=lambda: ResumeCompositionAudit(
            passed=True
        )
    )


    # Deterministic Phase 11 cover-letter audit.
    cover_letter_composition: CoverLetterCompositionAudit = Field(
        default_factory=lambda: CoverLetterCompositionAudit(
            passed=True
        )
    )


# =========================================================
# RECRUITER / HIRING-MANAGER SIMULATION
# =========================================================

class RecruiterConcern(BaseModel):

    severity: str

    category: str

    observation: str

    why_it_matters: str

    evidence: str = ""

    suggested_fix: str = ""


class RecruiterInterviewQuestion(BaseModel):

    question: str

    why_asked: str

    evidence_to_prepare: str = ""


class RecruiterReviewResult(BaseModel):

    interview_recommendation: str

    first_impression: str

    strongest_signals: List[str] = []

    concerns: List[RecruiterConcern] = []

    unclear_points: List[str] = []

    missing_signals: List[str] = []

    buzzword_risks: List[str] = []

    likely_interview_questions: List[
        RecruiterInterviewQuestion
    ] = []

    bottom_line: str


# =========================================================
# INTERVIEW PREPARATION
# =========================================================

class LikelyInterviewQuestion(BaseModel):

    question: str

    category: str

    likelihood: str

    why_likely: str

    interviewer_is_testing: str


class STARStory(BaseModel):

    title: str

    evidence_strength: str

    situation: str

    task: str

    action: str

    result: str

    source_evidence: str

    useful_for_questions: List[str] = []

    missing_details: List[str] = []


class GapInterviewPreparation(BaseModel):

    requirement: str

    likely_question: str

    gap_type: str

    truthful_answer_strategy: str

    transferable_evidence: List[str] = []

    bridge_to_strength: str

    do_not_claim: List[str] = []


class EmployerInterviewQuestion(BaseModel):

    question: str

    audience: str

    why_ask: str


class InterviewPreparationResult(BaseModel):

    preparation_summary: str

    likely_questions: List[
        LikelyInterviewQuestion
    ] = []

    star_stories: List[
        STARStory
    ] = []

    gap_preparation: List[
        GapInterviewPreparation
    ] = []

    questions_for_employer: List[
        EmployerInterviewQuestion
    ] = []

    final_advice: List[str] = []


# =========================================================
# COMPANY INTELLIGENCE
# =========================================================

class CompanyResearchSource(BaseModel):
    id: str
    title: str
    url: str
    domain: str = ""
    publication_date: str = ""


class GroundedResearchSegment(BaseModel):
    text: str
    source_ids: List[str]
    confidence_scores: List[float] = []


class CompanyResearchFinding(BaseModel):
    id: str
    category: str

    # A factual statement about the employer.
    finding: str

    # Interpretation is deliberately separate from fact.
    interpretation: str = ""

    relevance_to_role: str

    # References must resolve to grounded sources in
    # CompanyResearchResult.sources.
    source_ids: List[str] = []

    confidence: str = "MEDIUM"
    caveat: str = ""


class CompanyResearchResult(BaseModel):
    company: str
    job_title: str
    research_date: str

    strategic_priorities: List[
        CompanyResearchFinding
    ] = []

    recent_initiatives: List[
        CompanyResearchFinding
    ] = []

    relevant_investments: List[
        CompanyResearchFinding
    ] = []

    business_direction: List[
        CompanyResearchFinding
    ] = []

    role_relevant_developments: List[
        CompanyResearchFinding
    ] = []

    potential_future_capabilities: List[
        CompanyResearchFinding
    ] = []

    organizational_challenges: List[
        CompanyResearchFinding
    ] = []

    grounded_segments: List[
        GroundedResearchSegment
    ] = []

    sources: List[
        CompanyResearchSource
    ] = []

    summary: str = ""


# =========================================================
# ROLE OPPORTUNITY MAPPING
# =========================================================

class RoleOpportunityMapping(BaseModel):

    requirement: str

    importance: str

    # DIRECT / TRANSFERABLE / NONE
    connection: str

    # Where the employer-side requirement originated.
    # Phase 8A currently permits JOB_POSTING only.
    signal_source: str = "JOB_POSTING"

    # Employer/role evidence. This describes what the role
    # requires; it is never candidate evidence.
    role_evidence: str

    # Candidate evidence copied only from the established
    # ResumeAnalysis requirement classification.
    candidate_evidence: str = ""

    keywords: List[str] = []

    rationale: str = ""

    should_ask_gap_question: bool = False


class RoleOpportunityMappingResult(BaseModel):

    mappings: List[RoleOpportunityMapping]

    direct_count: int = 0
    transferable_count: int = 0
    none_count: int = 0

    source: str = "JOB_POSTING"

    summary: str = ""
