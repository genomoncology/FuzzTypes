import click

from fuzzterms import Admin, Collection
from fuzzterms.cli import app


@app.command()
@click.argument("params", nargs=-1)
@click.pass_context
def init(ctx, params):
    """Initialize a new collection."""
    collection: Collection = ctx.obj["collection"]
    admin: Admin = Admin(collection)
    kw = dict([param.split("=", maxsplit=1) for param in params])
    admin.initialize(**kw)
    click.echo(f"Collection initialized: {collection.path}")
