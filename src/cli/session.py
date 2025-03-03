import click

from src.cli.entrypoint import cli
from src.dsl import load_commands, query_command_similarities


@cli.command()
def session():
    """Start a new commanding session."""
    click.echo("Welcome to HANSEN AI!")
    click.echo("What would you like to do today?")
    prompt = click.prompt(">> ", type=str, prompt_suffix="")
    click.echo(f"Captured prompt => {prompt}")

    # Find most likely command based on embedded similarity to prompt
    commands = load_commands()
    results = query_command_similarities(prompt, commands)
    for idx, (command, similarity) in enumerate(results):
        click.echo(f"{idx+1}) {command.name} ({similarity:0.2f})")
