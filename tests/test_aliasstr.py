import pytest
from pydantic import BaseModel, ValidationError

from fuzztypes import AliasStr, AliasCasedStr, NamedEntity


@pytest.fixture(scope="session")
def MythicalFigure(MythSource):
    return AliasStr(MythSource)


@pytest.fixture(scope="session")
def CasedMythicalFigure(MythSource):
    return AliasCasedStr(MythSource)


def test_alias_uncased_getitem(MythicalFigure):
    # Testing AliasStr with aliases
    assert MythicalFigure["Odysseus"].value == "Odysseus"
    assert MythicalFigure["Ulysses"].value == "Odysseus"  # alias
    assert MythicalFigure["athena"].value == "Athena"  # case insensitivity


def test_alias_cased_getitem(CasedMythicalFigure):
    # Testing AliasCasedStr, expecting case-sensitive behavior
    assert CasedMythicalFigure["Athena"].value == "Athena"

    assert CasedMythicalFigure.get_entity("athena") is None

    with pytest.raises(KeyError):
        # This should fail because CasedMythicalFigure is case-sensitive
        assert CasedMythicalFigure["athena"].value == "Athena"


def test_uncased_alias_str(MythicalFigure):
    class Example(BaseModel):
        value: MythicalFigure

    # Exact match
    assert Example(value="Zeus").value == "Zeus"
    # Alias match
    assert Example(value="Jupiter").value == "Zeus"
    # Case-insensitive alias match
    assert Example(value="jove").value == "Zeus"


def test_cased_alias_str(CasedMythicalFigure):
    class Example(BaseModel):
        value: CasedMythicalFigure

    # Exact match
    assert Example(value="Zeus").value == "Zeus"
    # Alias match
    assert Example(value="Jupiter").value == "Zeus"
    # Case-sensitive alias match should fail
    with pytest.raises(ValidationError):
        Example(value="jove")


def test_duplicate_records():
    source = [["c", "b"], ["a", "b"], ["d", "b"]]
    try:
        A = AliasStr(source, tiebreaker_mode="raise")
        assert A["a"].value == "a"
        assert False, "Didn't raise exception!"
    except ValueError:
        pass

    A = AliasStr(source, tiebreaker_mode="lesser")
    assert A["b"].value == "a"

    A = AliasStr(source, tiebreaker_mode="greater")
    assert A["b"].value == "d"
