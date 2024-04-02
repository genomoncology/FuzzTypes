import click

from fuzzterms import Project, const
from fuzzterms.cli import app


@app.command()
@click.option(
    "--device",
    type=click.Choice(const.DeviceChoices, case_sensitive=True),
    default=None,
    help="Device for calculating embeddings",
)
@click.option(
    "--encoder",
    type=str,
    default=None,
    help="Model used for calculating embeddings",
)
@click.option(
    "--search",
    type=click.Choice(const.SearchChoices, case_sensitive=True),
    default=None,
    help="Search method for finding terms",
)
@click.pass_context
def config(
    ctx,
    device: str = None,
    encoder: str = None,
    search: str = None,
):
    """Initialize a new project or update existing project configuration."""
    project: Project = ctx.obj["project"]

    msg = "Updating" if project.config_path.exists() else "Initializing"
    click.echo(f"{msg} project: {project.path}")
    project.save(
        device=device,
        encoder=encoder,
        search=search,
    )
    click.echo("Done.")
