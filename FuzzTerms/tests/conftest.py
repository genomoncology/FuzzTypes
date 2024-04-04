from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from pytest import fixture

from fuzzterms import Admin, Collection


@fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent / "data"


@fixture(scope="session")
def collection() -> Collection:
    # create temporary project
    path = Path(mkdtemp())
    collection = Collection.load(path=path)

    # default == alias ok
    assert collection.config.search_flag.is_alias
    assert collection.config.vss_enabled
    yield collection

    # delete temporary project
    rmtree(path)


@fixture(scope="session")
def admin(collection: Collection) -> Admin:
    admin = Admin(collection)
    admin.initialize()
    return admin
