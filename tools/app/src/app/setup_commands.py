import click
import subprocess
import sys
import shutil
from pathlib import Path
from .state_manager import StateManager
from .branch_manager import BranchManager
from .stack_config import StackConfig
from .service_discovery import ServiceDiscovery
from .database_utils import DatabaseUtils
from .laravel_utils import LaravelUtils


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(name="setup", context_settings=CONTEXT_SETTINGS)
def setup_group():
    """Commands for environment setup, reset, and maintenance."""
    pass


@setup_group.command(name="fresh")
@click.option('--stack', '-s', default="default", help="Stack to use for setup")
@click.option('--no-seed', is_flag=True, help="Skip database seeding")
@click.option('--skip-assets', is_flag=True, help="Skip NPM install and build")
@click.option('--env-file', help="Environment file to copy (default: .env.example)")
@click.option('--force-env', is_flag=True, help="Overwrite existing .env file")
def fresh(stack, no_seed, skip_assets, env_file, force_env):
    """Complete fresh setup for new installation."""
    click.echo("Setting up Customer Dashboard...")
    
    # Environment file setup
    env_path = LaravelUtils.get_laravel_env_path()
    if not env_path.exists() or force_env:
        source_env = Path(env_file) if env_file else Path(".env.example")
        if source_env.exists():
            shutil.copy(source_env, env_path)
            click.echo("Environment file ready")
        else:
            click.echo(f"Warning: {source_env} not found", err=True)
    
    # Stop any currently running stacks
    click.echo("Stopping current stacks")
    subprocess.run(['docker', 'compose', 'down'], capture_output=True)
    
    # Start specified stack
    click.echo(f"Starting {stack} stack")
    from .utils import get_services_for_stack, build_compose_command, run_compose_command
    from .state_manager import StateManager
    
    services = get_services_for_stack(stack)
    command = build_compose_command(services, 'up', [], ['--detach'])
    run_compose_command(command)
    StateManager.mark_stack_active(stack, services)
    
    # Wait for services
    click.echo("Waiting for services...")
    services = StackConfig.get_stack_services(stack)
    if LaravelUtils.wait_for_services(services, timeout=60):
        click.echo("All services ready")
    else:
        click.echo("Some services may not be ready", err=True)
    
    # Update state tracking
    StateManager.mark_stack_active(stack, services)
    
    # Laravel application setup
    php_container = ServiceDiscovery.get_php_container()
    if not php_container:
        click.echo("Error: PHP container not running", err=True)
        sys.exit(1)
    
    # Generate app key if missing
    env_check = LaravelUtils.check_env_file()
    if not env_check['has_app_key']:
        LaravelUtils.generate_app_key()
        click.echo("Generated application key")
    
    # Install Composer dependencies
    click.echo("Installing dependencies...")
    subprocess.run(
        ['docker', 'exec', php_container, 'composer', 'install', '--no-interaction'],
        capture_output=True
    )
    click.echo("Dependencies installed")
    
    # Run migrations
    migrate_cmd = ['docker', 'exec', php_container, 'php', 'artisan', 'migrate:fresh', '--force']
    if not no_seed:
        migrate_cmd.append('--seed')
    
    subprocess.run(migrate_cmd, capture_output=True)
    click.echo("Database migrated" + (" and seeded" if not no_seed else ""))
    
    # Create storage link
    subprocess.run(
        ['docker', 'exec', php_container, 'php', 'artisan', 'storage:link'],
        capture_output=True
    )
    
    # Frontend assets
    if not skip_assets:
        node_container = ServiceDiscovery.get_node_container()
        if node_container:
            click.echo("Building assets...")
            subprocess.run(
                ['docker', 'exec', node_container, 'npm', 'install', '--silent'],
                capture_output=True
            )
            subprocess.run(
                ['docker', 'exec', node_container, 'npm', 'run', 'build'],
                capture_output=True
            )
            click.echo("Assets built")
    
    # Clear and optimize caches
    LaravelUtils.clear_laravel_queues(stack)
    LaravelUtils.optimize_laravel_caches(stack)
    click.echo("Caches optimized")
    
    # Display success message
    access_url = StackConfig.get_stack_access_url(stack)
    click.echo(f"\nSetup complete!")
    click.echo(f"Access your application: {access_url}")
    click.echo("Next steps:")
    click.echo("  → Run tests: app dev test")
    click.echo("  → Check logs: app stack logs")


