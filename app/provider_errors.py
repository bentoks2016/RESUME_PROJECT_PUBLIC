from fastapi import HTTPException
from google.genai import errors


def raise_ai_service_http_error(
    error: Exception,
    fallback: str,
) -> None:
    """
    Translate known Gemini service failures into useful
    HTTP responses without exposing provider internals.
    """
    if isinstance(error, errors.APIError):

        if error.code == 429:
            raise HTTPException(
                status_code=429,
                detail=(
                    "AI request quota or rate limit has "
                    "been reached. Your application has "
                    "been preserved. Please retry when "
                    "quota is available."
                )
            ) from error

        if error.code == 503:
            raise HTTPException(
                status_code=503,
                detail=(
                    "The AI service is temporarily busy. "
                    "Your application has been preserved. "
                    "Please retry shortly."
                )
            ) from error

    raise HTTPException(
        status_code=500,
        detail=fallback
    ) from error
