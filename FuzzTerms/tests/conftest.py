from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from pytest import fixture

from fuzzterms import Project


@fixture(scope="session")
def alias_project() -> Project:
    # create temporary project
    path = Path(mkdtemp())
    project = Project.load(path=path)

    # default == alias ok
    assert project.config.search_flag.is_alias_ok
    yield project

    # delete temporary project
    rmtree(path)
