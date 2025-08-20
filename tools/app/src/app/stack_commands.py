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
@click.option('--check-ports', is_flag=True, default=True, show_default=True, help="check for port conflicts before starting")
def up(attach, stack, build, verbose, check_ports):
    """Start every container in the specified stack with integrated state tracking"""
    from .state_manager import StateManager
    from .stack_config import StackConfig
    from .laravel_utils import LaravelUtils
    
    if not StackConfig.stack_exists(stack):
        click.secho(f"Error: Stack '{stack}' not found", fg="red")
        click.echo(f"Available stacks: {', '.join([s['id'] for s in StackConfig.get_all_stacks()])}")
        sys.exit(1)
    
    if check_ports:
        conflicts = StateManager.check_port_conflicts(stack)
        if conflicts:
            click.secho("Port conflicts detected:", fg="red")
            for conflict in conflicts:
                click.echo(f"  Port {conflict['port']}: used by {conflict['existing_stack']} (service: {conflict['service']})")
            click.echo("\nStop conflicting stacks or use different ports.")
            sys.exit(1)
    
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
    
    service_names = StackConfig.get_stack_services(stack)
    StateManager.mark_stack_active(stack, service_names)
    
    try:
        LaravelUtils.optimize_laravel_caches()
        if verbose:
            click.echo("Laravel caches optimized")
    except Exception as e:
        if verbose:
            click.echo(f"Cache optimization skipped: {e}")
    
    stack_info = StackConfig.get_stack_access_url(stack)
    click.secho("Application Started", fg="green")
    click.echo(f"Access URL: {stack_info}")

@stack_group.command(name="down")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to stop")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
@click.option('--clear-queues', is_flag=True, default=True, show_default=True, help="clear Laravel queues before stopping")
def down(stack, verbose, clear_queues):
    """Stop every container in the specified stack with queue cleanup"""
    from .state_manager import StateManager
    from .laravel_utils import LaravelUtils
    
    if clear_queues:
        try:
            LaravelUtils.clear_laravel_queues()
            if verbose:
                click.echo("Laravel queues cleared")
        except Exception as e:
            if verbose:
                click.echo(f"Queue clearing skipped: {e}")
    
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'down')

    if verbose:
        stream_compose_command(command)
    else:
        run_compose_command(command)
    
    StateManager.mark_stack_inactive(stack)

    click.secho("Application Stopped", fg="green")

@stack_group.command(name="restart")
@click.option('--stack', '-s', type=str, default="default", show_default=True, help="Stack of containers to restart")
@click.option('--verbose', '-V', is_flag=True, default=False, show_default=True, help="Display more detailed output")
@click.option('--clear-queues', is_flag=True, default=True, show_default=True, help="clear Laravel queues before restarting")
def restart(stack, verbose, clear_queues):
    """Restart every container in the specified stack with queue management"""
    from .state_manager import StateManager
    from .laravel_utils import LaravelUtils
    
    if clear_queues:
        try:
            LaravelUtils.clear_laravel_queues()
            if verbose:
                click.echo("Laravel queues cleared")
        except Exception as e:
            if verbose:
                click.echo(f"Queue clearing skipped: {e}")
    
    services = get_services_for_stack(stack)

    command = build_compose_command(services, 'restart')

    if verbose:
        stream_compose_command(command)
        return

    run_compose_command(command)
    
    from .stack_config import StackConfig
    service_names = StackConfig.get_stack_services(stack)
    StateManager.mark_stack_active(stack, service_names)
    
    try:
        LaravelUtils.optimize_laravel_caches()
        if verbose:
            click.echo("Laravel caches optimized")
    except Exception as e:
        if verbose:
            click.echo(f"Cache optimization skipped: {e}")

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

    service_names = [s['service'] for s in services]
    click.echo(f"Building stack '{stack}' ({len(service_names)} services)...")
    
    for i, service_name in enumerate(service_names, 1):
        click.echo(f"  {i}/{len(service_names)}: {service_name}")
    
    click.echo()
    
    if verbose:
        stream_compose_command(command)
        return

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
    """Show comprehensive status with state information"""
    from .state_manager import StateManager
    from .stack_config import StackConfig
    
    if stack == "all":
        click.secho("Customer Dashboard Status - All Stacks", fg="blue", bold=True)
    else:
        click.secho(f"Customer Dashboard Status - {stack.title()} Stack", fg="blue", bold=True)
    click.echo("")
    
    active_stacks = StateManager.get_active_stacks()
    if active_stacks:
        click.secho("Active Stacks (from state):", fg="green")
        for stack_name, stack_info in active_stacks.items():
            uptime = StateManager.get_stack_uptime(stack_name)
            access_url = stack_info.get('access_url', 'N/A')
            click.echo(f"  {stack_name}: {access_url} (uptime: {uptime})")
        click.echo("")
    else:
        click.secho("No active stacks (from state)", fg="yellow")
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
                
                for stack_name in active_stacks.keys():
                    monitoring_urls = StackConfig.get_monitoring_urls(stack_name)
                    if monitoring_urls:
                        click.secho(f"\nMonitoring URLs for '{stack_name}':", fg="cyan")
                        for service, url in monitoring_urls.items():
                            click.echo(f"  {service}: {url}")
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
                    
                    # Show additional stack info if it's active in state
                    if stack in active_stacks:
                        stack_info = active_stacks[stack]
                        uptime = StateManager.get_stack_uptime(stack)
                        click.echo(f"Access URL: {stack_info.get('access_url', 'N/A')}")
                        click.echo(f"Uptime: {uptime}")
                        
                        monitoring_urls = StackConfig.get_monitoring_urls(stack)
                        if monitoring_urls:
                            click.secho("\nMonitoring URLs:", fg="cyan")
                            for service, url in monitoring_urls.items():
                                click.echo(f"  {service}: {url}")
            else:
                click.secho(f"No containers found for the '{stack}' stack.", fg="yellow")
                click.echo(f"Start the stack with: app stack up -s {stack}")
                
                if StackConfig.stack_exists(stack):
                    requirements = StackConfig.get_stack_requirements(stack)
                    click.echo(f"\nStack requirements:")
                    click.echo(f"  Memory: {requirements.get('min_memory', 'N/A')}")
                    click.echo(f"  Ports: {', '.join(map(str, requirements.get('ports', [])))}")
                    click.echo(f"  Features: {', '.join(requirements.get('features', []))}")
                
    except Exception as e:
        click.secho(f"Error getting container status: {e}", fg="red")
    
    cleaned = StateManager.cleanup_stale_state()
    if cleaned > 0 and stack == "all":
        click.echo(f"\nCleaned up {cleaned} stale state entries.")
    
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
    
    if stack != "all":
        try:
            conflicts = StateManager.check_port_conflicts(stack)
            if conflicts:
                click.secho("\nPort conflicts detected:", fg="red")
                for conflict in conflicts:
                    click.echo(f"  Port {conflict['port']}: used by {conflict['existing_stack']}")
        except Exception:
            pass  # Ignore errors in conflict checking for status display

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
