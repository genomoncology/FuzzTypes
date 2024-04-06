from typing import List

from numpy import inf
from pydantic import TypeAdapter


def test_hybrid_search(searcher, load_myths):
    assert load_myths == 5
    result = searcher.search(query="Athena", limit=5)

    # assert result == [
    #     {
    #         "entity": {
    #             "aliases": [],
    #             "label": "NULL",
    #             "meta": {"dominion": "Wisdom"},
    #             "name": "Athena",
    #             "priority": 0,
    #         },
    #         "fts_distance": -inf,
    #         "fts_rank": 6,
    #         "rrf": 0.26785714285714285,
    #         "term": "Athena",
    #         "vss_distance": 0.0,
    #         "vss_rank": 1,
    #     },
    #     {
    #         "entity": {
    #             "aliases": [],
    #             "label": "NULL",
    #             "meta": {"dominion": "Power"},
    #             "name": "Zeus",
    #             "priority": 0,
    #         },
    #         "fts_distance": -inf,
    #         "fts_rank": 6,
    #         "rrf": 0.1111111111111111,
    #         "term": "Zeus",
    #         "vss_distance": 64.08448028564453,
    #         "vss_rank": 3,
    #     },
    #     {
    #         "entity": {
    #             "aliases": [],
    #             "label": "NULL",
    #             "meta": {"dominion": "Strength"},
    #             "name": "Hercules",
    #             "priority": 0,
    #         },
    #         "fts_distance": -inf,
    #         "fts_rank": 6,
    #         "rrf": 0.1,
    #         "term": "Heracles",
    #         "vss_distance": 75.92005920410156,
    #         "vss_rank": 4,
    #     },
    #     {
    #         "entity": {
    #             "aliases": [],
    #             "label": "NULL",
    #             "meta": {"dominion": "Speed"},
    #             "name": "Mercury",
    #             "priority": 0,
    #         },
    #         "fts_distance": -inf,
    #         "fts_rank": 6,
    #         "rrf": 0.09090909090909091,
    #         "term": "Hermes",
    #         "vss_distance": 83.61416625976562,
    #         "vss_rank": 5,
    #     },
    # ]

    # best = results[0]
    # assert best.pop("vector") is not None
    # assert best == {
    #     "name": "Athena",
    #     "label": "NULL",
    #     "priority": None,
    #     "meta": '{"dominion": "Wisdom"}',
    #     "aliases": '["Minerva","Pallas"]',
    #     "term": "Athena",
    #     "vss_distance": 0.0,
    #     "vss_rank": 1,
    #     "fts_distance": -2.1338763047496614,
    #     "fts_rank": 1,
    # }
    #
    # # results = searcher.hybrid_search(query="Herakles", limit=5)
    # # assert dict(results[0]) == {
    # #     "aliases": '["Heracles"]',
    # #     "fts_distance": 999999,
    # #     "fts_rank": 999999,
    # #     "label": "NULL",
    # #     "meta": '{"dominion": "Strength"}',
    # #     "name": "Hercules",
    # #     "priority": None,
    # #     "term": "Heracles",
    # #     "vss_distance": 47.091766357421875,
    # #     "vss_rank": 1,
    # # }
