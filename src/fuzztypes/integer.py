from typing import Callable, Union

from fuzztypes import FunctionStr

_tx = None


def get_tx() -> Callable:
    global _tx

    if _tx is None:
        try:
            # Note: number-parser is a BSD-3 licensed optional dependency.
            # You must import it yourself to use this functionality.
            # https://github.com/scrapinghub/number-parser

            # using parse_ordinal since it handles both: three and third
            # noinspection PyUnresolvedReferences
            from number_parser import parse_ordinal

            _tx = parse_ordinal

        except ImportError:
            pass

    return _tx


def to_int(key: Union[int, str]) -> int:
    if isinstance(key, int):
        val = key
    else:
        f = _tx or get_tx()
        val = f(key)
    return val


Integer = FunctionStr(to_int, python_type=int)