from pathlib import Path

from pytest import fixture

from fuzztypes import EntitySource, NamedEntity


@fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent / "data"


@fixture(scope="session")
def EmojiSource(data_path):
    source = EntitySource(data_path / "emojis.csv")
    assert len(source) == 4
    return source


@fixture(scope="session")
def FruitSource(data_path):
    # loading separately from AnimalSource to test lazy loading
    MixedSource = EntitySource(data_path / "mixed.jsonl")
    assert MixedSource.loaded is False

    FruitSource = MixedSource["fruit"]
    assert isinstance(FruitSource, EntitySource)
    assert FruitSource.loaded is False

    # first access loads FruitSource -> MixedSource
    assert isinstance(FruitSource[0], NamedEntity)
    assert FruitSource[0].value == "Apple"
    assert FruitSource.loaded is True
    assert MixedSource.loaded is True
    assert len(FruitSource) == 3

    return FruitSource


@fixture(scope="session")
def AnimalSource(data_path):
    MixedSource = EntitySource(data_path / "mixed.jsonl")
    return MixedSource["animal"]


@fixture(scope="session")
def MythSource(data_path):
    source = EntitySource(data_path / "myths.tsv")
    assert len(source) == 5
    return source


@fixture(scope="session")
def EmotionSource(data_path):
    source = EntitySource(data_path / "emotions.txt")
    assert len(source) == 12
    return source
