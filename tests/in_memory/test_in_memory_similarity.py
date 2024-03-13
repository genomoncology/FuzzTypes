import pytest

from fuzztypes import flags
from fuzztypes.in_memory import InMemoryStorage
from fuzztypes.lazy import create_reranker


@pytest.fixture(scope="session")
def EmotionMemoryStorage(EmotionSource):
    storage = InMemoryStorage(EmotionSource, search_flag=flags.SemanticSearch)
    storage.prepare()
    return storage


def test_check_storage_directly(EmotionMemoryStorage):
    matches = EmotionMemoryStorage.get("happiness")
    assert len(matches) == 1
    assert matches[0].entity.value == "Happiness"
    assert matches[0].score == 100.0

    matches = EmotionMemoryStorage.get("scared")
    assert len(matches) == 10
    assert matches[0].entity.value == "Fear"
    assert matches[0].score == pytest.approx(91.23)


def test_reranker_directly_1(EmotionMemoryStorage):
    ranker = create_reranker("mixedbread-ai/mxbai-rerank-xsmall-v1")
    documents = EmotionMemoryStorage._terms

    results = ranker("afraid", documents, 3)
    assert len(results) == 3
    assert results[0]["text"] == "fear"
    assert results[0]["score"] >= 0.3


def test_reranker_directly_2(EmotionMemoryStorage):
    ranker = create_reranker("mixedbread-ai/mxbai-rerank-xsmall-v1")
    documents = EmotionMemoryStorage._terms

    results = ranker("joyous", sorted(documents), 3)
    assert len(results) == 3
    assert results[0]["text"] in ("happiness", "joy")
    assert results[0]["score"] >= 0.3
