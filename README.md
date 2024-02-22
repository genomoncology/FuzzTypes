#
 FuzzType

FuzzType is a [Pydantic](https://github.com/pydantic/pydantic) extension for annotating autocorrecting fields.

It uses [RapidFuzz](https://github.com/rapidfuzz/RapidFuzz) to handle the fuzzy matching.

## Motivation 

- Pydantic is a popular library for creating type-annotated Python classes that handles the validation and automatic conversion of some input data types (e.g. int: “3" => 3).
- FuzzType is a collection of easy to understand type-annotations (e.g. FuzzStr, FuzzBool) that uses fuzzy logic to convert input data (e.g. FuzzBool: “yes” => True).
- LLMs can generate structured outputs through the use of function and tool calling. Several libraries (e.g. [Instructor](https://github.com/jxnl/instructor), [Outlines](https://github.com/outlines-dev/outlines), [Marvin](https://github.com/prefecthq/marvin)) use Pydantic for declaring desired object structures and leverage Pydantic’s jsonschema and validation capabilities to guide the LLM’s generation through function definitions and retries. 
- LLM function definitions can accept literals, enums and examples. However, providing comprehensive lists of possible values uses up tokens. FuzzyStr allows for larger vocabularies get automatically normalized.
- Relying on validation and retries to instruct the LLM into providing correct values is highly inefficient due to LLM processing and API calling overhead. Instead, FuzzType can map to the preferred input from synonyms, case adjustments, and other functional logic (e.g. FuzzDate: "today" => date.today()).
- Pydantic used by FastAPI which generates OpenAPI schema which is used by OpenAI's plugins and custom GPT actions.
- Creating new fuzzy type annotations is very to do and there are lots of examples. 
- Low cardinality (e.g. birth sex, race) fields are fine, but high-cardinality (e.g. countries, genes) fields can be expensive from a token perspective when communicating the OpenAPI or jsonschema specification.

## FuzzStr

```python
from pydantic import BaseModel

from fuzztype import FuzzStr, Entity

FruitStr = FuzzStr(["Apple", "Banana"])
DirectionStr = FuzzStr(
    [
        ("Left", "L"),
        ("Right", "R"),
        ("Middle", "M"),
    ]
)


class Model(BaseModel):
    fruit: FruitStr = None
    direction: DirectionStr = None


def test_exact_matches():
    obj = Model(fruit="Apple", title="Hello World", direction="Left")
    assert obj.fruit == "Apple"
    assert obj.direction == "Left"


def test_case_insensitive():
    obj = Model(fruit="banana", title="hello world", direction="right")
    assert obj.fruit == "Banana"
    assert obj.direction == "Right"


def test_case_fuzzy():
    obj = Model(fruit="appel", direction="lft.")
    assert obj.fruit == "Apple"
    assert obj.direction == "Left"


def test_synonyms():
    assert Model(direction="L").direction == "Left"
    assert Model(direction="r").direction == "Right"
    assert Model(direction="M.").direction == "Middle"
```