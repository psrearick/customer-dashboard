import click
import subprocess
import sys
from typing import Optional
from .service_discovery import ServiceDiscovery
from .database_utils import DatabaseUtils
from .state_manager import StateManager


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(name="dev", context_settings=CONTEXT_SETTINGS)
def dev_group():
    """Commands for daily Laravel development tasks."""
    pass


@dev_group.command(name="artisan", context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, required=False)
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--dry-run', is_flag=True, help="Show command that would be executed")
def artisan(args, container, dry_run):
    """Run Laravel Artisan commands in the PHP container."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            click.echo("  → Start a stack first: app stack up", err=True)
            click.echo("  → Check stack status: app stack status", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it', container, 'php', 'artisan'] + list(args)
    
    if dry_run:
        click.echo(f"Would run: {' '.join(cmd)}")
        return
    
    subprocess.run(cmd)


@dev_group.command(name="tinker")
@click.option('--container', '-c', help="Specific PHP container to use")
def tinker(container):
    """Start Laravel Tinker REPL."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            click.echo("  → Start a stack first: app stack up", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it', container, 'php', 'artisan', 'tinker']
    subprocess.run(cmd)


@dev_group.command(name="test", context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, required=False)
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--coverage', is_flag=True, help="Generate code coverage report")
@click.option('--filter', '-f', help="Filter tests to run")
def test(args, container, coverage, filter):
    """Run PHPUnit tests."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it', container, 'php', 'artisan', 'test']
    
    if coverage:
        cmd.append('--coverage')
    
    if filter:
        cmd.extend(['--filter', filter])
    
    cmd.extend(args)
    subprocess.run(cmd)


@dev_group.command(name="composer", context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, required=False)
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--dry-run', is_flag=True, help="Show command that would be executed")
def composer(args, container, dry_run):
    """Run Composer commands in the PHP container."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it', container, 'composer'] + list(args)
    
    if dry_run:
        click.echo(f"Would run: {' '.join(cmd)}")
        return
    
    subprocess.run(cmd)


