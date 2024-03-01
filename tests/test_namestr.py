from typing import Optional

from pydantic import BaseModel, ValidationError, Field

from fuzztypes import NamedEntity, NameStr, CasedNameStr

names = ["George Washington", "John Adams", "Thomas Jefferson"]
President = NameStr(names)
CasedPresident = CasedNameStr(names)
NullablePresident = NameStr(names, notfound_mode="none")
AllowablePresident = NameStr(names, notfound_mode="allow")


def test_namestr_getitem():
    entity = NamedEntity(value="Thomas Jefferson")
    assert President["Thomas Jefferson"] == entity
    assert President["THOMAS JEFFERSON"] == entity

    assert CasedPresident["Thomas Jefferson"] == entity
    try:
        assert CasedPresident["THOMAS JEFFERSON"] == entity
        assert False, "Didn't raise KeyError!"
    except KeyError:
        pass

    assert NullablePresident["The Rock"] is None
    assert AllowablePresident["The Rock"].value == "The Rock"


def test_uncased_name_str():
    class Example(BaseModel):
        value: President

    # exact match
    assert Example(value="George Washington").value == "George Washington"

    # case-insensitive match
    assert Example(value="john ADAMS").value == "John Adams"


def test_cased_name_str():
    class Example(BaseModel):
        value: CasedPresident

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
        value: Optional[NullablePresident] = Field(None)

    assert Example().model_dump() == {"value": None}
    assert Example(value="The Rock").model_dump() == {"value": None}


def test_duplicate_records():
    try:
        A = NameStr(["a", "a"], tiebreaker_mode="raise")
        assert A["a"].value == "a"

        assert False, "Didn't raise exception!"
    except ValueError:
        pass

    A = NameStr(["a", "a"], tiebreaker_mode="alphabetical")
    assert A["a"].value == "a"
