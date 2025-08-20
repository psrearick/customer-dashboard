import click
import subprocess
import sys
from .utils import get_services_files, build_compose_command, run_compose_command, stream_compose_command, PROJECT_NAME

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

def get_service_file(service_name):
    """Find the service file for a given service name."""
    service_files = get_services_files()
    for service_file in service_files:
        if service_file.stem == service_name:
            return [{'service': service_file.stem, 'path': service_file}]
    
    click.secho(f"Error: Service '{service_name}' not found", fg="red")
    click.echo("Available services:")
    
    available_services = []
    for service_file in service_files:
        available_services.append(service_file.stem)
    
    if available_services:
        for service in sorted(available_services):
            click.echo(f"  - {service}")
    else:
        click.echo("  No services found in docker/services/")
    
    sys.exit(1)

@click.group(name="container", context_settings=CONTEXT_SETTINGS)
def container_group():
    """Commands to manage a single container."""
    pass

@container_group.command()
@click.pass_context
def help(ctx):
    """Show this message and exit."""
    click.echo(container_group.get_help(ctx))

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

@container_group.command(name="exec", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.option('--user', '-u', help="Username or UID to run the command as")
@click.option('--env', '-e', multiple=True, help="Set environment variables (can be used multiple times)")
@click.option('--workdir', '-w', help="Working directory inside the container")
@click.argument('name')
@click.pass_context
def exec(ctx, name, user, env, workdir):
    """Execute a command inside a running container."""
    service = get_service_file(name)
    
    # Get the command from remaining args
    command = ctx.args
    if not command:
        click.echo("Error: No command specified")
        sys.exit(1)
    
    # Build the docker compose exec command manually for proper argument order
    # docker compose -f service.yml exec [options] service_name command...
    compose_command = [
        "docker", "compose", "--project-name", "customer-dashboard",
        "-f", str(service[0]['path']),
        "exec"
    ]
    
    # Add exec options
    if user:
        compose_command.extend(["--user", user])
    if workdir:
        compose_command.extend(["--workdir", workdir])
    for env_var in env:
        compose_command.extend(["--env", env_var])
    
    # Add service name and command
    compose_command.append(service[0]['service'])
    compose_command.extend(command)
    
    
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
@click.option('--verbose', '-V', is_flag=True, default=False, help="Display detailed build output")
def build(name, no_cache, pull, verbose):
    """Build or rebuild image for a single container."""
    service = get_service_file(name)
    
    options = []
    
    if no_cache:
        options.append('--no-cache')
    
    if pull:
        options.append('--pull')
    
    command = build_compose_command(service, 'build', [], options)
    
    click.echo(f"Building container '{name}'...")
    
    if no_cache:
        click.echo("  Using --no-cache (build will be slower but completely fresh)")
    if pull:
        click.echo("  Using --pull (will fetch latest base images)")
    
    if verbose:
        click.echo("Build output:")
        stream_compose_command(command)
    else:
        click.echo("Building... (use --verbose to see detailed output)")
        run_compose_command(command)
    
    click.secho(f"Container '{name}' built successfully", fg="green")