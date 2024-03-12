import pytest

from pydantic import BaseModel

from fuzztypes import flags, on_disk, Vibemoji

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

storage = on_disk.OnDiskStorage(
    "Emotions",
    emotions,
    search_flag=flags.SemanticSearch,
)


def test_check_storage_directly():
    storage.prepare(force_drop_table=True)

    matches = storage.get("happiness")
    assert len(matches) == 1
    assert matches[0].entity.value == "Happiness"
    assert matches[0].score == 100.0

    matches = storage.get("scared")
    assert len(matches) == 10
    assert matches[0].entity.value == "Fear"
    assert matches[0].score == pytest.approx(91.23)


class MyModel(BaseModel):
    emoji: Vibemoji


def test_vibemoji_get_value():
    assert Vibemoji("bacon tastes good") == "🥓"
    assert Vibemoji("take the bus to school") == "🚌"
    assert Vibemoji("jolly santa") == "🎅"
    assert Vibemoji("st. nick") == "🇲🇫"  # can't win them all!
    assert Vibemoji("United States") == "🇺🇸"
