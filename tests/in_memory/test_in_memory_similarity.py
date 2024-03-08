import pytest

from fuzztypes import flags
from fuzztypes.in_memory import InMemoryStorage

emotions = [
    "Happiness",
    "Sadness",
    "Anger",
    "Fear",
    "Surprise",
    "Disgust",
    "Trust",
    "Anticipation",
    "Love",
    "Joy",
    "Courage",
    "Serenity",
]

storage = InMemoryStorage(emotions, search_flag=flags.SemanticSearch)


def test_check_storage_directly():
    storage.prepare()

    matches = storage.get("happiness")
    assert len(matches) == 1
    assert matches[0].entity.value == "Happiness"
    assert matches[0].score == 100.0

    matches = storage.get("scared")
    assert len(matches) == 10
    assert matches[0].entity.value == "Fear"
    assert matches[0].score == pytest.approx(91.23)
