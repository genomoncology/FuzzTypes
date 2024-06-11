from typing import Callable, Literal, Optional, Union

from vokab import Collection, Row, const

from . import FuzzValidator

CollectionConstructor = Callable[[], Collection]
Selection = Literal["exact", "first"]
IfMissing = Literal["pass_through", "raise_exception", "return_none"]


def VocabularyValidator(
    collection: Union[Collection, CollectionConstructor],
    preprocess: Optional[Callable[[str], str]] = None,
    label: Optional[str] = None,
    num_candidates: int = 10,
    search_type: const.SearchType = "best",
    selection: Selection = "first",
    if_missing: IfMissing = "return_none",
):
    collection_obj: Optional[Collection] = None

    def do_lookup(q: str) -> Optional[str]:
        nonlocal collection, collection_obj, label, preprocess

        if collection_obj is None:
            if isinstance(collection, Collection):
                collection_obj = collection
            elif callable(collection):
                collection_obj = collection()
            else:
                collection_obj = Collection.load()

        # preprocess the query string before searching
        search_q = preprocess(q) if preprocess else q

        # perform search query
        response = collection_obj.search(
            q=search_q,
            label=label,
            search_type=search_type,
            limit=num_candidates,
        )

        row: Row = getattr(response, selection)

        output: Optional[str] = None

        if not row:

            if if_missing == "raise_exception":
                msg = f"No match found for {q}"
                if response.rows:
                    closest = [f'"{r.name}"' for r in response.rows[:3]]
                    msg += f" (did you mean: {', '.join(closest)})"
                raise ValueError(msg)

            elif if_missing == "return_none":
                output = None

            elif if_missing == "pass_through":
                output = q

        else:
            output = row.name

        return output

    return FuzzValidator(do_lookup)
