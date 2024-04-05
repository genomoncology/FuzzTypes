from fuzzterms import loader


def test_from_csv(data_path):
    entities = list(loader.from_file(data_path / "emojis.csv"))
    assert len(entities) == 4
    assert entities[0] == {
        "name": "happy",
        "aliases": ["😀"],
        "priority": "1",
    }


def test_from_tsv(data_path):
    entities = list(loader.from_file(data_path / "myths.tsv"))
    assert len(entities) == 5
    assert entities[2] == {
        "name": "Zeus",
        "aliases": ["Jupiter", "Jove"],
        "meta": {
            "dominion": "Power",
        },
    }


def test_from_txt(data_path):
    entities = list(loader.from_file(data_path / "emotions.txt"))
    assert len(entities) == 12
    assert entities[-1] == {
        "name": "Serenity",
    }


def test_from_jsonl(data_path):
    entities = list(loader.from_file(data_path / "mixed.jsonl"))
    assert len(entities) == 6
    assert entities[0] == {
        "name": "Dog",
        "aliases": ["Canine", "Hound"],
        "label": "animal",
    }
