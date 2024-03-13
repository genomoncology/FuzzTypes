from typing import Callable

from fuzztypes import Function, lazy

_tx = None


def get_tx() -> Callable:  # pragma: no cover
    global _tx

    if _tx is None:
        _tx = lazy.lazy_import(
            "unidecode",
            "unidecode",
            return_none_on_error=True,
        )
        _tx = _tx or lazy.lazy_import(
            "anyascii",
            "anyascii",
            return_none_on_error=True,
        )

    if _tx is None:
        msg = "Failed: `pip install ascii` or `pip install unidecode`"
        raise RuntimeError(msg)

    return _tx


def to_ascii(key: str) -> str:
    f = _tx or get_tx()
    return f(key)


ASCII = Function(to_ascii)
