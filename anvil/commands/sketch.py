"""Sketch command for generating creative content using v0 API."""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Set

import httpx
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

app = typer.Typer(name="sketch", help="Generate creative content from text prompts using v0 API")
console = Console()

V0_API_URL = "https://api.v0.dev/v1/chat/completions"

# File extensions to include in codebase analysis
INCLUDE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.sass', '.less',
    '.html', '.htm', '.vue', '.svelte', '.json', '.yaml', '.yml', '.toml',
    '.md', '.mdx', '.txt', '.env', '.gitignore', '.dockerignore',
    '.sql', '.graphql', '.gql', '.xml', '.svg'
}

# Directories to exclude from analysis
EXCLUDE_DIRS = {
    'node_modules', '.git', '.svn', '.hg', '__pycache__', '.pytest_cache',
    '.mypy_cache', '.ruff_cache', 'dist', 'build', '.next', '.nuxt',
    'coverage', 'htmlcov', '.coverage', '.env', '.venv', 'venv', 'env',
    '.DS_Store', 'Thumbs.db', '.idea', '.vscode', '*.egg-info'
}


def get_api_key() -> Optional[str]:
    """Get the V0 API key from environment variables or .env files."""
    # Load from .env file in current directory
    load_dotenv()
    
    # Try current directory .env first
    current_dir_env = Path.cwd() / ".env"
    if current_dir_env.exists():
        load_dotenv(current_dir_env)
    
    # Try global config in home directory
    global_env = Path.home() / ".anvil" / ".env"
    if global_env.exists():
        load_dotenv(global_env)
    
    # Finally check environment variable
    return os.getenv("V0_API_KEY")


def save_api_key_globally(api_key: str) -> None:
    """Save the API key to global config."""
    config_dir = Path.home() / ".anvil"
    config_dir.mkdir(exist_ok=True)
    
    env_file = config_dir / ".env"
    
    # Read existing content if file exists
    existing_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Remove any existing V0_API_KEY lines
        lines = [line for line in lines if not line.strip().startswith('V0_API_KEY=')]
        existing_content = ''.join(lines)
    
    # Write back with new API key
    with open(env_file, 'w') as f:
        f.write(existing_content)
        if existing_content and not existing_content.endswith('\n'):
            f.write('\n')
        f.write(f'V0_API_KEY={api_key}\n')
    
    console.print(f"✅ API key saved to: {env_file}", style="green")


@app.command(name="config")
def config_cmd(
    set_key: Optional[str] = typer.Option(None, "--set-key", help="Set your v0 API key"),
    show: bool = typer.Option(False, "--show", help="Show current API key status"),
    global_config: bool = typer.Option(False, "--global", help="Save to global config (in ~/.anvil/.env)")
) -> None:
    """Manage v0 API key configuration."""
    
    if set_key:
        if global_config:
            save_api_key_globally(set_key)
        else:
            # Save to current directory .env
            env_file = Path.cwd() / ".env"
            
            # Read existing content if file exists
            existing_content = ""
            if env_file.exists():
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                # Remove any existing V0_API_KEY lines
                lines = [line for line in lines if not line.strip().startswith('V0_API_KEY=')]
                existing_content = ''.join(lines)
            
            # Write back with new API key
            with open(env_file, 'w') as f:
                f.write(existing_content)
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                f.write(f'V0_API_KEY={set_key}\n')
            
            console.print(f"✅ API key saved to: {env_file}", style="green")
            console.print("💡 Tip: Add .env to your .gitignore to keep your API key private", style="dim")
        
        return
    
    if show:
        api_key = get_api_key()
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            console.print(f"✅ API key found: {masked_key}", style="green")
            
            # Show where it's loaded from
            current_dir_env = Path.cwd() / ".env"
            global_env = Path.home() / ".anvil" / ".env"
            
            if current_dir_env.exists() and "V0_API_KEY" in current_dir_env.read_text():
                console.print(f"📁 Loaded from: {current_dir_env}", style="dim")
            elif global_env.exists() and "V0_API_KEY" in global_env.read_text():
                console.print(f"🌍 Loaded from: {global_env}", style="dim")
            else:
                console.print("🌍 Loaded from environment variable", style="dim")
        else:
            console.print("❌ No API key found", style="red")
            console.print("\n💡 Set your API key using one of these methods:", style="dim")
            console.print("   • anvil sketch config --set-key YOUR_KEY", style="dim")
            console.print("   • anvil sketch config --set-key YOUR_KEY --global", style="dim")
            console.print("   • export V0_API_KEY=YOUR_KEY", style="dim")
        return
    
    # Default: show help
    console.print("🔧 v0 API Key Configuration", style="bold")
    console.print("\nAvailable options:")
    console.print("  --set-key KEY     Set API key for current project (.env file)")
    console.print("  --set-key KEY --global   Set API key globally (~/.anvil/.env)")
    console.print("  --show            Show current API key status")
    console.print("\nExamples:")
    console.print("  anvil sketch config --set-key v0_xxxxx", style="dim")
    console.print("  anvil sketch config --set-key v0_xxxxx --global", style="dim")
    console.print("  anvil sketch config --show", style="dim")


