from fuzzterms import Entity


def test_meta():
    entity = Entity(name="a", meta=dict(b=1, c=None), priority=10)
    assert entity.name == "a"
    assert entity.b == 1
    assert entity.c is None
    assert entity.priority == 10
    assert entity.model_dump(by_alias=True) == {
        "name": "a",
        "label": None,
        "aliases": [],
        "meta": {"b": 1, "c": None},
        "priority": 10,
    }


def test_meta_edge_cases():
    entity = Entity(name="a")

    try:
        assert entity.unknown
        assert False, "Did not throw AttributeError exception."

    except AttributeError:
        pass

    entity.unknown = 123
    assert entity.unknown == 123

    assert entity.label is None
    entity.label = "LABEL"
    assert entity.label == "LABEL"
