from pathlib import Path
from typing import Iterable

from pytest import fixture

from fuzztype import EntitySource


@fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent / "data"


@fixture(scope="session")
def EmojiSource(data_path):
    source = EntitySource(data_path / "emojis.csv")
    assert len(source) == 3
    return source


@fixture(scope="session")
def MixedSource(data_path):
    source = EntitySource(data_path / "mixed.jsonl")
    assert len(source) == 6
    return source


@fixture(scope="session")
def MythSource(data_path):
    source = EntitySource(data_path / "myths.tsv")
    assert len(source) == 5
    return source
