import click
import yaml
from tabulate import tabulate
import sys
from .utils import get_stack_files
from .container_commands import container_group
from .stack_commands import stack_group

@click.group()
def cli():
    """Customer Dashboard Environment Manager"""
    pass

cli.add_command(stack_group)
cli.add_command(container_group)


@cli.command()
def stacks():
    """List all available stacks."""
    data = []
    for file_path in get_stack_files():
        try:
            with open(file_path, 'r') as file:
                file_data = yaml.safe_load(file)
                data.append([
                    file_data['id'],
                    ', '.join(file_data['stack_services']),
                    file_data['description']
                ])
        except yaml.YAMLError as exc:
            click.echo(exc)
            sys.exit(1)

    headers = ['ID', 'Services', 'Description']
    click.echo(tabulate(data, headers=headers, tablefmt="simple"))