@dev_group.command(name="npm", context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, required=False)
@click.option('--container', '-c', help="Specific Node container to use")
@click.option('--dry-run', is_flag=True, help="Show command that would be executed")
def npm(args, container, dry_run):
    """Run NPM commands in the Node container."""
    if not container:
        container = ServiceDiscovery.get_node_container()
        if not container:
            click.echo("Error: No Node container is running", err=True)
            click.echo("  → Start a stack first: app stack up", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it', container, 'npm'] + list(args)
    
    if dry_run:
        click.echo(f"Would run: {' '.join(cmd)}")
        return
    
    subprocess.run(cmd)


@dev_group.command(name="node", context_settings={'ignore_unknown_options': True})
@click.argument('args', nargs=-1, required=False)
@click.option('--container', '-c', help="Specific Node container to use")
def node(args, container):
    """Run Node.js commands in the Node container."""
    if not container:
        container = ServiceDiscovery.get_node_container()
        if not container:
            click.echo("Error: No Node container is running", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it', container, 'node'] + list(args)
    subprocess.run(cmd)


@dev_group.command(name="shell")
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--user', '-u', help="User to run shell as")
@click.option('--shell', '-s', help="Shell to use (bash, sh, zsh)")
def shell(container, user, shell):
    """Open interactive shell in the PHP container."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            sys.exit(1)
    
    # Auto-detect best available shell
    if not shell:
        for sh in ['bash', 'zsh', 'sh']:
            result = subprocess.run(
                ['docker', 'exec', container, 'which', sh],
                capture_output=True
            )
            if result.returncode == 0:
                shell = sh
                break
        else:
            shell = 'sh'  # Fallback
    
    cmd = ['docker', 'exec', '-it']
    
    if user:
        cmd.extend(['-u', user])
    
    cmd.extend([container, shell])
    subprocess.run(cmd)


@dev_group.command(name="node-shell")
@click.option('--container', '-c', help="Specific Node container to use")
@click.option('--user', '-u', help="User to run shell as")
def node_shell(container, user):
    """Open interactive shell in the Node container."""
    if not container:
        container = ServiceDiscovery.get_node_container()
        if not container:
            click.echo("Error: No Node container is running", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it']
    
    if user:
        cmd.extend(['-u', user])
    
    # Alpine Linux typically uses sh
    cmd.extend([container, 'sh'])
    subprocess.run(cmd)


@dev_group.command(name="mysql")
@click.option('--host', help="MySQL host (override auto-detection)")
@click.option('--port', type=int, help="MySQL port (override auto-detection)")
@click.option('--user', '-u', help="MySQL user (override auto-detection)")
@click.option('--password', '-p', help="MySQL password (override auto-detection)")
@click.option('--database', '-d', help="Database name (override auto-detection)")
@click.option('--dry-run', is_flag=True, help="Show connection details without connecting")
def mysql(host, port, user, password, database, dry_run):
    """Connect to MySQL database with auto-discovered credentials."""
    credentials = DatabaseUtils.get_mysql_credentials()
    
    # Override with provided options
    if host:
        credentials['host'] = host
    if port:
        credentials['port'] = str(port)
    if user:
        credentials['username'] = user
    if password:
        credentials['password'] = password
    if database:
        credentials['database'] = database
    
    if dry_run:
        click.echo("MySQL connection details:")
        click.echo(f"  Host: {credentials['host']}")
        click.echo(f"  Port: {credentials['port']}")
        click.echo(f"  User: {credentials['username']}")
        click.echo(f"  Database: {credentials['database']}")
        return
    
    # Check if mysql container is running
    mysql_container = ServiceDiscovery.get_database_container()
    if mysql_container:
        cmd = [
            'docker', 'exec', '-it', mysql_container,
            'mysql',
            '-u', credentials['username'],
            f"-p{credentials['password']}",
            credentials['database']
        ]
    else:
        # Try local mysql client
        cmd = [
            'mysql',
            '-h', credentials['host'],
            '-P', credentials['port'],
            '-u', credentials['username'],
            f"-p{credentials['password']}",
            credentials['database']
        ]
    
    subprocess.run(cmd)


@dev_group.command(name="mysql-root")
@click.option('--host', help="MySQL host (override auto-detection)")
@click.option('--port', type=int, help="MySQL port (override auto-detection)")
@click.option('--password', '-p', help="Root password (override auto-detection)")
@click.option('--dry-run', is_flag=True, help="Show connection details without connecting")
def mysql_root(host, port, password, dry_run):
    """Connect to MySQL as root user."""
    credentials = DatabaseUtils.get_mysql_root_credentials()
    
    if host:
        credentials['host'] = host
    if port:
        credentials['port'] = str(port)
    if password:
        credentials['password'] = password
    
    if dry_run:
        click.echo("MySQL root connection details:")
        click.echo(f"  Host: {credentials['host']}")
        click.echo(f"  Port: {credentials['port']}")
        click.echo(f"  User: root")
        return
    
    mysql_container = ServiceDiscovery.get_database_container()
    if mysql_container:
        cmd = [
            'docker', 'exec', '-it', mysql_container,
            'mysql',
            '-u', 'root',
            f"-p{credentials['password']}"
        ]
    else:
        cmd = [
            'mysql',
            '-h', credentials['host'],
            '-P', credentials['port'],
            '-u', 'root',
            f"-p{credentials['password']}"
        ]
    
    subprocess.run(cmd)


@dev_group.command(name="redis-cli")
@click.option('--host', help="Redis host (override auto-detection)")
@click.option('--port', type=int, help="Redis port (override auto-detection)")
@click.option('--password', '-p', help="Redis password (override auto-detection)")
@click.option('--database', '-n', type=int, help="Redis database number")
@click.option('--dry-run', is_flag=True, help="Show connection details without connecting")
def redis_cli(host, port, password, database, dry_run):
    """Connect to Redis CLI with auto-discovered credentials."""
    credentials = DatabaseUtils.get_redis_credentials()
    
    if host:
        credentials['host'] = host
    if port:
        credentials['port'] = str(port)
    if password:
        credentials['password'] = password
    if database is not None:
        credentials['database'] = str(database)
    
    if dry_run:
        click.echo("Redis connection details:")
        click.echo(f"  Host: {credentials['host']}")
        click.echo(f"  Port: {credentials['port']}")
        click.echo(f"  Database: {credentials['database']}")
        if credentials.get('password'):
            click.echo(f"  Authentication: enabled")
        return
    
    redis_container = ServiceDiscovery.get_cache_container()
    if redis_container:
        cmd = ['docker', 'exec', '-it', redis_container, 'redis-cli']
        
        if credentials.get('password'):
            cmd.extend(['-a', credentials['password']])
        
        if credentials.get('database'):
            cmd.extend(['-n', credentials['database']])
    else:
        cmd = ['redis-cli', '-h', credentials['host'], '-p', credentials['port']]
        
        if credentials.get('password'):
            cmd.extend(['-a', credentials['password']])
        
        if credentials.get('database'):
            cmd.extend(['-n', credentials['database']])
    
    subprocess.run(cmd)


@dev_group.command(name="cache-clear")
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--all', is_flag=True, help="Clear all caches including compiled views, routes, config")
@click.option('--dry-run', is_flag=True, help="Show commands that would be executed")
def cache_clear(container, all, dry_run):
    """Clear Laravel caches."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            sys.exit(1)
    
    if all:
        commands = [
            ['docker', 'exec', container, 'php', 'artisan', 'cache:clear'],
            ['docker', 'exec', container, 'php', 'artisan', 'config:clear'],
            ['docker', 'exec', container, 'php', 'artisan', 'route:clear'],
            ['docker', 'exec', container, 'php', 'artisan', 'view:clear'],
            ['docker', 'exec', container, 'php', 'artisan', 'event:clear']
        ]
        for cmd in commands:
            if dry_run:
                click.echo(f"Would run: {' '.join(cmd)}")
            else:
                click.echo(f"Running: {' '.join(cmd[-2:])}")
                subprocess.run(cmd)
    else:
        cmd = ['docker', 'exec', container, 'php', 'artisan', 'optimize:clear']
        if dry_run:
            click.echo(f"Would run: {' '.join(cmd)}")
        else:
            subprocess.run(cmd)
    
    if not dry_run:
        click.echo("Caches cleared")
    else:
        click.echo("Dry run complete - no commands executed")


@dev_group.command(name="queue-clear")
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--queue', help="Specific queue to clear")
@click.option('--connection', help="Queue connection to clear")
@click.option('--dry-run', is_flag=True, help="Show command that would be executed")
def queue_clear(container, queue, connection, dry_run):
    """Clear Laravel queue jobs."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', container, 'php', 'artisan', 'queue:clear']
    
    if connection:
        cmd.extend(['--connection', connection])
    
    if queue:
        cmd.extend(['--queue', queue])
    
    if dry_run:
        click.echo(f"Would run: {' '.join(cmd)}")
    else:
        subprocess.run(cmd)
        click.echo("Queue cleared")


@dev_group.command(name="queue-work", context_settings={'ignore_unknown_options': True})
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--queue', help="Queue(s) to process")
@click.option('--connection', help="Queue connection to use")
@click.option('--timeout', type=int, help="Job timeout in seconds")
@click.option('--memory', type=int, help="Memory limit in MB")
@click.option('--sleep', type=int, help="Sleep time when no jobs available")
@click.option('--tries', type=int, help="Number of attempts")
def queue_work(container, queue, connection, timeout, memory, sleep, tries):
    """Start Laravel queue worker with proper signal handling."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            sys.exit(1)
    
    cmd = ['docker', 'exec', '-it', container, 'php', 'artisan', 'queue:work']
    
    if connection:
        cmd.extend(['--connection', connection])
    
    if queue:
        cmd.extend(['--queue', queue])
    
    if timeout:
        cmd.extend(['--timeout', str(timeout)])
    
    if memory:
        cmd.extend(['--memory', str(memory)])
    
    if sleep:
        cmd.extend(['--sleep', str(sleep)])
    
    if tries:
        cmd.extend(['--tries', str(tries)])
    
    click.echo("Starting queue worker (Ctrl+C to stop)...")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        click.echo("\nQueue worker stopped")