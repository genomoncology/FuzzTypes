from pydantic import ValidationError

from fuzztypes import Email, SSN, ZipCode, validate_python


def test_email_regexer():
    assert (
        validate_python(Email, "Jane Doe <jdoe@example.com>")
        == "jdoe@example.com"
    )
    assert validate_python(Email, "<jdoe@example.com>") == "jdoe@example.com"

    try:
        assert validate_python(Email, "abc@xyz") is not None
        assert False, "Invalid email did not fail!"
    except ValidationError:
        pass


def test_valid_ssn():
    # Value call
    assert validate_python(SSN, "Valid SSN: 123-45-6789") == "123-45-6789"

    # Entity value comparison
    assert validate_python(SSN, "Valid SSN: 123-45-6789") == "123-45-6789"

    # Entity equivalence to a value
    assert validate_python(SSN, "Valid SSN: 123-45-6789") == "123-45-6789"


def test_valid_ssn_with_touching_bounding_chars():
    assert validate_python(SSN, "Valid SSN:123-45-6789.") == "123-45-6789"


def test_invalid_ssn_format():
    try:
        validate_python(SSN, "Invalid SSN: 123-456-789")
        assert False, "Invalid SSN format was accepted."
    except ValidationError:
        pass


def test_ssn_needs_bounding_spaces():
    try:
        validate_python(SSN, "SSN text: abc123-45-6789xyz")
        assert False, "SSNs require some sort of bounding characters."
    except ValidationError:
        pass


def test_multiple_ssns():
    # This test depends on how you decide to handle multiple SSNs.
    multi_ssn_string = "Two SSNs: 123-45-6789 and 987-65-4321"
    try:
        assert validate_python(SSN, multi_ssn_string) is not None
        assert False, "Invalid SSN format was accepted."
    except ValidationError:
        pass


def test_valid_zip_code_5_digits():
    assert validate_python(ZipCode, "Postal code: 12345") == "12345"


def test_valid_zip_code_9_digits():
    assert validate_python(ZipCode, "ZIP:12345-6789") == "12345-6789"


def test_zip_code_within_text():
    assert (
        validate_python(ZipCode, "Send it to 98765-4321, please.")
        == "98765-4321"
    )


def test_invalid_zip_code():
    try:
        validate_python(ZipCode, "Invalid ZIP: 1234")
        assert False, "Invalid ZIP code did not fail."
    except ValidationError:
        pass


def test_zip_code_with_invalid_four_format():
    # Python's re module does not support lookbehinds (?<!)
    # tried: r"\b\d{5}(?:-\d{4})?\b(?<!-\d{1,3}\b)",
    assert validate_python(ZipCode, "Invalid ZIP: 12345-678") == "12345"
