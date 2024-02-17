from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from . import load_source, Registry


def FuzzStr(entity_source):
    if callable(entity_source):
        lookup = entity_source
    else:
        labels = load_source(entity_source)
        assert len(labels) == 1, "Only 1 label per FuzzStr type."
        label = labels.pop()
        lookup = Registry.get_lookup(label)

    # noinspection PyUnusedLocal
    class _FuzzStr(str):
        @classmethod
        def __get_pydantic_core_schema__(
            cls,
            source_type: type,
            handler: GetCoreSchemaHandler,
        ) -> CoreSchema:
            return core_schema.with_info_before_validator_function(
                cls._validate,
                core_schema.str_schema(),
            )

        @staticmethod
        def _validate(key: str, _) -> str:
            return lookup(key)

    return _FuzzStr
