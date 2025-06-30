#!/bin/bash

# Setup script for Claude Code SDK integration in Anvil CLI
# This script installs all necessary dependencies and helps configure the API key

set -e

echo "🔨 Setting up Claude Code SDK integration for Anvil CLI"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Node.js is installed
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed!"
    print_info "Please install Node.js first:"
    print_info "  • macOS: brew install node"
    print_info "  • Ubuntu/Debian: sudo apt install nodejs npm"
    print_info "  • Or download from: https://nodejs.org/"
    exit 1
else
    NODE_VERSION=$(node --version)
    print_status "Node.js is installed: $NODE_VERSION"
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    print_error "npm is not available!"
    print_info "Please install npm along with Node.js"
    exit 1
else
    NPM_VERSION=$(npm --version)
    print_status "npm is available: $NPM_VERSION"
fi

# Check if Python 3.10+ is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    print_info "Please install Python 3.10 or higher"
    exit 1
else
    PYTHON_VERSION=$(python3 --version)
    print_status "Python is installed: $PYTHON_VERSION"
fi

echo ""
echo "Installing dependencies..."

# Install Claude Code CLI globally
print_info "Installing Claude Code CLI..."
if npm install -g @anthropic-ai/claude-code; then
    print_status "Claude Code CLI installed successfully"
else
    print_error "Failed to install Claude Code CLI"
    print_info "You may need to run with sudo or check your npm permissions"
    exit 1
fi

# Install Python dependencies
print_info "Installing Python dependencies..."

# Try different installation methods
if command -v pipx &> /dev/null; then
    print_info "Using pipx to install claude-code-sdk..."
    if pipx install claude-code-sdk; then
        print_status "claude-code-sdk installed with pipx"
    else
        print_warning "pipx installation failed, trying pip..."
    fi
elif python3 -m pip install --user claude-code-sdk anyio; then
    print_status "Python dependencies installed with pip --user"
elif python3 -m pip install claude-code-sdk anyio --break-system-packages; then
    print_warning "Python dependencies installed with --break-system-packages"
    print_warning "This may affect your system Python installation"
else
    print_error "Failed to install Python dependencies"
    print_info "Please try one of these methods manually:"
    print_info "  • pipx install claude-code-sdk"
    print_info "  • python3 -m venv venv && source venv/bin/activate && pip install claude-code-sdk anyio"
    print_info "  • pip install --user claude-code-sdk anyio"
fi

echo ""
echo "Verifying installation..."

# Verify Claude Code CLI installation
if command -v claude &> /dev/null; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "installed")
    print_status "Claude Code CLI is available: $CLAUDE_VERSION"
else
    print_error "Claude Code CLI not found in PATH"
    print_info "Try running: npm install -g @anthropic-ai/claude-code"
fi

# Verify Python SDK installation
if python3 -c "import claude_code_sdk" 2>/dev/null; then
    print_status "Claude Code SDK Python package is available"
else
    print_warning "Claude Code SDK Python package not found"
    print_info "The integration will show helpful error messages if dependencies are missing"
fi

echo ""
echo "Setup complete! 🎉"
echo "=================="

print_info "Next steps:"
echo "1. Get your Anthropic API key from: https://console.anthropic.com/"
echo "2. Set your API key: anvil build config --set-key YOUR_API_KEY --global"
echo "3. Test the integration: anvil build create 'a simple hello world script'"

echo ""
print_info "Usage examples:"
echo "• anvil build create 'a React todo app with TypeScript'"
echo "• anvil build create 'a Python web scraper for news articles'"
echo "• anvil build chat  # Start interactive session"
echo "• anvil build config --show  # Check configuration"

echo ""
print_info "For more information, see: CLAUDE_CODE_SDK_INTEGRATION.md"

echo ""
print_status "Setup script completed successfully!"