from pydantic import BaseModel, BeforeValidator, TypeAdapter
from typing import Annotated

from fuzztypes.ascii import to_ascii
from fuzztypes.in_memory import InMemory


def test_ascii():
    ASCII = Annotated[str, BeforeValidator(to_ascii)]

    assert TypeAdapter(ASCII).validate_python("άνθρωποι") == "anthropoi"

    class MyModel(BaseModel):
        ascii: ASCII

    assert MyModel(ascii="άνθρωποι").ascii == "anthropoi"
    assert MyModel(ascii=123).ascii == "123"


def test_in_memory(MythSource):
    Myth = Annotated[str, InMemory(MythSource)]
    assert TypeAdapter(Myth).validate_python("zeus") == "Zeus"

    class MyModel(BaseModel):
        myth: Myth

    assert MyModel(myth="jove").myth == "Zeus"
