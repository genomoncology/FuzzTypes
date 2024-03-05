from fuzztypes import NamedEntity, InMemory


def test_entity_conv():
    def c(item):
        return NamedEntity.convert(item).model_dump(
            exclude_defaults=True, by_alias=True
        )

    assert c("A") == dict(value="A")
    assert c(("A", "B")) == dict(value="A", aliases=["B"])
    assert c(("A", ["B"])) == dict(value="A", aliases=["B"])
    assert c(("A", ["B", "C"])) == dict(value="A", aliases=["B", "C"])


def test_meta():
    entity = NamedEntity(value="a", meta=dict(b=1, c=None), priority=10)
    assert entity.value == "a"
    assert entity.b == 1
    assert entity.c is None
    assert entity.priority == 10
    assert entity.model_dump(by_alias=True) == {
        "value": "a",
        "label": None,
        "aliases": [],
        "meta": {"b": 1, "c": None},
        "priority": 10,
    }


def test_meta_edge_cases():
    entity = NamedEntity(value="a")

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


def test_csv_load(EmojiSource):
    Emoji = InMemory(EmojiSource)
    assert Emoji["happy"].value == "happy"
    assert Emoji["🎉"].value == "party"
    assert Emoji["party"].rank < Emoji["celebrate"].rank


def test_jsonl_load_animal(AnimalSource):
    assert AnimalSource[0].value == "Dog"

    AnimalStr = InMemory(AnimalSource)
    assert AnimalStr["dog"] == AnimalSource[0]
    assert AnimalStr["Bird of prey"].value == "Eagle"


def test_jsonl_label_source(FruitSource):
    FruitStr = InMemory(
        FruitSource,
        case_sensitive=True,
        notfound_mode="none",
    )
    assert FruitStr["apple"] is None
    assert FruitStr["Pome"].value == "Apple"


def test_tsv_load(MythSource):
    Myth = InMemory(MythSource)
    assert Myth["Pallas"].value == "Athena"
    assert Myth["Jupiter"].value == "Zeus"
