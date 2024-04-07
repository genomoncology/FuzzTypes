from pathlib import Path
from tempfile import TemporaryDirectory

from click.testing import CliRunner
from pytest import fixture

from fuzzterms import Admin, Collection, cli


@fixture(scope="session")
def data_path() -> Path:
    return Path(__file__).parent / "data"


@fixture(scope="session", params=["sqlite", "lancedb"])
def collection(request, data_path):
    with TemporaryDirectory(ignore_cleanup_errors=True) as dir_name:
        # initialize collection in temp directory using db_backend
        args = ["--path", dir_name, "init", f"db_backend={request.param}"]
        CliRunner().invoke(cli.app, args)

        # confirm db_backend set correctly
        collection = Collection.load(Path(dir_name))
        assert collection.config.db_backend == request.param

        # load myths.tsv file
        myths_tsv = str(data_path / "myths.tsv")
        CliRunner().invoke(cli.app, ["--path", dir_name, "load", myths_tsv])

        yield collection
