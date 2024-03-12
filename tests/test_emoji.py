from fuzztypes import Emoji


def test_key_access():
    assert Emoji("balloon") == "🎈"
    assert Emoji(":atm_sign:") == "🏧"
    assert Emoji("atm sign") == "🏧"
    assert Emoji("atm") == "🏧"
    assert Emoji("United States") == "🇺🇸"
