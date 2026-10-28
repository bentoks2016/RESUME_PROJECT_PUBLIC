import os

from dotenv import load_dotenv
from google import genai


load_dotenv(
    dotenv_path=".env"
)


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

# GEMINI_MODEL is retained as the legacy/default model setting.
# Application AI operations use the role-specific models below.
DEFAULT_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash",
)

DISCOVERY_MODEL = os.getenv(
    "GEMINI_DISCOVERY_MODEL",
    "gemini-3.1-flash-lite",
)

ADVISORY_MODEL = os.getenv(
    "GEMINI_ADVISORY_MODEL",
    "gemini-3.5-flash-lite",
)

CRITICAL_MODEL = os.getenv(
    "GEMINI_CRITICAL_MODEL",
    "gemini-3.6-flash",
)

# Research is configured independently because grounded
# search quota/model compatibility can differ from normal
# text generation.
RESEARCH_MODEL = os.getenv(
    "GEMINI_RESEARCH_MODEL",
    "",
)


client = None

if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY
    )


def check_ai_configuration():
    if not GEMINI_API_KEY or client is None:
        raise RuntimeError(
            "Gemini is not configured. "
            "Add GEMINI_API_KEY to .env."
        )
