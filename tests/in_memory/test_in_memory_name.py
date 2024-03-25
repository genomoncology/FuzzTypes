from typing import Annotated, Optional

from pydantic import BaseModel, ValidationError, Field

from fuzztypes import NamedEntity, InMemoryValidator, flags

names = ["George Washington", "John Adams", "Thomas Jefferson"]
President = InMemoryValidator(names, search_flag=flags.NameSearch)
CasedPrez = InMemoryValidator(
    names, case_sensitive=True, search_flag=flags.NameSearch
)
NullPrez = InMemoryValidator(
    names, notfound_mode="none", search_flag=flags.NameSearch
)
AllowPrez = InMemoryValidator(
    names, notfound_mode="allow", search_flag=flags.NameSearch
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
        value: Annotated[str, President]

    # exact match
    assert Example(value="George Washington").value == "George Washington"

    # case-insensitive match
    assert Example(value="john ADAMS").value == "John Adams"


def test_cased_name_str():
    class Example(BaseModel):
        value: Annotated[str, CasedPrez]

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
        value: Annotated[Optional[str], NullPrez] = Field(default=None)

    assert Example().model_dump() == {"value": None}
    assert Example(value="The Rock").model_dump() == {"value": None}
