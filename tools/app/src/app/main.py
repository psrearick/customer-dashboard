import click
import json
import sys
from datetime import datetime
from .container_commands import container_group
from .stack_commands import stack_group
from .dev_commands import dev_group
from .setup_commands import setup_group
from .stack_config import StackConfig
from .state_manager import StateManager
from .branch_manager import BranchManager
from .service_discovery import ServiceDiscovery
from .output_utils import OutputFormatter
from .error_handler import ErrorHandler


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """Customer Dashboard Environment Manager"""
    pass


# Add command groups
cli.add_command(stack_group)
cli.add_command(container_group)
cli.add_command(dev_group)
cli.add_command(setup_group)


@cli.command()
@click.pass_context
def help(ctx):
    """Show this message and exit."""
    click.echo(cli.get_help(ctx))


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help="Show detailed information")
def list(verbose):
    """List all available stacks."""
    try:
        stacks = StackConfig.get_all_stacks()

        if not stacks:
            click.echo("No stacks found")
            return

        if verbose:
            for stack in stacks:
                click.echo(f"\n{stack['name']} ({stack['id']})")
                click.echo(f"  Description: {stack['description']}")
                click.echo(f"  Access URL: {stack.get('access_url', 'N/A')}")
                click.echo(f"  Services: {', '.join(stack['services'])}")

                requirements = stack.get('requirements', {})
                if requirements:
                    click.echo(f"  Memory: {requirements.get('min_memory', 'N/A')}")
                    features = requirements.get('features', [])
                    if features:
                        click.echo(f"  Features: {', '.join(features)}")
        else:
            # Simple table format
            headers = ['ID', 'Name', 'Services', 'Description']
            rows = []

            for stack in stacks:
                rows.append([
                    stack['id'],
                    stack['name'],
                    ', '.join(stack['services'][:3]) + ('...' if len(stack['services']) > 3 else ''),
                    stack['description'][:50] + ('...' if len(stack['description']) > 50 else '')
                ])

            click.echo(OutputFormatter.format_table(headers, rows))

    except Exception as e:
        ErrorHandler.handle_docker_error(e)
        sys.exit(1)


@cli.command(name="status")
@click.option('--stack', '-s', help="Show status for specific stack only")
@click.option('--verbose', '-v', is_flag=True, help="Show detailed information")
@click.option('--json', is_flag=True, help="Output in JSON format")
def status(stack, verbose, json):
    """Show comprehensive environment status."""
    try:
        if stack:
            StateManager.update_container_status(stack)
        else:
            [StateManager.update_container_status(stack_info['id']) for stack_info in StackConfig.get_all_stacks()]

        active_stacks = StateManager.get_active_stacks()

        current_branch = BranchManager.get_current_branch()
        branch_info = BranchManager.get_branch_info(current_branch)

        status_data = {
            'timestamp': datetime.now().isoformat(),
            'active_stacks': {},
            'current_branch': branch_info,
            'services': [],
            'system': {}
        }

        for stack_name, stack_info in active_stacks.items():
            if stack and stack_name != stack:
                continue

            uptime = StateManager.get_stack_uptime_seconds(stack_name)
            access_info = StateManager.get_stack_access_info(stack_name)

            status_data['active_stacks'][stack_name] = {
                'uptime_seconds': int(uptime) if uptime else 0,
                'uptime_formatted': OutputFormatter.format_uptime(uptime) if uptime else 'Unknown',
                'access_info': access_info,
                'containers': stack_info.get('containers', {}),
                'ports': stack_info.get('ports', []),
                'services': stack_info.get('services', [])
            }

        php_container = ServiceDiscovery.get_php_container()
        db_container = ServiceDiscovery.get_database_container()
        cache_container = ServiceDiscovery.get_cache_container()
        node_container = ServiceDiscovery.get_node_container()

        status_data['services'] = [
            {'name': 'PHP', 'container': php_container, 'status': 'ready' if php_container else 'unavailable'},
            {'name': 'Database', 'container': db_container, 'status': 'ready' if db_container else 'unavailable'},
            {'name': 'Cache', 'container': cache_container, 'status': 'ready' if cache_container else 'unavailable'},
            {'name': 'Assets', 'container': node_container, 'status': 'ready' if node_container else 'unavailable'}
        ]

        if json:
            click.echo(OutputFormatter.format_json_output(status_data))
            return

        click.echo("Customer Dashboard Environment Status")
        click.echo()

        if active_stacks:
            click.echo("Active Stacks:")
            for stack_name, stack_data in status_data['active_stacks'].items():
                access_url = stack_data['access_info'].get('main', 'N/A')
                running_containers = sum(1 for s in stack_data['containers'].values() if s == 'running')
                total_containers = len(stack_data['containers'])

                click.echo(f"  {stack_name} (running {stack_data['uptime_formatted']})")
                click.echo(f"    {access_url}")
                click.echo(f"    {running_containers}/{total_containers} containers running")
        else:
            click.echo("No active stacks")

        click.echo()

        if branch_info['in_registry']:
            click.echo(f"Current Branch: {current_branch}")
            click.echo(f"  Title: {branch_info['title']}")
            click.echo(f"  Stack: {branch_info['stack']} ({'running' if branch_info['stack'] in active_stacks else 'not running'})")
            if branch_info['blog_post']:
                click.echo(f"  Blog Post: {branch_info['blog_post']}")
        else:
            click.echo(f"Current Branch: {current_branch} (not in registry)")

        click.echo()
        click.echo("Services:")
        for service in status_data['services']:
            status_icon = OutputFormatter.colorize_status(service['status'])
            click.echo(f"  {status_icon} {service['name']} - {service['status'].title()}")

        if verbose:
            issues = ErrorHandler.check_common_issues()
            if issues:
                click.echo()
                click.echo("Issues detected:")
                for issue in issues:
                    click.echo(f"  - {issue}")

    except Exception as e:
        ErrorHandler.handle_docker_error(e)
        sys.exit(1)


