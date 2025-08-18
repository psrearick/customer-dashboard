import click
import sys
import os
import subprocess
from tabulate import tabulate
from .utils import get_services_for_stack, build_compose_command, run_compose_command, stream_compose_command, PROJECT_NAME

@click.group(name="stack")
def stack_group():
    """Commands to manage entire stacks of containers."""
    pass

@stack_group.command(name="up")
@click.option('--attach/--detach', '-a/-d', is_flag=True, default=False, show_default=True, help="detached mode: run containers in the background")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="stack of containers to run")
@click.option('--build', '-b', is_flag=True, default=False, show_default=True, help="build images before starting containers")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
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
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def down(stack, verbose):
    """Stop every container in the specified stack"""
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'down')

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

    click.secho("Application Stopped", fg="green")

@stack_group.command(name="restart")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to restart")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def restart(stack, verbose):
    """Restart every container in the specified stack"""
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'restart')

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

    click.secho("Application Restarted", fg="green")

@stack_group.command(name="stop")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to stop")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def stop(stack, verbose):
    """Stop every container in the specified stack without removing them"""
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'stop')

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

    click.secho("Application Stopped", fg="green")

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
    click.secho("Customer Dashboard Status", fg="blue", bold=True)
    click.echo("")
    
    filter_services = []
    if stack != "all":
        try:
            services = get_services_for_stack(stack)
            filter_services = [s['service'] for s in services]
        except Exception as e:
            click.secho(f"Error loading stack '{stack}': {e}", fg="red")
            sys.exit(1)
    
    try:
        if stack == "all":
            container_result = subprocess.run(
                ["docker", "ps", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}", 
                 "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
                capture_output=True, text=True, check=False
            )
        else:
            container_result = subprocess.run(
                ["docker", "ps", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}",
                 "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Label \"com.docker.compose.service\"}}"],
                capture_output=True, text=True, check=False
            )
            
        if container_result.returncode == 0 and container_result.stdout.strip():
            lines = container_result.stdout.strip().split('\n')
            
            if stack != "all":
                filtered_lines = []
                headers = ["NAMES", "STATUS", "PORTS"]
                
                for line in lines:
                    parts = line.split('\t')
                    if len(parts) >= 4:
                        service_name = parts[3]
                        if service_name in filter_services:
                            filtered_lines.append(parts[:3])
                
                if filtered_lines:
                    click.secho("Running containers:", fg="green")
                    table_output = tabulate(filtered_lines, headers=headers, tablefmt="plain")
                    click.echo(table_output)
                else:
                    click.secho("No containers currently running for this stack", fg="yellow")
            else:
                click.secho("Running containers:", fg="green")
                click.echo(lines[0] if lines else "")
                for line in lines[1:] if len(lines) > 1 else []:
                    click.echo(line)
        else:
            click.secho("No containers currently running", fg="yellow")
            click.echo("")
            click.echo("Start the application with: app stack up")
    except Exception as e:
        click.secho(f"Error getting container status: {e}", fg="red")
    
    click.echo("")
    
    try:
        network_result = subprocess.run(
            ["docker", "network", "ls", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}",
             "--format", "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"],
            capture_output=True, text=True, check=False
        )
        
        if network_result.returncode == 0 and network_result.stdout.strip():
            lines = network_result.stdout.strip().split('\n')
            if len(lines) > 1:
                click.secho("Active networks:", fg="green")
                for line in lines:
                    click.echo(line)
            else:
                click.secho("No active networks", fg="yellow")
        else:
            click.secho("No active networks", fg="yellow")
    except Exception as e:
        click.secho(f"Error getting network status: {e}", fg="red")
    
    click.echo("")
    
    try:
        volume_result = subprocess.run(
            ["docker", "volume", "ls", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}",
             "--format", "table {{.Name}}\t{{.Driver}}"],
            capture_output=True, text=True, check=False
        )
        
        if volume_result.returncode == 0 and volume_result.stdout.strip():
            lines = volume_result.stdout.strip().split('\n')
            if len(lines) > 1:
                click.secho("Created volumes:", fg="green")
                for line in lines:
                    click.echo(line)
            else:
                click.secho("No created volumes", fg="yellow")
        else:
            click.secho("No created volumes", fg="yellow")
    except Exception as e:
        click.secho(f"Error getting volume status: {e}", fg="red")

@stack_group.command(name="clean")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to remove")
@click.option('--volumes', '-v', is_flag=True, default=False, show_default=True, help="Remove named volumes declared in the compose file")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def clean(stack, volumes, verbose):
    """Remove all containers, networks, and volumes for the specified stack"""
    services = get_services_for_stack(stack)

    options = []
    
    if volumes:
        options.append('--volumes')

    command = build_compose_command(services, 'down', [], options)

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

    click.secho(f"Stack '{stack}' cleaned successfully", fg="green")
