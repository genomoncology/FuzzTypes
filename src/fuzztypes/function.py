from typing import Callable, Type, Optional, TypeVar

from . import Entity, MatchResult, const, abstract


T = TypeVar("T", bound=abstract.SupportedType)


def Function(
    source: Callable[[T], abstract.SupportedType],
    examples: Optional[list] = None,
    notfound_mode: const.NotFoundMode = "raise",
    input_type: Type[abstract.SupportedType] = str,
    output_type: Optional[Type[abstract.SupportedType]] = None,
    validator_mode: const.ValidatorMode = "before",
):
    def do_lookup(key: T) -> MatchResult:
        value = source(key)
        match_list = MatchResult()
        if value is not None:
            entity = Entity(value=value)
            match_list.set(key=key, entity=entity)
        return match_list

    return abstract.AbstractType(
        do_lookup,
        examples=examples,
        input_type=input_type,
        output_type=output_type,
        notfound_mode=notfound_mode,
        validator_mode=validator_mode,
    )
