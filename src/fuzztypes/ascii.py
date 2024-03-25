from typing import Annotated, Any, Callable

from fuzztypes import FuzzValidator, lazy

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


def to_ascii(key: Any) -> str:
    f = _tx or get_tx()
    return f(str(key))


ASCII = Annotated[str, FuzzValidator(to_ascii)]
