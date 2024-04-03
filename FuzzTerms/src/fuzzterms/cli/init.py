import click

from fuzzterms import Collection
from fuzzterms.cli import app


@app.command()
@click.pass_context
def init(ctx):
    """Initialize a new collection."""
    collection: Collection = ctx.obj["collection"]

    if collection.config_path.exists():
        click.echo(f"Project already exists: {collection.path}")
    else:
        collection.save()
        click.echo(f"Initialized collection: {collection.path}")

    click.echo("Done.")
