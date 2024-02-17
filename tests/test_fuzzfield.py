from pydantic import BaseModel, Field
from fuzztype import FuzzStr

FruitStr = FuzzStr(["Apple", "Banana"])
UpperStr = FuzzStr(str.upper)


class MyModel(BaseModel):
    fruit: FruitStr = None
    upper: UpperStr = None


def test_fruit_list():
    assert MyModel(fruit="Apple").fruit == "Apple"
    assert MyModel(fruit="apple").fruit == "Apple"
    assert MyModel(fruit="appel").fruit == "Apple"


def test_upper_function():
    assert MyModel(upper="monkey").upper == "MONKEY"
