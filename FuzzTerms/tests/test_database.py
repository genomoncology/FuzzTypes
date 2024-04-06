from fuzzterms.databases import SQLiteDatabase, LanceDBDatabase


def test_database_initialization(collection):
    assert isinstance(collection.database, (SQLiteDatabase, LanceDBDatabase))

    if isinstance(collection.database, SQLiteDatabase):
        with collection.database.acquire() as conn:
            c = conn.cursor()
            c.execute("SELECT 1 as num")
            row = c.fetchone()
            assert row.keys() == ["num"]
            assert row["num"] == 1
            assert dict(row) == {"num": 1}
