from datetime import date
from typing import Iterable

from app.ai_config import (
    RESEARCH_MODEL,
    client,
)
from app.models import (
    CompanyResearchFinding,
    CompanyResearchResult,
    CompanyResearchSource,
    GroundedResearchSegment,
)


FINDING_FIELDS = (
    "strategic_priorities",
    "recent_initiatives",
    "relevant_investments",
    "business_direction",
    "role_relevant_developments",
    "potential_future_capabilities",
    "organizational_challenges",
)


def check_research_configuration() -> None:
    if client is None:
        raise RuntimeError(
            "Gemini is not configured. "
            "Add GEMINI_API_KEY to .env."
        )

    if not RESEARCH_MODEL:
        raise RuntimeError(
            "Company research model is not configured. "
            "Set GEMINI_RESEARCH_MODEL."
        )


def extract_grounded_sources(
    response,
) -> list[CompanyResearchSource]:
    """
    Extract web sources only from Gemini grounding metadata.

    URLs supplied merely in generated prose are never
    accepted here as provenance.
    """
    sources = []
    seen_urls = set()

    candidates = getattr(
        response,
        "candidates",
        None,
    ) or []

    for candidate in candidates:
        metadata = getattr(
            candidate,
            "grounding_metadata",
            None,
        )

        if metadata is None:
            continue

        chunks = getattr(
            metadata,
            "grounding_chunks",
            None,
        ) or []

        for chunk in chunks:
            web = getattr(
                chunk,
                "web",
                None,
            )

            if web is None:
                continue

            url = (
                getattr(web, "uri", None)
                or ""
            ).strip()

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)

            sources.append(
                CompanyResearchSource(
                    id=f"source-{len(sources) + 1}",
                    title=(
                        getattr(web, "title", None)
                        or ""
                    ).strip(),
                    url=url,
                    domain=(
                        getattr(web, "domain", None)
                        or ""
                    ).strip(),
                    publication_date="",
                )
            )

    return sources


def extract_grounded_segments(
    response,
    sources: list[CompanyResearchSource],
) -> list[GroundedResearchSegment]:
    """
    Extract provider-supported response segments and map
    grounding chunk indices to the source registry.

    Source IDs are assigned in the same unique-URL order
    used by extract_grounded_sources().
    """
    segments = []

    candidates = getattr(
        response,
        "candidates",
        None,
    ) or []

    for candidate in candidates:
        metadata = getattr(
            candidate,
            "grounding_metadata",
            None,
        )

        if metadata is None:
            continue

        chunks = getattr(
            metadata,
            "grounding_chunks",
            None,
        ) or []

        # Build chunk-index -> source-ID mapping using URLs.
        url_to_source_id = {
            source.url: source.id
            for source in sources
        }

        chunk_source_ids = {}

        for index, chunk in enumerate(chunks):
            web = getattr(
                chunk,
                "web",
                None,
            )

            if web is None:
                continue

            url = (
                getattr(web, "uri", None)
                or ""
            ).strip()

            source_id = url_to_source_id.get(
                url
            )

            if source_id:
                chunk_source_ids[index] = source_id

        supports = getattr(
            metadata,
            "grounding_supports",
            None,
        ) or []

        for support in supports:
            segment = getattr(
                support,
                "segment",
                None,
            )

            text = (
                getattr(segment, "text", None)
                or ""
            ).strip()

            if not text:
                continue

            indices = getattr(
                support,
                "grounding_chunk_indices",
                None,
            ) or []

            source_ids = []

            for index in indices:
                source_id = chunk_source_ids.get(
                    index
                )

                if (
                    source_id
                    and source_id not in source_ids
                ):
                    source_ids.append(source_id)

            if not source_ids:
                continue

            segments.append(
                GroundedResearchSegment(
                    text=text,
                    source_ids=source_ids,
                    confidence_scores=list(
                        getattr(
                            support,
                            "confidence_scores",
                            None,
                        )
                        or []
                    ),
                )
            )

    return segments


def validate_finding_sources(
    findings: Iterable[CompanyResearchFinding],
    sources: list[CompanyResearchSource],
) -> None:
    """
    Refuse findings that cite source IDs which do not
    exist in the grounded source registry.
    """
    valid_ids = {
        source.id
        for source in sources
    }

    for finding in findings:
        unknown = set(
            finding.source_ids
        ) - valid_ids

        if unknown:
            raise ValueError(
                f"Finding {finding.id} references "
                f"unknown grounded source IDs: "
                f"{sorted(unknown)}"
            )


def validate_company_research(
    research: CompanyResearchResult,
) -> CompanyResearchResult:
    for field_name in FINDING_FIELDS:
        validate_finding_sources(
            getattr(research, field_name),
            research.sources,
        )

    return research


def new_research_result(
    company: str,
    job_title: str,
    sources: list[CompanyResearchSource],
) -> CompanyResearchResult:
    """
    Create an empty research result around an established
    grounded source registry.

    Finding generation will be added separately.
    """
    return CompanyResearchResult(
        company=company,
        job_title=job_title,
        research_date=date.today().isoformat(),
        sources=sources,
    )
