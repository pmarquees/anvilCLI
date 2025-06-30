"""Tests for the build command integration."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from anvil.cli import app


def test_build_command_exists():
    """Test that the build command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["build", "--help"])
    assert result.exit_code == 0
    assert "Build projects using Claude Code SDK" in result.stdout


def test_build_config_help():
    """Test that the build config command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["build", "config"])
    assert result.exit_code == 0
    assert "Anthropic API Key Configuration" in result.stdout


def test_build_create_help():
    """Test that the build create command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["build", "create", "--help"])
    assert result.exit_code == 0
    assert "Build something using Claude Code SDK" in result.stdout


def test_build_chat_help():
    """Test that the build chat command shows help."""
    runner = CliRunner()
    result = runner.invoke(app, ["build", "chat", "--help"])
    assert result.exit_code == 0
    assert "Start an interactive chat session" in result.stdout


@patch('anvil.commands.build.get_anthropic_api_key')
def test_build_create_no_api_key(mock_get_key):
    """Test build create command fails without API key."""
    mock_get_key.return_value = None
    
    runner = CliRunner()
    result = runner.invoke(app, ["build", "create", "test prompt"])
    
    assert result.exit_code == 1
    assert "ANTHROPIC_API_KEY not found" in result.stdout


@patch('anvil.commands.build.check_claude_code_installation')
@patch('anvil.commands.build.get_anthropic_api_key')
def test_build_create_no_claude_cli(mock_get_key, mock_check_claude):
    """Test build create command fails without Claude Code CLI."""
    mock_get_key.return_value = "test-key"
    mock_check_claude.return_value = False
    
    runner = CliRunner()
    result = runner.invoke(app, ["build", "create", "test prompt"])
    
    assert result.exit_code == 1
    assert "Claude Code CLI not found" in result.stdout


@patch('anvil.commands.build.query', None)  # Simulate SDK not installed
def test_build_create_no_sdk():
    """Test build create command fails without Claude Code SDK."""
    runner = CliRunner()
    result = runner.invoke(app, ["build", "create", "test prompt"])
    
    assert result.exit_code == 1
    assert "Claude Code SDK not installed" in result.stdout


def test_build_config_show_no_key():
    """Test build config show when no API key is set."""
    runner = CliRunner()
    with patch('anvil.commands.build.get_anthropic_api_key', return_value=None):
        result = runner.invoke(app, ["build", "config", "--show"])
        
        assert result.exit_code == 0
        assert "No Anthropic API key found" in result.stdout


def test_build_config_show_with_key():
    """Test build config show when API key is set."""
    runner = CliRunner()
    with patch('anvil.commands.build.get_anthropic_api_key', return_value="sk-ant-test123456"):
        result = runner.invoke(app, ["build", "config", "--show"])
        
        assert result.exit_code == 0
        assert "API key found" in result.stdout
        assert "sk-ant-te...3456" in result.stdout  # Masked key


@patch('anvil.commands.build.save_api_key_globally')
def test_build_config_set_key_global(mock_save):
    """Test setting API key globally."""
    runner = CliRunner()
    result = runner.invoke(app, ["build", "config", "--set-key", "test-key", "--global"])
    
    assert result.exit_code == 0
    mock_save.assert_called_once_with("test-key")


@patch('builtins.open', create=True)
@patch('pathlib.Path.exists')
def test_build_config_set_key_local(mock_exists, mock_open):
    """Test setting API key locally."""
    mock_exists.return_value = False
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    
    runner = CliRunner()
    result = runner.invoke(app, ["build", "config", "--set-key", "test-key"])
    
    assert result.exit_code == 0
    assert "API key saved to" in result.stdout