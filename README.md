
# RESUME_PROJECT

### Evidence-Controlled AI Career Application Platform

RESUME_PROJECT is a Python/FastAPI application that helps candidates develop targeted, evidence-based job applications. It analyzes résumés against job requirements, identifies qualification gaps, discovers measurable achievements, generates tailored application documents, checks factual integrity, and supports recruiter evaluation and interview preparation.

Unlike a conventional AI résumé generator, RESUME_PROJECT combines specialized AI models with deterministic validation to reduce unsupported claims and preserve the distinction between verified experience, transferable skills, and missing qualifications.

## Key Features

- **Résumé Analysis:** Extracts candidate information from PDF and DOCX documents and evaluates it against job requirements.
- **Qualification Matching:** Identifies supported qualifications, transferable experience, and genuine evidence gaps.
- **Achievement Discovery:** Helps candidates uncover measurable accomplishments through targeted questions.
- **Evidence Verification:** Evaluates candidate responses before incorporating new claims into application materials.
- **Application Generation:** Produces tailored résumés and cover letters.
- **Factual Integrity Auditing:** Flags unsupported claims, contradictions, and potentially misleading wording.
- **ATS Optimization:** Evaluates authorized keywords and application composition.
- **Recruiter Review:** Simulates recruiter-style evaluation of application strengths and weaknesses.
- **Interview Preparation:** Generates interview questions, STAR preparation guidance, and strategies for discussing qualification gaps.
- **Document Generation:** Produces downloadable Word documents.

## AI Architecture

The application coordinates multiple AI models across eight specialized functions.

| Function | Primary AI Resource | Backup |
|---|---|---|
| Résumé and Job Analysis | Gemini Flash Lite | Ling |
| Achievement Discovery | Gemini Flash Lite | Union Alpha |
| Gap Verification | Groq GPT-OSS 120B | Union Alpha |
| Achievement Verification | Groq GPT-OSS 120B | Ling |
| Application Generation | Union Alpha | Ling |
| Factual Integrity | Groq GPT-OSS 120B | Ling |
| Recruiter Review | Gemini Flash Lite | Ling |
| Interview Preparation | Gemini Flash Lite | Ling |

A reserve Gemini generation route is also configured.

The resource allocation was selected through task-specific testing rather than assigning every task to a single model.

The project is designed around zero-priced inference routes. Actual provider availability, quotas, pricing, and data-handling terms must be verified before use.

## Automated Workflow

1. Upload a résumé and provide a target job description.
2. Parse candidate experience and job requirements.
3. Analyze qualification alignment and identify evidence gaps.
4. Ask targeted questions to clarify missing information.
5. Discover and verify additional achievements.
6. Generate tailored résumé and cover-letter content.
7. Audit generated claims for factual integrity.
8. Evaluate ATS alignment and recruiter readiness.
9. Prepare interview guidance.
10. Download application documents for review.

## Engineering and Reliability

RESUME_PROJECT combines generative AI with deterministic Python safeguards.

These include:

- Pydantic structured-output validation.
- Evidence-based qualification matching.
- Separation of direct experience, transferable experience, and missing qualifications.
- Verification of candidate-supplied achievements.
- Factual-integrity checks for unsupported claims.
- ATS keyword authorization and auditing.
- Document composition validation.
- Task-specific AI fallback mechanisms.
- Automated regression testing.

AI-generated content is intended for human review before submission.

## Technology Stack

- **Backend:** Python, FastAPI
- **Frontend:** JavaScript, HTML, CSS
- **AI:** Google Gemini, Groq, OpenRouter
- **Validation:** Pydantic
- **Document Processing:** PDF/DOCX parsing and generation
- **Testing:** pytest
- **API Communication:** HTTP-based AI provider integrations

## Installation

Clone the repository:

    git clone https://github.com/bentoks2016/RESUME_PROJECT.git
    cd RESUME_PROJECT

Create and activate a Python virtual environment:

    python3 -m venv venv
    source venv/bin/activate

Install dependencies:

    python3 -m pip install -r requirements.txt

Create a local .env file containing:

    GEMINI_API_KEY=your_key_here
    GROQ_API_KEY=your_key_here
    OPENROUTER_API_KEY=your_key_here

Never commit API keys or .env files.

Start the application:

    python3 -m uvicorn app.main:app --reload

Open http://127.0.0.1:8000 in your browser.

## Testing

Install development dependencies:

    python3 -m pip install -r requirements-dev.txt

Run the automated regression suite:

    python3 -m pytest tests -q

Current status: 112 automated tests passing.

## Screenshots

Screenshots demonstrating the application interface and workflow
will be added using fictional candidate information.

## Development Status

RESUME_PROJECT is functional and undergoing final refinement.

Current priorities include improving qualification-match and ATS
scoring, refining application quality, and completing end-to-end testing.

## Privacy and Responsible AI

The application is designed to avoid inventing candidate experience,
qualifications, employers, certifications, or achievements.

AI-generated application materials require human review before submission.

Uploaded résumé content may be processed by external AI providers.
Users should review provider privacy policies and data-handling terms
before submitting personal information.

API credentials must remain private.

## Project Purpose

RESUME_PROJECT demonstrates practical engineering capabilities in
AI orchestration, workflow automation, API integration, structured
validation, document processing, evidence verification, cost
optimization, and automated software testing.

It serves as both a functional career application tool and a
technical engineering portfolio.
