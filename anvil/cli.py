"""Main CLI entry point for anvil."""

import importlib
import json
import pkgutil
import subprocess
import sys
from pathlib import Path

import typer
from PIL import Image

from . import __version__
from .repl import repl
from .commands import sketch

# ASCII logo using figlet-style text
LOGO = """
 █████╗ ███╗   ██╗██╗   ██╗██╗██╗
██╔══██╗████╗  ██║██║   ██║██║██║
███████║██╔██╗ ██║██║   ██║██║██║
██╔══██║██║╚██╗██║╚██╗ ██╔╝██║██║
██║  ██║██║ ╚████║ ╚████╔╝ ██║███████╗
╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝╚══════╝
"""

app = typer.Typer(help="A powerful CLI tool for creative development workflows")

# Register the sketch command
app.add_typer(sketch.app, name="sketch")

# Global state for flags
class GlobalState:
    verbose: bool = False
    no_color: bool = False

state = GlobalState()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Launch REPL when no sub-command is provided."""
    if ctx.invoked_subcommand is None:
        repl()


@app.command()
def version() -> None:
    """Show version information."""
    print(f"anvil {__version__}")


@app.command()
def palette(image_path: str) -> None:
    """Extract color palette from an image."""
    image_file = Path(image_path)

    if not image_file.exists():
        print(f"✗ Image file not found: {image_file}", file=sys.stderr)
        raise typer.Exit(1)

    print(f"🎨 Extracting colors from: {image_file}")

    try:
        with Image.open(image_file) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize image for faster processing
            img.thumbnail((150, 150))

            # Get colors using quantize
            quantized = img.quantize(colors=5)
            palette_colors = quantized.getpalette()

            # Convert RGB tuples to hex
            hex_colors = []
            if palette_colors:
                max_colors = min(5, len(palette_colors) // 3)
                for i in range(max_colors):
                    r = palette_colors[i * 3]
                    g = palette_colors[i * 3 + 1]
                    b = palette_colors[i * 3 + 2]
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    hex_colors.append(hex_color)

            # If we didn't get enough colors, add some default ones
            if len(hex_colors) < 5:
                # Get the dominant color from the image
                pixels = list(img.getdata())
                if pixels:
                    r, g, b = pixels[0]
                    hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")

                # Fill remaining with black
                while len(hex_colors) < 5:
                    hex_colors.append("#000000")

            # Print colors as JSON
            colors_json = json.dumps(hex_colors, indent=2)
            print("🌈 Extracted colors:")
            print(colors_json)

            # Save to file
            output_path = image_file.parent / f"{image_file.stem}_palette.json"
            with open(output_path, "w") as f:
                json.dump(hex_colors, f, indent=2)
            print(f"✓ Saved palette to: {output_path}")

    except Exception as e:
        print(f"✗ Failed to process image: {e}", file=sys.stderr)
        raise typer.Exit(1)


@app.command()
def upgrade() -> None:
    """Upgrade anvil to the latest version using pipx."""
    try:
        result = subprocess.run(
            ["pipx", "upgrade", "anvil-cli"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ anvil upgraded successfully!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to upgrade anvil: {e.stderr}", file=sys.stderr)
        raise typer.Exit(1)
    except FileNotFoundError:
        print("✗ pipx not found. Please install pipx first.", file=sys.stderr)
        raise typer.Exit(1)


def discover_and_register_plugins() -> None:
    """Discover and register plugins from anvil/plugins/ and entry points."""
    # Register built-in plugins from anvil/plugins/
    try:
        from . import plugins as plugins_package
        for _, name, _ in pkgutil.iter_modules(plugins_package.__path__, plugins_package.__name__ + "."):
            try:
                module = importlib.import_module(name)
                if hasattr(module, "register"):
                    module.register(app)
                    print(f"Registered built-in plugin: {name.split('.')[-1]}")
            except Exception as e:
                print(f"Failed to load built-in plugin {name}: {e}")
    except ImportError:
        pass

    # Register third-party plugins via entry points
    try:
        import pkg_resources
        for entry_point in pkg_resources.iter_entry_points("anvil.plugins"):
            try:
                plugin = entry_point.load()
                if hasattr(plugin, "register"):
                    plugin.register(app)
                    print(f"Registered external plugin: {entry_point.name}")
            except Exception as e:
                print(f"Failed to load external plugin {entry_point.name}: {e}")
    except ImportError:
        pass


# Discover and register plugins
# discover_and_register_plugins()


if __name__ == "__main__":
    app()
