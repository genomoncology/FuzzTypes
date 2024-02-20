from pydantic import BaseModel
from fuzztype import FindStr


class MyClass(BaseModel):
    upper: FindStr(str.upper)
    lower: FindStr(str.lower)


def test_simple_transforms():
    obj = MyClass(upper="Abc", lower="ABc")
    assert obj.upper == "ABC"
    assert obj.lower == "abc"
