from typing import Type, TypeVar, Any, get_args

from . import FuzzValidator

T = TypeVar("T")


def LiteralValidator(literal: Type[T]) -> Any:
    values = get_args(literal)
    mapping = {str(v).lower(): v for v in values}

    def do_lookup(q: str) -> Any:
        val = mapping.get(q.lower())
        return val

    return FuzzValidator(do_lookup)
