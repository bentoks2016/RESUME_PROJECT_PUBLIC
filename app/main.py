import json
import re

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from fastapi.responses import (
    HTMLResponse,
    StreamingResponse,
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.achievements import (
    analyze_achievements,
    verify_achievements,
)

from app.ai import (
    analyze_resume,
    generate_application,
    verify_gap_answers,
)

from app.integrity import (
    check_factual_integrity,
)

from app.recruiter import (
    review_application_as_recruiter,
)

from app.interview import (
    generate_interview_preparation,
)

from app.opportunity_mapping import (
    build_job_posting_gap_questions,
    build_role_opportunity_mapping,
)

from app.provider_errors import (
    raise_ai_service_http_error,
)

from app.document import (
    cover_letter_to_docx,
    resume_to_docx,
)

from app.models import (
    CoverLetterDocument,
    FactualIntegrityResult,
    GeneratedApplication,
    GapVerificationResult,
    RecruiterReviewResult,
    ResumeAnalysis,
    ResumeDocument,
)

from app.parser import extract_text


app = FastAPI(
    title="Resume Project",
    version="2.0.0"
)


app.mount(
    "/static",
    StaticFiles(
        directory="app/static"
    ),
    name="static"
)


templates = Jinja2Templates(
    directory="app/templates"
)


@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "application": "RESUME_PROJECT",
        "version": "2.0.0"
    }


async def get_input_text(
    pasted_text: str,
    uploaded_file: UploadFile | None,
    label: str
) -> str:

    if pasted_text and pasted_text.strip():

        return pasted_text.strip()

    if (
        uploaded_file
        and uploaded_file.filename
    ):

        content = await uploaded_file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail=f"{label}: uploaded file is empty."
            )

        if len(content) > 10 * 1024 * 1024:

            raise HTTPException(
                status_code=400,
                detail=f"{label}: file exceeds 10 MB."
            )

        try:

            text = extract_text(
                uploaded_file.filename,
                content
            )

        except Exception as error:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{label}: could not read file. "
                    f"{error}"
                )
            )

        if not text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    f"{label}: no readable text "
                    "was found."
                )
            )

        return text.strip()

    raise HTTPException(
        status_code=400,
        detail=(
            f"{label}: paste text or upload "
            "PDF, DOCX, or TXT."
        )
    )


@app.post("/api/analyze")
async def analyze(
    job_text: str = Form(""),
    resume_text: str = Form(""),

    job_file: UploadFile | None = File(None),
    resume_file: UploadFile | None = File(None),
):

    try:

        job = await get_input_text(
            job_text,
            job_file,
            "Job posting"
        )

        resume = await get_input_text(
            resume_text,
            resume_file,
            "Resume"
        )

        if len(job) < 100:

            raise HTTPException(
                status_code=400,
                detail="Job posting appears too short."
            )

        if len(resume) < 100:

            raise HTTPException(
                status_code=400,
                detail="Resume appears too short."
            )

        analysis = analyze_resume(
            job,
            resume
        )

        analysis.gap_questions = (
            build_job_posting_gap_questions(
                analysis
            )
        )

        role_opportunity_mapping = (
            build_role_opportunity_mapping(
                analysis
            )
        )

        return {
            "job_text": job,
            "resume_text": resume,
            "analysis": analysis.model_dump(),
            "role_opportunity_mapping": (
                role_opportunity_mapping.model_dump()
            ),
        }

    except HTTPException:
        raise

    except Exception as error:

        print(
            "ANALYSIS ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Analysis failed. Check the "
                "server terminal for details."
            )
        )


@app.post("/api/verify-gaps")
async def verify_gaps(
    job_text: str = Form(...),
    resume_text: str = Form(...),
    analysis_json: str = Form(...),
    gap_answers_json: str = Form(...),
):

    try:

        analysis = ResumeAnalysis.model_validate_json(
            analysis_json
        )

        gap_answers = json.loads(
            gap_answers_json
        )

        verification = verify_gap_answers(
            job_text,
            resume_text,
            analysis,
            gap_answers
        )

        return verification.model_dump()

    except Exception as error:

        print(
            "GAP VERIFICATION ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Gap verification failed. "
                "Check the server terminal."
            )
        )


@app.post("/api/analyze-achievements")
async def analyze_achievement_opportunities(
    job_text: str = Form(...),
    resume_text: str = Form(...),
    analysis_json: str = Form(...),
):

    try:

        analysis = ResumeAnalysis.model_validate_json(
            analysis_json
        )

        result = analyze_achievements(
            job_text,
            resume_text,
            analysis
        )

        return result.model_dump()

    except Exception as error:

        print(
            "ACHIEVEMENT ANALYSIS ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Achievement analysis failed. "
                "Check the server terminal."
            )
        )


@app.post("/api/verify-achievements")
async def verify_achievement_answers(
    job_text: str = Form(...),
    achievement_answers_json: str = Form(...),
):

    try:

        answers = json.loads(
            achievement_answers_json
        )

        result = verify_achievements(
            job_text,
            answers
        )

        return result.model_dump()

    except Exception as error:

        print(
            "ACHIEVEMENT VERIFICATION ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Achievement verification failed. "
                "Check the server terminal."
            )
        )


