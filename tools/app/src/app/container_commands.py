import click
import subprocess
import sys
from .utils import get_services_files, build_compose_command, run_compose_command, stream_compose_command, PROJECT_NAME

def get_service_file(service_name):
    """Find the service file for a given service name."""
    service_files = get_services_files()
    for service_file in service_files:
        if service_file.stem == service_name:
            return [{'service': service_file.stem, 'path': service_file}]
    
    click.secho(f"Service '{service_name}' not found", fg="red")
    sys.exit(1)

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
    service = get_service_file(name)
    
    options = []
    
    if build:
        options.append('--build')
    
    if not attach:
        options.append('--detach')
    
    command = build_compose_command(service, 'up', [], options)
    run_compose_command(command)
    
    click.secho(f"Container '{name}' started", fg="green")

@container_group.command(name="down")
@click.argument('name')
def down(name):
    """Stop and remove a single container by name."""
    service = get_service_file(name)
    
    command = build_compose_command(service, 'down')
    run_compose_command(command)
    
    click.secho(f"Container '{name}' stopped and removed", fg="green")

@container_group.command(name="restart")
@click.argument('name')
def restart(name):
    """Restart a single container by name."""
    service = get_service_file(name)
    
    command = build_compose_command(service, 'restart')
    run_compose_command(command)
    
    click.secho(f"Container '{name}' restarted", fg="green")

@container_group.command(name="stop")
@click.argument('name')
def stop(name):
    """Stop a single container by name without removing it."""
    service = get_service_file(name)
    
    command = build_compose_command(service, 'stop')
    run_compose_command(command)
    
    click.secho(f"Container '{name}' stopped", fg="green")

@container_group.command(name="remove")
@click.argument('name')
@click.option('--force', '-f', is_flag=True, default=False, show_default=True, help="Don't ask to confirm removal")
@click.option('--stop', '-s', is_flag=True, default=False, show_default=True, help="Stop the container, if required, before removing")
@click.option('--volumes', '-v', is_flag=True, default=False, show_default=True, help="Remove any anonymous volumes attached to container")
def remove(name, force, stop, volumes):
    """Remove a single container by name."""
    service = get_service_file(name)
    
    options = []
    
    if force:
        options.append('--force')
    
    if stop:
        options.append('--stop')
    
    if volumes:
        options.append('--volumes')
    
    command = build_compose_command(service, 'rm', [], options)
    run_compose_command(command)
    
    click.secho(f"Container '{name}' removed", fg="green")

@container_group.command(name="logs")
@click.argument('name')
@click.option('--follow', '-f', is_flag=True, default=False, show_default=True, help="Follow log output.")
@click.option('--tail', '-n', default="100", show_default=True, help="Number of lines to show from the end of the logs.")
def logs(name, follow, tail):
    """Displays log output from a single container."""
    service = get_service_file(name)
    
    continuous = False
    options = []
    
    if follow:
        options.append("--follow")
        continuous = True
    
    if tail and tail != "all":
        options.extend(["--tail", tail])
    
    command = build_compose_command(service, 'logs', [], options)
    stream_compose_command(command, continuous)

@container_group.command(name="exec")
@click.argument('name')
@click.argument('command', nargs=-1, required=True)
@click.option('--user', '-u', help="Username or UID to run the command as")
@click.option('--env', '-e', multiple=True, help="Set environment variables (can be used multiple times)")
@click.option('--workdir', '-w', help="Working directory inside the container")
def exec(name, command, user, env, workdir):
    """Execute a command inside a running container."""
    service = get_service_file(name)
    
    # Build the exec command options
    options = []
    
    if user:
        options.extend(["--user", user])
    
    if workdir:
        options.extend(["--workdir", workdir])
    
    for env_var in env:
        options.extend(["--env", env_var])
    
    # Add the command to execute
    command_str = " ".join(command)
    options.append(command_str)
    
    # Build and run the docker compose exec command
    compose_command = build_compose_command(service, 'exec', [], options)
    
    # Use subprocess directly for exec to allow interactive commands
    try:
        subprocess.run(compose_command, check=True)
    except subprocess.CalledProcessError as e:
        click.secho(f"Command failed with exit code {e.returncode}", fg="red")
        sys.exit(e.returncode)
    except Exception as e:
        click.secho(f"Error executing command: {e}", fg="red")
        sys.exit(1)

@container_group.command(name="start")
@click.argument('name')
def start(name):
    """Start a stopped container by name."""
    service = get_service_file(name)
    
    command = build_compose_command(service, 'start')
    run_compose_command(command)
    
    click.secho(f"Container '{name}' started", fg="green")

@container_group.command(name="status")
@click.argument('name')
def status(name):
    """Show status of a specific container."""
    click.secho(f"Status for container '{name}':", fg="blue", bold=True)
    click.echo("")
    
    try:
        # Get container status using docker ps
        container_result = subprocess.run(
            ["docker", "ps", "-a", "--filter", f"label=com.docker.compose.project={PROJECT_NAME}",
             "--filter", f"label=com.docker.compose.service={name}",
             "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True, text=True, check=False
        )
        
        if container_result.returncode == 0 and container_result.stdout.strip():
            click.echo(container_result.stdout)
        else:
            click.secho(f"Container '{name}' not found", fg="yellow")
            click.echo(f"Start it with: app container up {name}")
    except Exception as e:
        click.secho(f"Error getting container status: {e}", fg="red")

@container_group.command(name="build")
@click.argument('name')
@click.option('--no-cache', is_flag=True, default=False, help="Build without using cache")
@click.option('--pull', is_flag=True, default=False, help="Always pull latest base images")
def build(name, no_cache, pull):
    """Build or rebuild image for a single container."""
    service = get_service_file(name)
    
    options = []
    
    if no_cache:
        options.append('--no-cache')
    
    if pull:
        options.append('--pull')
    
    command = build_compose_command(service, 'build', [], options)
    run_compose_command(command)
    
    click.secho(f"Container '{name}' built successfully", fg="green")