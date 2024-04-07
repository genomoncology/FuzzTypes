from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from pytest import fixture

from fuzzterms import Admin, Collection, loader, Searcher


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
    rmtree(path, ignore_errors=True)


@fixture(scope="session")
def admin(collection: Collection) -> Admin:
    admin = Admin(collection, batch_size=2)
    admin.initialize()
    return admin


@fixture(scope="session")
def searcher(collection: Collection, admin: Admin) -> Searcher:
    assert admin is not None, "Needed for initialization"
    return Searcher(collection)


@fixture(scope="session")
def load_myths(admin, data_path):
    entities = loader.from_file(data_path / "myths.tsv")
    count = admin.upsert(entities)
    return count
