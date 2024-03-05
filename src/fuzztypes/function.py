from typing import Callable, Type

from . import Entity, MatchList, const, abstract


def Function(
    source: Callable[[abstract.SupportedType], abstract.SupportedType],
    examples: list = None,
    notfound_mode: const.NotFoundMode = "raise",
    input_type: Type[abstract.SupportedType] = str,
    validator_mode: const.ValidatorMode = "before",
):
    def do_lookup(key: str) -> MatchList:
        value = source(key)
        match_list = MatchList()
        if value is not None:
            entity = Entity(value=value)
            match_list.set(key=key, entity=entity)
        return match_list

    return abstract.AbstractType(
        do_lookup,
        examples=examples,
        input_type=input_type,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )
