import click

from fuzzterms import Admin, Collection
from fuzzterms.cli import app


@app.command()
@click.pass_context
def init(ctx):
    """Initialize a new collection."""
    collection: Collection = ctx.obj["collection"]
    admin: Admin = Admin(collection)
    admin.initialize()
    click.echo(f"Collection initialized: {collection.path}")
