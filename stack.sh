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

# Available compose files
declare -A COMPOSE_FILES=(
    ["base"]="docker-compose.yml"
    ["traditional"]="docker-compose.traditional.yml"
    ["frankenphp"]="docker-compose.frankenphp.yml"
    ["octane"]="docker-compose.octane.yml"
    ["monitoring"]="docker-compose.monitoring.yml"
    ["multitenant"]="docker-compose.multitenant.yml"
    ["database-tools"]="docker-compose.database-tools.yml"
)

# Predefined stack configurations
declare -A STACKS=(
    ["traditional"]="base traditional"
    ["frankenphp"]="base frankenphp"
    ["octane"]="base octane"
    ["performance"]="base traditional monitoring"
    ["enterprise"]="base traditional monitoring multitenant database-tools"
    ["comparison"]="base traditional frankenphp octane monitoring"
    ["full"]="base traditional frankenphp octane monitoring multitenant database-tools"
    ["minimal"]="base traditional"
)

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
    if [[ ! ${STACKS[$stack]+_} ]]; then
        echo -e "${RED}Error: Unknown stack '$stack'${NC}" >&2
        echo -e "${YELLOW}Available stacks:${NC} ${!STACKS[*]}" >&2
        exit 1
    fi
}

# Function to build compose file arguments
build_compose_args() {
    local stack=$1
    local components=${STACKS[$stack]}
    local args=""

    for component in $components; do
        if [[ ${COMPOSE_FILES[$component]+_} ]]; then
            args="$args -f ${COMPOSE_FILES[$component]}"
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
    local components=${STACKS[$stack]}
    local missing_files=()

    for component in $components; do
        local file=${COMPOSE_FILES[$component]}
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done

    # Check for required configuration files
    if [[ "$stack" == *"monitoring"* ]] || [[ "$stack" == "enterprise" ]] || [[ "$stack" == "full" ]]; then
        local required_configs=(
            "docker/prometheus/prometheus.yml"
            "docker/grafana/datasources/datasources.yml"
        )

        for config in "${required_configs[@]}"; do
            if [[ ! -f "$config" ]]; then
                missing_files+=("$config")
            fi
        done
    fi

    if [[ "$stack" == "traditional" ]] || [[ "$stack" == "enterprise" ]] || [[ "$stack" == "full" ]]; then
        local nginx_configs=(
            "docker/nginx/nginx.conf"
            "docker/nginx/conf.d/laravel.conf"
        )

        for config in "${nginx_configs[@]}"; do
            if [[ ! -f "$config" ]]; then
                missing_files+=("$config")
            fi
        done
    fi

    if [[ "$stack" == "frankenphp" ]] || [[ "$stack" == "enterprise" ]] || [[ "$stack" == "full" ]]; then
        local frankenphp_configs=(
            "docker/frankenphp/Caddyfile"
        )

        for config in "${frankenphp_configs[@]}"; do
            if [[ ! -f "$config" ]]; then
                missing_files+=("$config")
            fi
        done
    fi

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo -e "${RED}Error: Missing required files:${NC}" >&2
        printf '  %s\n' "${missing_files[@]}" >&2
        echo -e "${YELLOW}Hint: Make sure you've created all configuration files for the selected stack.${NC}" >&2
        exit 1
    fi
}

