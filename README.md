 █████╗ ███╗   ██╗██╗   ██╗██╗██╗     
██╔══██╗████╗  ██║██║   ██║██║██║     
███████║██╔██╗ ██║██║   ██║██║██║     
██╔══██║██║╚██╗██║╚██╗ ██╔╝██║██║     
██║  ██║██║ ╚████║ ╚████╔╝ ██║███████╗
╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝╚══════╝
```

# Anvil CLI

[![CI/CD](https://github.com/yourusername/anvil-cli/workflows/CI%2FCD/badge.svg)](https://github.com/yourusername/anvil-cli/actions)
[![PyPI version](https://badge.fury.io/py/anvil-cli.svg)](https://badge.fury.io/py/anvil-cli)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful CLI tool for creative development workflows. Anvil provides essential utilities for designers and developers, with an extensible plugin architecture.

## ✨ Features

- 🎨 **Color Palette Extraction** - Extract color palettes from any image
- 🎭 **Creative Sketching** - Generate creative content from text prompts
- 🔌 **Plugin Architecture** - Extensible with custom and third-party plugins
- 💾 **Smart Caching** - SQLite-based caching for performance
- 🎯 **Rich CLI Experience** - Beautiful output with colors and emojis
- ⚡ **Fast & Reliable** - Built with modern Python and comprehensive testing

## 🚀 Quick Start

### Installation

Install anvil using pipx (recommended):

```bash
pipx install anvil-cli
```

Or using pip:

```bash
pip install anvil-cli
```

### Verify Installation

```bash
anvil --help
```

You should see the beautiful ASCII logo and help information!

## 🖥️ Interactive Shell

Anvil features a powerful interactive REPL (Read-Eval-Print Loop) that provides a Claude Code-style shell experience.

### Launching the REPL

Run `anvil` without any arguments to launch the interactive shell:

```bash
anvil
```

Or use the dedicated shell command:

```bash
anvil-shell
```

### REPL Features

```
┌─────────────────────────────────────────────────────────────┐
│ Welcome to anvilCLI!                                        │
│                                                             │
│ /help for help, /status for your current setup             │
│                                                             │
│ cwd: /Users/you/projects                                    │
└─────────────────────────────────────────────────────────────┘

* Tip: Start with small features or bug fixes, ask Anvil to propose a plan, and verify its suggested edits *

> 
```

**Available slash commands:**
- `/help`, `?` - Show help message
- `/status` - Display current working directory and Python version  
- `/exit`, `/quit` - Exit the shell

**Regular commands:**
Any other input is forwarded to the normal anvil CLI, so you can run commands like:
```bash
> sketch "modern login page"
> palette grab image.jpg
> version
```

The REPL keeps running after each command, making it perfect for iterative workflows and experimentation.

## 📖 Core Commands

### Sketch Command

The sketch command uses [v0's API](https://vercel.com/docs/v0/api) to generate modern web applications from text prompts.

#### Setup

You have several convenient ways to set your v0 API key:

**Option 1: Global Configuration (Recommended)**
```bash
# Get your API key from v0.dev
anvil sketch config --set-key YOUR_V0_API_KEY --global
```
This saves your key to `~/.anvil/.env` and works for all projects.

**Option 2: Project-specific Configuration**
```bash
# Set for current project only
anvil sketch config --set-key YOUR_V0_API_KEY
```
This creates a `.env` file in your current directory.

**Option 3: Manual .env File**
Create a `.env` file in your project or home directory:
```bash
# In your project directory
echo "V0_API_KEY=YOUR_V0_API_KEY" > .env

# Or globally at ~/.anvil/.env
mkdir -p ~/.anvil
echo "V0_API_KEY=YOUR_V0_API_KEY" > ~/.anvil/.env
```

**Option 4: Environment Variable (Temporary)**
```bash
export V0_API_KEY=YOUR_V0_API_KEY
```

**Check Your Configuration**
```bash
anvil sketch config --show
```

#### Usage

**Basic usage:**
```bash
anvil sketch create "Create a Next.js todo app with dark mode"
```

**Preview only (don't create files):**
```bash
anvil sketch create "Build a React dashboard with charts" --no-files
```

#### Features

- **Streaming responses**: See the AI response in real-time as it's generated
- **Automatic file creation**: Parses code blocks and creates files in your current directory
- **Smart file detection**: Automatically detects file types and names based on content
- **Multiple formats**: Supports v0's `file="filename"` format and other common formats
- **Rich terminal output**: Beautiful, colored output with progress indicators

#### Examples

```bash
# Create a simple website
anvil sketch create "Build a landing page for a coffee shop with hero section, menu, and contact form"

# Generate a React component
anvil sketch create "Create a reusable button component in React with TypeScript"

# Build a full-stack app
anvil sketch create "Make a Next.js blog with authentication and a CMS"

# Generate utility functions
anvil sketch create "Create Python utility functions for data processing"

# Analyze existing codebase for improvements
anvil sketch doctor

# Analyze specific project directory
anvil sketch doctor ./my-react-app
```

The command will:
1. 🚀 Call the v0 API with your prompt
2. 📺 Stream the response in real-time in your terminal
3. 📁 Parse any code blocks from the response
4. ✅ Create the appropriate files in your current directory

#### Supported Code Block Formats

Anvil automatically recognizes and parses multiple code block formats:

**v0 Format (Primary):**
````
```tsx file="app/page.tsx"
export default function Home() {
  return <div>Hello World</div>
}
```
````

**Colon Format:**
````
```tsx:components/Button.tsx
export default function Button() {
  return <button>Click me</button>
}
```
````

**Direct Filename:**
````
```styles.css
body { margin: 0; }
```
````

All formats will create the appropriate directory structure and files automatically.

#### Doctor Command

The doctor command analyzes your existing codebase and provides improvement suggestions:

```bash
# Analyze current directory
anvil sketch doctor

