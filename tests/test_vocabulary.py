from typing import Annotated
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from vokab import Collection, config, etl
from fuzztypes import VocabularyValidator, validate_python


@pytest.fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def collection(data_path):
    with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
        myths_tsv = str(data_path / "myths.tsv")

        collection = Collection(
            path=Path(dir_name),
            config=config.Config(
                database=config.DatabaseConfig(
                    type="lancedb",
                    url=None,
                )
            ),
        )

        collection.initialize()
        count = etl.load(collection, myths_tsv)
        assert count == 10
        yield collection


def test_vocabulary_validator(collection):
    Myth = Annotated[str, VocabularyValidator(collection)]
    Deity = Annotated[str, VocabularyValidator(collection, label="DEITY")]

    assert validate_python(Myth, "Zeus") == "Zeus"
    assert validate_python(Myth, "jove") == "Zeus"
    assert validate_python(Myth, "Madusa") == "Medusa"

    assert validate_python(Deity, "Jove") == "Zeus"

    # todo: minimum similarity needed
    assert validate_python(Deity, "Madusa") != "Medusa"

