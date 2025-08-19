import click
import yaml
from tabulate import tabulate
import sys
from .utils import get_stack_files
from .container_commands import container_group
from .stack_commands import stack_group

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Customer Dashboard Environment Manager"""
    pass

cli.add_command(stack_group)
cli.add_command(container_group)

@cli.command()
@click.pass_context
def help(ctx):
    """Show this message and exit."""
    click.echo(cli.get_help(ctx))

@cli.command()
def list():
    """List all available stacks."""
    data = []
    for file_path in get_stack_files():
        try:
            with open(file_path, 'r') as file:
                file_data = yaml.safe_load(file)
                data.append([
                    file_data['id'],
                    ', '.join(file_data['services']),
                    file_data['description']
                ])
        except yaml.YAMLError as exc:
            click.echo(exc)
            sys.exit(1)

    headers = ['ID', 'Services', 'Description']
    click.echo(tabulate(data, headers=headers, tablefmt="simple"))
