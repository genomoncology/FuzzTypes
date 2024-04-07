from pathlib import Path
from tempfile import mkdtemp
from shutil import rmtree
from click.testing import CliRunner

from fuzzterms import Collection
from fuzzterms.cli import app

runner = CliRunner()


def run_command(path, command, *args):
    assert command in {"init"}
    basic_args = ["--path", str(path), command]
    result = runner.invoke(app, basic_args + list(args))
    if result.exit_code != 0:
        raise RuntimeError(f"Config failed:\n{result.output}")


def test_cli_init():
    path = Path(mkdtemp())
    run_command(path, "init", "sqlite")
    assert Collection.load(path).config.model_dump(exclude_defaults=True) == {}
    rmtree(path)
