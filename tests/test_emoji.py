from pydantic import BaseModel

from fuzztypes import Emoji, Vibemoji


def test_key_access():
    assert Emoji.get_value("balloon") == "🎈"
    assert Emoji.get_value(":atm_sign:") == "🏧"
    assert Emoji.get_value("atm sign") == "🏧"
    assert Emoji.get_value("atm") == "🏧"
    assert Emoji.get_value("United States") == "🇺🇸"


class MyModel(BaseModel):
    emoji: Vibemoji


def test_vibemoji_get_value():
    assert Vibemoji.get_value("bacon tastes good") in ("😋", "🥓", "🍞")
    assert Vibemoji.get_value("take the bus to school") in ("🚌", "🚍")
    assert Vibemoji.get_value("jolly santa") == "🎅"
    assert Vibemoji.get_value("st. nick") == "🇲🇫"  # can't win them all!
