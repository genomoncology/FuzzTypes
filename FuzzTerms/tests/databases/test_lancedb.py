from pathlib import Path
from tempfile import mkdtemp

import pytest

from fuzzterms import Admin, Collection, loader
from fuzzterms.databases.lancedb import (
    LanceDBDatabase,
    TermsTable,
    EntitiesTable,
)


@pytest.fixture(scope="session")
def collection(data_path):
    path = Path(mkdtemp())
    collection = Collection.load(path=path)
    collection.config.db_backend = "lancedb"
    Admin(collection).upsert(loader.from_file(data_path / "myths.tsv"))
    return collection


def test_database_construct(collection):
    assert isinstance(collection.database, LanceDBDatabase)
    assert isinstance(collection.database.terms, TermsTable)
    assert isinstance(collection.database.entities, EntitiesTable)


def test_entities_table(collection):
    entities: EntitiesTable = collection.database.entities
    assert entities.count() == 5


def test_terms_table(collection):
    terms: TermsTable = collection.database.terms
    assert terms.count() == 12
