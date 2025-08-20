import click
import sys
import os
import subprocess
from tabulate import tabulate
from .utils import get_services_for_stack, build_compose_command, run_compose_command, stream_compose_command, PROJECT_NAME

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(name="stack", context_settings=CONTEXT_SETTINGS)
def stack_group():
    """Commands to manage entire stacks of containers."""
    pass

@stack_group.command()
@click.pass_context
def help(ctx):
    """Show this message and exit."""
    click.echo(stack_group.get_help(ctx))

@stack_group.command(name="up")
@click.option('--attach/--detach', '-a/-d', is_flag=True, default=False, show_default=True, help="detached mode: run containers in the background")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="stack of containers to run")
@click.option('--build', '-b', is_flag=True, default=False, show_default=True, help="build images before starting containers")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def up(attach, stack, build, verbose):
    """Start every container in the specified stack"""
    from .state_manager import StateManager
    
    services = get_services_for_stack(stack)

    options = []

    if build:
        options.append('--build')

    if not attach:
        options.append('--detach')

    command = build_compose_command(services, 'up', [], options)

    if verbose:
        stream_compose_command(command)
    else:
        run_compose_command(command)
    
    # Track the stack as active (convert Path objects to service names)
    from .stack_config import StackConfig
    service_names = StackConfig.get_stack_services(stack)
    StateManager.mark_stack_active(stack, service_names)
    
    click.secho("Application Started", fg="green")

@stack_group.command(name="down")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to stop")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def down(stack, verbose):
    """Stop every container in the specified stack"""
    from .state_manager import StateManager
    
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'down')

    if verbose:
        stream_compose_command(command)
    else:
        run_compose_command(command)
    
    # Mark the stack as inactive
    StateManager.mark_stack_inactive(stack)

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

@stack_group.command(name="stop-all")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def stop_all(verbose):
    """Stop all containers across all stacks in the project"""
    try:
        container_result = subprocess.run(
            ["docker", "ps", "-q", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}"],
            capture_output=True, text=True, check=False
        )
        
        if container_result.returncode != 0:
            click.secho(f"Error getting container list: {container_result.stderr}", fg="red")
            sys.exit(1)
        
        container_ids = container_result.stdout.strip().split('\n')
        container_ids = [cid for cid in container_ids if cid]
        
        if not container_ids:
            click.secho("No running containers found for this project.", fg="yellow")
            return
        
        click.secho(f"Stopping {len(container_ids)} container(s) across all stacks...", fg="blue")
        
        if verbose:
            names_result = subprocess.run(
                ["docker", "ps", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}",
                 "--format", "{{.Names}}"],
                capture_output=True, text=True, check=False
            )
            if names_result.returncode == 0:
                container_names = names_result.stdout.strip().split('\n')
                click.echo("Containers to stop:")
                for name in container_names:
                    if name:
                        click.echo(f"  - {name}")
                click.echo("")
        
        stop_result = subprocess.run(
            ["docker", "stop"] + container_ids,
            capture_output=True, text=True, check=False
        )
        
        if stop_result.returncode != 0:
            click.secho(f"Error stopping containers: {stop_result.stderr}", fg="red")
            sys.exit(1)
        
        if verbose and stop_result.stdout:
            click.echo("Stopped containers:")
            for container_id in stop_result.stdout.strip().split('\n'):
                if container_id:
                    click.echo(f"  - {container_id}")
        
        click.secho(f"Successfully stopped all containers in project '{PROJECT_NAME}'", fg="green")
        
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red")
        sys.exit(1)

