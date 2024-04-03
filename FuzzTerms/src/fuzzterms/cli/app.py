import click

from fuzzterms import Collection, const


@click.group()
@click.option(
    "--home",
    "-h",
    type=click.Path(),
    help="Path to FuzzTerms home folder.",
)
@click.option(
    "--name",
    "-n",
    type=str,
    help="Name of FuzzTerms database.",
)
@click.pass_context
def app(ctx, home: str, name: str):
    ctx.ensure_object(dict)
    path = const.make_project_path(home, name)
    ctx.obj["collection"] = Collection.load(path)
