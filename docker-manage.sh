#!/bin/bash
# Docker management script for IPL Analytics

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project name
# Project name
PROJECT_NAME="ipl-analysis-and-predictions"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build Docker image
build() {
    print_status "Building Docker image for IPL Analytics..."
    docker build -t $PROJECT_NAME .
    print_status "Docker image built successfully!"
}

# Function to run container
run() {
    print_status "Starting IPL Analytics container..."
    docker-compose up -d
    print_status "Container started! Visit http://localhost:8501"
}

# Function to stop container
stop() {
    print_status "Stopping IPL Analytics container..."
    docker-compose down
    print_status "Container stopped!"
}

# Function to restart container
restart() {
    stop
    run
}

# Function to view logs
logs() {
    print_status "Showing container logs..."
    docker-compose logs -f ipl-analysis-and-predictions
}

# Function to clean up
clean() {
    print_warning "Cleaning up Docker images and containers..."
    docker-compose down
    docker rmi $PROJECT_NAME 2>/dev/null || true
    docker system prune -f
    print_status "Cleanup completed!"
}

# Function to show status
status() {
    print_status "Docker container status:"
    docker-compose ps
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    run)
        run
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    clean)
        clean
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {build|run|stop|restart|logs|clean|status}"
        echo ""
        echo "Commands:"
        echo "  build   - Build the Docker image"
        echo "  run     - Start the container"
        echo "  stop    - Stop the container"
        echo "  restart - Restart the container"
        echo "  logs    - View container logs"
        echo "  clean   - Clean up images and containers"
        echo "  status  - Show container status"
        exit 1
esac
