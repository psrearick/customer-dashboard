import click
import sys
import subprocess
import os
from .utils import get_services_for_stack

PROJECT_NAME = "customer-dashboard"

@click.group(name="stack")
def stack_group():
    """Commands to manage entire stacks of containers."""
    pass

@stack_group.command(name="up")
@click.option('--attach/--detach', '-a/-d', is_flag=True, default=False, show_default=True, help="detached mode: run containers in the background")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="stack of containers to run")
@click.option('--build', '-b', is_flag=True, default=False, show_default=True, help="build images before starting containers")
def up(attach, stack, build):
    """Start every container in the specified stack"""
    services = get_services_for_stack(stack)
    
    command = [
        "docker",
        "compose",
        "--project-name",
        PROJECT_NAME,
    ]
    
    for service in services:
        command.extend(["-f", str(service['path'])])
    
    command.append('up')
    
    if build:
        command.append('--build')
    
    if not attach:
        command.append('--detach')

    try:
        project_root = os.environ.get('PROJECT_ROOT', '/project_root')
        cwd = os.path.join(project_root, 'docker', 'services')
        
        click.echo(f"Running command: {' '.join(command)}")
        result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=cwd)
        click.echo("Docker Compose command executed successfully.")
        if result.stdout:
            click.echo(result.stdout)
    except subprocess.CalledProcessError as e:
        click.echo(f"Docker Compose command failed: {e}", file=sys.stderr)
        if e.stderr:
            click.echo(f"Error output: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

@stack_group.command(name="down")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to stop")
def down():
    """Stop every container in the specified stack"""
    pass

@stack_group.command(name="restart")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to restart")
def restart(stack):
    """Restart every container in the specified stack"""
    pass

@stack_group.command(name="logs")
@click.option('--follow', '-f', is_flag=True, default=False, show_default=True, help="Follow log output")
@click.option('--tail', '-n', default="all", show_default=True, help="Number of lines to show from the end of the logs for each container")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to view the log output of")
def logs(follow, tail, stack):
    """Displays log output from all services in the specified stack"""
    pass

@stack_group.command(name="status")
@click.option('--stack', '-s', type=str, default="all", show_default=True, help="Stack of containers to view the status of")
def status(stack):
    """Show status of running containers"""
    pass

@stack_group.command(name="clean")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to remove")
def clean(stack):
    """Remove all containers, networks, and volumes for the specified stack"""
    pass
