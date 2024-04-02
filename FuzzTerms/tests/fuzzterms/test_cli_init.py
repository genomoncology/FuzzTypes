from pathlib import Path
from tempfile import mkdtemp
from shutil import rmtree
from click.testing import CliRunner

from fuzzterms import Project, flags
from fuzzterms.cli import app

runner = CliRunner()


def run_config(home, name, *args):
    basic_args = ["--home", home, "--name", name, "config"]
    # noinspection PyTypeChecker
    result = runner.invoke(app, basic_args + list(args))
    if result.exit_code != 0:
        raise RuntimeError(f"Config failed:\n{result.output}")


# noinspection PyTypeChecker
def test_cli_config():
    home = mkdtemp()
    name = "my_cli_init_test_project"
    path = Path(home) / name
    assert not path.exists()

    # run initialization with defaults
    run_config(home, name)
    assert Project.load(path).config.model_dump(exclude_defaults=True) == {}

    run_config(home, name, "--search", "name", "--device", "cuda")
    assert Project.load(path).config.model_dump(exclude_defaults=True) == {
        "device": "cuda",
        "search": "name",
    }
    run_config(home, name, "--encoder", "my-org/my-model", "--search", "fuzz")
    assert Project.load(path).config.model_dump(exclude_defaults=True) == {
        "device": "cuda",
        "encoder": "my-org/my-model",
        "search": "fuzz",
    }

    rmtree(home)
