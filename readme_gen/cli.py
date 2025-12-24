"""CLI interface for readme-gen."""

import click
from pathlib import Path
from rich.console import Console
import sys

from .scanner import scan_project
from .generator import generate_readme

console = Console(file=sys.stderr)


@click.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', type=click.Path(), default=None,
              help='Output file path (default: stdout)')
@click.option('--dry-run', is_flag=True, help='Preview without writing')
@click.version_option()
def main(path: str, output: str, dry_run: bool):
    """Generate HN-optimized README in 60 seconds.

    Examples:

        readme-gen                     # Scan current dir, print to stdout
        readme-gen ./myproject         # Scan specific dir
        readme-gen -o README.md        # Write to file
        readme-gen --dry-run           # Preview context only
    """
    project_path = Path(path).resolve()

    console.print(f"[bold blue]Scanning:[/] {project_path}")

    # Scan project
    context = scan_project(project_path)

    if dry_run:
        console.print("\n[bold yellow]--- Context (dry-run) ---[/]")
        for key, value in context.items():
            if key == 'files':
                console.print(f"[bold]{key}:[/] {len(value)} files")
            else:
                console.print(f"[bold]{key}:[/] {value}")
        return

    console.print("[bold blue]Generating README...[/]")

    # Generate README
    try:
        readme = generate_readme(context)
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}")
        raise click.Abort()

    # Output
    if output:
        output_path = project_path / output if not Path(output).is_absolute() else Path(output)
        output_path.write_text(readme)
        console.print(f"[bold green]Written:[/] {output_path}")
    else:
        click.echo(readme)


if __name__ == '__main__':
    main()
