from fuzztypes import Emoji, emojis, validate_python


def test_key_access():
    assert validate_python(Emoji, "balloon") == "🎈"
    assert validate_python(Emoji, ":atm_sign:") == "🏧"
    assert validate_python(Emoji, "atm sign") == "🏧"
    assert validate_python(Emoji, "atm") == "🏧"
    assert validate_python(Emoji, "United States") == "🇺🇸"


def test_load_emojis():
    entities = emojis.load_emoji_entities()
    assert len(entities) > 2000
    assert entities[0].value == "🥇"
    assert set(entities[0].aliases) == {"1st place medal", ":1st_place_medal:"}