@cli.command(name="urls")
@click.option('--stack', '-s', help="Show URLs for specific stack only")
@click.option('--type', '-t', help="Filter by service type (web, monitoring, database)")
@click.option('--copy', is_flag=True, help="Copy main URL to clipboard")
@click.option('--open', is_flag=True, help="Open main URL in browser")
def urls(stack, type, copy, open):
    """Show all access URLs for running services."""
    try:
        active_stacks = StateManager.get_active_stacks()

        if not active_stacks:
            click.echo("No active stacks found")
            click.echo("Start a stack first: app stack up")
            return

        all_urls = []

        for stack_name, stack_info in active_stacks.items():
            if stack and stack_name != stack:
                continue

            access_info = StateManager.get_stack_access_info(stack_name)

            # Main application URL
            main_url = access_info.get('main')
            if main_url:
                all_urls.append({
                    'name': f'{stack_name.title()} App',
                    'url': main_url,
                    'description': f'{stack_name} stack application',
                    'type': 'web'
                })

            # Monitoring URLs
            for service, url in access_info.items():
                if service != 'main':
                    all_urls.append({
                        'name': service.title(),
                        'url': url,
                        'description': f'{service} monitoring interface',
                        'type': 'monitoring'
                    })

        # Add database connections
        try:
            from .database_utils import DatabaseUtils
            mysql_creds = DatabaseUtils.get_mysql_credentials()
            redis_creds = DatabaseUtils.get_redis_credentials()

            all_urls.extend([
                {
                    'name': 'MySQL',
                    'url': f"mysql://{mysql_creds['username']}@{mysql_creds['host']}:{mysql_creds['port']}/{mysql_creds['database']}",
                    'description': 'Main application database',
                    'type': 'database'
                },
                {
                    'name': 'Redis',
                    'url': f"redis://{redis_creds['host']}:{redis_creds['port']}",
                    'description': 'Cache, sessions, and queue storage',
                    'type': 'database'
                }
            ])
        except Exception:
            pass

        # Filter by type if specified
        if type:
            all_urls = [url for url in all_urls if url.get('type') == type]

        if not all_urls:
            click.echo("No URLs found")
            return

        # Group by type
        web_urls = [u for u in all_urls if u.get('type') == 'web']
        monitoring_urls = [u for u in all_urls if u.get('type') == 'monitoring']
        database_urls = [u for u in all_urls if u.get('type') == 'database']

        click.echo("Customer Dashboard - Service URLs")
        click.echo()

        if web_urls:
            click.echo("Web Applications:")
            click.echo(OutputFormatter.format_url_table(web_urls))
            click.echo()

        if monitoring_urls:
            click.echo("Monitoring:")
            click.echo(OutputFormatter.format_url_table(monitoring_urls))
            click.echo()

        if database_urls:
            click.echo("Database Connections:")
            click.echo(OutputFormatter.format_url_table(database_urls))

        # Handle copy/open options
        if copy or open:
            main_urls = [u for u in all_urls if 'app' in u['name'].lower()]
            if main_urls:
                main_url = main_urls[0]['url']
                if copy:
                    try:
                        import pyperclip
                        pyperclip.copy(main_url)
                        click.echo(f"\nCopied to clipboard: {main_url}")
                    except ImportError:
                        click.echo(f"\nMain URL: {main_url}")

                if open:
                    import webbrowser
                    webbrowser.open(main_url)
                    click.echo(f"\nOpened in browser: {main_url}")

    except Exception as e:
        ErrorHandler.handle_docker_error(e)
        sys.exit(1)


