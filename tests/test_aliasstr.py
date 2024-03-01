import pytest
from pydantic import BaseModel, ValidationError

from fuzztypes import AliasStr, CasedAliasStr, NamedEntity


@pytest.fixture(scope="session")
def MythicalFigure(MythSource):
    return AliasStr(MythSource)


@pytest.fixture(scope="session")
def CasedMythicalFigure(MythSource):
    return CasedAliasStr(MythSource)


def test_alias_uncased_getitem(MythicalFigure):
    # Testing AliasStr with aliases
    assert MythicalFigure["Odysseus"].name == "Odysseus"
    assert MythicalFigure["Ulysses"].name == "Odysseus"  # alias
    assert MythicalFigure["athena"].name == "Athena"  # case insensitivity


def test_alias_cased_getitem(CasedMythicalFigure):
    # Testing CasedAliasStr, expecting case-sensitive behavior
    assert CasedMythicalFigure["Athena"].name == "Athena"

    assert CasedMythicalFigure.get_entity("athena") is None

    with pytest.raises(KeyError):
        # This should fail because CasedMythicalFigure is case-sensitive
        assert CasedMythicalFigure["athena"].name == "Athena"


def test_uncased_alias_str(MythicalFigure):
    class Example(BaseModel):
        name: MythicalFigure

    # Exact match
    assert Example(name="Zeus").name == "Zeus"
    # Alias match
    assert Example(name="Jupiter").name == "Zeus"
    # Case-insensitive alias match
    assert Example(name="jove").name == "Zeus"


def test_cased_alias_str(CasedMythicalFigure):
    class Example(BaseModel):
        name: CasedMythicalFigure

    # Exact match
    assert Example(name="Zeus").name == "Zeus"
    # Alias match
    assert Example(name="Jupiter").name == "Zeus"
    # Case-sensitive alias match should fail
    with pytest.raises(ValidationError):
        Example(name="jove")


def test_duplicate_records():
    source = [["c", "b"], ["a", "b"], ["d", "b"]]
    try:
        A = AliasStr(source, tiebreaker_mode="raise")
        assert A["a"].name == "a"
        assert False, "Didn't raise exception!"
    except ValueError:
        pass

    A = AliasStr(source, tiebreaker_mode="alphabetical")
    assert A["b"].name == "a"
