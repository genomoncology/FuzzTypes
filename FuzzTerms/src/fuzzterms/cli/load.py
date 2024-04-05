import click
from pathlib import Path
from tqdm import tqdm

from fuzzterms import Collection, loader, Admin
from fuzzterms.cli import app


@app.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--mv-splitter",
    default="|",
    help="Multi-value splitter used for parsing aliases (default: '|')",
)
@click.pass_context
def load(ctx, filename, mv_splitter):
    """Load entities from a file."""
    collection: Collection = ctx.obj["collection"]
    admin: Admin = Admin(collection)

    path = Path(filename)
    with path.open() as file:
        total_lines = sum(1 for _ in file)

    source = loader.from_file(path, mv_splitter=mv_splitter)
    with tqdm(source, total=total_lines, unit="entities") as progress:
        count = admin.upsert(progress)

    click.echo(f"Loaded {count} entities from {path}")
