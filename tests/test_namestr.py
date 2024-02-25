from typing import Optional
from pydantic import BaseModel, ValidationError, Field

from fuzztype import NameStr, CasedNameStr

names = ["George Washington", "John Adams", "Thomas Jefferson"]
President = NameStr(names)
CasedPresident = CasedNameStr(names)
NullablePresident = NameStr(names, notfound_mode="none")
AllowablePresident = NameStr(names, notfound_mode="allow")


def test_getitem():
    assert President["Thomas Jefferson"] == "Thomas Jefferson"
    assert President["THOMAS JEFFERSON"] == "Thomas Jefferson"

    assert CasedPresident["Thomas Jefferson"] == "Thomas Jefferson"
    try:
        assert CasedPresident["THOMAS JEFFERSON"] == "Thomas Jefferson"
        assert False, "Didn't raise KeyError!"
    except KeyError:
        pass

    assert NullablePresident["The Rock"] is None
    assert AllowablePresident["The Rock"] == "The Rock"


def test_uncased_name_str():
    class Example(BaseModel):
        name: President

    # exact match
    assert Example(name="George Washington").name == "George Washington"

    # case-insensitive match
    assert Example(name="john ADAMS").name == "John Adams"


def test_cased_name_str():
    class Example(BaseModel):
        name: CasedPresident

    # exact match
    assert Example(name="George Washington").name == "George Washington"

    # case-insensitive match
    try:
        assert Example(name="john ADAMS").name == "John Adams"
        assert False, "Didn't raise PydanticCustomError!"
    except ValidationError:
        pass


def test_nullable_name_str():
    class Example(BaseModel):
        name: Optional[NullablePresident] = Field(None)

    assert Example().model_dump() == {"name": None}
    assert Example(name="The Rock").model_dump() == {"name": None}
