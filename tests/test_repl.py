"""Tests for the REPL functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

from anvil.repl import repl, show_help, show_status, show_welcome


def test_show_welcome(capsys):
    """Test welcome panel display."""
    show_welcome()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "/help for help, /status for your current setup" in captured.out
    assert f"cwd: {Path.cwd()}" in captured.out
    assert "Tip: Start with small features or bug fixes" in captured.out


def test_show_help(capsys):
    """Test help command display."""
    show_help()
    captured = capsys.readouterr()

    assert "Available slash commands:" in captured.out
    assert "/help, ?" in captured.out
    assert "/status" in captured.out
    assert "/exit, /quit" in captured.out
    assert "forwarded to the normal anvil CLI" in captured.out


def test_show_status(capsys):
    """Test status command display."""
    show_status()
    captured = capsys.readouterr()

    assert "Current Status:" in captured.out
    assert f"Working Directory: {Path.cwd()}" in captured.out
    assert f"Python Version: {sys.version.split()[0]}" in captured.out


@patch("builtins.input")
def test_repl_help_command(mock_input, capsys):
    """Test REPL responds to /help command."""
    # Mock input sequence: /help, then /exit
    mock_input.side_effect = ["/help", "/exit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Available slash commands:" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


@patch("builtins.input")
def test_repl_status_command(mock_input, capsys):
    """Test REPL responds to /status command."""
    # Mock input sequence: /status, then /exit
    mock_input.side_effect = ["/status", "/exit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Current Status:" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


@patch("builtins.input")
def test_repl_question_mark_help(mock_input, capsys):
    """Test REPL responds to ? as help command."""
    # Mock input sequence: ?, then /exit
    mock_input.side_effect = ["?", "/exit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Available slash commands:" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


@patch("builtins.input")
def test_repl_quit_command(mock_input, capsys):
    """Test REPL exits on /quit command."""
    mock_input.side_effect = ["/quit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


@patch("builtins.input")
def test_repl_exit_command(mock_input, capsys):
    """Test REPL exits on /exit command."""
    mock_input.side_effect = ["/exit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


@patch("builtins.input")
def test_repl_keyboard_interrupt(mock_input, capsys):
    """Test REPL handles KeyboardInterrupt gracefully."""
    # Mock input sequence: raise KeyboardInterrupt, then /exit
    mock_input.side_effect = [KeyboardInterrupt(), "/exit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Use /exit or /quit to leave the shell" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


@patch("builtins.input")
def test_repl_eof_error(mock_input, capsys):
    """Test REPL handles EOFError gracefully."""
    mock_input.side_effect = EOFError()

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


@patch("builtins.input")
@patch("anvil.repl.execute_anvil_command")
def test_repl_delegates_commands(mock_execute, mock_input, capsys):
    """Test REPL delegates non-slash commands to anvil CLI."""
    # Mock input sequence: "version", then /exit
    mock_input.side_effect = ["version", "/exit"]

    repl()

    # Verify execute_anvil_command was called with parsed args
    mock_execute.assert_called_once_with(["version"])


@patch("builtins.input")
def test_repl_handles_empty_input(mock_input, capsys):
    """Test REPL handles empty input gracefully."""
    # Mock input sequence: empty string, then /exit
    mock_input.side_effect = ["", "/exit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out


def test_anvil_shell_entry_point():
    """Test that anvil-shell entry point works."""
    # We can't easily test the full REPL interactively, but we can test
    # that the function is importable and callable
    from anvil.repl import repl
    assert callable(repl)


@patch("builtins.input")
@patch("anvil.repl.execute_anvil_command")
def test_repl_parses_quoted_commands(mock_execute, mock_input, capsys):
    """Test REPL correctly parses commands with quotes."""
    # Mock input sequence: command with quotes, then /exit
    mock_input.side_effect = ['sketch "hello world"', "/exit"]

    repl()

    # Verify execute_anvil_command was called with properly parsed args
    mock_execute.assert_called_once_with(["sketch", "hello world"])


@patch("builtins.input")
def test_repl_handles_invalid_shell_syntax(mock_input, capsys):
    """Test REPL handles invalid shell syntax gracefully."""
    # Mock input sequence: invalid syntax, then /exit
    mock_input.side_effect = ['sketch "unclosed quote', "/exit"]

    repl()
    captured = capsys.readouterr()

    assert "Welcome to anvilCLI!" in captured.out
    assert "Error parsing command:" in captured.out
    assert "Bye - thanks for forging with Anvil!" in captured.out
