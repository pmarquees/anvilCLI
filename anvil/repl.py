"""Interactive REPL for anvil-cli."""

import shlex
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typer.testing import CliRunner

console = Console()


def show_welcome() -> None:
    """Display the welcome panel and tip."""
    # Create welcome message
    welcome_text = Text()
    welcome_text.append("""
                                                         
                                                         
     ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑   ↖↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↗       
     ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑   ↗↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑       
      ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑   ↗↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑         
        ↑↑↑↑↑↑↑↑↑↑↑↑↑   ↗↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑         
           ↑↑↑↑↑↑↑↑↑↑   ↗↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑         
                 ↖↙↓↓   ↑↑↑↑↑↑↑↑↑↑↑↑→↘↘↘↘↘↘↘↘↘↘↖         
                        ↑↑↑↑↑↑↑↑↑↑↑→                     
                      ↘↑↑↑↑↑↑↑↑↑↑↑↑↑                     
                    ↘↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑                    
                ↓↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑                  
             ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑           
             ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑           
             ↑↑↑↑↑↑↑↑↑↑↑↓         ↖↗↑↑↑↑↑↑↑↑↑↑           
             ↑↑↑↑↑↑↑↑←                ↑↑↑↑↑↑↑↑           
             →↗↑↑↑↑↓                    ↗↑↑↑↑↗  
                                               
                    Welcome to AnvilCLI!        
                                                      

""", style="yellow")
    welcome_text.append("Welcome to anvilCLI!\n\n", style="bold")
    welcome_text.append("""What can I do?:
  • Sketch a new idea using v0's API (sketch create "your prompt")
  • Analyze your codebase for improvements (sketch doctor)
  • Generate Images
  • Get colour pallets from images

""")
    welcome_text.append(f"cwd: {Path.cwd()}")

    # Display yellow-bordered panel
    panel = Panel(
        welcome_text,
        border_style="yellow",
        expand=False
    )
    console.print(panel)

    # Display tip line
    tip = Text(
        "* Tip: Start with small features or bug fixes, ask Anvil to propose a plan, "
        "and verify its suggested edits *",
        style="dim"
    )
    console.print(tip)
    console.print()


def show_help() -> None:
    """Display available slash commands."""
    help_text = Text()
    help_text.append("Available slash commands:\n", style="bold")
    help_text.append("  /help, ?     - Show this help message\n")
    help_text.append(
        "  /status      - Show current working directory and Python version\n"
    )
    help_text.append("  /exit, /quit - Exit the REPL\n\n")
    help_text.append(
        "Anything else will be forwarded to the normal anvil CLI", style="dim"
    )
    console.print(help_text)


def show_status() -> None:
    """Display current status information."""
    status_text = Text()
    status_text.append("Current Status:\n", style="bold cyan")
    status_text.append(f"  Working Directory: {Path.cwd()}\n")
    status_text.append(f"  Python Version: {sys.version.split()[0]}\n")
    console.print(status_text)


def execute_anvil_command(args: list[str]) -> None:
    """Execute an anvil command in-process."""
    from .cli import app

    try:
        # Use typer's testing functionality to run commands in-process
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(app, args, catch_exceptions=False)
        if result.stdout:
            console.print(result.stdout, end="")
        if result.stderr:
            console.print(result.stderr, end="", style="red")
    except SystemExit:
        # Ignore SystemExit to keep REPL running
        pass
    except Exception as e:
        console.print(f"Error executing command: {e}", style="red")


def repl() -> None:
    """Main REPL loop."""
    show_welcome()

    try:
        while True:
            try:
                # Prompt for input
                prompt_text = Text("> ", style="bold cyan")
                console.print(prompt_text, end="")

                user_input = input().strip()

                if not user_input:
                    continue

                # Handle slash commands
                if user_input in ("/help", "?"):
                    show_help()
                elif user_input == "/status":
                    show_status()
                elif user_input in ("/exit", "/quit"):
                    break
                else:
                    # Parse and execute as anvil command
                    try:
                        args = shlex.split(user_input)
                        if args:
                            execute_anvil_command(args)
                    except ValueError as e:
                        console.print(f"Error parsing command: {e}", style="red")

                console.print()  # Add spacing between commands

            except KeyboardInterrupt:
                console.print("\nUse /exit or /quit to leave the shell", style="dim")
                console.print()
            except EOFError:
                break

    finally:
        console.print("Bye - thanks for forging with Anvil!", style="dim")


if __name__ == "__main__":
    repl()
