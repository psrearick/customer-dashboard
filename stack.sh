#!/bin/bash

# Laravel Performance Testing Environment Manager
# Simplifies running different Docker stack combinations for performance testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
PROJECT_NAME="laravel-perf"

# Function to get compose file for a component
get_compose_file() {
    local component=$1
    case $component in
        base) echo "docker-compose.yml" ;;
        traditional) echo "docker-compose.traditional.yml" ;;
        frankenphp) echo "docker-compose.frankenphp.yml" ;;
        octane) echo "docker-compose.octane.yml" ;;
        monitoring) echo "docker-compose.monitoring.yml" ;;
        multitenant) echo "docker-compose.multitenant.yml" ;;
        database-tools) echo "docker-compose.database-tools.yml" ;;
        *) echo "" ;;
    esac
}

# Function to get stack components
get_stack_components() {
    local stack=$1
    case $stack in
        traditional) echo "base traditional" ;;
        frankenphp) echo "base frankenphp" ;;
        octane) echo "base octane" ;;
        performance) echo "base traditional monitoring" ;;
        enterprise) echo "base traditional monitoring multitenant database-tools" ;;
        comparison) echo "base traditional frankenphp octane monitoring" ;;
        full) echo "base traditional frankenphp octane monitoring multitenant database-tools" ;;
        minimal) echo "base traditional" ;;
        *) echo "" ;;
    esac
}

# Function to check if stack exists
stack_exists() {
    local stack=$1
    local components
    components=$(get_stack_components "$stack")
    if [ -z "$components" ]; then
        return 1
    fi
    return 0
}

# Function to display usage information
show_usage() {
    echo -e "${BLUE}Laravel Performance Testing Environment Manager${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [STACK] [OPTIONS]"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  up         Start the specified stack"
    echo "  down       Stop the specified stack"
    echo "  restart    Restart the specified stack"
    echo "  logs       Show logs for the specified stack"
    echo "  status     Show status of running containers"
    echo "  clean      Remove all containers, networks, and volumes"
    echo "  list       List available stacks and components"
    echo "  setup      Create directory structure for configurations"
    echo "  validate   Validate configuration files for a stack"
    echo "  help       Show this help message"
    echo ""
    echo -e "${YELLOW}Available Stacks:${NC}"
    echo "  traditional    - Nginx + PHP-FPM (most common setup)"
    echo "  frankenphp     - FrankenPHP with worker mode"
    echo "  octane         - Laravel Octane with Swoole"
    echo "  performance    - Traditional + monitoring tools"
    echo "  enterprise     - Full enterprise stack with multi-tenancy"
    echo "  comparison     - All web servers + monitoring for benchmarking"
    echo "  full           - Everything (heavy resource usage)"
    echo "  minimal        - Just basic traditional setup"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -d, --detach   Run in background (daemon mode)"
    echo "  -b, --build    Force rebuild of images"
    echo "  -v, --verbose  Show verbose output"
    echo "  --no-deps      Don't start dependent services"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 setup                        # Create configuration directory structure"
    echo "  $0 validate traditional         # Validate configs for traditional stack"
    echo "  $0 up traditional               # Start traditional Nginx + PHP-FPM stack"
    echo "  $0 up performance -d            # Start performance testing stack in background"
    echo "  $0 restart frankenphp           # Restart FrankenPHP stack"
    echo "  $0 logs enterprise              # Show logs for enterprise stack"
    echo "  $0 down full                    # Stop the full stack"
    echo ""
}

# Function to validate stack name
validate_stack() {
    local stack=$1
    if ! stack_exists "$stack"; then
        echo -e "${RED}Error: Unknown stack '$stack'${NC}" >&2
        echo -e "${YELLOW}Available stacks:${NC} traditional frankenphp octane performance enterprise comparison full minimal" >&2
        exit 1
    fi
}

# Function to build compose file arguments
build_compose_args() {
    local stack=$1
    local components
    components=$(get_stack_components "$stack")
    local args=""

    for component in $components; do
        local file
        file=$(get_compose_file "$component")
        if [ -n "$file" ]; then
            args="$args -f $file"
        else
            echo -e "${RED}Error: Unknown component '$component' in stack '$stack'${NC}" >&2
            exit 1
        fi
    done

    echo "$args"
}

