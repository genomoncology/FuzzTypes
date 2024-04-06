from typing import Literal, get_args

# Search types available for a given project
# See flag.py for mappings
SearchType = Literal["name", "alias", "fuzz", "semantic", "hybrid"]
SearchChoices = get_args(SearchType)


# Device to use for generating semantic embeddings
# https://www.sbert.net/examples/applications/computing-embeddings/README.html
DeviceType = Literal["cpu", "cuda", "mps", "npu"]
DeviceChoices = get_args(DeviceType)
