from fuzztypes.ext.person_name import *


def test_mixed_capitalization():
    assert FullName.get_value("shirley maclaine") == "Shirley MacLaine"
    assert FullName.get_value("john smith") == "John Smith"

    NoCap = PersonName(capitalize=False)
    assert NoCap.get_value("shirley maclaine") == "shirley maclaine"
    assert NoCap.get_value("john smith") == "john smith"


def test_all_patterns_long_name():
    value = "Dr. Juan Q. Xavier de la Vega III"
    assert FullName.get_value(value) == "Dr. Juan Q. Xavier de la Vega III"
    assert BibliographyName.get_value(value) == "de la Vega, Juan Q. Xavier"
    assert FirstLastName.get_value(value) == "Juan de la Vega"
    assert ProfessionalName.get_value(value) == "Juan Q. Xavier de la Vega III"


def test_all_patterns_with_nickname():
    value = "Arthur 'Fonz' Fonzerelli"
    assert FullName.get_value(value) == "Arthur Fonzerelli (Fonz)"
    assert BibliographyName.get_value(value) == "Fonzerelli, Arthur"
    assert FirstLastName.get_value(value) == "Arthur Fonzerelli"
    assert ProfessionalName.get_value(value) == "Arthur Fonzerelli"
    assert FirstNickLastName.get_value(value) == "Arthur 'Fonz' Fonzerelli"
