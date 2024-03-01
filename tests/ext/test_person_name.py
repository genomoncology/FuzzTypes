from fuzztype.ext.person_name import *


def test_mixed_capitalization():
    assert FullName.get_value("shirley maclaine") == "Shirley MacLaine"
    assert FullName.get_value("john smith") == "John Smith"

    NoCap = PersonName(capitalize=False)
    assert NoCap.get_value("shirley maclaine") == "shirley maclaine"
    assert NoCap.get_value("john smith") == "john smith"


def test_all_patterns_long_name():
    name = "Dr. Juan Q. Xavier de la Vega III"

    assert AllName.get_value(name) == "Dr. Juan Q. Xavier de la Vega III"
    assert Bibliography.get_value(name) == "de la Vega, Juan Q. Xavier"
    assert BusinessFormat.get_value(name) == "Dr. Juan de la Vega"
    assert FirstLastName.get_value(name) == "Juan de la Vega"
    assert FirstNickLastName.get_value(name) == "Juan de la Vega"
    assert FullName.get_value(name) == "Dr. Juan Q. Xavier de la Vega III"
    assert LegalName.get_value(name) == "Juan Q. Xavier de la Vega III"
    assert NicknameOnly.get_value(name) == "de la Vega"
    assert ProfessionalName.get_value(name) == "Juan Q. Xavier de la Vega III"
    assert ProfessionalTitle.get_value(name) == "Dr. de la Vega"


def test_all_patterns_with_nickname():
    name = "Arthur 'Fonz' Fonzerelli"

    assert AllName.get_value(name) == "Arthur Fonzerelli (Fonz)"
    assert Bibliography.get_value(name) == "Fonzerelli, Arthur"
    assert BusinessFormat.get_value(name) == "Arthur Fonzerelli"
    assert FirstLastName.get_value(name) == "Arthur Fonzerelli"
    assert FirstNickLastName.get_value(name) == "Arthur Fonz Fonzerelli"
    assert FullName.get_value(name) == "Arthur Fonzerelli"
    assert LegalName.get_value(name) == "Arthur Fonzerelli"
    assert NicknameOnly.get_value(name) == "Fonz Fonzerelli"
    assert ProfessionalName.get_value(name) == "Arthur Fonzerelli"
    assert ProfessionalTitle.get_value(name) == "Fonzerelli"