def parse_code_blocks(content: str) -> Dict[str, str]:
    """Parse code blocks from markdown content and extract filename and code."""
    files = {}
    
    # Pattern to match code blocks with various filename formats:
    # 1. ```tsx file="app/page.tsx" (v0 format)
    # 2. ```tsx:filename.tsx (colon format)  
    # 3. ```filename.tsx (direct filename)
    pattern = r'```(?:(\w+)\s+file="([^"]+)"|(\w+):([^\n]+\.(tsx?|jsx?|py|css|html|json|md|yml|yaml|toml|sh|txt))|([^\n]+\.(tsx?|jsx?|py|css|html|json|md|yml|yaml|toml|sh|txt)))\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for match in matches:
        language_v0, filename_v0, language_colon, filename_colon, ext_colon, filename_direct, ext_direct, code = match
        
        # Handle v0 format: ```tsx file="app/page.tsx"
        if language_v0 and filename_v0:
            files[filename_v0] = code.strip()
        # Handle colon format: ```tsx:filename.tsx
        elif language_colon and filename_colon:
            files[filename_colon] = code.strip()
        # Handle direct filename: ```filename.tsx
        elif filename_direct:
            files[filename_direct] = code.strip()
        # Handle language-only blocks (fallback to default names)
        elif language_v0 and code.strip():
            # Try to infer filename from language for language-only blocks
            if language_v0 == "typescript" or language_v0 == "ts" or language_v0 == "tsx":
                files["index.ts"] = code.strip()
            elif language_v0 == "javascript" or language_v0 == "js" or language_v0 == "jsx":
                files["index.js"] = code.strip()
            elif language_v0 == "python" or language_v0 == "py":
                files["main.py"] = code.strip()
            elif language_v0 == "css":
                files["styles.css"] = code.strip()
            elif language_v0 == "html":
                files["index.html"] = code.strip()
            elif language_v0 == "json":
                files["config.json"] = code.strip()
            elif language_v0 == "markdown" or language_v0 == "md":
                files["README.md"] = code.strip()
        elif language_colon and code.strip():
            # Try to infer filename from language for language-only blocks
            if language_colon == "typescript" or language_colon == "ts" or language_colon == "tsx":
                files["index.ts"] = code.strip()
            elif language_colon == "javascript" or language_colon == "js" or language_colon == "jsx":
                files["index.js"] = code.strip()
            elif language_colon == "python" or language_colon == "py":
                files["main.py"] = code.strip()
            elif language_colon == "css":
                files["styles.css"] = code.strip()
            elif language_colon == "html":
                files["index.html"] = code.strip()
            elif language_colon == "json":
                files["config.json"] = code.strip()
            elif language_colon == "markdown" or language_colon == "md":
                files["README.md"] = code.strip()
    
    return files


def create_files(files: Dict[str, str], base_path: Path = Path.cwd()) -> None:
    """Create files from the parsed code blocks."""
    if not files:
        console.print("⚠️  No files found in the response to create.", style="yellow")
        return
    
    console.print(f"\n📁 Creating {len(files)} file(s):", style="bold green")
    
    for filename, content in files.items():
        file_path = base_path / filename
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            console.print(f"  ✅ Created: {file_path}", style="green")
        except Exception as e:
            console.print(f"  ❌ Failed to create {file_path}: {e}", style="red")


