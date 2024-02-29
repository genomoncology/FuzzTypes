from typing import Callable, Union

from . import FuzzType, NamedEntity, MatchList


def FindStr(
    source: Callable[[str], Union[str, MatchList]],
    examples: list = None,
):
    def do_lookup(key: str) -> MatchList:
        response = source(key)
        if isinstance(response, str):
            entity = NamedEntity(name=response)
            response = MatchList()
            response.set(key=key, entity=entity)
        return response

    return FuzzType(do_lookup, examples=examples)
