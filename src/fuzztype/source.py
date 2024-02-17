from pathlib import Path
from typing import List, Union

from pydantic import TypeAdapter

from . import Entity, Registry

SourceType = Union[List[Entity], List[str], str, Path]
EntityAdapter = TypeAdapter(Union[Entity, List[str]])


def load_source(source: SourceType) -> set[str]:
    if isinstance(source, Path):
        source = source.open("r").read()

    if isinstance(source, str):
        entities = EntityAdapter.validate_json(source)
    else:
        entities = source

    entities = map(Entity.convert, entities)
    labels = Registry.update(entities)
    return labels
