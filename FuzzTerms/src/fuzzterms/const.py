import os
import pathlib
from typing import Literal, get_args

# Home directory of fuzzterms library.
FuzzTermsHome = os.environ.get("FUZZTERMS_HOME") or "~/.local/fuzzterms/"
FuzzTermsHome = os.path.expanduser(FuzzTermsHome)

# Search types available for a given project
# See flag.py for mappings
SearchType = Literal["name", "alias", "fuzz", "semantic", "hybrid"]
SearchChoices = get_args(SearchType)


# Device to use for generating semantic embeddings
# https://www.sbert.net/examples/applications/computing-embeddings/README.html
DeviceType = Literal["cpu", "cuda", "mps", "npu"]
DeviceChoices = get_args(DeviceType)


def make_project_path(home: str, name: str):
    name = name or os.environ.get("FUZZTERMS_NAME")
    if name:
        home = home or os.environ.get("FUZZTERMS_HOME") or "~/.local/fuzzterms"
        home = os.path.expanduser(home)
        return pathlib.Path(home) / name