@app.post("/api/generate")
async def generate(
    job_text: str = Form(...),
    resume_text: str = Form(...),
    analysis_json: str = Form(...),
    gap_answers_json: str = Form("[]"),
    verification_json: str = Form(...),
    achievement_verification_json: str = Form("{}"),
):

    try:

        analysis = ResumeAnalysis.model_validate_json(
            analysis_json
        )

        gap_answers = json.loads(
            gap_answers_json
        )

        verification = (
            GapVerificationResult.model_validate_json(
                verification_json
            )
        )

        achievement_verification = json.loads(
            achievement_verification_json
        )

        application = generate_application(
            job_text,
            resume_text,
            analysis,
            gap_answers,
            verification,
            achievement_verification
        )

        return application.model_dump()

    except Exception as error:

        print(
            "GENERATION ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Resume generation failed. Check "
                "the server terminal for details."
            )
        )


def safe_filename(
    value: str
) -> str:

    cleaned = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        value.strip()
    )

    return (
        cleaned.strip("_")
        or "Document"
    )


@app.post("/api/check-integrity")
async def check_integrity(
    job_text: str = Form(...),
    resume_text: str = Form(...),
    gap_answers_json: str = Form(...),
    verification_json: str = Form(...),
    application_json: str = Form(...),
    achievement_verification_json: str = Form("{}"),
):

    try:

        gap_answers = json.loads(
            gap_answers_json
        )

        verification = (
            GapVerificationResult.model_validate_json(
                verification_json
            )
        )

        application = (
            GeneratedApplication.model_validate_json(
                application_json
            )
        )

        achievement_verification = json.loads(
            achievement_verification_json
        )

        result = check_factual_integrity(
            job_text,
            resume_text,
            gap_answers,
            verification,
            application,
            achievement_verification
        )

        return result.model_dump()

    except Exception as error:

        print(
            "INTEGRITY CHECK ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Factual-integrity check failed. "
                "Check the server terminal."
            )
        )


@app.post("/api/download/resume")
async def download_resume(
    resume_json: str = Form(...),
    filename: str = Form("Tailored_Resume")
):

    resume = ResumeDocument.model_validate_json(
        resume_json
    )

    document = resume_to_docx(
        resume
    )

    name = safe_filename(
        filename
    )

    return StreamingResponse(
        document,

        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),

        headers={
            "Content-Disposition":
                f'attachment; filename="{name}.docx"'
        }
    )


@app.post("/api/download/cover-letter")
async def download_cover_letter(
    cover_letter_json: str = Form(...),
    filename: str = Form("Cover_Letter")
):

    cover_letter = (
        CoverLetterDocument.model_validate_json(
            cover_letter_json
        )
    )

    document = cover_letter_to_docx(
        cover_letter
    )

    name = safe_filename(
        filename
    )

    return StreamingResponse(
        document,

        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),

        headers={
            "Content-Disposition":
                f'attachment; filename="{name}.docx"'
        }
    )


@app.post("/api/recruiter-review")
async def recruiter_review(
    job_text: str = Form(...),
    application_json: str = Form(...),
):

    try:

        application = (
            GeneratedApplication.model_validate_json(
                application_json
            )
        )

        result = review_application_as_recruiter(
            job_text,
            application,
        )

        return result.model_dump()

    except Exception as error:

        print(
            "RECRUITER REVIEW ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Recruiter review failed. "
                "Please try again."
            )
        )


@app.post("/api/interview-preparation")
async def interview_preparation(
    job_text: str = Form(...),
    resume_text: str = Form(...),
    application_json: str = Form(...),
    verification_json: str = Form(...),
    achievement_verification_json: str = Form("{}"),
    recruiter_review_json: str = Form(""),
):

    try:

        application = (
            GeneratedApplication.model_validate_json(
                application_json
            )
        )

        verification = (
            GapVerificationResult.model_validate_json(
                verification_json
            )
        )

        achievement_verification = json.loads(
            achievement_verification_json
        )

        recruiter_review = None

        if recruiter_review_json.strip():

            recruiter_review = (
                RecruiterReviewResult.model_validate_json(
                    recruiter_review_json
                )
            )

        result = generate_interview_preparation(
            job_text,
            resume_text,
            application,
            verification,
            achievement_verification,
            recruiter_review,
        )

        return result.model_dump()

    except Exception as error:

        print(
            "INTERVIEW PREPARATION ERROR:",
            repr(error)
        )

        raise_ai_service_http_error(
            error,
            (
                "Interview preparation failed. "
                "Please try again."
            )
        )


@app.get("/api/scoring-methodology")
async def scoring_methodology():

    qualification_weights = {
        "required_skills": 37.5,
        "experience_alignment": 31.25,
        "leadership_seniority": 12.5,
        "education": 6.25,
        "preferred_qualifications": 6.25,
        "industry_alignment": 6.25,
    }

    return {
        "qualification_match_weights": (
            qualification_weights
        ),

        # Compatibility alias. ATS coverage is deliberately
        # absent because it is not part of Qualification Match.
        "match_weights": qualification_weights,

        "ats_coverage": {
            "independent_from_qualification_match": True,
            "basis": (
                "Authorized job terminology represented "
                "in the resume."
            ),
        },

        "keyword_importance": {
            "critical": 4,
            "required": 3,
            "high": 3,
            "preferred": 2,
            "medium": 2,
            "low": 1,
        },

        "keyword_status": {
            "supported": 100,
            "transferable": 70,
            "missing": 0,
        },

        "calculated_by": "Python",

        "description": (
            "Qualification Match measures candidate evidence "
            "alignment with the role. ATS Coverage independently "
            "measures authorized job terminology represented in "
            "the resume. Tailoring alone cannot increase "
            "Qualification Match."
        )
    }
