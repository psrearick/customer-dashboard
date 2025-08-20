import subprocess
from typing import List


class ErrorHandler:
    """Centralized error handling with helpful suggestions."""
    
    @staticmethod
    def handle_docker_error(error: Exception) -> None:
        """Handle Docker-related errors with helpful suggestions."""
        error_message = str(error)
        
        if "docker daemon" in error_message.lower() or "cannot connect" in error_message.lower():
            ErrorHandler._print_error(
                "Docker daemon not running",
                [
                    "Start Docker Desktop or Docker service",
                    "Check Docker installation: docker --version",
                    "Verify Docker is running: docker info"
                ]
            )
        elif "permission denied" in error_message.lower():
            ErrorHandler._print_error(
                "Docker permission denied",
                [
                    "Add user to docker group: sudo usermod -aG docker $USER",
                    "Restart terminal session or run: newgrp docker",
                    "Try running with sudo (not recommended for production)"
                ]
            )
        elif "no such container" in error_message.lower():
            ErrorHandler._print_error(
                "Container not found",
                [
                    "Check running containers: docker ps",
                    "Start the required stack: app stack up",
                    "Check stack status: app stack status"
                ]
            )
        else:
            ErrorHandler._print_error(
                f"Docker error: {error_message}",
                [
                    "Check Docker logs: docker logs <container>",
                    "Restart Docker service",
                    "Check available resources: docker system df"
                ]
            )
    
    @staticmethod
    def handle_container_not_found(container_name: str) -> None:
        """Handle missing container errors with stack suggestions."""
        from .state_manager import StateManager
        
        active_stacks = StateManager.get_active_stacks()
        
        suggestions = [
            "Start a stack first: app stack up",
            "Check stack status: app stack status"
        ]
        
        if active_stacks:
            suggestions.insert(0, f"Available stacks: {', '.join(active_stacks.keys())}")
        
        ErrorHandler._print_error(
            f"Container '{container_name}' not running",
            suggestions
        )
    
    @staticmethod
    def handle_service_not_available(service_type: str) -> None:
        """Handle missing service errors with setup suggestions."""
        service_suggestions = {
            'php': [
                "Start a stack with PHP: app stack up [default|octane|frankenphp]",
                "Check PHP container: docker ps | grep php"
            ],
            'database': [
                "Start MySQL service: app stack up",
                "Check database container: docker ps | grep mysql"
            ],
            'cache': [
                "Start Redis service: app stack up", 
                "Check Redis container: docker ps | grep redis"
            ],
            'build': [
                "Start Node.js service: app stack up",
                "Check Node container: docker ps | grep node"
            ]
        }
        
        suggestions = service_suggestions.get(service_type, [
            f"Start services that include {service_type}",
            "Check available stacks: app list"
        ])
        
        ErrorHandler._print_error(
            f"No {service_type} service available",
            suggestions
        )
    
    @staticmethod
    def handle_git_error(error: Exception, branch_name: str = None) -> None:
        """Handle git operation errors."""
        error_message = str(error)
        
        if "not a git repository" in error_message.lower():
            ErrorHandler._print_error(
                "Not in a git repository",
                [
                    "Initialize git repository: git init",
                    "Clone the project repository",
                    "Navigate to project directory"
                ]
            )
        elif branch_name and "pathspec" in error_message.lower():
            ErrorHandler._print_error(
                f"Branch '{branch_name}' not found",
                [
                    "List available branches: git branch -a",
                    "Fetch remote branches: git fetch origin",
                    f"Create branch: git checkout -b {branch_name}"
                ]
            )
        elif "uncommitted changes" in error_message.lower():
            ErrorHandler._print_error(
                "Uncommitted changes detected",
                [
                    "Commit changes: git add . && git commit -m 'WIP'",
                    "Stash changes: git stash",
                    "Discard changes: git checkout -- ."
                ]
            )
        else:
            ErrorHandler._print_error(
                f"Git error: {error_message}",
                [
                    "Check git status: git status",
                    "Check current branch: git branch",
                    "Check remote repositories: git remote -v"
                ]
            )
    
    @staticmethod
    def handle_laravel_error(error: Exception, command: str) -> None:
        """Handle Laravel/Artisan command errors."""
        error_message = str(error)
        
        if "connection refused" in error_message.lower() or "could not find driver" in error_message.lower():
            ErrorHandler._print_error(
                "Database connection failed",
                [
                    "Check database container: app dev mysql --dry-run",
                    "Verify .env database settings",
                    "Start database service: app stack up"
                ]
            )
        elif "key:generate" in command and "encryption key" in error_message.lower():
            ErrorHandler._print_error(
                "Application key not set",
                [
                    "Generate app key: app dev artisan key:generate",
                    "Check .env file has APP_KEY setting"
                ]
            )
        elif "migrate" in command:
            ErrorHandler._print_error(
                "Migration failed",
                [
                    "Check database connection: app dev mysql",
                    "Reset migrations: app dev artisan migrate:fresh",
                    "Check migration files for syntax errors"
                ]
            )
        else:
            ErrorHandler._print_error(
                f"Laravel command failed: {command}",
                [
                    "Check container logs: app stack logs",
                    "Verify PHP container is running: app dev shell",
                    "Check artisan commands: app dev artisan list"
                ]
            )
    
    @staticmethod
    def format_error_message(error: str, suggestions: List[str]) -> str:
        """Format error message with suggestions."""
        lines = [f"Error: {error}"]
        
        for suggestion in suggestions:
            lines.append(f"  → {suggestion}")
        
        return '\n'.join(lines)
    
    @staticmethod
    def check_common_issues() -> List[str]:
        """Check for common configuration issues."""
        issues = []
        
        try:
            subprocess.run(['docker', 'info'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Docker is not running or not installed")
        
        from .laravel_utils import LaravelUtils
        if not LaravelUtils.validate_laravel_project():
            issues.append("Not in a Laravel project directory")
        
        env_path = LaravelUtils.get_laravel_env_path()
        if not env_path.exists():
            issues.append(".env file not found")
        
        try:
            subprocess.run(['git', 'status'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Not in a git repository or git not installed")
        
        return issues
    
    @staticmethod
    def _print_error(error: str, suggestions: List[str], context: str = None) -> None:
        """Print formatted error message."""
        import sys
        
        message = ErrorHandler.format_error_message(error, suggestions)
        
        if context:
            message += f"\n\nContext: {context}"
        
        print(message, file=sys.stderr)
    
    @staticmethod
    def suggest_next_steps(current_command: str) -> List[str]:
        """Suggest logical next steps based on current command context."""
        if 'stack up' in current_command:
            return [
                "Check stack status: app stack status",
                "View access URLs: app urls",
                "Run development commands: app dev --help"
            ]
        elif 'setup fresh' in current_command:
            return [
                "Run tests: app dev test",
                "Start development: app dev npm run dev",
                "Check application: app urls"
            ]
        elif 'setup branch' in current_command:
            return [
                "Explore branch features",
                "Check blog post for details",
                "Run branch-specific tests"
            ]
        else:
            return [
                "Check overall status: app status",
                "View available commands: app --help",
                "Check documentation"
            ]