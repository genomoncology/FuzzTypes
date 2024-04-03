from pytest import fixture
from fuzzterms import Collection, Database
from fuzzterms.backends.sqlite import SQLiteDatabase


@fixture(scope="session")
def database(collection: Collection):
    return Database.construct(collection)


def test_acquire_connection(database: Database):
    assert isinstance(database, SQLiteDatabase)

    with database.acquire() as conn:
        c = conn.cursor()
        c.execute("SELECT 1")
        assert c.fetchone() == (1,)
