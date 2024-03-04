from pydantic import BaseModel, ValidationError
from fuzztypes import Vibemoji


class MyModel(BaseModel):
    emoji: Vibemoji


def test_vibemoji_model():
    assert MyModel(emoji="bacon tastes good").emoji == "🥓"


def test_vibemoji_get_value():
    assert Vibemoji.get_value("bacon tastes good") == "🥓"
    assert Vibemoji.get_value("take the bus to school") == "🚌"
    assert Vibemoji.get_value("software developer") == "🧑‍💻"
    assert Vibemoji.get_value("jolly santa") == "🎅"
    assert Vibemoji.get_value("st. nick") == "🇲🇫"  # can't win them all!
