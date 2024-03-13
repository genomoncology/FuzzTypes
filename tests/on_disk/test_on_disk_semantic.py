import pytest
from pydantic import BaseModel

from fuzztypes import flags, on_disk, Vibemoji


@pytest.fixture(scope="session")
def EmotionOnDiskStorage(EmotionSource):
    storage = on_disk.OnDiskStorage(
        "Emotions", EmotionSource, search_flag=flags.SemanticSearch
    )
    storage.prepare(force_drop_table=True)
    return storage


def test_check_storage_directly(EmotionOnDiskStorage):
    matches = EmotionOnDiskStorage.get("happiness")
    assert len(matches) == 1
    assert matches[0].entity.value == "Happiness"
    assert matches[0].score == 100.0

    matches = EmotionOnDiskStorage.get("scared")
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
