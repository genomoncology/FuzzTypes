from typing import Optional

from pydantic import BaseModel, ValidationError, Field

from fuzztypes import NamedEntity, InMemory, flags

names = ["George Washington", "John Adams", "Thomas Jefferson"]
President = InMemory(names, search_mode=flags.NameSearch)
CasedPrez = InMemory(names, case_sensitive=True, search_mode=flags.NameSearch)
NullPrez = InMemory(names, notfound_mode="none", search_mode=flags.NameSearch)
AllowPrez = InMemory(
    names, notfound_mode="allow", search_mode=flags.NameSearch
)


def test_namestr_getitem():
    entity = NamedEntity(value="Thomas Jefferson")
    assert President["Thomas Jefferson"] == entity
    assert President["THOMAS JEFFERSON"] == entity

    assert CasedPrez["Thomas Jefferson"] == entity
    try:
        assert CasedPrez["THOMAS JEFFERSON"] == entity
        assert False, "Didn't raise KeyError!"
    except KeyError:
        pass

    assert NullPrez["The Rock"] is None
    assert AllowPrez["The Rock"].value == "The Rock"


def test_uncased_name_str():
    class Example(BaseModel):
        value: President

    # exact match
    assert Example(value="George Washington").value == "George Washington"

    # case-insensitive match
    assert Example(value="john ADAMS").value == "John Adams"


def test_cased_name_str():
    class Example(BaseModel):
        value: CasedPrez

    # exact match
    assert Example(value="George Washington").value == "George Washington"

    # case-insensitive match
    try:
        assert Example(value="john ADAMS").value == "John Adams"
        assert False, "Didn't raise PydanticCustomError!"
    except ValidationError:
        pass


def test_nullable_name_str():
    class Example(BaseModel):
        value: Optional[NullPrez] = Field(None)

    assert Example().model_dump() == {"value": None}
    assert Example(value="The Rock").model_dump() == {"value": None}


def test_duplicate_records():
    try:
        A = InMemory(["a", "a"], tiebreaker_mode="raise")
        assert A["a"].value == "a"

        assert False, "Didn't raise exception!"
    except ValueError:
        pass

    A = InMemory(["a", "a"], tiebreaker_mode="lesser")
    assert A["a"].value == "a"
