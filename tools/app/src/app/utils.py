import os
import click
import sys
import subprocess
import yaml
from pathlib import Path

PROJECT_PATH = Path(os.environ.get('PROJECT_ROOT', '/project_root'))
PROJECT_NAME = "customer-dashboard"

STACKS_DIR = PROJECT_PATH.joinpath("docker", "stacks")
SERVICES_DIR = PROJECT_PATH.joinpath("docker", "services")

def get_services_files():
    return list(SERVICES_DIR.glob('*.yml'))

def get_stack_files():
    return list(STACKS_DIR.glob('*.yml'))

def get_stack_file(stack_name):
    stack_file = STACKS_DIR / f"{stack_name}.yml"
    if not stack_file.exists():
        click.echo(f"Error: Stack '{stack_name}' not found", file=sys.stderr)
        click.echo(f"Available stacks:", file=sys.stderr)

        available_stacks = []
        for yml_file in STACKS_DIR.glob("*.yml"):
            available_stacks.append(yml_file.stem)

        if available_stacks:
            for stack in sorted(available_stacks):
                click.echo(f"  - {stack}", file=sys.stderr)
        else:
            click.echo("  No stacks found in docker/stacks/", file=sys.stderr)

        sys.exit(1)
    return stack_file

def get_service_files_for_stack(stack_name):
    stack_file = get_stack_file(stack_name)
    service_list = []
    stack_file_service_list = []

    with open(stack_file, 'r') as file:
        file_data = yaml.safe_load(file)
        stack_file_service_list = file_data['services']

    for service in stack_file_service_list:
        service_file = SERVICES_DIR / f"{service}.yml"
        if service_file.exists():
            service_list.append(service_file)

    return service_list

def get_services_for_stack(stack_name):
    try:
        services = get_service_files_for_stack(stack_name)
    except FileNotFoundError as err:
        click.echo(err)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    return [{'service': service.stem, 'path': service} for service in services]

def build_compose_command(services, compose_command, compose_options = [], command_options = []):
    if not services:
        return

    command = [
        "docker",
        "compose",
        "--project-name",
        PROJECT_NAME,
    ]

    for service in services:
        command.extend(["-f", str(service['path'])])

    for option in compose_options:
        if isinstance(option, str):
            option = [option]
        command.extend(option)

    command.append(compose_command)

    for option in command_options:
        if isinstance(option, str):
            option = [option]
        command.extend(option)

    return command

def run_compose_command(command):
    try:
        project_root = os.environ.get('PROJECT_ROOT', '/project_root')
        cwd = os.path.join(project_root, 'docker', 'services')

        result = subprocess.run(command, check=True, capture_output=True, text=True, cwd=cwd)
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

def stream_compose_command(command, continuous = False):
    process = None

    try:
        if continuous:
            click.echo(f"--> Running command. Press Ctrl+C to exit.")

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in iter(process.stdout.readline, ''):
            sys.stdout.write(line)
            sys.stdout.flush()

    except KeyboardInterrupt:
        click.echo(f"\n--> User interruption detected. Stopping process.")

    except FileNotFoundError:
        click.secho(f"Error: The 'docker' command was not found.", fg='red')
        click.echo("Please ensure Docker is installed and in your system's PATH.")

    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg='red')

    finally:
        if process:
            if continuous:
                click.echo("--> Terminating the process.")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                click.echo("--> Process did not terminate in time, killing it.")
                process.kill()
            if continuous:
                click.echo("--> Process terminated.")
