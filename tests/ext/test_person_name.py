from fuzztypes.ext.person_name import *


def test_mixed_capitalization():
    assert FullName.get_value("shirley maclaine") == "Shirley MacLaine"
    assert FullName.get_value("john smith") == "John Smith"

    NoCap = PersonName(capitalize=False)
    assert NoCap.get_value("shirley maclaine") == "shirley maclaine"
    assert NoCap.get_value("john smith") == "john smith"


def test_all_patterns_long_name():
    name = "Dr. Juan Q. Xavier de la Vega III"
    assert FullName.get_value(name) == "Dr. Juan Q. Xavier de la Vega III"
    assert BibliographyName.get_value(name) == "de la Vega, Juan Q. Xavier"
    assert FirstLastName.get_value(name) == "Juan de la Vega"
    assert ProfessionalName.get_value(name) == "Juan Q. Xavier de la Vega III"


def test_all_patterns_with_nickname():
    name = "Arthur 'Fonz' Fonzerelli"
    assert FullName.get_value(name) == "Arthur Fonzerelli (Fonz)"
    assert BibliographyName.get_value(name) == "Fonzerelli, Arthur"
    assert FirstLastName.get_value(name) == "Arthur Fonzerelli"
    assert ProfessionalName.get_value(name) == "Arthur Fonzerelli"
    assert FirstNickLastName.get_value(name) == "Arthur 'Fonz' Fonzerelli"
