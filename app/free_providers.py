"""
Minimal helpers for the selected free inference resources.

This module contains transport/structured-response mechanics
only. Task selection remains in the existing domain modules.
"""

import json
import os
from typing import TypeVar

import httpx
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel


load_dotenv(".env")


T = TypeVar(
    "T",
    bound=BaseModel,
)


GPT_OSS_MODEL = "openai/gpt-oss-120b"
LING_MODEL = "inclusionai/ling-3.0-flash-vl:free"
UNION_MODEL = "stealth/union-alpha"

OPENROUTER_ENDPOINT = (
    "https://openrouter.ai/api/v1/chat/completions"
)


def _strict_schema(value):
    if isinstance(value, dict):
        result = {
            key: _strict_schema(item)
            for key, item in value.items()
        }

        if result.get("type") == "object":
            result["additionalProperties"] = False

            properties = result.get(
                "properties",
                {},
            )

            if properties:
                result["required"] = list(
                    properties.keys()
                )

        return result

    if isinstance(value, list):
        return [
            _strict_schema(item)
            for item in value
        ]

    return value


def groq_structured(
    prompt: str,
    response_model: type[T],
    *,
    temperature: float = 0.0,
) -> T:
    """
    Call the selected Groq GPT-OSS resource using native
    strict JSON Schema and validate the returned object.
    """
    key = os.getenv(
        "GROQ_API_KEY"
    )

    if not key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    client = Groq(
        api_key=key,
    )

    response = client.chat.completions.create(
        model=GPT_OSS_MODEL,
        temperature=temperature,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": (
                    response_model.__name__.lower()
                ),
                "strict": True,
                "schema": _strict_schema(
                    response_model.model_json_schema()
                ),
            },
        },
        messages=[
            {
                "role": "system",
                "content": (
                    "Return only valid JSON matching the "
                    "requested contract. Never invent "
                    "candidate evidence."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    content = (
        response.choices[0]
        .message.content
    )

    if not content:
        raise RuntimeError(
            "Groq returned an empty response."
        )

    return response_model.model_validate_json(
        content
    )


def _require_union_zero_cost() -> None:
    """
    Refuse Union Alpha before inference unless OpenRouter's
    current model metadata explicitly reports zero prompt
    and completion prices.
    """
    response = httpx.get(
        "https://openrouter.ai/api/v1/models",
        timeout=30.0,
    )

    response.raise_for_status()

    models = response.json().get(
        "data",
        [],
    )

    matches = [
        item
        for item in models
        if item.get("id") == UNION_MODEL
    ]

    if len(matches) != 1:
        raise RuntimeError(
            "Union Alpha zero-cost status could not "
            "be verified before inference."
        )

    pricing = matches[0].get(
        "pricing",
        {},
    )

    if (
        pricing.get("prompt") not in {
            "0",
            0,
            0.0,
        }
        or pricing.get("completion") not in {
            "0",
            0,
            0.0,
        }
    ):
        raise RuntimeError(
            "Union Alpha is not currently confirmed "
            "as zero-cost. Inference refused."
        )


def openrouter_structured(
    prompt: str,
    response_model: type[T],
    model: str,
    *,
    temperature: float = 0.0,
) -> T:
    """
    Call one explicitly selected OpenRouter $0 resource.

    The Pydantic schema is supplied in the prompt because
    the selected routes proved reliable with prompt-schema
    output during qualification.
    """
    if model not in {
        LING_MODEL,
        UNION_MODEL,
    }:
        raise RuntimeError(
            "OpenRouter model is not an approved "
            "free resource."
        )

    key = os.getenv(
        "OPENROUTER_API_KEY"
    )

    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    if model == UNION_MODEL:
        _require_union_zero_cost()

    schema_json = json.dumps(
        _strict_schema(
            response_model.model_json_schema()
        ),
        indent=2,
        ensure_ascii=False,
    )

    structured_prompt = f"""
{prompt}

REQUIRED JSON CONTRACT
======================

{schema_json}

Return exactly one raw JSON object matching this contract.
Do not use Markdown.
Do not use code fences.
Do not rename fields.
Do not omit required fields.
Return JSON only.
"""

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Follow the supplied evidence boundaries. "
                    "Return exactly one raw JSON object "
                    "matching the requested contract."
                ),
            },
            {
                "role": "user",
                "content": structured_prompt,
            },
        ],
    }

    with httpx.Client(
        timeout=300.0,
    ) as client:
        response = client.post(
            OPENROUTER_ENDPOINT,
            headers={
                "Authorization": (
                    f"Bearer {key}"
                ),
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if response.status_code != 200:
        raise RuntimeError(
            "OpenRouter request failed with HTTP "
            f"{response.status_code}."
        )

    data = response.json()

    choices = data.get(
        "choices",
        [],
    )

    if not choices:
        raise RuntimeError(
            "OpenRouter returned no choices."
        )

    usage = data.get(
        "usage",
        {},
    )

    cost = usage.get(
        "cost"
    )

    if cost not in (
        0,
        0.0,
    ):
        raise RuntimeError(
            "OpenRouter request was not explicitly "
            f"zero-cost: {cost!r}."
        )

    content = (
        choices[0]
        .get("message", {})
        .get("content")
    )

    if not content:
        raise RuntimeError(
            "OpenRouter returned an empty response."
        )

    return response_model.model_validate_json(
        content
    )
