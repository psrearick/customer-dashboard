import os
import errno
import click
import sys
import yaml
from pathlib import Path

# Use the PROJECT_ROOT environment variable which now contains the actual host path
# Since we mount at the same path in the container, this works for both reading files and Docker commands
PROJECT_PATH = Path(os.environ.get('PROJECT_ROOT', '/project_root'))

STACKS_DIR = PROJECT_PATH.joinpath("docker", "stacks")
SERVICES_DIR = PROJECT_PATH.joinpath("docker", "services")

def get_services_files():
    return list(SERVICES_DIR.glob('*.yml'))

def get_stack_files():
    return list(STACKS_DIR.glob('*.yml'))

def get_stack_file(stack_name):
    stack_file = STACKS_DIR / f"{stack_name}.yml"
    click.echo(stack_file)
    if not stack_file.exists():
        raise FileNotFoundError(
            errno.ENOENT,
            os.strerror(errno.ENOENT),
            stack_file
        )
    return stack_file

def get_service_files_for_stack(stack_name):
    stack_file = get_stack_file(stack_name)
    service_list = []
    stack_file_service_list = []

    with open(stack_file, 'r') as file:
        file_data = yaml.safe_load(file)
        stack_file_service_list = file_data['stack_services']

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

    # Return container paths - Docker will access files through the mounted volume
    return [{'service': service.stem, 'path': service} for service in services]