# Function to display stack information
show_stack_info() {
    local stack=$1
    local components=${STACKS[$stack]}

    echo -e "${BLUE}Stack: $stack${NC}"
    echo -e "${YELLOW}Components:${NC} $components"
    echo -e "${YELLOW}Compose files:${NC}"
    for component in $components; do
        echo "  - ${COMPOSE_FILES[$component]}"
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

    if [[ "$VERBOSE" == "true" ]]; then
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

    if [[ -n "$running_containers" && "$running_containers" != *"NAMES"* ]]; then
        echo -e "${GREEN}Running containers:${NC}"
        echo "$running_containers"
    else
        echo -e "${YELLOW}No containers currently running${NC}"
    fi

    echo ""

    # Show network information
    local networks
    networks=$(docker network ls --filter "name=${PROJECT_NAME}" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" 2>/dev/null || echo "")
    if [[ -n "$networks" && "$networks" != *"NAME"* ]]; then
        echo -e "${GREEN}Active networks:${NC}"
        echo "$networks"
    fi

    echo ""

    # Show volume information
    local volumes
    volumes=$(docker volume ls --filter "name=${PROJECT_NAME}" --format "table {{.Name}}\t{{.Driver}}" 2>/dev/null || echo "")
    if [[ -n "$volumes" && "$volumes" != *"VOLUME NAME"* ]]; then
        echo -e "${GREEN}Created volumes:${NC}"
        echo "$volumes"
    fi
}

# Function to clean up everything
clean_all() {
    echo -e "${YELLOW}This will remove all containers, networks, and volumes for this project.${NC}"
    echo -e "${RED}This action cannot be undone!${NC}"
    echo ""
    read -p "Are you sure you want to continue? (y/N): " -r

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi

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
    for stack in "${!STACKS[@]}"; do
        echo -e "  ${GREEN}$stack${NC}: ${STACKS[$stack]}"
    done

    echo ""
    echo -e "${YELLOW}Available Components:${NC}"
    for component in "${!COMPOSE_FILES[@]}"; do
        echo -e "  ${GREEN}$component${NC}: ${COMPOSE_FILES[$component]}"
    done
}

# Function to create directory structure and example configs
setup_configs() {
    echo -e "${BLUE}Setting up configuration directory structure...${NC}"

    # Create directory structure
    local dirs=(
        "docker/prometheus"
        "docker/grafana/datasources"
        "docker/grafana/dashboards/laravel"
        "docker/grafana/dashboards/system"
        "docker/nginx/conf.d"
        "docker/frankenphp"
        "docker/php/conf.d"
        "docker/mysql/conf.d"
        "docker/mysql/init"
        "docker/redis"
        "docker/percona/scripts"
        "docker/artillery"
        "docker/proxysql"
    )

    for dir in "${dirs[@]}"; do
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
    if [[ "$stack" == *"monitoring"* ]] || [[ "$stack" == "enterprise" ]] || [[ "$stack" == "full" ]]; then
        if [[ -f "docker/prometheus/prometheus.yml" ]]; then
            echo "✓ Prometheus configuration found"
        else
            echo -e "${YELLOW}⚠ Prometheus configuration missing${NC}"
        fi
    fi

    # Validate Nginx config if traditional stack
    if [[ "$stack" == "traditional" ]] || [[ "$stack" == "enterprise" ]] || [[ "$stack" == "full" ]]; then
        if [[ -f "docker/nginx/nginx.conf" ]]; then
            echo "✓ Nginx configuration found"
        else
            echo -e "${YELLOW}⚠ Nginx configuration missing${NC}"
        fi
    fi

    # Validate FrankenPHP config
    if [[ "$stack" == "frankenphp" ]] || [[ "$stack" == "enterprise" ]] || [[ "$stack" == "full" ]]; then
        if [[ -f "docker/frankenphp/Caddyfile" ]]; then
            echo "✓ FrankenPHP Caddyfile found"
        else
            echo -e "${YELLOW}⚠ FrankenPHP Caddyfile missing${NC}"
        fi
    fi

    echo -e "${GREEN}Configuration validation complete${NC}"
}

# Parse command line arguments
VERBOSE=false
DETACH=false
BUILD=false
NO_DEPS=false

while [[ $# -gt 0 ]]; do
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
        validate_stack "$STACK"
        validate_configs "$STACK"
        exit 0
        ;;
esac

# Validate that we have both command and stack for commands that need them
if [[ -z ${COMMAND:-} ]]; then
    echo -e "${RED}Error: Command is required${NC}" >&2
    show_usage
    exit 1
fi

# Commands that require a stack
case $COMMAND in
    up|down|restart|logs|build|pull)
        if [[ -z ${STACK:-} ]]; then
            echo -e "${RED}Error: Stack name is required for '$COMMAND' command${NC}" >&2
            show_usage
            exit 1
        fi
        ;;
esac

# Build additional arguments
ADDITIONAL_ARGS=""

if [[ "$DETACH" == "true" ]]; then
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS -d"
fi

if [[ "$BUILD" == "true" ]]; then
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS --build"
fi

if [[ "$NO_DEPS" == "true" ]]; then
    ADDITIONAL_ARGS="$ADDITIONAL_ARGS --no-deps"
fi

# Show stack information in verbose mode
if [[ "$VERBOSE" == "true" ]]; then
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