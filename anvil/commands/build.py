"""Build command for creating projects using Claude Code SDK."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

import anyio
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock, ToolUseBlock, ToolResultBlock
    from claude_code_sdk._errors import ClaudeSDKError, CLINotFoundError, CLIConnectionError, ProcessError
except ImportError:
    # Fallback if SDK not installed
    query = None
    ClaudeCodeOptions = None
    AssistantMessage = None
    TextBlock = None
    ToolUseBlock = None
    ToolResultBlock = None
    ClaudeSDKError = Exception
    CLINotFoundError = Exception
    CLIConnectionError = Exception
    ProcessError = Exception

app = typer.Typer(name="build", help="Build projects using Claude Code SDK with natural language")
console = Console()


def get_anthropic_api_key() -> Optional[str]:
    """Get the Anthropic API key from environment variables or .env files."""
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
    return os.getenv("ANTHROPIC_API_KEY")


def save_api_key_globally(api_key: str) -> None:
    """Save the Anthropic API key to global config."""
    config_dir = Path.home() / ".anvil"
    config_dir.mkdir(exist_ok=True)
    
    env_file = config_dir / ".env"
    
    # Read existing content if file exists
    existing_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Remove any existing ANTHROPIC_API_KEY lines
        lines = [line for line in lines if not line.strip().startswith('ANTHROPIC_API_KEY=')]
        existing_content = ''.join(lines)
    
    # Write back with new API key
    with open(env_file, 'w') as f:
        f.write(existing_content)
        if existing_content and not existing_content.endswith('\n'):
            f.write('\n')
        f.write(f'ANTHROPIC_API_KEY={api_key}\n')
    
    console.print(f"✅ Anthropic API key saved to: {env_file}", style="green")


@app.command(name="config")
def config_cmd(
    set_key: Optional[str] = typer.Option(None, "--set-key", help="Set your Anthropic API key"),
    show: bool = typer.Option(False, "--show", help="Show current API key status"),
    global_config: bool = typer.Option(False, "--global", help="Save to global config (in ~/.anvil/.env)")
) -> None:
    """Manage Anthropic API key configuration for Claude Code SDK."""
    
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
                
                # Remove any existing ANTHROPIC_API_KEY lines
                lines = [line for line in lines if not line.strip().startswith('ANTHROPIC_API_KEY=')]
                existing_content = ''.join(lines)
            
            # Write back with new API key
            with open(env_file, 'w') as f:
                f.write(existing_content)
                if existing_content and not existing_content.endswith('\n'):
                    f.write('\n')
                f.write(f'ANTHROPIC_API_KEY={set_key}\n')
            
            console.print(f"✅ Anthropic API key saved to: {env_file}", style="green")
            console.print("💡 Tip: Add .env to your .gitignore to keep your API key private", style="dim")
        
        return
    
    if show:
        api_key = get_anthropic_api_key()
        if api_key:
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
            console.print(f"✅ Anthropic API key found: {masked_key}", style="green")
            
            # Show where it's loaded from
            current_dir_env = Path.cwd() / ".env"
            global_env = Path.home() / ".anvil" / ".env"
            
            if current_dir_env.exists() and "ANTHROPIC_API_KEY" in current_dir_env.read_text():
                console.print(f"📁 Loaded from: {current_dir_env}", style="dim")
            elif global_env.exists() and "ANTHROPIC_API_KEY" in global_env.read_text():
                console.print(f"🌍 Loaded from: {global_env}", style="dim")
            else:
                console.print("🌍 Loaded from environment variable", style="dim")
        else:
            console.print("❌ No Anthropic API key found", style="red")
            console.print("\n💡 Set your API key using one of these methods:", style="dim")
            console.print("   • anvil build config --set-key YOUR_KEY", style="dim")
            console.print("   • anvil build config --set-key YOUR_KEY --global", style="dim")
            console.print("   • export ANTHROPIC_API_KEY=YOUR_KEY", style="dim")
        return
    
    # Default: show help
    console.print("🔧 Anthropic API Key Configuration", style="bold")
    console.print("\nAvailable options:")
    console.print("  --set-key KEY     Set API key for current project (.env file)")
    console.print("  --set-key KEY --global   Set API key globally (~/.anvil/.env)")
    console.print("  --show            Show current API key status")
    console.print("\nExamples:")
    console.print("  anvil build config --set-key sk-ant-xxxxx", style="dim")
    console.print("  anvil build config --set-key sk-ant-xxxxx --global", style="dim")
    console.print("  anvil build config --show", style="dim")


def check_claude_code_installation() -> bool:
    """Check if Claude Code CLI is installed."""
    import shutil
    return shutil.which("claude") is not None


async def stream_claude_response(
    prompt: str, 
    options: Optional[ClaudeCodeOptions] = None,
    progress: Optional[Progress] = None
) -> List[Dict[str, Any]]:
    """Stream response from Claude Code SDK and display it in real-time."""
    if query is None:
        console.print("❌ Claude Code SDK not installed. Run: pip install claude-code-sdk", style="red")
        return []
    
    messages = []
    current_text = ""
    
    try:
        console.print("🤖 Starting Claude Code session...", style="bold cyan")
        
        # Create a live display for streaming
        text_display = Text()
        
        with Live(Panel(text_display, title="🤖 Claude Response", border_style="cyan"), refresh_per_second=10) as live:
            async for message in query(prompt=prompt, options=options):
                messages.append(message)
                
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Add new text to display
                            new_text = block.text
                            if new_text not in current_text:
                                additional_text = new_text[len(current_text):]
                                text_display.append(additional_text)
                                current_text = new_text
                                live.update(Panel(text_display, title="🤖 Claude Response", border_style="cyan"))
                        
                        elif isinstance(block, ToolUseBlock):
                            # Show tool usage
                            tool_text = f"\n🔧 Using tool: {block.name}\n"
                            if block.input:
                                tool_text += f"   Input: {block.input}\n"
                            text_display.append(tool_text)
                            live.update(Panel(text_display, title="🤖 Claude Response (Tool Use)", border_style="yellow"))
                
                elif hasattr(message, 'content') and isinstance(message.content, list):
                    for item in message.content:
                        if hasattr(item, 'content') and isinstance(item.content, str):
                            # Tool result
                            result_text = f"\n📋 Tool result: {item.content[:100]}{'...' if len(item.content) > 100 else ''}\n"
                            text_display.append(result_text)
                            live.update(Panel(text_display, title="🤖 Claude Response (Tool Result)", border_style="green"))
    
    except CLINotFoundError:
        console.print("❌ Claude Code CLI not found. Please install it first:", style="red")
        console.print("   npm install -g @anthropic-ai/claude-code", style="dim")
    except CLIConnectionError as e:
        console.print(f"❌ Failed to connect to Claude Code: {e}", style="red")
    except ProcessError as e:
        console.print(f"❌ Claude Code process error: {e}", style="red")
    except ClaudeSDKError as e:
        console.print(f"❌ Claude SDK error: {e}", style="red")
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
    
    return messages


@app.command()
def create(
    prompt: str = typer.Argument(..., help="What you want Claude to build"),
    allowed_tools: Optional[List[str]] = typer.Option(None, "--tools", help="Comma-separated list of allowed tools"),
    max_turns: int = typer.Option(10, "--max-turns", help="Maximum number of conversation turns"),
    working_dir: Optional[str] = typer.Option(None, "--dir", help="Working directory for the build"),
    verbose: bool = typer.Option(False, "--verbose", help="Enable verbose output"),
    auto_approve: bool = typer.Option(False, "--auto-approve", help="Auto-approve file edits and tool usage"),
) -> None:
    """Build something using Claude Code SDK with natural language.
    
    Examples:
        anvil build create "a React todo app with TypeScript"
        anvil build create "a Python web scraper for news articles" --tools Read,Write,Bash
        anvil build create "fix the bugs in my code" --dir ./my-project --auto-approve
    """
    if query is None:
        console.print("❌ Claude Code SDK not installed.", style="red")
        console.print("💡 Install it with: pip install claude-code-sdk", style="dim")
        console.print("💡 Also install Claude Code CLI: npm install -g @anthropic-ai/claude-code", style="dim")
        raise typer.Exit(1)
    
    # Check for API key
    api_key = get_anthropic_api_key()
    if not api_key:
        console.print("❌ ANTHROPIC_API_KEY not found.", style="red")
        console.print("\n💡 Set your API key using one of these methods:", style="dim")
        console.print("   • anvil build config --set-key YOUR_KEY", style="dim")
        console.print("   • anvil build config --set-key YOUR_KEY --global", style="dim")
        console.print("   • Create a .env file with: ANTHROPIC_API_KEY=YOUR_KEY", style="dim")
        console.print("   • export ANTHROPIC_API_KEY=YOUR_KEY", style="dim")
        raise typer.Exit(1)
    
    # Check Claude Code installation
    if not check_claude_code_installation():
        console.print("❌ Claude Code CLI not found.", style="red")
        console.print("💡 Install it with: npm install -g @anthropic-ai/claude-code", style="dim")
        raise typer.Exit(1)
    
    # Set working directory
    if working_dir:
        work_path = Path(working_dir).resolve()
        if not work_path.exists():
            console.print(f"❌ Working directory does not exist: {work_path}", style="red")
            raise typer.Exit(1)
    else:
        work_path = Path.cwd()
    
    console.print(f"🏗️  Building: {prompt}", style="bold")
    console.print(f"📂 Working directory: {work_path}", style="dim")
    
    # Configure Claude Code options
    options = ClaudeCodeOptions(
        cwd=str(work_path),
        max_turns=max_turns,
        system_prompt="You are a helpful coding assistant. Use the available tools to help build, modify, and improve code projects. Be thorough and explain your actions.",
    )
    
    # Set allowed tools
    if allowed_tools:
        # Parse comma-separated tools
        tools_list = [tool.strip() for tool in allowed_tools[0].split(',') if tool.strip()]
        options.allowed_tools = tools_list
        console.print(f"🔧 Allowed tools: {', '.join(tools_list)}", style="dim")
    else:
        # Default tools for building projects
        options.allowed_tools = ["Read", "Write", "Bash", "Edit"]
        console.print("🔧 Using default tools: Read, Write, Bash, Edit", style="dim")
    
    # Set permission mode
    if auto_approve:
        options.permission_mode = 'acceptEdits'
        console.print("⚡ Auto-approval enabled for file edits", style="yellow")
    
    console.print()
    
    # Create a more specific prompt for building
    enhanced_prompt = f"""I want you to help me build: {prompt}

