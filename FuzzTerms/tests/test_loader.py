from fuzzterms import loader


def test_from_csv(data_path):
    entities = loader.from_file(data_path / "emojis.csv")
    assert len(entities) == 4
    assert entities[0].name == "happy"
    assert entities[0].aliases == ["😀"]
    assert entities[0].priority == 1


def test_from_tsv(data_path):
    entities = loader.from_file(data_path / "myths.tsv")
    assert len(entities) == 5
    assert entities[2].name == "Zeus"
    assert entities[2].aliases == ["Jupiter", "Jove"]
    assert entities[2].priority is None


def test_from_txt(data_path):
    entities = loader.from_file(data_path / "emotions.txt")
    assert len(entities) == 12
    assert entities[-1].name == "Serenity"
    assert entities[-1].aliases == []
    assert entities[-1].priority is None


def test_from_jsonl(data_path):
    entities = loader.from_file(data_path / "mixed.jsonl")
    assert len(entities) == 6
    assert entities[0].name == "Dog"
    assert entities[0].aliases == ["Canine", "Hound"]
    assert entities[0].label == "animal"
    assert entities[0].priority is None
