from pydantic import BaseModel, ValidationError
import pytest

from fuzztype import AliasStr, CasedAliasStr, Entity

# Defining entities with aliases
entities = [
    Entity(name="Odysseus", aliases=["Ulysses"]),
    Entity(name="Athena", aliases=["Minerva", "Pallas"]),
    Entity(name="Zeus", aliases=["Jupiter", "Jove"]),
]

MythicalFigure = AliasStr(entities, case_sensitive=False)
CasedMythicalFigure = CasedAliasStr(entities)


def test_alias_uncased_getitem():
    # Testing AliasStr with aliases
    assert MythicalFigure["Odysseus"] == "Odysseus"
    assert MythicalFigure["Ulysses"] == "Odysseus"
    assert MythicalFigure["athena"] == "Athena"  # Testing case insensitivity


def test_alias_cased_getitem():
    # Testing CasedAliasStr, expecting case-sensitive behavior
    assert CasedMythicalFigure["Athena"] == "Athena"
    with pytest.raises(KeyError):
        # This should fail because CasedMythicalFigure is case-sensitive
        assert CasedMythicalFigure["athena"] == "Athena"


def test_uncased_alias_str():
    class Example(BaseModel):
        name: MythicalFigure

    # Exact match
    assert Example(name="Zeus").name == "Zeus"
    # Alias match
    assert Example(name="Jupiter").name == "Zeus"
    # Case-insensitive alias match
    assert Example(name="jove").name == "Zeus"


def test_cased_alias_str():
    class Example(BaseModel):
        name: CasedMythicalFigure

    # Exact match
    assert Example(name="Zeus").name == "Zeus"
    # Alias match
    assert Example(name="Jupiter").name == "Zeus"
    # Case-sensitive alias match should fail
    with pytest.raises(ValidationError):
        Example(name="jove")
