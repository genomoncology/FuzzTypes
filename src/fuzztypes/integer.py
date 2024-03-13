from typing import Callable, Union

from fuzztypes import Function, lazy

_tx = None


def get_tx() -> Callable:
    global _tx

    if _tx is None:
        _tx = lazy.lazy_import("number_parser", "parse_ordinal")

    return _tx


def to_int(key: Union[int, str]) -> int:
    if isinstance(key, int):
        val = key
    else:
        f = _tx or get_tx()
        val = f(key)
    return val


Integer = Function(to_int, input_type=int)
