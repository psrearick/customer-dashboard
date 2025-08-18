import click
from .utils import get_stack_files

@click.group(name="container")
def container_group():
    """Commands to manage a single container."""
    pass

@container_group.command(name="up")
@click.argument('name')
@click.option('--attach/--detach', '-a/-d', is_flag=True, default=False, show_default=True, help="detached mode: run container in the background")
@click.option('--build', '-b', is_flag=True, default=False, show_default=True, help="build image before starting container")
def up(name, attach, build):
    """Start a single container by name."""
    pass

@container_group.command(name="down")
@click.argument('name')
def down(name):
    """Stop a single container by name."""
    pass

@container_group.command(name="restart")
@click.argument('name')
def restart(name):
    """Restart a single container by name."""
    pass

@container_group.command(name="down")
@click.argument('name')
def stop(name):
    """Stop a single container by name."""
    pass

@container_group.command(name="remove")
@click.argument('name')
@click.option('--force', '-f', is_flag=True, default=False, show_default=True, help="Don't ask to confirm removal")
@click.option('--stop', '-s', is_flag=True, default=False, show_default=True, help="Stop the container, if required, before removing")
@click.option('--volumes', '-v', is_flag=True, default=False, show_default=True, help="Remove any anonymous volumes attached to container")
def restart(name, force, stop, volumes):
    """Remove a single container by name."""
    pass

@container_group.command(name="logs")
@click.argument('name')
@click.option('--follow', '-f', is_flag=True, default=False, show_default=True, help="Follow log output.")
@click.option('--tail', '-n', default="100", show_default=True, help="Number of lines to show from the end of the logs.")
def logs(name, follow, tail):
    """Displays log output from a single container."""
    pass

@container_group.command(name="exec")
@click.argument('name')
@click.argument('command', nargs=-1)
def exec(name, command):
    """Execute a command inside a running container."""
    command_str = " ".join(command)
    click.echo(f"Executing '{command_str}' in container '{name}'...")
