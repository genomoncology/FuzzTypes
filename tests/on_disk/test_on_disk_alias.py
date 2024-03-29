from typing import Annotated

import pytest
from pydantic import BaseModel, ValidationError

from fuzztypes import OnDiskValidator, flags


@pytest.fixture(scope="session")
def MythicalFigure(MythSource):
    return OnDiskValidator(
        "MythicalFigure", MythSource, search_flag=flags.AliasSearch
    )


@pytest.fixture(scope="session")
def CasedMythicalFigure(MythSource):
    return OnDiskValidator(
        "CasedMythicalFigure",
        MythSource,
        search_flag=flags.AliasSearch,
        case_sensitive=True,
    )


def test_alias_uncased_getitem(MythicalFigure):
    # Testing Alias with aliases
    assert MythicalFigure["Odysseus"].value == "Odysseus"
    assert MythicalFigure["Ulysses"].value == "Odysseus"  # alias
    assert MythicalFigure["athena"].value == "Athena"  # case insensitivity


def test_alias_cased_getitem(CasedMythicalFigure):
    # Testing AliasCasedStr, expecting case-sensitive behavior
    assert CasedMythicalFigure["Athena"].value == "Athena"

    with pytest.raises(KeyError):
        # This should fail because CasedMythicalFigure is case-sensitive
        assert CasedMythicalFigure["athena"].value == "Athena"


def test_uncased_alias_str(MythicalFigure):
    class Example(BaseModel):
        value: Annotated[str, MythicalFigure]

    # Exact match
    assert Example(value="Zeus").value == "Zeus"
    # Alias match
    assert Example(value="Jupiter").value == "Zeus"
    # Case-insensitive alias match
    assert Example(value="jove").value == "Zeus"


def test_cased_alias_str(CasedMythicalFigure):
    class Example(BaseModel):
        value: Annotated[str, CasedMythicalFigure]

    # Exact match
    assert Example(value="Zeus").value == "Zeus"
    # Alias match
    assert Example(value="Jupiter").value == "Zeus"
    # Case-sensitive alias match should fail
    with pytest.raises(ValidationError):
        Example(value="jove")


def test_duplicate_records():
    source = [["c", "b"], ["a", "b"], ["d", "b"]]

    A = OnDiskValidator("DupeRec", source)
    assert A["a"].value == "a"

    try:
        assert A["b"].value == "a"
        assert False, "Didn't raise exception!"
    except KeyError as e:
        assert (
            str(e) == "'Key Error: b "
            '["b" could not be resolved, did you mean "c", "a", or "d"?]\''
        )

    A = OnDiskValidator("DupeRec", source, tiebreaker_mode="lesser")
    assert A["b"].value == "a"

    A = OnDiskValidator("DupeRec", source, tiebreaker_mode="greater")
    assert A["b"].value == "d"