# Analyze specific directory
anvil sketch doctor /path/to/project

# Get analysis without the full output (summary only)
anvil sketch doctor --no-analysis
```

**What it does:**
- 🔍 Scans your project files (automatically excludes node_modules, .git, etc.)
- 📊 Sends your codebase to v0 for analysis
- 💡 Receives detailed suggestions for improvements, best practices, and optimizations
- 🎯 Identifies potential issues, code smells, and enhancement opportunities

**Supported file types:**
- Python (.py), JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
- Styles (.css, .scss, .sass, .less)
- Markup (.html, .vue, .svelte)
- Config (.json, .yaml, .toml, .md)
- And many more...

**Example output:**
- Code quality improvements
- Security recommendations  
- Performance optimizations
- Architecture suggestions
- Best practices compliance

### Palette Command

Extract color palettes from images:

```bash
# Extract colors from an image
anvil palette grab ./path/to/image.jpg

# Works with various formats (PNG, JPG, GIF, etc.)
anvil palette grab screenshot.png
```

**Output:**
```
🎨 Extracting colors from: ./path/to/image.jpg
🌈 Extracted colors:
[
  "#ff6b35",
  "#2c5aa0",
  "#ffffff",
  "#1a1a1a",
  "#f5f5f5"
]
✓ Saved palette to: ./path/to/image_palette.json
```

### Upgrade Command

Keep anvil up to date:

```bash
anvil upgrade
```

### Global Flags

- `--version` - Show version and exit
- `--verbose`, `-v` - Enable verbose output
- `--no-color` - Disable colored output

## 🔌 Writing Plugins

Anvil supports both built-in and third-party plugins through a simple registration system.

### Built-in Plugin Structure

Create a file in `anvil/plugins/your_plugin.py`:

```python
"""Your custom plugin."""

import typer
from rich.console import Console

console = Console()

def register(main_app: typer.Typer) -> None:
    """Register the plugin with the main CLI app."""
    plugin_app = typer.Typer(name="your-plugin", help="Your plugin description")
    
    @plugin_app.command()
    def hello(name: str = "World") -> None:
        """Say hello from your plugin."""
        console.print(f"[green]👋 Hello {name} from your plugin![/green]")
    
    main_app.add_typer(plugin_app, name="your-plugin")
```

### Third-party Plugin Distribution

Distribute your plugin as a separate package with entry points in `pyproject.toml`:

```toml
[tool.poetry.plugins."anvil.plugins"]
my_awesome_plugin = "my_package.plugin:register"
```

Your plugin module should export a `register` function:

```python
# my_package/plugin.py
import typer

def register(main_app: typer.Typer) -> None:
    """Register your plugin commands."""
    # Add your commands here
    pass
```

### Plugin Examples

- **Development Tools**: Code formatters, linters, generators
- **Design Utilities**: Image processors, color tools, font managers  
- **Project Management**: Template generators, deployment tools
- **Creative Tools**: AI integrations, content generators

## 🛠️ Development

### Prerequisites

- Python 3.10+
- Poetry

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/anvil-cli.git
cd anvil-cli

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy anvil

# Test the CLI
anvil --help
```

### Quality Gates

Before submitting changes, ensure:

- `pytest` passes with ≥90% coverage
- `ruff check .` and `ruff format .` pass
- `mypy anvil` passes with strict checking

### Project Structure

```
anvil-cli/
├── anvil/
│   ├── __init__.py          # Package metadata
│   ├── cli.py               # Main CLI entry point
│   ├── cache.py             # SQLite caching layer
│   ├── py.typed             # Type hint marker
│   ├── commands/            # Built-in commands
│   │   ├── __init__.py
│   │   ├── sketch.py        # Sketch command
│   │   └── palette.py       # Palette command
│   └── plugins/             # Plugin system
│       ├── __init__.py
│       └── example.py       # Example plugin
├── tests/                   # Test suite
├── .github/workflows/       # CI/CD
├── pyproject.toml          # Project configuration
└── README.md               # Documentation
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and add tests
4. **Ensure** all quality gates pass
5. **Commit** your changes: `git commit -m 'Add amazing feature'`
6. **Push** to the branch: `git push origin feature/amazing-feature`
7. **Submit** a Pull Request

### Contribution Guidelines

- Follow the existing code style (enforced by ruff)
- Add tests for new functionality
- Update documentation as needed
- Ensure backwards compatibility
- Write clear, descriptive commit messages

### Reporting Issues

Please use the [GitHub Issues](https://github.com/yourusername/anvil-cli/issues) page to report bugs or request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI framework
- [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- [Pillow](https://pillow.readthedocs.io/) for image processing
- ASCII art generated with inspiration from figlet

## Configuration

### API Key Management

Anvil provides flexible API key management for v0 integration:

```bash
# Set API key globally (works for all projects)
anvil sketch config --set-key YOUR_KEY --global

# Set API key for current project only
anvil sketch config --set-key YOUR_KEY

# Check current API key status
anvil sketch config --show

# See all configuration options
anvil sketch config --help
```

### Configuration Priority

Anvil looks for your API key in this order:
1. **Current directory `.env` file** - Project-specific
2. **Global `~/.anvil/.env` file** - User-wide settings  
3. **Environment variable `V0_API_KEY`** - Session-specific

### Best Practices

- **For development**: Use global configuration (`--global`) for convenience
- **For teams**: Use project-specific `.env` files and add `.env` to `.gitignore`
- **For CI/CD**: Use environment variables
- **Security**: Never commit API keys to version control

### Environment Variables

- `V0_API_KEY`: Your v0 API key (required for sketch command)

---

**Happy building with Anvil! 🔨✨** 