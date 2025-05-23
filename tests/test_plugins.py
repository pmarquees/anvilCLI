"""Tests for the plugin system."""

from unittest.mock import MagicMock, patch

import typer
from typer.testing import CliRunner

from anvil.cli import app, discover_and_register_plugins


class TestPlugins:
    """Test cases for the plugin system."""

    def setup_method(self) -> None:
        """Set up test runner."""
        self.runner = CliRunner()

    def test_example_plugin_loaded(self) -> None:
        """Test that the example plugin is loaded and available."""
        result = self.runner.invoke(app, ["example", "hello"])
        assert result.exit_code == 0
        assert "Hello World from the example plugin!" in result.stdout

    def test_example_plugin_with_name(self) -> None:
        """Test example plugin with custom name."""
        result = self.runner.invoke(app, ["example", "hello", "Alice"])
        assert result.exit_code == 0
        assert "Hello Alice from the example plugin!" in result.stdout

    def test_example_plugin_help(self) -> None:
        """Test example plugin help."""
        result = self.runner.invoke(app, ["example", "--help"])
        assert result.exit_code == 0
        assert "Example plugin command" in result.stdout

    @patch("anvil.cli.importlib.import_module")
    @patch("anvil.cli.pkgutil.iter_modules")
    def test_plugin_discovery_failure(self, mock_iter_modules, mock_import_module) -> None:
        """Test plugin discovery handles import failures gracefully."""
        # Mock a plugin that fails to import
        mock_iter_modules.return_value = [("", "failing_plugin", True)]
        mock_import_module.side_effect = ImportError("Plugin failed to import")

        # Should not raise an exception
        discover_and_register_plugins()

    @patch("anvil.cli.pkg_resources.iter_entry_points")
    def test_external_plugin_discovery(self, mock_iter_entry_points) -> None:
        """Test external plugin discovery via entry points."""
        # Mock an external plugin
        mock_plugin = MagicMock()
        mock_plugin.register = MagicMock()

        mock_entry_point = MagicMock()
        mock_entry_point.name = "test_external_plugin"
        mock_entry_point.load.return_value = mock_plugin

        mock_iter_entry_points.return_value = [mock_entry_point]

        # Create a new app to test with
        test_app = typer.Typer()

        # Mock the discover function to use our test app
        with patch("anvil.cli.app", test_app):
            discover_and_register_plugins()

        # Verify the plugin was loaded and register was called
        mock_entry_point.load.assert_called_once()
        mock_plugin.register.assert_called_once()

    @patch("anvil.cli.pkg_resources.iter_entry_points")
    def test_external_plugin_without_register(self, mock_iter_entry_points) -> None:
        """Test external plugin without register method is handled gracefully."""
        # Mock an external plugin without register method
        mock_plugin = MagicMock()
        del mock_plugin.register  # Remove register attribute

        mock_entry_point = MagicMock()
        mock_entry_point.name = "test_external_plugin"
        mock_entry_point.load.return_value = mock_plugin

        mock_iter_entry_points.return_value = [mock_entry_point]

        # Should not raise an exception
        discover_and_register_plugins()

    def test_plugin_register_function_signature(self) -> None:
        """Test that plugin register functions have correct signature."""
        from anvil.plugins.example import register

        # Should accept a Typer app
        test_app = typer.Typer()
        register(test_app)

        # Verify the plugin was added (check commands exist)
        assert len(test_app.commands) > 0
