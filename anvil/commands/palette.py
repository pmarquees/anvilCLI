"""Palette command for extracting colors from images."""

import json
import sys
from pathlib import Path

import typer
from PIL import Image

app = typer.Typer(name="palette", help="Extract color palettes from images")


def extract_colors(image_path: Path, num_colors: int = 5) -> list[str]:
    """Extract top colors from an image.

    Args:
        image_path: Path to the image file
        num_colors: Number of colors to extract

    Returns:
        List of hex color codes

    Raises:
        typer.Exit: If image processing fails
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize image for faster processing
            img.thumbnail((150, 150))

            # Get colors using quantize
            quantized = img.quantize(colors=num_colors)
            palette_colors = quantized.getpalette()

            # Convert RGB tuples to hex
            hex_colors = []
            for i in range(num_colors):
                r = palette_colors[i * 3]
                g = palette_colors[i * 3 + 1]
                b = palette_colors[i * 3 + 2]
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                hex_colors.append(hex_color)

            return hex_colors

    except FileNotFoundError:
        print(f"✗ Image file not found: {image_path}", file=sys.stderr)
        raise typer.Exit(1)
    except Exception as e:
        print(f"✗ Failed to process image: {e}", file=sys.stderr)
        raise typer.Exit(1)


@app.command()
def grab(image_path: Path = typer.Argument(..., help="Path to the image file")) -> None:
    """Extract top 5 colors from an image and save as JSON.

    Args:
        image_path: Path to the image file
    """
    if not image_path.exists():
        print(f"✗ Image file not found: {image_path}", file=sys.stderr)
        raise typer.Exit(1)

    print(f"🎨 Extracting colors from: {image_path}")

    # Extract colors
    colors = extract_colors(image_path)

    # Print colors as JSON
    colors_json = json.dumps(colors, indent=2)
    print("🌈 Extracted colors:")
    print(colors_json)

    # Save to file
    output_path = image_path.parent / f"{image_path.stem}_palette.json"
    try:
        with open(output_path, "w") as f:
            json.dump(colors, f, indent=2)
        print(f"✓ Saved palette to: {output_path}")
    except Exception as e:
        print(f"✗ Failed to save palette: {e}", file=sys.stderr)
        raise typer.Exit(1)
