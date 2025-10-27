#!/bin/bash

# GitHub Actions Credential Setup Helper
# This script helps you set up credentials for automated court monitoring

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

# Function to check if GitHub CLI is installed
check_gh_cli() {
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed!"
        print_status "Please install it first:"
        print_status "  macOS: brew install gh"
        print_status "  Ubuntu: sudo apt install gh"
        print_status "  Windows: winget install GitHub.cli"
        exit 1
    fi
    print_success "GitHub CLI is installed"
}

# Function to check if user is authenticated
check_gh_auth() {
    if ! gh auth status &> /dev/null; then
        print_error "Not authenticated with GitHub!"
        print_status "Please run: gh auth login"
        exit 1
    fi
    print_success "Authenticated with GitHub"
}

# Function to get repository name
get_repo_name() {
    if [ -d ".git" ]; then
        REPO_NAME=$(git remote get-url origin | sed 's/.*github.com[:/]\([^.]*\).*/\1/')
        print_success "Detected repository: $REPO_NAME"
    else
        print_error "Not in a Git repository!"
        exit 1
    fi
}

# Function to prompt for credentials
prompt_credentials() {
    print_status "Setting up credentials for automated court monitoring..."
    echo ""
    
    # BTC Credentials
    print_status "=== BTC Tennis Club Credentials ==="
    read -p "BTC Username (email): " BTC_USERNAME
    read -s -p "BTC Password: " BTC_PASSWORD
    echo ""
    read -p "BTC Notification Email: " BTC_NOTIFICATION_EMAIL
    read -s -p "BTC Gmail App Password: " BTC_GMAIL_APP_PASSWORD
    echo ""
    read -p "BTC SMS Phone (+1234567890): " BTC_SMS_PHONE
    echo ""
    
    # UBC Credentials
    print_status "=== UBC Tennis Centre Credentials ==="
    read -p "UBC Username (email): " UBC_USERNAME
    read -s -p "UBC Password: " UBC_PASSWORD
    echo ""
    read -p "UBC Notification Email: " UBC_NOTIFICATION_EMAIL
    read -s -p "UBC Gmail App Password: " UBC_GMAIL_APP_PASSWORD
    echo ""
    read -p "UBC SMS Phone (+1234567890): " UBC_SMS_PHONE
    echo ""
    
    # Twilio Credentials
    print_status "=== Twilio Credentials (Optional) ==="
    read -p "Twilio SID: " TWILIO_SID
    read -s -p "Twilio Token: " TWILIO_TOKEN
    echo ""
    read -p "Twilio Phone (+1234567890): " TWILIO_PHONE
    echo ""
}

# Function to set secrets
set_secrets() {
    print_status "Setting GitHub Secrets..."
    
    # BTC Secrets
    gh secret set BTC_USERNAME --body "$BTC_USERNAME"
    gh secret set BTC_PASSWORD --body "$BTC_PASSWORD"
    gh secret set BTC_NOTIFICATION_EMAIL --body "$BTC_NOTIFICATION_EMAIL"
    gh secret set BTC_GMAIL_APP_PASSWORD --body "$BTC_GMAIL_APP_PASSWORD"
    gh secret set BTC_SMS_PHONE --body "$BTC_SMS_PHONE"
    
    # UBC Secrets
    gh secret set UBC_USERNAME --body "$UBC_USERNAME"
    gh secret set UBC_PASSWORD --body "$UBC_PASSWORD"
    gh secret set UBC_NOTIFICATION_EMAIL --body "$UBC_NOTIFICATION_EMAIL"
    gh secret set UBC_GMAIL_APP_PASSWORD --body "$UBC_GMAIL_APP_PASSWORD"
    gh secret set UBC_SMS_PHONE --body "$UBC_SMS_PHONE"
    
    # Twilio Secrets
    if [ ! -z "$TWILIO_SID" ]; then
        gh secret set TWILIO_SID --body "$TWILIO_SID"
        gh secret set TWILIO_TOKEN --body "$TWILIO_TOKEN"
        gh secret set TWILIO_PHONE --body "$TWILIO_PHONE"
    fi
    
    print_success "All secrets set successfully!"
}

# Function to verify secrets
verify_secrets() {
    print_status "Verifying secrets..."
    
    # List all secrets
    gh secret list
    
    print_success "Secrets verification complete!"
}

# Function to test workflow
test_workflow() {
    print_status "Testing periodic monitoring workflow..."
    
    # Trigger the workflow
    gh workflow run periodic-monitoring.yml
    
    print_success "Workflow triggered! Check the Actions tab for results."
    print_status "You can monitor progress with: gh run list"
}

# Function to show help
show_help() {
    echo "GitHub Actions Credential Setup Helper"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup     Interactive setup of all credentials"
    echo "  verify    Verify that secrets are properly set"
    echo "  test      Test the periodic monitoring workflow"
    echo "  list      List all current secrets"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 verify"
    echo "  $0 test"
}

# Main script logic
case "${1:-help}" in
    setup)
        check_gh_cli
        check_gh_auth
        get_repo_name
        prompt_credentials
        set_secrets
        verify_secrets
        print_success "Setup complete! Your credentials are now securely stored in GitHub Secrets."
        print_status "You can now run: $0 test"
        ;;
    verify)
        check_gh_cli
        check_gh_auth
        verify_secrets
        ;;
    test)
        check_gh_cli
        check_gh_auth
        test_workflow
        ;;
    list)
        check_gh_cli
        check_gh_auth
        gh secret list
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
