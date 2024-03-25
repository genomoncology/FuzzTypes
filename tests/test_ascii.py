# -*- coding: utf-8 -*-

from pydantic import BaseModel, TypeAdapter

from fuzztypes import ASCII


def test_ascii_usable_type():
    ta = TypeAdapter(ASCII)
    assert ta.validate_python("άνθρωποι") == "anthropoi"


def test_transliterate_utf8_to_ascii():
    class MyModel(BaseModel):
        ascii: ASCII

    obj = MyModel(ascii="άνθρωποι")
    assert obj.ascii == "anthropoi"

    assert MyModel(ascii="kožušček").ascii == "kozuscek"
    assert (
        MyModel(ascii="30 \U0001d5c4\U0001d5c6/\U0001d5c1").ascii == "30 km/h"
    )

    # Note: unidecode and anyascii have differences in some situations
    allowed = ("kakoi-to tekst", "kakoy-to tekst")  # unidecode, anyascii
    assert MyModel(ascii="какой-то текст").ascii in allowed

    allowed = ("Bei Jing ", "BeiJing")  # unidecode, anyascii
    assert MyModel(ascii="\u5317\u4EB0").ascii in allowed
