from pathlib import Path
from typing import Callable, Optional, Union

from . import FuzzValidator, const, lazy


def VocabularyValidator(
    collection: Optional[Union[str, Path, object]] = None,
    label: Optional[str] = None,
    examples: Optional[list] = None,
    preprocess: Callable = None,
):
    # set to default path if None
    collection = collection or const.FUZZTYPES_VOCAB_COLLECTION

    # load collection if path or str provided
    if isinstance(collection, (Path, str)):
        Collection = lazy.lazy_import("vokab", "Collection")
        collection = Collection.load(collection)

    def do_lookup(key: str) -> str:
        if preprocess:
            key = preprocess(key)

        response = collection(q=key, labels=[label])

        return response.match.name if response and response.match else key

    return FuzzValidator(do_lookup, examples=examples)

