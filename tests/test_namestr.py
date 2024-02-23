from pydantic import BaseModel, ValidationError

from fuzztype import NameStr, CasedNameStr

names = ["George Washington", "John Adams", "Thomas Jefferson"]
President = NameStr(names)
CasedPresident = CasedNameStr(names)


def test_getitem():
    assert President["Thomas Jefferson"] == "Thomas Jefferson"
    assert President["THOMAS JEFFERSON"] == "Thomas Jefferson"

    assert CasedPresident["Thomas Jefferson"] == "Thomas Jefferson"
    try:
        assert CasedPresident["THOMAS JEFFERSON"] == "Thomas Jefferson"
        assert False, "Didn't raise KeyError!"
    except KeyError:
        pass


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