Please use the available tools to:
1. Analyze the current directory structure if relevant
2. Create or modify files as needed
3. Set up any necessary configuration
4. Provide clear explanations of what you're doing

Working directory: {work_path}
"""
    
    try:
        # Run the async function
        messages = anyio.run(stream_claude_response, enhanced_prompt, options)
        
        if messages:
            console.print("\n" + "="*50, style="dim")
            console.print("✅ Build completed successfully!", style="bold green")
            
            # Show summary of what was done
            tool_uses = []
            for message in messages:
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            tool_uses.append(f"{block.name}: {block.input}")
            
            if tool_uses:
                console.print("\n🔧 Tools used:", style="bold")
                for tool_use in tool_uses[-5:]:  # Show last 5 tool uses
                    console.print(f"  • {tool_use}", style="dim")
                if len(tool_uses) > 5:
                    console.print(f"  ... and {len(tool_uses) - 5} more", style="dim")
        else:
            console.print("❌ No response received from Claude", style="red")
            
    except KeyboardInterrupt:
        console.print("\n⚠️  Build cancelled by user", style="yellow")
    except Exception as e:
        console.print(f"❌ Error during build: {e}", style="red")
        if verbose:
            import traceback
            console.print(traceback.format_exc(), style="dim")
        raise typer.Exit(1)


@app.command()
def chat(
    working_dir: Optional[str] = typer.Option(None, "--dir", help="Working directory for the chat"),
    allowed_tools: Optional[List[str]] = typer.Option(None, "--tools", help="Comma-separated list of allowed tools"),
    auto_approve: bool = typer.Option(False, "--auto-approve", help="Auto-approve file edits and tool usage"),
) -> None:
    """Start an interactive chat session with Claude Code SDK.
    
    This allows you to have a conversation with Claude where you can iteratively
    build and modify your project.
    """
    if query is None:
        console.print("❌ Claude Code SDK not installed.", style="red")
        console.print("💡 Install it with: pip install claude-code-sdk", style="dim")
        raise typer.Exit(1)
    
    # Check for API key
    api_key = get_anthropic_api_key()
    if not api_key:
        console.print("❌ ANTHROPIC_API_KEY not found.", style="red")
        console.print("💡 Use 'anvil build config --set-key YOUR_KEY' to set it", style="dim")
        raise typer.Exit(1)
    
    # Check Claude Code installation
    if not check_claude_code_installation():
        console.print("❌ Claude Code CLI not found.", style="red")
        console.print("💡 Install it with: npm install -g @anthropic-ai/claude-code", style="dim")
        raise typer.Exit(1)
    
    # Set working directory
    if working_dir:
        work_path = Path(working_dir).resolve()
        if not work_path.exists():
            console.print(f"❌ Working directory does not exist: {work_path}", style="red")
            raise typer.Exit(1)
    else:
        work_path = Path.cwd()
    
    console.print("🗣️  Starting Claude Code chat session", style="bold cyan")
    console.print(f"📂 Working directory: {work_path}", style="dim")
    console.print("💡 Type 'exit' or 'quit' to end the session", style="dim")
    console.print("💡 Type 'help' for available commands", style="dim")
    console.print()
    
    # Configure Claude Code options
    options = ClaudeCodeOptions(
        cwd=str(work_path),
        max_turns=5,  # Smaller turns for interactive chat
        system_prompt="You are a helpful coding assistant in an interactive session. Use tools to help with coding tasks and explain your actions clearly.",
    )
    
    # Set allowed tools
    if allowed_tools:
        tools_list = [tool.strip() for tool in allowed_tools[0].split(',') if tool.strip()]
        options.allowed_tools = tools_list
    else:
        options.allowed_tools = ["Read", "Write", "Bash", "Edit"]
    
    # Set permission mode
    if auto_approve:
        options.permission_mode = 'acceptEdits'
    
    try:
        while True:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'bye']:
                break
                
            if user_input.lower() == 'help':
                console.print("\n📚 Available commands:", style="bold")
                console.print("  • Any natural language request (e.g., 'create a new file')")
                console.print("  • 'exit' or 'quit' - End the session")
                console.print("  • 'help' - Show this help")
                console.print()
                continue
            
            # Process with Claude
            console.print()
            try:
                messages = anyio.run(stream_claude_response, user_input, options)
                console.print()
            except Exception as e:
                console.print(f"❌ Error: {e}", style="red")
                console.print()
    
    except KeyboardInterrupt:
        pass
    
    console.print("👋 Chat session ended", style="dim")


@app.callback()
def main() -> None:
    """Build projects using Claude Code SDK with natural language commands."""
    pass


if __name__ == "__main__":
    app()