@cli.command(name="info")
@click.option('--verbose', '-v', is_flag=True, help="Show detailed system information")
@click.option('--check-requirements', is_flag=True, help="Verify system requirements")
def info(verbose, check_requirements):
    """Show system information and requirements check."""
    import subprocess
    from pathlib import Path

    click.echo("Customer Dashboard - System Information")
    click.echo()

    # Docker environment
    click.echo("Docker Environment:")
    try:
        docker_version = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if docker_version.returncode == 0:
            version = docker_version.stdout.strip().split()[2].rstrip(',')
            click.echo(f"  Docker: {version}")

        compose_version = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
        if compose_version.returncode == 0:
            version = compose_version.stdout.split()[3]
            click.echo(f"  Compose: {version}")

        # Check resources if verbose
        if verbose:
            docker_info = subprocess.run(['docker', 'system', 'df'], capture_output=True, text=True)
            if docker_info.returncode == 0:
                click.echo("  Resources: Available")

    except Exception:
        click.echo("  Docker: Not available")

    # Project information
    click.echo()
    click.echo("Project:")
    project_path = Path.cwd()
    click.echo(f"  Location: {project_path}")

    # Laravel version
    composer_json = project_path / "composer.json"
    if composer_json.exists():
        try:
            import json
            with open(composer_json) as f:
                data = json.load(f)
                laravel_version = data.get('require', {}).get('laravel/framework', 'Unknown')
                click.echo(f"  Laravel: {laravel_version}")
        except Exception:
            click.echo("  Laravel: Version unknown")

    # Git status
    try:
        git_branch = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
        if git_branch.returncode == 0:
            branch = git_branch.stdout.strip()

            git_status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
            status = "clean" if not git_status.stdout.strip() else "modified"

            click.echo(f"  Git Branch: {branch} ({status})")
    except Exception:
        click.echo("  Git: Not available")

    # Environment file
    env_file = project_path / ".env"
    status = 'exists' if env_file.exists() else 'missing'
    click.echo(f"  Environment: .env {status}")

    # Available stacks
    try:
        stacks = StackConfig.get_all_stacks()
        click.echo(f"\nAvailable Stacks: {len(stacks)}")
        if verbose:
            for stack in stacks:
                click.echo(f"  → {stack['id']}: {stack['name']}")
        else:
            stack_names = [s['id'] for s in stacks]
            click.echo(f"  → {', '.join(stack_names)}")
    except Exception:
        click.echo("\nAvailable Stacks: Error loading")

    # Registered branches
    try:
        branches = BranchManager.list_available_branches()
        click.echo(f"\nRegistered Branches: {len(branches)}")
        if verbose:
            feature_counts = {}
            for branch in branches:
                for feature in branch['features']:
                    feature_counts[feature] = feature_counts.get(feature, 0) + 1

            for feature, count in feature_counts.items():
                click.echo(f"  → {count} {feature} demos")
        else:
            performance_count = len([b for b in branches if 'performance' in b['features']])
            architecture_count = len([b for b in branches if 'architecture' in b['features']])
            click.echo(f"  → {performance_count} performance demos, {architecture_count} architecture demos")
    except Exception:
        click.echo("\nRegistered Branches: Error loading")

    if check_requirements:
        click.echo()
        issues = ErrorHandler.check_common_issues()
        if issues:
            click.echo("Issues found:")
            for issue in issues:
                click.echo(f"  - {issue}")
        else:
            click.echo("All requirements met")


if __name__ == '__main__':
    cli()
