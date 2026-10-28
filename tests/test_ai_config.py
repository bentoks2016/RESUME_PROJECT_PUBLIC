from pathlib import Path

from app import ai_config


def test_ai_model_role_defaults():
    assert (
        ai_config.DISCOVERY_MODEL
        == "gemini-3.1-flash-lite"
    )
    assert (
        ai_config.ADVISORY_MODEL
        == "gemini-3.5-flash-lite"
    )
    assert (
        ai_config.CRITICAL_MODEL
        == "gemini-3.6-flash"
    )


def test_gemini_configuration_is_centralized():
    domain_modules = [
        Path("app/ai.py"),
        Path("app/achievements.py"),
        Path("app/integrity.py"),
        Path("app/recruiter.py"),
        Path("app/interview.py"),
    ]

    prohibited = [
        "genai.Client(",
        'os.getenv("GEMINI_API_KEY"',
        'os.getenv("GEMINI_MODEL"',
        "load_dotenv(",
    ]

    for path in domain_modules:
        text = path.read_text()

        for pattern in prohibited:
            assert pattern not in text, (
                f"{path} contains centralized AI "
                f"configuration pattern: {pattern}"
            )


def test_ai_tasks_use_expected_model_roles():
    expected = {
        "app/ai.py": {
            "ADVISORY_MODEL": 1,
            "CRITICAL_MODEL": 1,
        },
        "app/achievements.py": {
            "DISCOVERY_MODEL": 1,
            "CRITICAL_MODEL": 0,
        },
        "app/integrity.py": {
            "CRITICAL_MODEL": 0,
        },
        "app/recruiter.py": {
            "ADVISORY_MODEL": 1,
        },
        "app/interview.py": {
            "ADVISORY_MODEL": 1,
        },
    }

    total_model_calls = 0

    for filename, roles in expected.items():
        text = Path(filename).read_text()

        assert "model=MODEL" not in text
        assert "MODEL =" not in text

        for role, expected_count in roles.items():
            actual = text.count(
                f"model={role}"
            )

            assert actual == expected_count, (
                f"{filename}: expected "
                f"{expected_count} calls using {role}, "
                f"found {actual}"
            )

            total_model_calls += actual

    assert total_model_calls == 5
