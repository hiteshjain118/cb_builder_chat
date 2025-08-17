#!/bin/bash
# Chat App Terminal Interface
# A simple wrapper for the send_message.py script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
CHAT_URL="http://localhost:5002"
SESSION_ID="terminal-session"
PYTHON_SCRIPT="send_message.py"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to show help
show_help() {
    echo "Chat App Terminal Interface"
    echo "=========================="
    echo ""
    echo "Usage:"
    echo "  ./chat.sh [message] [options]"
    echo ""
    echo "Examples:"
    echo "  ./chat.sh \"Hello, how are you?\""
    echo "  ./chat.sh \"What's the weather?\" --session weather-chat"
    echo "  ./chat.sh \"Show me my data\" --login user@example.com --password mypass"
    echo "  ./chat.sh \"Show me my data\" --token your-jwt-token"
    echo "  ./chat.sh --history --session my-session --login user@example.com --password mypass"
    echo "  ./chat.sh --status"
    echo "  ./chat.sh --check-env"
    echo ""
    echo "Options:"
    echo "  --session, -s    Session ID (default: terminal-session)"
    echo "  --user, -u       User ID"
    echo "  --token, -t      Supabase JWT token for authentication"
    echo "  --login, -l      Supabase user email for authentication"
    echo "  --password, -p   Supabase user password for authentication"
    echo "  --url            Chat app URL (default: http://localhost:5002)"
    echo "  --supabase-url   Supabase project URL (overrides .env)"
    echo "  --supabase-key   Supabase anonymous key (overrides .env)"
    echo "  --history        Get conversation history instead of sending message"
    echo "  --status         Check chat app status"
    echo "  --check-env      Check environment configuration (.env file)"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Quick Commands:"
    echo "  ./chat.sh --status                    # Check if app is running"
    echo "  ./chat.sh --check-env                # Check .env configuration"
    echo "  ./chat.sh \"Hello\"                    # Send simple message"
    echo "  ./chat.sh --history                   # Get conversation history"
    echo ""
    echo "Authentication Examples:"
    echo "  # Using email/password (from .env file)"
    echo "  ./chat.sh \"Hello\" --login user@example.com --password mypass"
    echo ""
    echo "  # Using existing token"
    echo "  ./chat.sh \"Hello\" --token your-jwt-token"
    echo ""
    echo "  # Custom Supabase project (overrides .env)"
    echo "  ./chat.sh \"Hello\" --supabase-url https://your-project.supabase.co --supabase-key your-key --login user@example.com --password mypass"
    echo ""
    echo "Environment Setup:"
    echo "  # Create .env file in chat directory:"
    echo "  SUPABASE_URL=https://your-project.supabase.co"
    echo "  SUPABASE_ANON_KEY=your-anon-key"
}

# Function to check if Python script exists
check_python_script() {
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "Python script '$PYTHON_SCRIPT' not found!"
        print_info "Make sure you're in the chat directory and the script exists."
        exit 1
    fi
}

# Function to check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_error "Python is not installed or not in PATH!"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
}

# Function to activate virtual environment if it exists
activate_venv() {
    if [ -d "venv" ]; then
        print_info "Activating virtual environment..."
        source venv/bin/activate
    fi
}

# Function to check environment variables and .env file
check_env_vars() {
    print_info "Checking environment configuration..."
    
    # Check if .env file exists
    if [ -f ".env" ]; then
        print_status ".env file found"
        
        # Check if python-dotenv is available
        if $PYTHON_CMD -c "import dotenv" 2>/dev/null; then
            print_status "python-dotenv is available"
        else
            print_warning "python-dotenv not installed"
            print_info "Install with: pip install python-dotenv"
            print_info "Or set environment variables manually"
        fi
    else
        print_warning ".env file not found"
        print_info "Create .env file with your Supabase credentials:"
        echo "  SUPABASE_URL=https://your-project.supabase.co"
        echo "  SUPABASE_ANON_KEY=your-anon-key"
        echo ""
    fi
    
    # Check if environment variables are set
    if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_ANON_KEY" ]; then
        print_status "Environment variables set"
        print_info "SUPABASE_URL: $SUPABASE_URL"
        print_info "SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY:0:20}..."
    else
        print_warning "SUPABASE_URL and SUPABASE_ANON_KEY environment variables not set"
        print_info "Set them in your shell or create a .env file"
        echo ""
    fi
}

# Function to check environment configuration using Python script
check_env_config() {
    print_info "Checking environment configuration with Python script..."
    $PYTHON_CMD "$PYTHON_SCRIPT" --check-env
}

# Main script logic
main() {
    # Check if Python script exists
    check_python_script
    
    # Check if Python is available
    check_python
    
    # Activate virtual environment if it exists
    activate_venv
    
    # Check environment variables
    check_env_vars
    
    # If no arguments, show help
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # Check for help flag
    if [[ "$1" == "--help" || "$1" == "-h" ]]; then
        show_help
        exit 0
    fi
    
    # Check for environment check flag
    if [[ "$1" == "--check-env" ]]; then
        check_env_config
        exit 0
    fi
    
    # Run the Python script with all arguments
    print_info "Running chat script..."
    $PYTHON_CMD "$PYTHON_SCRIPT" "$@"
}

# Run main function with all arguments
main "$@" 