@setup_group.command(name="reset")
@click.option('--no-seed', is_flag=True, help="Skip database seeding")
@click.option('--skip-assets', is_flag=True, help="Skip NPM operations")
@click.option('--keep-data', is_flag=True, help="Use migrate instead of migrate:fresh")
@click.option('--stack', '-s', help="Switch to different stack during reset")
def reset(no_seed, skip_assets, keep_data, stack):
    """Reset existing environment to clean state."""
    click.echo("Resetting environment...")
    
    # Ensure .env file exists
    env_path = LaravelUtils.get_laravel_env_path()
    if not env_path.exists():
        click.echo("Error: .env file not found", err=True)
        click.echo("Run 'app setup fresh' for initial setup", err=True)
        sys.exit(1)
    
    # Switch stack if specified
    if stack:
        click.echo(f"Switching to {stack} stack...")
        from .utils import get_services_for_stack, build_compose_command, run_compose_command
        
        # Stop current stack
        subprocess.run(['docker', 'compose', 'down'], capture_output=True)
        
        # Start new stack
        services = get_services_for_stack(stack)
        command = build_compose_command(services, 'up', [], ['--detach'])
        run_compose_command(command)
        services = StackConfig.get_stack_services(stack)
        StateManager.mark_stack_active(stack, services)
    
    php_container = ServiceDiscovery.get_php_container()
    if not php_container:
        click.echo("Error: PHP container not running", err=True)
        sys.exit(1)
    
    # Clear queues and caches first
    LaravelUtils.clear_laravel_queues(stack or 'default')
    subprocess.run(
        ['docker', 'exec', php_container, 'php', 'artisan', 'optimize:clear'],
        capture_output=True
    )
    
    # Reinstall dependencies
    click.echo("Reinstalling dependencies...")
    subprocess.run(
        ['docker', 'exec', php_container, 'composer', 'install', '--no-interaction'],
        capture_output=True
    )
    
    # Database migration
    if keep_data:
        migrate_cmd = ['docker', 'exec', php_container, 'php', 'artisan', 'migrate', '--force']
    else:
        migrate_cmd = ['docker', 'exec', php_container, 'php', 'artisan', 'migrate:fresh', '--force']
        if not no_seed:
            migrate_cmd.append('--seed')
    
    subprocess.run(migrate_cmd, capture_output=True)
    click.echo("Database reset")
    
    # Frontend assets
    if not skip_assets:
        node_container = ServiceDiscovery.get_node_container()
        if node_container:
            click.echo("Rebuilding assets...")
            subprocess.run(
                ['docker', 'exec', node_container, 'npm', 'install', '--silent'],
                capture_output=True
            )
            subprocess.run(
                ['docker', 'exec', node_container, 'npm', 'run', 'build'],
                capture_output=True
            )
            click.echo("Assets rebuilt")
    
    # Recreate storage link
    subprocess.run(
        ['docker', 'exec', php_container, 'php', 'artisan', 'storage:link'],
        capture_output=True
    )
    
    # Optimize caches
    LaravelUtils.optimize_laravel_caches(stack or 'default')
    
    click.echo("\nReset complete!")


