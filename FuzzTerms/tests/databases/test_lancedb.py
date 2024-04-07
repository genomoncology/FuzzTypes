from pathlib import Path
from tempfile import mkdtemp

import pytest
from click.testing import CliRunner

from fuzzterms import Admin, Collection, cli
from fuzzterms.databases.lancedb import (
    LanceDBDatabase,
    TermsTable,
    EntitiesTable,
)


@pytest.fixture(scope="session")
def collection(data_path):
    path = Path(mkdtemp())
    args = ["--path", str(path)]

    CliRunner().invoke(cli.app, args + ["init", "lancedb"])

    collection = Collection.load(path)
    assert collection.config.db_backend == "lancedb"

    CliRunner().invoke(cli.app, args + ["load", str(data_path / "myths.tsv")])
    return collection


def test_database_construct(collection):
    assert isinstance(collection.database, LanceDBDatabase)
    assert isinstance(collection.database.terms, TermsTable)
    assert isinstance(collection.database.entities, EntitiesTable)
    assert Admin(collection).stats() == {
        "entities": 5,
        "terms": 12,
    }


def test_entities_table(collection):
    entities: EntitiesTable = collection.database.entities
    assert entities.count() == 5


def test_terms_table(collection):
    terms: TermsTable = collection.database.terms
    assert terms.count() == 12
