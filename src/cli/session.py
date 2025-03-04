import click
import typing_extensions as T

from src.cli.entrypoint import cli
from src.dsl import (
    Command,
    CommandType,
    load_commands,
    query_command_similarities,
)


@cli.command()
def session():
    """Start a new commanding session."""
    _echo("Welcome to HANSEN AI!")
    _echo("What would you like to do today?")

    buffer = []
    while (command := get_command()) is not None:
        # Process command
        _echo(f"Selected command => {command.name}")
        res = process_command(command, buffer)
        _echo(f"Result => {res}")
        _echo("What would you like to do next?")
    _echo("Goodbye!")


def process_command(command: Command, buffer: T.List[T.Any]) -> T.Optional[T.Any]:
    res = None
    if command.command_type == CommandType.INTAKE:
        res = command.action()
        buffer.append(res)
    elif command.command_type == CommandType.PROCESS:
        res = command.action(buffer.pop())
        buffer.append(res)
    return res


def get_command() -> T.Optional[Command]:
    # Let user prompt for an action
    cmd_prompt = _input()
    _echo(f"Captured prompt => {cmd_prompt}")

    # Present user with most likely commands
    commands = load_commands()
    results = query_command_similarities(cmd_prompt, commands)
    _echo_commands(results)

    cmd_num = _input("(Select command) >> ", int)
    num_commands = len(results)
    if cmd_num == num_commands + 1:
        return None
    selected_command = results[cmd_num - 1][0]
    return selected_command


def _echo(msg: str):
    click.echo(msg)


def _input(greeting: str = ">> ", prompt_type: T.Type = str) -> T.Any:
    return click.prompt(greeting, type=prompt_type, prompt_suffix="")


def _echo_commands(results: T.List[T.Tuple[Command, float]]):
    for idx, (command, similarity) in enumerate(results):
        _echo(f"{idx+1}) {command.name} ({similarity:0.2f})")
    _echo(f"{len(results)+1}) Quit")
