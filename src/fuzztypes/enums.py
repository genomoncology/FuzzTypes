from enum import Enum
from typing import Any, Optional, Type, TypeVar

from . import FuzzValidator

E = TypeVar("E", bound=Enum)


def EnumValidator(enum_cls: Type[E]):

    mapping: dict[str, E] = {}

    for member in enum_cls.__members__.values():
        mapping[str(member.name).lower()] = member
        mapping[str(member.value).lower()] = member

    def do_lookup(q: str) -> Any:
        val: Optional[E] = mapping.get(q.lower())
        return val.value if val else None

    return FuzzValidator(do_lookup)
