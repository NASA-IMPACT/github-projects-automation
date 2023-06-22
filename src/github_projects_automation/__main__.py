"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Github Projects Automation."""


if __name__ == "__main__":
    main(prog_name="github-projects-automation")  # pragma: no cover
