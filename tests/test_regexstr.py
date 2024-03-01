from pydantic_core import PydanticCustomError

from fuzztypes import Email, SSN, ZipCode


def test_email_regexer():
    assert Email.get_value("Jane Doe <jdoe@example.com>") == "jdoe@example.com"
    assert Email["<jdoe@example.com>"] == "jdoe@example.com"

    try:
        assert Email["abc@xyz"] is not None
        assert False, "Invalid email did not fail!"
    except KeyError:
        pass


def test_valid_ssn():
    assert SSN.get_value("Valid SSN: 123-45-6789") == "123-45-6789"


def test_valid_ssn_with_touching_bounding_chars():
    assert SSN.get_value("Valid SSN:123-45-6789.") == "123-45-6789"


def test_invalid_ssn_format():
    try:
        SSN.get_value("Invalid SSN: 123-456-789")
        assert False, "Invalid SSN format was accepted."
    except PydanticCustomError:
        pass


def test_ssn_needs_bounding_spaces():
    try:
        SSN.get_value("SSN text: abc123-45-6789xyz")
        assert False, "SSNs require some sort of bounding characters."
    except PydanticCustomError:
        pass


def test_multiple_ssns():
    # This test depends on how you decide to handle multiple SSNs.
    multi_ssn_string = "Two SSNs: 123-45-6789 and 987-65-4321"
    try:
        assert SSN.get_value(multi_ssn_string) is not None
        assert False, "Invalid SSN format was accepted."
    except PydanticCustomError as e:
        pass


def test_valid_zip_code_5_digits():
    assert ZipCode.get_value("Postal code: 12345") == "12345"


def test_valid_zip_code_9_digits():
    assert ZipCode.get_value("ZIP:12345-6789") == "12345-6789"


def test_zip_code_within_text():
    assert ZipCode.get_value("Send it to 98765-4321, please.") == "98765-4321"


def test_invalid_zip_code():
    try:
        ZipCode.get_value("Invalid ZIP: 1234")
        assert False, "Invalid ZIP code did not fail."
    except PydanticCustomError:
        pass


def test_zip_code_with_invalid_four_format():
    # Python's re module does not support lookbehinds (?<!)
    # tried: r"\b\d{5}(?:-\d{4})?\b(?<!-\d{1,3}\b)",
    assert ZipCode.get_value("Invalid ZIP: 12345-678") == "12345"
