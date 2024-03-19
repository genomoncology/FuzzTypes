from pydantic import BaseModel

from fuzztypes import Language, LanguageCode, LanguageName
from fuzztypes.language import load_languages, LanguageType, LanguageScope


def test_load_languages():
    source = load_languages()
    entities = source()
    assert len(entities) == 7910
    assert entities[0].resolve() == 'Ghotuo'


def test_language_model_resolution():
    class Model(BaseModel):
        language: Language
        language_code: LanguageCode
        language_name: LanguageName

    # Test that Language resolves to the complete language object
    model = Model(language="English", language_code="en", language_name="ENG")
    assert model.language.scope == LanguageScope.INDIVIDUAL
    assert model.language.type == LanguageType.LIVING
    assert model.model_dump(exclude_defaults=True, mode="json") == {
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
    assert LanguageName("En") == "En"
    assert LanguageCode("En") == "enc"

    # 'en' is the alpha2 code for English
    assert LanguageName("en") == "English"
    assert LanguageCode("en") == "en"

    # Bangla is common name for Bengali
    assert LanguageName("Bangla") == "Bengali"
    assert LanguageCode("Bangla") == "bn"
    assert Language("Bangla").model_dump(
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
