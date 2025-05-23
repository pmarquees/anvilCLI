"""Tests for the palette command."""

import json
import tempfile
from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

from anvil.commands.palette import app, extract_colors


class TestPalette:
    """Test cases for the palette command."""

    def setup_method(self) -> None:
        """Set up test runner."""
        self.runner = CliRunner()

    def create_test_image(self, temp_dir: Path) -> Path:
        """Create a test image for testing.

        Args:
            temp_dir: Temporary directory for the image

        Returns:
            Path to the created test image
        """
        image_path = temp_dir / "test_image.png"

        # Create a simple test image with known colors
        img = Image.new("RGB", (10, 10), color="red")
        img.save(image_path)

        return image_path

    def test_extract_colors_success(self) -> None:
        """Test successful color extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = self.create_test_image(temp_path)

            colors = extract_colors(image_path)

            assert isinstance(colors, list)
            assert len(colors) <= 5
            assert all(color.startswith("#") for color in colors)
            assert all(len(color) == 7 for color in colors)

    def test_extract_colors_nonexistent_file(self) -> None:
        """Test color extraction with non-existent file."""
        with pytest.raises(SystemExit):
            extract_colors(Path("nonexistent.png"))

    def test_grab_command_success(self) -> None:
        """Test successful palette grab command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_path = self.create_test_image(temp_path)

            result = self.runner.invoke(app, ["grab", str(image_path)])

            assert result.exit_code == 0
            assert "Extracting colors from" in result.stdout
            assert "Extracted colors" in result.stdout
            assert "Saved palette to" in result.stdout

            # Check that JSON file was created
            json_path = temp_path / "test_image_palette.json"
            assert json_path.exists()

            # Verify JSON content
            with open(json_path) as f:
                colors = json.load(f)
            assert isinstance(colors, list)
            assert len(colors) <= 5

    def test_grab_command_nonexistent_file(self) -> None:
        """Test palette grab command with non-existent file."""
        result = self.runner.invoke(app, ["grab", "nonexistent.png"])
        assert result.exit_code == 1
        assert "Image file not found" in result.stdout

    def test_grab_command_help(self) -> None:
        """Test palette grab command help."""
        result = self.runner.invoke(app, ["grab", "--help"])
        assert result.exit_code == 0
        assert "Extract top 5 colors" in result.stdout
