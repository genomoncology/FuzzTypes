# FuzzType

FuzzType is a [Pydantic](https://github.com/pydantic/pydantic) extension for annotating autocorrecting fields.

It uses [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) to handle the fuzzy matching.

## FuzzStr

```python
from pydantic import BaseModel

from fuzztype import FuzzStr

FruitStr = FuzzStr(["Apple", "Banana"])
UpperStr = FuzzStr(str.upper)
DirStr = FuzzStr([("Left", "L"), ("Right", "R"), ("Middle", "Straight", "M")])


class MyModel(BaseModel):
    fruit: FruitStr = None
    upper: UpperStr = None
    direction: DirStr = None


def test_fruit_list():
    assert MyModel(fruit="Apple").fruit == "Apple"
    assert MyModel(fruit="apple").fruit == "Apple"  # mis-cased
    assert MyModel(fruit="appel").fruit == "Apple"  # mis-spelling


def test_upper_function():
    assert MyModel(upper="MONKEY").upper == "MONKEY"
    assert MyModel(upper="monkey").upper == "MONKEY"


def test_synonyms():
    assert MyModel(direction="Left").direction == "Left"
    assert MyModel(direction="r").direction == "Right"
    assert MyModel(direction="mid").direction == "Middle"
    assert MyModel(direction="midle").direction == "Middle"
    assert MyModel(direction="streight").direction == "Middle"
```