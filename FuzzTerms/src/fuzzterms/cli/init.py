import click

from fuzzterms import Admin, Collection
from fuzzterms.cli import app


@app.command()
@click.argument("db_backend", type=str)
@click.pass_context
def init(ctx, db_backend: str):
    """Initialize a new collection."""
    collection: Collection = ctx.obj["collection"]
    admin: Admin = Admin(collection)
    admin.initialize(db_backend=db_backend)
    click.echo(f"Collection initialized: {collection.path}")