# Function to check if required files exist
check_files() {
    local stack=$1
    local components
    components=$(get_stack_components "$stack")
    local missing_files=""

    for component in $components; do
        local file
        file=$(get_compose_file "$component")
        if [ ! -f "$file" ]; then
            if [ -z "$missing_files" ]; then
                missing_files="$file"
            else
                missing_files="$missing_files $file"
            fi
        fi
    done

    # Check for required configuration files
    case $stack in
        *monitoring*|enterprise|full)
            local required_configs="docker/prometheus/prometheus.yml docker/grafana/datasources/datasources.yml"
            for config in $required_configs; do
                if [ ! -f "$config" ]; then
                    if [ -z "$missing_files" ]; then
                        missing_files="$config"
                    else
                        missing_files="$missing_files $config"
                    fi
                fi
            done
            ;;
    esac

    case $stack in
        traditional|enterprise|full)
            local nginx_configs="docker/nginx/nginx.conf docker/nginx/conf.d/laravel.conf"
            for config in $nginx_configs; do
                if [ ! -f "$config" ]; then
                    if [ -z "$missing_files" ]; then
                        missing_files="$config"
                    else
                        missing_files="$missing_files $config"
                    fi
                fi
            done
            ;;
    esac

    case $stack in
        frankenphp|enterprise|full)
            local frankenphp_configs="docker/frankenphp/Caddyfile"
            for config in $frankenphp_configs; do
                if [ ! -f "$config" ]; then
                    if [ -z "$missing_files" ]; then
                        missing_files="$config"
                    else
                        missing_files="$missing_files $config"
                    fi
                fi
            done
            ;;
    esac

    if [ -n "$missing_files" ]; then
        echo -e "${RED}Error: Missing required files:${NC}" >&2
        for file in $missing_files; do
            echo "  $file" >&2
        done
        echo -e "${YELLOW}Hint: Make sure you've created all configuration files for the selected stack.${NC}" >&2
        exit 1
    fi
}

# Function to display stack information
show_stack_info() {
    local stack=$1
    local components
    components=$(get_stack_components "$stack")

    echo -e "${BLUE}Stack: $stack${NC}"
    echo -e "${YELLOW}Components:${NC} $components"
    echo -e "${YELLOW}Compose files:${NC}"
    for component in $components; do
        local file
        file=$(get_compose_file "$component")
        echo "  - $file"
    done
    echo ""
}

# Function to run docker-compose command
run_compose() {
    local command=$1
    local stack=$2
    shift 2
    local additional_args="$*"

    validate_stack "$stack"
    check_files "$stack"

    local compose_args
    compose_args=$(build_compose_args "$stack")
    local full_command="docker-compose -p $PROJECT_NAME $compose_args $command $additional_args"

    if [ "$VERBOSE" = "true" ]; then
        echo -e "${BLUE}Executing:${NC} $full_command"
        echo ""
    fi

    eval "$full_command"
}

# Function to show status of all containers
show_status() {
    echo -e "${BLUE}Laravel Performance Testing Environment Status${NC}"
    echo ""

    # Check if any containers are running
    local running_containers
    running_containers=$(docker ps --filter "label=com.docker.compose.project=$PROJECT_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "")

    if [ -n "$running_containers" ]; then
        case "$running_containers" in
            *NAMES*) 
                echo -e "${YELLOW}No containers currently running${NC}"
                ;;
            *)
                echo -e "${GREEN}Running containers:${NC}"
                echo "$running_containers"
                ;;
        esac
    else
        echo -e "${YELLOW}No containers currently running${NC}"
    fi

    echo ""

    # Show network information
    local networks
    networks=$(docker network ls --filter "name=${PROJECT_NAME}" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" 2>/dev/null || echo "")
    if [ -n "$networks" ]; then
        case "$networks" in
            *NAME*) ;;
            *)
                echo -e "${GREEN}Active networks:${NC}"
                echo "$networks"
                ;;
        esac
    fi

    echo ""

    # Show volume information
    local volumes
    volumes=$(docker volume ls --filter "name=${PROJECT_NAME}" --format "table {{.Name}}\t{{.Driver}}" 2>/dev/null || echo "")
    if [ -n "$volumes" ]; then
        case "$volumes" in
            *"VOLUME NAME"*) ;;
            *)
                echo -e "${GREEN}Created volumes:${NC}"
                echo "$volumes"
                ;;
        esac
    fi
}

