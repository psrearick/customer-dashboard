import click
import sys
import os
from .utils import get_services_for_stack, build_compose_command, run_compose_command, stream_compose_command

@click.group(name="stack")
def stack_group():
    """Commands to manage entire stacks of containers."""
    pass

@stack_group.command(name="up")
@click.option('--attach/--detach', '-a/-d', is_flag=True, default=False, show_default=True, help="detached mode: run containers in the background")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="stack of containers to run")
@click.option('--build', '-b', is_flag=True, default=False, show_default=True, help="build images before starting containers")
@click.option('--verbose', '-v', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def up(attach, stack, build, verbose):
    """Start every container in the specified stack"""
    services = get_services_for_stack(stack)

    options = []

    if build:
        options.append('--build')

    if not attach:
        options.append('--detach')

    command = build_compose_command(services, 'up', [], options)

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

    click.secho("Application Started", fg="green")

@stack_group.command(name="down")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to stop")
@click.option('--verbose', '-v', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def down(stack, verbose):
    """Stop every container in the specified stack"""
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'down')

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

@stack_group.command(name="restart")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to restart")
@click.option('--verbose', '-v', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def restart(stack, verbose):
    """Restart every container in the specified stack"""
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'restart')

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

@stack_group.command(name="logs")
@click.option('--follow', '-f', is_flag=True, default=False, show_default=True, help="Follow log output. Press Ctrl+C to stop following.")
@click.option('--tail', '-n', default="all", show_default=True, help="Number of lines to show from the end of the logs for each container")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to view the log output of")
def logs(follow, tail, stack):
    """Displays log output from all services in the specified stack"""
    services = get_services_for_stack(stack)
    continuous = False
    options = []

    if follow:
        options.append("--follow")
        continuous = True

    if tail and tail != "all":
        options.append(["--tail", tail])

    command = build_compose_command(services, 'logs', [], options)

    stream_compose_command(command, continuous)

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