@stack_group.command(name="build")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to build")
@click.option('--no-cache', is_flag=True, default=False, help="Build without using cache")
@click.option('--pull', is_flag=True, default=False, help="Always pull latest base images")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def build(stack, no_cache, pull, verbose):
    """Build or rebuild services for the specified stack"""
    services = get_services_for_stack(stack)

    options = []
    
    if no_cache:
        options.append('--no-cache')
    
    if pull:
        options.append('--pull')

    command = build_compose_command(services, 'build', [], options)

    # Show what's being built
    service_names = [s['service'] for s in services]
    click.echo(f"Building stack '{stack}' ({len(service_names)} services)...")
    
    for i, service_name in enumerate(service_names, 1):
        click.echo(f"  {i}/{len(service_names)}: {service_name}")
    
    click.echo()
    
    if verbose:
        stream_compose_command(command)
        return

    # For non-verbose, show a progress indicator
    click.echo("Building... (this may take several minutes)")
    click.echo("Use --verbose to see detailed build output")
    
    run_compose_command(command)

    click.secho(f"Stack '{stack}' built successfully", fg="green")

@stack_group.command(name="pull")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to pull images for")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
def pull(stack, verbose):
    """Pull service images for the specified stack"""
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'pull')

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)

    click.secho(f"Images for stack '{stack}' pulled successfully", fg="green")

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
    """Show status of all containers"""
    if stack == "all":
        click.secho("Customer Dashboard Status - All Stacks", fg="blue", bold=True)
    else:
        click.secho(f"Customer Dashboard Status - {stack.title()} Stack", fg="blue", bold=True)
    click.echo("")
    
    expected_services = []
    if stack != "all":
        try:
            services = get_services_for_stack(stack)
            expected_services = [s['service'] for s in services]
        except Exception as e:
            click.secho(f"Error loading stack '{stack}': {e}", fg="red")
            sys.exit(1)
    
    try:
        container_result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}",
             "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Label \"com.docker.compose.service\"}}"],
            capture_output=True, text=True, check=False
        )
        
        all_containers = []
        running_containers = []
        stack_containers = []
        stack_running = []
        
        if container_result.returncode == 0 and container_result.stdout.strip():
            lines = container_result.stdout.strip().split('\n')
            
            for line in lines:
                parts = line.split('\t')
                if len(parts) >= 4:
                    name, status, ports, service = parts[0], parts[1], parts[2], parts[3]
                    container_info = [name, status, ports if ports else "-"]
                    
                    all_containers.append(container_info)
                    if "Up" in status:
                        running_containers.append(container_info)
                    
                    if stack != "all" and service in expected_services:
                        stack_containers.append(container_info)
                        if "Up" in status:
                            stack_running.append(container_info)
        
        headers = ["NAME", "STATUS", "PORTS"]
        
        if stack == "all":
            if all_containers:
                click.secho("All containers:", fg="green")
                table_output = tabulate(all_containers, headers=headers, tablefmt="plain")
                click.echo(table_output)
                click.echo("")
                
                if not running_containers:
                    click.secho("No containers are currently running.", fg="yellow")
                    click.echo("Start a stack with: app stack up -s <stack-name>")
                elif len(running_containers) < len(all_containers):
                    click.secho(f"{len(running_containers)} of {len(all_containers)} containers are running.", fg="yellow")
                else:
                    click.secho("All containers are running.", fg="green")
            else:
                click.secho("No containers found for this project.", fg="yellow")
                click.echo("Start a stack with: app stack up -s <stack-name>")
        else:
            if stack_containers:
                click.secho(f"Containers in '{stack}' stack:", fg="green")
                table_output = tabulate(stack_containers, headers=headers, tablefmt="plain")
                click.echo(table_output)
                click.echo("")
                
                if not stack_running:
                    click.secho(f"The '{stack}' stack is not running.", fg="yellow")
                    click.echo(f"Start the stack with: app stack up -s {stack}")
                elif len(stack_running) < len(stack_containers):
                    click.secho(f"The '{stack}' stack is partially running ({len(stack_running)} of {len(stack_containers)} containers).", fg="yellow")
                    click.echo(f"Start all containers with: app stack up -s {stack}")
                else:
                    click.secho(f"The '{stack}' stack is fully running.", fg="green")
            else:
                click.secho(f"No containers found for the '{stack}' stack.", fg="yellow")
                click.echo(f"Start the stack with: app stack up -s {stack}")
                
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
