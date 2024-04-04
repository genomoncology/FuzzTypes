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
    # path = Path(mkdtemp())
    path = Path("/tmp/test/")
    rmtree(path, ignore_errors=True)
    collection = Collection.load(path=path)

    # default == alias ok
    assert collection.config.search_flag.is_alias
    assert collection.config.vss_enabled
    yield collection

    # delete temporary project
    # rmtree(path)


@fixture(scope="session")
def admin(collection: Collection) -> Admin:
    admin = Admin(collection)
    admin.initialize()
    return admin


@fixture(scope="session")
def searcher(collection: Collection, admin: Admin) -> Searcher:
    assert admin is not None, "Needed for initialization"
    return Searcher(collection)


@fixture(scope="session")
def entities(admin, data_path):
    entities = loader.from_file(data_path / "myths.tsv")
    assert len(entities) == 5

    assert admin.stats().model_dump() == {
        "entities": 0,
        "terms": 0,
    }

    count = admin.upsert(entities)
    assert count == 5
    return entities
