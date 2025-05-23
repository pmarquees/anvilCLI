"""Example plugin to demonstrate the plugin architecture."""

import typer


def register(main_app: typer.Typer) -> None:
    """Register the example plugin with the main CLI app.

    Args:
        main_app: The main Typer application
    """
    example_app = typer.Typer(name="example", help="Example plugin command")

    @example_app.command()
    def hello(name: str = "World") -> None:
        """Say hello from the example plugin.

        Args:
            name: Name to greet
        """
        print(f"👋 Hello {name} from the example plugin!")

    main_app.add_typer(example_app, name="example")
