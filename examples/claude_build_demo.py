#!/usr/bin/env python3
"""
Demo script showing how to use the anvil build command with Claude Code SDK.

This script demonstrates various ways to use the build command to create
projects using natural language.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> None:
    """Run a command and display the result."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)


def main():
    """Run the demo."""
    print("🔨 Anvil Build Command Demo")
    print("This demo shows how to use Claude Code SDK integration")
    
    # Check if anvil is installed
    try:
        subprocess.run(["anvil", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Anvil CLI not found. Please install it first:")
        print("   pip install anvil-cli")
        sys.exit(1)
    
    # Demo commands (these would normally be run interactively)
    demos = [
        ("anvil build config --show", "Check API key configuration"),
        ("anvil build --help", "Show build command help"),
        ("anvil build create --help", "Show create subcommand help"),
        ("anvil build chat --help", "Show chat subcommand help"),
    ]
    
    print("\n📚 Available Demo Commands:")
    for cmd, desc in demos:
        run_command(cmd, desc)
    
    print(f"\n{'='*60}")
    print("🎯 Example Usage (run these manually):")
    print("="*60)
    
    examples = [
        'anvil build create "a simple Python calculator with GUI"',
        'anvil build create "a REST API for a todo app using FastAPI"',
        'anvil build create "a React component for user authentication"',
        'anvil build chat --dir ./my-project',
        'anvil build create "fix bugs in my code" --auto-approve',
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    print(f"\n{'='*60}")
    print("📋 Setup Checklist:")
    print("="*60)
    print("1. ✅ Install anvil: pip install anvil-cli")
    print("2. 📦 Install Claude Code SDK: pip install claude-code-sdk")
    print("3. 🌐 Install Claude Code CLI: npm install -g @anthropic-ai/claude-code")
    print("4. 🔑 Set API key: anvil build config --set-key YOUR_KEY --global")
    print("5. 🚀 Start building: anvil build create 'your project idea'")
    
    print(f"\n{'='*60}")
    print("💡 Tips:")
    print("="*60)
    print("• Use natural language to describe what you want to build")
    print("• The chat mode is great for iterative development")
    print("• Claude can read existing code and make improvements")
    print("• Use --auto-approve for trusted operations")
    print("• Specify --tools to limit which tools Claude can use")
    print("• Set --dir to work in a specific directory")


if __name__ == "__main__":
    main()