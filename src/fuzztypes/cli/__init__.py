import click


@click.group()
def app():
    pass


from . import fuzz
