from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from pytest import fixture

from fuzzterms import Collection


@fixture(scope="session")
def collection() -> Collection:
    # create temporary project
    path = Path(mkdtemp())
    collection = Collection.load(path=path)

    # default == alias ok
    assert collection.config.search_type_default_flag.is_alias
    assert collection.config.vss_enabled
    yield collection

    # delete temporary project
    rmtree(path)