@setup_group.command(name="branch")
@click.argument('branch_name')
@click.option('--stack', '-s', help="Override stack specified in branch config")
@click.option('--no-setup', is_flag=True, help="Switch branch without running setup commands")
@click.option('--dry-run', is_flag=True, help="Show what would be done without executing")
def branch(branch_name, stack, no_setup, dry_run):
    """Switch to blog post branch with automatic setup."""
    # Load branch configuration
    branch_config = BranchManager.load_branch_config(branch_name)
    if not branch_config:
        click.echo(f"Error: Branch '{branch_name}' not found in registry", err=True)
        click.echo("Available branches:", err=True)
        for branch in BranchManager.list_available_branches():
            click.echo(f"  - {branch['name']}: {branch['title']}", err=True)
        sys.exit(1)
    
    # Determine stack
    target_stack = stack or branch_config.get('stack', 'default')
    
    if dry_run:
        click.echo(f"Would switch to branch: {branch_name}")
        click.echo(f"Would use stack: {target_stack}")
        click.echo(f"Would run setup commands:")
        for cmd in branch_config.get('setup_commands', []):
            click.echo(f"  - {cmd}")
        return
    
    # Check for uncommitted changes
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        click.echo("Warning: You have uncommitted changes", err=True)
        if not click.confirm("Continue anyway?"):
            sys.exit(1)
    
    # Switch git branch
    click.echo(f"Switching to branch: {branch_name}")
    result = subprocess.run(
        ['git', 'checkout', branch_name],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        # Try fetching and checking out remote branch
        subprocess.run(['git', 'fetch', 'origin'], capture_output=True)
        result = subprocess.run(
            ['git', 'checkout', '-b', branch_name, f'origin/{branch_name}'],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Error: Could not checkout branch {branch_name}", err=True)
            click.echo(result.stderr, err=True)
            sys.exit(1)
    
    # Switch to required stack
    click.echo(f"Starting {target_stack} stack...")
    from .utils import get_services_for_stack, build_compose_command, run_compose_command
    
    # Stop current stack
    subprocess.run(['docker', 'compose', 'down'], capture_output=True)
    
    # Start new stack
    services = get_services_for_stack(target_stack)
    command = build_compose_command(services, 'up', [], ['--detach'])
    run_compose_command(command)
    
    services = StackConfig.get_stack_services(target_stack)
    StateManager.mark_stack_active(target_stack, services)
    
    # Run branch-specific setup
    if not no_setup:
        php_container = ServiceDiscovery.get_php_container()
        if php_container:
            click.echo("Running branch setup commands...")
            for cmd in branch_config.get('setup_commands', []):
                click.echo(f"  → {cmd}")
                if cmd.startswith('artisan'):
                    cmd_parts = cmd.split()
                    full_cmd = ['docker', 'exec', php_container, 'php'] + cmd_parts
                else:
                    full_cmd = ['docker', 'exec', php_container, 'sh', '-c', cmd]
                
                subprocess.run(full_cmd, capture_output=True)
    
    # Display branch information
    click.echo(f"\nSwitched to: {branch_config.get('title', branch_name)}")
    click.echo(f"Description: {branch_config.get('description', '')}")
    
    blog_post = branch_config.get('blog_post')
    if blog_post:
        click.echo(f"Blog post: {blog_post}")
    
    access_url = StackConfig.get_stack_access_url(target_stack)
    click.echo(f"Access URL: {access_url}")


@setup_group.command(name="optimize")
@click.option('--container', '-c', help="Specific PHP container to use")
@click.option('--production', is_flag=True, help="Use production optimizations")
@click.option('--clear-first', is_flag=True, help="Clear caches before optimizing")
@click.option('--dry-run', is_flag=True, help="Show commands that would be executed")
def optimize(container, production, clear_first, dry_run):
    """Run Laravel optimizations for better performance."""
    if not container:
        container = ServiceDiscovery.get_php_container()
        if not container:
            click.echo("Error: No PHP container is running", err=True)
            sys.exit(1)
    
    if clear_first:
        clear_cmd = ['docker', 'exec', container, 'php', 'artisan', 'optimize:clear']
        if dry_run:
            click.echo(f"Would run: {' '.join(clear_cmd)}")
        else:
            subprocess.run(clear_cmd, capture_output=True)
            click.echo("Cleared existing caches")
    
    # Standard optimizations
    commands = [
        ('config:cache', 'Configuration cached'),
        ('route:cache', 'Routes cached'),
        ('view:cache', 'Views cached')
    ]
    
    # Check if we can cache routes (no closures) - only if not dry-run
    can_cache_routes = True
    if not dry_run:
        result = subprocess.run(
            ['docker', 'exec', container, 'php', 'artisan', 'route:list'],
            capture_output=True,
            text=True
        )
        can_cache_routes = 'Closure' not in result.stdout
    
    for cmd, message in commands:
        artisan_cmd = ['docker', 'exec', container, 'php', 'artisan', cmd]
        
        if cmd == 'route:cache' and not can_cache_routes:
            click.echo("Skipping route cache (closures detected)")
            continue
        
        if dry_run:
            click.echo(f"Would run: {' '.join(artisan_cmd)}")
        else:
            subprocess.run(artisan_cmd, capture_output=True)
            click.echo(f"{message}")
    
    if production:
        composer_cmd = ['docker', 'exec', container, 'composer', 'dump-autoload', '--optimize', '--classmap-authoritative']
        if dry_run:
            click.echo(f"Would run: {' '.join(composer_cmd)}")
        else:
            subprocess.run(composer_cmd, capture_output=True)
            click.echo("Optimized composer autoloader")
    
    click.echo("\nOptimization complete!")


@setup_group.command(name="permissions")
@click.option('--user', help="User to set as owner (default: current user)")
@click.option('--group', help="Group to set (default: www-data)")
@click.option('--dry-run', is_flag=True, help="Show what would be changed")
def permissions(user, group, dry_run):
    """Fix Laravel file permissions for development."""
    import os
    import platform
    
    project_root = LaravelUtils.PROJECT_ROOT
    storage_path = project_root / "storage"
    bootstrap_cache = project_root / "bootstrap" / "cache"
    
    if not user:
        user = os.getenv('USER', 'www-data')
    
    if not group:
        group = 'www-data' if platform.system() == 'Linux' else 'staff'
    
    if dry_run:
        click.echo("Would fix permissions:")
        click.echo(f"  Owner: {user}:{group}")
        click.echo(f"  Storage: {storage_path}")
        click.echo(f"  Bootstrap cache: {bootstrap_cache}")
        return
    
    # Fix storage permissions
    if storage_path.exists():
        subprocess.run(['chmod', '-R', '775', str(storage_path)])
        subprocess.run(['chown', '-R', f'{user}:{group}', str(storage_path)])
        click.echo(f"Fixed storage permissions")
    
    # Fix bootstrap cache permissions  
    if bootstrap_cache.exists():
        subprocess.run(['chmod', '-R', '775', str(bootstrap_cache)])
        subprocess.run(['chown', '-R', f'{user}:{group}', str(bootstrap_cache)])
        click.echo(f"Fixed bootstrap cache permissions")
    
    click.echo("\nPermissions fixed!")


@setup_group.command(name="clean-state")
@click.option('--force', '-f', is_flag=True, help="Don't ask for confirmation")
@click.option('--no-rediscover', is_flag=True, help="Don't attempt to rediscover running stacks")
def clean_state(force, no_rediscover):
    """Clean up Docker state and temporary files."""
    if not force:
        if not click.confirm("This will reset all Docker state tracking. Continue?"):
            return
    
    StateManager.reset_state()
    click.echo("State reset complete")
    
    if not no_rediscover:
        click.echo("Attempting to rediscover running stacks...")
        discovered = StateManager.rediscover_running_stacks()
        if discovered > 0:
            click.echo(f"Re-discovered {discovered} active stack(s)")
        else:
            click.echo("No running stacks detected")