from types import SimpleNamespace

import pytest

from app.company_research import (
    extract_grounded_sources,
    validate_company_research,
)
from app.models import (
    CompanyResearchFinding,
    CompanyResearchResult,
    CompanyResearchSource,
)


def grounded_response(chunks):
    return SimpleNamespace(
        candidates=[
            SimpleNamespace(
                grounding_metadata=SimpleNamespace(
                    grounding_chunks=chunks
                )
            )
        ]
    )


def web_chunk(
    uri,
    title="",
    domain="",
):
    return SimpleNamespace(
        web=SimpleNamespace(
            uri=uri,
            title=title,
            domain=domain,
        )
    )


def test_extracts_sources_only_from_grounding_metadata():
    response = grounded_response(
        [
            web_chunk(
                "https://example.com/strategy",
                "Company Strategy",
                "example.com",
            ),
        ]
    )

    sources = extract_grounded_sources(
        response
    )

    assert len(sources) == 1
    assert sources[0].url == (
        "https://example.com/strategy"
    )
    assert sources[0].title == (
        "Company Strategy"
    )
    assert sources[0].domain == "example.com"


def test_duplicate_grounded_urls_are_deduplicated():
    response = grounded_response(
        [
            web_chunk(
                "https://example.com/a"
            ),
            web_chunk(
                "https://example.com/a"
            ),
        ]
    )

    sources = extract_grounded_sources(
        response
    )

    assert len(sources) == 1


def test_missing_grounding_produces_no_sources():
    response = SimpleNamespace(
        candidates=[]
    )

    assert extract_grounded_sources(
        response
    ) == []


def test_unknown_source_reference_is_rejected():
    research = CompanyResearchResult(
        company="Example Company",
        job_title="Example Role",
        research_date="2026-09-15",
        strategic_priorities=[
            CompanyResearchFinding(
                id="finding-1",
                category="STRATEGY",
                finding=(
                    "Example grounded company fact."
                ),
                relevance_to_role="HIGH",
                source_ids=[
                    "source-does-not-exist"
                ],
            )
        ],
        sources=[
            CompanyResearchSource(
                id="source-1",
                title="Source",
                url="https://example.com",
            )
        ],
    )

    with pytest.raises(ValueError):
        validate_company_research(
            research
        )


def test_valid_source_reference_is_accepted():
    research = CompanyResearchResult(
        company="Example Company",
        job_title="Example Role",
        research_date="2026-09-15",
        strategic_priorities=[
            CompanyResearchFinding(
                id="finding-1",
                category="STRATEGY",
                finding=(
                    "Example grounded company fact."
                ),
                relevance_to_role="HIGH",
                source_ids=[
                    "source-1"
                ],
            )
        ],
        sources=[
            CompanyResearchSource(
                id="source-1",
                title="Source",
                url="https://example.com",
            )
        ],
    )

    assert validate_company_research(
        research
    ) is research


def test_grounding_support_maps_segment_to_source():
    from app.company_research import (
        extract_grounded_segments,
    )

    response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                grounding_metadata=SimpleNamespace(
                    grounding_chunks=[
                        web_chunk(
                            "https://example.com/strategy",
                            "Strategy",
                            "example.com",
                        ),
                        web_chunk(
                            "https://example.com/investment",
                            "Investment",
                            "example.com",
                        ),
                    ],
                    grounding_supports=[
                        SimpleNamespace(
                            segment=SimpleNamespace(
                                text=(
                                    "The company announced "
                                    "a new investment."
                                )
                            ),
                            grounding_chunk_indices=[
                                1
                            ],
                            confidence_scores=[
                                0.97
                            ],
                        )
                    ],
                )
            )
        ]
    )

    sources = extract_grounded_sources(
        response
    )

    segments = extract_grounded_segments(
        response,
        sources,
    )

    assert len(segments) == 1
    assert segments[0].source_ids == [
        "source-2"
    ]
    assert segments[0].confidence_scores == [
        0.97
    ]


def test_unsupported_segment_is_not_accepted():
    from app.company_research import (
        extract_grounded_segments,
    )

    response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                grounding_metadata=SimpleNamespace(
                    grounding_chunks=[
                        web_chunk(
                            "https://example.com/source"
                        )
                    ],
                    grounding_supports=[
                        SimpleNamespace(
                            segment=SimpleNamespace(
                                text="Unsupported statement."
                            ),
                            grounding_chunk_indices=[],
                            confidence_scores=[],
                        )
                    ],
                )
            )
        ]
    )

    sources = extract_grounded_sources(
        response
    )

    assert extract_grounded_segments(
        response,
        sources,
    ) == []
