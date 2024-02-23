from pathlib import Path
from typing import Iterator, Iterable

from pydantic import BaseModel, ValidationError
from pytest import fixture

from fuzztype import Entity
from fuzztype import FuzzStr, EntitySource


def test_entity_conv():
    def c(item):
        return Entity.convert(item).model_dump(exclude_defaults=True)

    assert c("A") == dict(name="A")
    assert c(("A", "B")) == dict(name="A", aliases=["B"])
    assert c(("A", ["B"])) == dict(name="A", aliases=["B"])
    assert c(("A", ["B", "C"])) == dict(name="A", aliases=["B", "C"])


def test_entity_json_schema():
    assert Entity.model_json_schema() == {
        "description": "An entity has a preferred term (name), aliases and "
        "label.",
        "properties": {
            "name": {
                "description": "Preferred term of Entity.",
                "title": "Name",
                "type": "string",
            },
            "aliases": {
                "description": "List of aliases for Entity.",
                "items": {"type": "string"},
                "title": "Aliases",
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
def MyEmojis():
    path = Path(__file__).parent / "emojis.csv"
    return EntitySource(path)


def test_csv_load(MyEmojis):
    assert isinstance(MyEmojis, EntitySource)
    assert isinstance(MyEmojis, Iterable)

    class MyClass(BaseModel):
        emoji: FuzzStr(MyEmojis)

    assert MyClass(emoji="😀").emoji == "happy"
    assert MyClass(emoji="sad").emoji == "sad"
    assert MyClass(emoji="🎉").emoji == "celebrate"


@fixture(scope="session")
def MyEntities():
    path = Path(__file__).parent / "entities.jsonl"
    return EntitySource(path)


def test_load_entities(MyEntities):
    assert len(MyEntities) == 6
    assert MyEntities[0].name == "Dog"


def test_loader_label_iterator(MyEntities):
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
    except ValidationError as e:
        assert e.errors(include_url=False) == [
            {
                "ctx": {
                    "key": "apple",
                    "nearest": "Eagle [60.0], canine => Dog [36.4], feline "
                               "=> Cat [36.4]",
                },
                "input": "apple",
                "loc": ("animal",),
                "msg": "key (apple) not resolved (nearest: Eagle [60.0], "
                       "canine => Dog [36.4], feline => Cat [36.4])",
                "type": "fuzz_str_not_resolved",
            },
            {
                "ctx": {
                    "key": "dog",
                    "nearest": "malus domestica => Apple [22.2], fragaria => "
                               "Strawberry [18.2], Apple [0.0]",
                },
                "input": "dog",
                "loc": ("fruit",),
                "msg": "key (dog) not resolved (nearest: malus domestica => "
                       "Apple [22.2], fragaria => Strawberry [18.2], Apple ["
                       "0.0])",
                "type": "fuzz_str_not_resolved",
            },
        ]
