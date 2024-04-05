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
    if path is None:
        msg = "You must specify a project name (--name or FUZZTERMS_NAME)."
        raise click.UsageError(msg)
    ctx.obj["collection"] = Collection.load(path)
