import functools
import importlib
import os
from typing import Any, List, TypedDict, Callable

from fuzztypes import const


@functools.lru_cache(maxsize=None)
def lazy_import(
    library_name: str,
    attr_name: str = None,
    return_none_on_error: bool = False,
) -> Any:
    """
    Lazily import a library or a specific attribute from a library.

    Args:
        library_name (str): The name of the library to import.
        attr_name (str, optional): Library attribute to import from library.
        return_none_on_error (bool, optional): Whether to return None if an
            import error occurs. Default is False, which raises an ImportError.

    Returns:
        The imported library or attribute, or None if an import error occurs
        and return_none_on_error is True.

    Raises:
        ImportError: If the library or attribute is not found and
        return_none_on_error is False.
    """
    info = _lib_info.get(library_name, {})

    module_name = info.get("module_name", library_name)
    install_name = info.get("install_name", library_name)
    purpose = info.get("purpose", "")
    license_type = info.get("license", "")
    url = info.get("url", "")
    version = info.get("version", "")

    try:
        module = importlib.import_module(module_name)
        if attr_name:
            return getattr(module, attr_name)
        return module
    except ImportError as e:
        version_info = f"(version {version})" if version else ""
        install = f"`pip install {install_name}{version_info}`"
        details = list(filter(None, [purpose, url, license_type]))
        if details:
            details = ", ".join(details)
            details = f" ({details})"
        msg = f"Import Failed: {install}{details}"

        if not info:
            additional_msg = (
                f"\nPlease add the library '{library_name}' to "
                f"the '_lib_info' dictionary in the 'lazy' "
                f"module."
            )
            msg += additional_msg

        if return_none_on_error:
            return None
        else:
            raise ImportError(msg) from e


@functools.lru_cache(maxsize=None)
def create_encoder(model_or_model_name: str, device: const.DeviceList):
    def get_encoder():
        nonlocal model_or_model_name

        if model_or_model_name is None:
            model_or_model_name = const.DefaultEncoder

        if isinstance(model_or_model_name, str):
            sbert = lazy_import("sentence_transformers")
            local_path = os.path.join(const.ModelsPath, model_or_model_name)

            if not os.path.exists(local_path):  # pragma: no cover
                encoder = sbert.SentenceTransformer(
                    model_or_model_name, device=device
                )
                encoder.save(local_path)
            else:
                encoder = sbert.SentenceTransformer(local_path)

            model_or_model_name = encoder

        return model_or_model_name

    def encode(texts: List[str]) -> List:
        return get_encoder().encode(texts, device=device)

    return encode


class RankResult(TypedDict):
    text: str
    score: float
    corpus_id: int


def create_reranker(
    model_name: str,
) -> Callable[[str, List[str], int], List[RankResult]]:
    """
    Creates a reranker function using the specified sentence transformer model.

    :param model_name: Name of the CrossEncoder model
                       (e.g. "mixedbread-ai/mxbai-rerank-xsmall-v1")

    :return: rerank function Callable
    """

    def get_reranker():
        sbert = lazy_import("sentence_transformers")
        local_path = os.path.join(const.ModelsPath, model_name)

        if not os.path.exists(local_path):  # pragma: no cover
            reranker = sbert.CrossEncoder(model_name)
            reranker.save(local_path)
        else:
            reranker = sbert.CrossEncoder(local_path)

        return reranker

    def rerank(
        query: str,
        documents: List[str],
        top_k: int = 3,
    ) -> List[RankResult]:
        reranker = get_reranker()
        results: List[RankResult] = reranker.rank(
            query, documents, return_documents=True, top_k=top_k
        )
        return results

    return rerank


_lib_info = {
    "sentence-transformers": {
        "module_name": "sentence_transformers",
        "install_name": "sentence-transformers",
        "purpose": "Encoding sentences into high-dimensional vectors",
        "license": "Apache 2.0",
        "url": "https://github.com/UKPLab/sentence-transformers",
    },
    "unidecode": {
        "module_name": "unidecode",
        "install_name": "Unidecode",
        "purpose": "Converting Unicode text into ASCII equivalents",
        "license": "GPL",
        "url": "https://github.com/avian2/unidecode",
    },
    "anyascii": {
        "module_name": "anyascii",
        "install_name": "anyascii",
        "purpose": "Converting Unicode text into ASCII equivalents",
        "license": "ISC",
        "url": "https://github.com/anyascii/anyascii",
    },
    "rapidfuzz": {
        "module_name": "rapidfuzz",
        "install_name": "rapidfuzz",
        "purpose": "Performing fuzzy string matching",
        "license": "MIT",
        "url": "https://github.com/maxbachmann/RapidFuzz",
    },
    "dateparser": {
        "module_name": "dateparser",
        "install_name": "dateparser",
        "purpose": "Parsing dates from strings",
        "license": "BSD-3-Clause",
        "url": "https://github.com/scrapinghub/dateparser",
    },
    "emoji": {
        "module_name": "emoji",
        "install_name": "emoji",
        "purpose": "Handling and manipulating emoji characters",
        "license": "BSD",
        "url": "https://github.com/carpedm20/emoji",
    },
    "nameparser": {
        "module_name": "nameparser",
        "install_name": "nameparser",
        "purpose": "Parsing person names",
        "license": "LGPL",
        "url": "https://github.com/derek73/python-nameparser",
    },
    "number-parser": {
        "module_name": "number_parser",
        "install_name": "number-parser",
        "purpose": "Parsing numbers from strings",
        "license": "BSD-3-Clause",
        "url": "https://github.com/scrapinghub/number-parser",
    },
    "pycountry": {
        "module_name": "pycountry",
        "install_name": "pycountry",
        "purpose": "Provides ISO country, subdivision, language, and currency",
        "license": "LGPL 2.1",
        "url": "https://github.com/flyingcircusio/pycountry",
    },
    "lancedb": {
        "module_name": "lancedb",
        "install_name": "lancedb",
        "purpose": "High-performance, on-disk vector database",
        "license": "Apache 2.0",
        "url": "https://github.com/lancedb/lancedb",
    },
    "numpy": {
        "module_name": "numpy",
        "install_name": "numpy",
        "purpose": "Numerical computing in Python",
        "license": "BSD",
        "url": "https://numpy.org/",
    },
    "sklearn": {
        "module_name": "sklearn",
        "install_name": "scikit-learn",
        "purpose": "Machine learning in Python",
        "license": "BSD",
        "url": "https://scikit-learn.org/",
    },
}
