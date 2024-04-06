import os
from pathlib import Path

import click

from fuzzterms import Collection


@click.group()
@click.option(
    "--path",
    "-p",
    type=click.Path(),
    help="Path to FuzzTerms collection.",
)
@click.pass_context
def app(ctx, path: str):
    ctx.ensure_object(dict)
    path = path or os.environ.get("FUZZTERMS_HOME") or "~/.local/fuzzterms/"
    path = Path(os.path.expanduser(path))

    if path is None:
        msg = "You must specify a project name (--name or FUZZTERMS_NAME)."
        raise click.UsageError(msg)

    ctx.obj["collection"] = Collection.load(path)
