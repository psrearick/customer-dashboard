import click

@click.group()
def cli():
    """A sample CLI tool."""
    pass

@cli.command()
def hello():
    """Prints a greeting."""
    click.echo("Hello from inside the Docker container!")

if __name__ == '__main__':
    cli()