# Function to clean up everything
clean_all() {
    echo -e "${YELLOW}This will remove all containers, networks, and volumes for this project.${NC}"
    echo -e "${RED}This action cannot be undone!${NC}"
    echo ""
    printf "Are you sure you want to continue? (y/N): "
    read -r REPLY

    case "$REPLY" in
        [Yy]|[Yy][Ee][Ss])
            ;;
        *)
            echo "Cancelled."
            exit 0
            ;;
    esac

    echo -e "${BLUE}Cleaning up...${NC}"

    # Stop and remove containers
    docker-compose -p $PROJECT_NAME down --remove-orphans 2>/dev/null || true

    # Remove project-specific containers, networks, and volumes
    docker container prune --filter "label=com.docker.compose.project=$PROJECT_NAME" -f 2>/dev/null || true
    docker network prune --filter "name=${PROJECT_NAME}" -f 2>/dev/null || true
    docker volume prune --filter "name=${PROJECT_NAME}" -f 2>/dev/null || true

    echo -e "${GREEN}Cleanup complete!${NC}"
}

# Function to list available stacks
list_stacks() {
    echo -e "${BLUE}Available Stacks and Components${NC}"
    echo ""

    echo -e "${YELLOW}Predefined Stacks:${NC}"
    echo -e "  ${GREEN}traditional${NC}: base traditional"
    echo -e "  ${GREEN}frankenphp${NC}: base frankenphp"
    echo -e "  ${GREEN}octane${NC}: base octane"
    echo -e "  ${GREEN}performance${NC}: base traditional monitoring"
    echo -e "  ${GREEN}enterprise${NC}: base traditional monitoring multitenant database-tools"
    echo -e "  ${GREEN}comparison${NC}: base traditional frankenphp octane monitoring"
    echo -e "  ${GREEN}full${NC}: base traditional frankenphp octane monitoring multitenant database-tools"
    echo -e "  ${GREEN}minimal${NC}: base traditional"

    echo ""
    echo -e "${YELLOW}Available Components:${NC}"
    echo -e "  ${GREEN}base${NC}: docker-compose.yml"
    echo -e "  ${GREEN}traditional${NC}: docker-compose.traditional.yml"
    echo -e "  ${GREEN}frankenphp${NC}: docker-compose.frankenphp.yml"
    echo -e "  ${GREEN}octane${NC}: docker-compose.octane.yml"
    echo -e "  ${GREEN}monitoring${NC}: docker-compose.monitoring.yml"
    echo -e "  ${GREEN}multitenant${NC}: docker-compose.multitenant.yml"
    echo -e "  ${GREEN}database-tools${NC}: docker-compose.database-tools.yml"
}

# Function to create directory structure and example configs
setup_configs() {
    echo -e "${BLUE}Setting up configuration directory structure...${NC}"

    # Create directory structure
    local dirs="docker/prometheus docker/grafana/datasources docker/grafana/dashboards/laravel docker/grafana/dashboards/system docker/nginx/conf.d docker/frankenphp docker/php/conf.d docker/mysql/conf.d docker/mysql/init docker/redis docker/percona/scripts docker/artillery docker/proxysql"

    for dir in $dirs; do
        mkdir -p "$dir"
        echo "Created directory: $dir"
    done

    echo -e "${GREEN}Directory structure created successfully!${NC}"
    echo -e "${YELLOW}Note: You'll need to create the actual configuration files.${NC}"
    echo -e "${YELLOW}Refer to the documentation for example configurations.${NC}"
}

