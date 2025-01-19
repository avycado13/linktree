import click
from db import Database

db = Database()


@click.group()
def cli():
    pass


@cli.group("add")
def add():
    pass


@add.command("link")
@click.argument("url")
@click.argument("tags", nargs=-1)  # Accept 0 or more tags
def add_link(url, tags):
    db.insert_link_with_tags(url, list(tags))  # Convert tuple to list
    click.echo("Added link with tags!")


if __name__ == "__main__":
    cli()
