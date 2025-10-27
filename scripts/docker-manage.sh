#!/bin/bash

# Tennis Bot Docker Management Script
# One-click experience for running BTC and UBC tennis bots

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        print_status "Creating .env file from template..."
        cp env.example .env
        print_warning "Please edit .env file with your credentials before running the bots!"
        print_status "Required: BTC_USERNAME, BTC_PASSWORD, BTC_NOTIFICATION_EMAIL, BTC_GMAIL_APP_PASSWORD"
        exit 1
    fi
}

# Function to start bots
start_bots() {
    print_status "Starting Tennis Bot containers..."
    
    # Start both services
    docker compose up -d
    
    print_success "Tennis Bot containers started!"
    print_status "BTC Bot: docker compose logs -f btc-tennis-bot"
    print_status "UBC Bot: docker compose logs -f ubc-tennis-bot"
    print_status "Both Bots: docker compose logs -f"
}

# Function to stop bots
stop_bots() {
    print_status "Stopping Tennis Bot containers..."
    docker compose down
    print_success "Tennis Bot containers stopped!"
}

# Function to restart bots
restart_bots() {
    print_status "Restarting Tennis Bot containers..."
    docker compose restart
    print_success "Tennis Bot containers restarted!"
}

# Function to show logs
show_logs() {
    if [ "$1" = "btc" ]; then
        docker compose logs -f btc-tennis-bot
    elif [ "$1" = "ubc" ]; then
        docker compose logs -f ubc-tennis-bot
    else
        docker compose logs -f
    fi
}

# Function to show status
show_status() {
    print_status "Tennis Bot Container Status:"
    echo ""
    docker compose ps --format table
    echo ""
    print_status "Container Health Check:"
    docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
}

# Function to build containers
build_containers() {
    print_status "Building Tennis Bot containers..."
    docker compose build --no-cache
    print_success "Tennis Bot containers built!"
}

# Function to show help
show_help() {
    echo "Tennis Bot Docker Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start both BTC and UBC tennis bots"
    echo "  stop      Stop both tennis bots"
    echo "  restart   Restart both tennis bots"
    echo "  logs      Show logs for both bots"
    echo "  logs btc  Show logs for BTC bot only"
    echo "  logs ubc  Show logs for UBC bot only"
    echo "  status    Show container status"
    echo "  build     Build containers from scratch"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs btc"
    echo "  $0 status"
}

# Main script logic
case "${1:-help}" in
    start)
        check_env_file
        start_bots
        ;;
    stop)
        stop_bots
        ;;
    restart)
        restart_bots
        ;;
    logs)
        show_logs "$2"
        ;;
    status)
        show_status
        ;;
    build)
        build_containers
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