# Function to validate configuration files
validate_configs() {
    local stack=$1
    echo -e "${BLUE}Validating configuration files for stack: $stack${NC}"

    # Validate Prometheus config if monitoring is included
    case $stack in
        *monitoring*|enterprise|full)
            if [ -f "docker/prometheus/prometheus.yml" ]; then
                echo "✓ Prometheus configuration found"
            else
                echo -e "${YELLOW}⚠ Prometheus configuration missing${NC}"
            fi
            ;;
    esac

    # Validate Nginx config if traditional stack
    case $stack in
        traditional|enterprise|full)
            if [ -f "docker/nginx/nginx.conf" ]; then
                echo "✓ Nginx configuration found"
            else
                echo -e "${YELLOW}⚠ Nginx configuration missing${NC}"
            fi
            ;;
    esac

    # Validate FrankenPHP config
    case $stack in
        frankenphp|enterprise|full)
            if [ -f "docker/frankenphp/Caddyfile" ]; then
                echo "✓ FrankenPHP Caddyfile found"
            else
                echo -e "${YELLOW}⚠ FrankenPHP Caddyfile missing${NC}"
            fi
            ;;
    esac

    echo -e "${GREEN}Configuration validation complete${NC}"
}

# Parse command line arguments
VERBOSE=false
DETACH=false
BUILD=false
NO_DEPS=false

while [ $# -gt 0 ]; do
    case $1 in
        up|down|restart|logs|build|pull)
            COMMAND=$1
            shift
            ;;
        status|clean|list|setup|help)
            COMMAND=$1
            shift
            break
            ;;
        validate)
            COMMAND=$1
            shift
            ;;
        -d|--detach)
            DETACH=true
            shift
            ;;
        -b|--build)
            BUILD=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-deps)
            NO_DEPS=true
            shift
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}" >&2
            show_usage
            exit 1
            ;;
        *)
            STACK=$1
            shift
            ;;
    esac
done

# Handle commands that don't require a stack
case ${COMMAND:-} in
    status)
        show_status
        exit 0
        ;;
    clean)
        clean_all
        exit 0
        ;;
    list)
        list_stacks
        exit 0
        ;;
    setup)
        setup_configs
        exit 0
        ;;
    help|"")
        show_usage
        exit 0
        ;;
esac

# Handle commands that require a stack
case ${COMMAND:-} in
    validate)
        if [ -z "${STACK:-}" ]; then
            echo -e "${RED}Error: Stack name is required for 'validate' command${NC}" >&2
            show_usage
            exit 1
        fi
        validate_stack "$STACK"
        validate_configs "$STACK"
        exit 0
        ;;
esac

# Validate that we have both command and stack for commands that need them
if [ -z "${COMMAND:-}" ]; then
    echo -e "${RED}Error: Command is required${NC}" >&2
    show_usage
    exit 1
fi

# Commands that require a stack
case $COMMAND in
    up|down|restart|logs|build|pull)
        if [ -z "${STACK:-}" ]; then
            echo -e "${RED}Error: Stack name is required for '$COMMAND' command${NC}" >&2
            show_usage
            exit 1
        fi
        ;;
esac

# Build additional arguments
ADDITIONAL_ARGS=""

if [ "$DETACH" = "true" ]; then
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS -d"
fi

if [ "$BUILD" = "true" ]; then
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS --build"
fi

if [ "$NO_DEPS" = "true" ]; then
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS --no-deps"
fi

# Show stack information in verbose mode
if [ "$VERBOSE" = "true" ]; then
    show_stack_info "$STACK"
fi

# Execute the command
case $COMMAND in
    up)
        echo -e "${GREEN}Starting $STACK stack...${NC}"
        run_compose "up" "$STACK" "$ADDITIONAL_ARGS"
        ;;
    down)
        echo -e "${YELLOW}Stopping $STACK stack...${NC}"
        run_compose "down" "$STACK" "$ADDITIONAL_ARGS"
        ;;
    restart)
        echo -e "${YELLOW}Restarting $STACK stack...${NC}"
        run_compose "restart" "$STACK" "$ADDITIONAL_ARGS"
        ;;
    logs)
        run_compose "logs" "$STACK" "$ADDITIONAL_ARGS"
        ;;
    build)
        echo -e "${BLUE}Building $STACK stack...${NC}"
        run_compose "build" "$STACK" "$ADDITIONAL_ARGS"
        ;;
    pull)
        echo -e "${BLUE}Pulling images for $STACK stack...${NC}"
        run_compose "pull" "$STACK" "$ADDITIONAL_ARGS"
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$COMMAND'${NC}" >&2
        show_usage
        exit 1
        ;;
esac