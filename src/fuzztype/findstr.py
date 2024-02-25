from typing import Callable, Union

from . import FuzzType, LookupReturn, Entity


def FindStr(
    source: Callable[[str], Union[str, LookupReturn]], examples: list = None
):
    def do_lookup(key: str) -> LookupReturn:
        response = source(key)
        if isinstance(response, str):
            response = Entity(name=response)
        return response

    return FuzzType(lookup_function=do_lookup, examples=examples)
