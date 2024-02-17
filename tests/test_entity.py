from fuzztype import Entity


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
