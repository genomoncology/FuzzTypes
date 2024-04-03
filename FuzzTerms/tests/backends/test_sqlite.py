from pytest import fixture
from fuzzterms import Collection, Database
from fuzzterms.databases import SQLiteDatabase


@fixture(scope="session")
def database(collection: Collection):
    database = Database.construct(collection)

    with database.acquire() as conn:
        c = conn.cursor()
        c.execute("SELECT 1")
        assert c.fetchone() == (1,)

    # initialize database
    database.initialize()

    return database


def test_database_initialization(database: Database):
    assert isinstance(database, SQLiteDatabase)

    with database.acquire() as conn:
        c = conn.cursor()
        c.execute("SELECT 1")
        assert c.fetchone() == (1,)