async def stream_v0_response(prompt: str, api_key: str) -> str:
    """Stream response from v0 API and display it in real-time."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "v0-1.0-md",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": True
    }
    
    full_response = ""
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            console.print("🚀 Calling v0 API...", style="bold cyan")
            console.print()
            
            async with client.stream("POST", V0_API_URL, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    console.print(f"❌ API Error ({response.status_code}): {error_text.decode()}", style="red")
                    return ""
                
                # Create a live display for streaming
                text_display = Text()
                
                with Live(Panel(text_display, title="🤖 v0 Response", border_style="cyan"), refresh_per_second=10) as live:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str.strip() == "[DONE]":
                                break
                                
                            try:
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        full_response += content
                                        text_display.append(content)
                                        live.update(Panel(text_display, title="🤖 v0 Response", border_style="cyan"))
                                        
                            except json.JSONDecodeError:
                                # Skip malformed JSON lines
                                continue
                            except Exception as e:
                                console.print(f"⚠️  Error processing stream: {e}", style="yellow")
                                continue
    
    except httpx.TimeoutException:
        console.print("⏱️  Request timed out. Please try again.", style="red")
    except httpx.RequestError as e:
        console.print(f"🌐 Network error: {e}", style="red")
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
    
    return full_response


@app.command(name="create")
def generate(prompt: str, no_files: bool = typer.Option(False, "--no-files", help="Don't create files, just show the response")) -> None:
    """Generate creative content from a text prompt using v0 API.

    Args:
        prompt: The creative prompt to process
        no_files: If True, don't create files from the response
    """
    # Check for API key
    api_key = get_api_key()
    if not api_key:
        console.print("❌ V0_API_KEY not found.", style="red")
        console.print("\n💡 Set your API key using one of these methods:", style="dim")
        console.print("   • anvil sketch config --set-key YOUR_KEY", style="dim")
        console.print("   • anvil sketch config --set-key YOUR_KEY --global", style="dim")
        console.print("   • Create a .env file with: V0_API_KEY=YOUR_KEY", style="dim")
        console.print("   • export V0_API_KEY=YOUR_KEY", style="dim")
        raise typer.Exit(1)
    
    console.print(f"📝 Prompt: {prompt}", style="bold")
    console.print(f"📂 Working directory: {Path.cwd()}", style="dim")
    console.print()
    
    # Use asyncio to handle the streaming response
    import asyncio
    
    try:
        response = asyncio.run(stream_v0_response(prompt, api_key))
        
        if response:
            console.print("\n" + "="*50, style="dim")
            
            if not no_files:
                # Parse and create files
                files = parse_code_blocks(response)
                create_files(files)
            else:
                console.print("🔍 File creation skipped (--no-files flag used)", style="yellow")
        else:
            console.print("❌ No response received from v0 API", style="red")
            
    except KeyboardInterrupt:
        console.print("\n⚠️  Request cancelled by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Error: {e}", style="red")
        raise typer.Exit(1)


@app.callback()
def main() -> None:
    """Generate creative content from text prompts using v0 API."""


def should_include_file(file_path: Path) -> bool:
    """Check if a file should be included in the codebase analysis."""
    # Check extension
    if file_path.suffix.lower() not in INCLUDE_EXTENSIONS:
        return False
    
    # Check if any parent directory should be excluded
    for part in file_path.parts:
        if part in EXCLUDE_DIRS:
            return False
    
    # Check file size (skip very large files)
    try:
        if file_path.stat().st_size > 100_000:  # 100KB limit
            return False
    except (OSError, FileNotFoundError):
        return False
    
    return True


def read_codebase(base_path: Path) -> Dict[str, str]:
    """Read all relevant files in the codebase."""
    codebase = {}
    
    try:
        for file_path in base_path.rglob('*'):
            if file_path.is_file() and should_include_file(file_path):
                try:
                    # Get relative path from base
                    relative_path = file_path.relative_to(base_path)
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    codebase[str(relative_path)] = content
                    
                except (UnicodeDecodeError, PermissionError, OSError):
                    # Skip files that can't be read
                    continue
                    
    except Exception as e:
        console.print(f"⚠️  Error reading codebase: {e}", style="yellow")
    
    return codebase


def format_codebase_for_api(codebase: Dict[str, str]) -> str:
    """Format the codebase data for sending to the v0 API."""
    formatted = "# Codebase Analysis\n\n"
    formatted += "Please analyze this codebase and offer improvements, suggestions, and best practices.\n\n"
    
    # Add file structure overview
    formatted += "## File Structure\n\n"
    sorted_files = sorted(codebase.keys())
    for file_path in sorted_files:
        formatted += f"- {file_path}\n"
    
    formatted += "\n## File Contents\n\n"
    
    # Add each file's content
    for file_path, content in sorted(codebase.items()):
        # Determine language for syntax highlighting
        extension = Path(file_path).suffix.lower()
        language_map = {
            '.py': 'python', '.js': 'javascript', '.jsx': 'jsx', 
            '.ts': 'typescript', '.tsx': 'tsx', '.css': 'css',
            '.html': 'html', '.json': 'json', '.md': 'markdown',
            '.yml': 'yaml', '.yaml': 'yaml', '.toml': 'toml',
            '.sql': 'sql', '.graphql': 'graphql'
        }
        language = language_map.get(extension, 'text')
        
        formatted += f"### {file_path}\n\n"
        formatted += f"```{language}\n{content}\n```\n\n"
    
    return formatted


async def analyze_codebase_with_v0(codebase_content: str, api_key: str) -> str:
    """Send codebase to v0 API for analysis."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "v0-1.0-md",
        "messages": [
            {"role": "user", "content": codebase_content}
        ],
        "stream": True
    }
    
    full_response = ""
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:  # Longer timeout for analysis
            console.print("🔍 Sending codebase to v0 for analysis...", style="bold cyan")
            console.print()
            
            async with client.stream("POST", V0_API_URL, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    console.print(f"❌ API Error ({response.status_code}): {error_text.decode()}", style="red")
                    return ""
                
                # Create a live display for streaming
                text_display = Text()
                
                with Live(Panel(text_display, title="🩺 v0 Codebase Analysis", border_style="cyan"), refresh_per_second=8) as live:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            
                            if data_str.strip() == "[DONE]":
                                break
                                
                            try:
                                data = json.loads(data_str)
                                choices = data.get("choices", [])
                                
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    
                                    if content:
                                        full_response += content
                                        text_display.append(content)
                                        live.update(Panel(text_display, title="🩺 v0 Codebase Analysis", border_style="cyan"))
                                        
                            except json.JSONDecodeError:
                                # Skip malformed JSON lines
                                continue
                            except Exception as e:
                                console.print(f"⚠️  Error processing stream: {e}", style="yellow")
                                continue
    
    except httpx.TimeoutException:
        console.print("⏱️  Request timed out. Your codebase might be too large.", style="red")
    except httpx.RequestError as e:
        console.print(f"🌐 Network error: {e}", style="red")
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
    
    return full_response


@app.command(name="doctor")
def doctor(
    path: Optional[str] = typer.Argument(None, help="Path to analyze (defaults to current directory)"),
    include_analysis: bool = typer.Option(True, "--analysis/--no-analysis", help="Include detailed analysis in output"),
) -> None:
    """Analyze your codebase and get improvement suggestions from v0.
    
    This command reads your project files and sends them to v0 for analysis,
    receiving suggestions for improvements, best practices, and optimizations.
    
    Args:
        path: Directory path to analyze (optional, defaults to current directory)
        include_analysis: Whether to include the full analysis output
    """
    # Check for API key
    api_key = get_api_key()
    if not api_key:
        console.print("❌ V0_API_KEY not found.", style="red")
        console.print("\n💡 Set your API key using one of these methods:", style="dim")
        console.print("   • anvil sketch config --set-key YOUR_KEY", style="dim")
        console.print("   • anvil sketch config --set-key YOUR_KEY --global", style="dim")
        raise typer.Exit(1)
    
    # Determine the path to analyze
    analysis_path = Path(path) if path else Path.cwd()
    
    if not analysis_path.exists():
        console.print(f"❌ Path does not exist: {analysis_path}", style="red")
        raise typer.Exit(1)
    
    if not analysis_path.is_dir():
        console.print(f"❌ Path is not a directory: {analysis_path}", style="red")
        raise typer.Exit(1)
    
    console.print(f"🩺 Analyzing codebase: {analysis_path}", style="bold")
    console.print(f"📂 Working directory: {Path.cwd()}", style="dim")
    console.print()
    
    # Read the codebase
    console.print("📖 Reading codebase files...", style="cyan")
    codebase = read_codebase(analysis_path)
    
    if not codebase:
        console.print("❌ No suitable files found for analysis.", style="red")
        console.print("💡 Make sure your directory contains code files (.py, .js, .tsx, etc.)", style="dim")
        raise typer.Exit(1)
    
    console.print(f"✅ Found {len(codebase)} files to analyze", style="green")
    
    # Check total size
    total_chars = sum(len(content) for content in codebase.values())
    if total_chars > 50_000:  # Rough token limit
        console.print(f"⚠️  Large codebase detected ({total_chars:,} characters)", style="yellow")
        console.print("   Analysis may be truncated. Consider analyzing specific subdirectories.", style="dim")
    
    # Format for API
    console.print("📝 Formatting codebase for analysis...", style="cyan")
    formatted_content = format_codebase_for_api(codebase)
    
    # Analyze with v0
    import asyncio
    
    try:
        response = asyncio.run(analyze_codebase_with_v0(formatted_content, api_key))
        
        if response:
            console.print("\n" + "="*60, style="dim")
            console.print("🎯 Analysis complete!", style="bold green")
            
            if not include_analysis:
                console.print("📋 Use --analysis to see the full analysis output", style="dim")
        else:
            console.print("❌ No analysis received from v0 API", style="red")
            
    except KeyboardInterrupt:
        console.print("\n⚠️  Analysis cancelled by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Error during analysis: {e}", style="red")
        raise typer.Exit(1)
