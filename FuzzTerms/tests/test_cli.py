from pathlib import Path
from tempfile import mkdtemp
from shutil import rmtree
from click.testing import CliRunner

from fuzzterms import Collection
from fuzzterms.cli import app

runner = CliRunner()


def run_command(home, name, command, *args):
    assert command in {
        "init",
    }
    basic_args = ["--home", home, "--name", name, command]
    # noinspection PyTypeChecker
    result = runner.invoke(app, basic_args + list(args))
    if result.exit_code != 0:
        raise RuntimeError(f"Config failed:\n{result.output}")


def test_cli_init():
    home = mkdtemp()
    name = "test_cli_init_collection"
    path = Path(home) / name
    assert not path.exists()
    run_command(home, name, "init")
    assert Collection.load(path).config.model_dump(exclude_defaults=True) == {}
    rmtree(home)
