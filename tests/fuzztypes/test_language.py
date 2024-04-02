from pydantic import BaseModel

from fuzztypes import (
    Language,
    LanguageCode,
    LanguageName,
    LanguageNamedEntity,
    LanguageScope,
    LanguageType,
    validate_python,
)
from fuzztypes.language import load_languages


def test_load_languages():
    source = load_languages(LanguageNamedEntity)
    entities = source()
    assert len(entities) == 7910
    assert entities[0].resolve() == "Ghotuo"


def test_language_model_resolution():
    class Model(BaseModel):
        language_code: LanguageCode
        language_name: LanguageName
        language: Language

    # Test that Language resolves to the complete language object
    data = dict(language_code="en", language="English", language_name="ENG")
    obj = validate_python(Model, data)
    assert obj.language_code == "en"
    assert obj.language_name == "English"
    assert obj.language.scope == LanguageScope.INDIVIDUAL
    assert obj.language.type == LanguageType.LIVING
    assert isinstance(obj.language, LanguageNamedEntity)
    assert obj.model_dump(exclude_defaults=True, mode="json") == {
        "language": {
            "aliases": ["en", "eng"],
            "alpha_2": "en",
            "alpha_3": "eng",
            "scope": "I",
            "type": "L",
            "value": "English",
        },
        "language_code": "en",
        "language_name": "English",
    }


def test_matching_edge_cases():
    # 'En' is a proper name of a language
    assert validate_python(LanguageName, "En") == "En"
    assert validate_python(LanguageCode, "En") == "enc"

    # 'en' is the alpha2 code for English
    assert validate_python(LanguageName, "en") == "English"
    assert validate_python(LanguageCode, "en") == "en"

    # Bangla is common name for Bengali
    assert validate_python(LanguageName, "Bangla") == "Bengali"
    assert validate_python(LanguageCode, "Bangla") == "bn"
    assert validate_python(Language, "Bangla").model_dump(
        exclude_defaults=True, mode="json"
    ) == {
        "aliases": ["bn", "ben", "Bangla"],
        "alpha_2": "bn",
        "alpha_3": "ben",
        "common_name": "Bangla",
        "scope": "I",
        "type": "L",
        "value": "Bengali",
    }
