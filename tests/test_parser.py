from app.parser import extract_contact_information


def test_extracts_email():
    text = """
    Test Candidate
    candidate@example.com
    Professional Profile
    """

    contact = extract_contact_information(text)

    assert contact["email"] == "candidate@example.com"


def test_extracts_linkedin():
    text = """
    Test Candidate
    www.linkedin.com/in/test-candidate
    """

    contact = extract_contact_information(text)

    assert (
        contact["linkedin"]
        == "www.linkedin.com/in/test-candidate"
    )


def test_missing_phone_remains_blank():
    text = """
    Test Candidate
    candidate@example.com
    www.linkedin.com/in/test-candidate
    """

    contact = extract_contact_information(text)

    assert contact["phone"] == ""


def test_extracts_standard_phone():
    text = """
    Test Candidate
    candidate@example.com
    +1 506 555 1234
    """

    contact = extract_contact_information(text)

    assert contact["phone"]


def test_does_not_invent_missing_contact():
    contact = extract_contact_information(
        "Professional profile with no contact details."
    )

    assert contact["email"] == ""
    assert contact["phone"] == ""
    assert contact["linkedin"] == ""
