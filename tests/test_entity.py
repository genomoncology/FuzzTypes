from pathlib import Path
from typing import Iterator, Iterable

from pydantic import BaseModel
from pytest import fixture

from fuzztype import Entity
from fuzztype import FuzzStr, EntityList


def test_entity_conv():
    def c(item):
        return Entity.convert(item).model_dump(exclude_defaults=True)

    assert c("A") == dict(name="A")
    assert c(("A", "B")) == dict(name="A", synonyms=["B"])
    assert c(("A", ["B"])) == dict(name="A", synonyms=["B"])
    assert c(("A", ["B", "C"])) == dict(name="A", synonyms=["B", "C"])


def test_entity_json_schema():
    assert Entity.model_json_schema() == {
        "properties": {
            "name": {
                "description": "Preferred term of Entity.",
                "title": "Name",
                "type": "string",
            },
            "synonyms": {
                "description": "List of aliases for Entity.",
                "items": {"type": "string"},
                "title": "Synonyms",
                "type": "array",
            },
            "label": {
                "default": "",
                "type": "string",
                "description": "Entity type such as PERSON, ORG, or GPE.",
                "title": "Label",
            },
        },
        "required": ["name"],
        "title": "Entity",
        "type": "object",
    }


@fixture(scope="session")
def MyEntities():
    path = Path(__file__).parent / "entities.jsonl"
    return EntityList.from_jsonl(path)


def test_load_entities(MyEntities):
    assert len(MyEntities) == 6
    assert MyEntities[0].name == "Dog"


def test_loader_label_iterator(MyEntities):
    assert isinstance(MyEntities["fruit"], Iterator)
    assert isinstance(MyEntities["fruit"], Iterable)

    FruitStr = FuzzStr(MyEntities["fruit"])
    AnimalStr = FuzzStr(MyEntities["animal"])

    class MyClass(BaseModel):
        animal: AnimalStr
        fruit: FruitStr

    me = MyClass(animal="bird-of-prey", fruit="apple")
    assert me.animal == "Eagle"
    assert me.fruit == "Apple"

    try:
        me = MyClass(animal="apple", fruit="dog")
    except KeyError as e:
        assert str(e) == "'Key not found: apple'"
