from typing import Callable

from fuzztypes import Function

_tx = None


def get_tx() -> Callable:  # pragma: no cover
    global _tx

    if _tx is None:
        try:
            # Note: unidecode is a GPL licensed optional dependency.
            # You must import it yourself to use this functionality.
            # https://github.com/avian2/unidecode

            # noinspection PyUnresolvedReferences
            from unidecode import unidecode

            _tx = unidecode

        except ImportError:
            pass

    if _tx is None:
        try:
            # Note: anyascii is an ISC licensed optional dependency.
            # You must import it yourself to use this functionality.
            # https://github.com/anyascii/anyascii

            # noinspection PyUnresolvedReferences
            from anyascii import anyascii

            _tx = anyascii

        except ImportError:
            msg = "Failed: `pip install ascii` or `pip install unidecode`"
            raise RuntimeError(msg)

    return _tx


def to_ascii(key: str) -> str:
    f = _tx or get_tx()
    return f(key)


ASCII = Function(to_ascii)
