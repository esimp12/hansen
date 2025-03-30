import click
import typing_extensions as T

from src.cli.entrypoint import cli
from src.command import Command, CommandOptions, Result
from src.dsl import (
    get_most_similar_word,
    load_command_options,
    query_command_options,
    query_keyphrases,
)


@cli.command()
def session():
    """Start a new commanding session."""
    _echo("Welcome to HANSEN AI!")
    _echo("What would you like to do today?")

    history = []
    while (command := get_command(history)) is not None:
        _echo(f"Executing command {command.name}...")
        res = command.execute()
        _echo(f"Result => {res}")
        _echo("What would you like to do next?")
    _echo("Goodbye!")


def get_command(history: T.List[Result]) -> T.Optional[Command]:
    # Let user prompt for an action
    cmd_prompt = _input()
    _echo(f"Captured prompt => {cmd_prompt}")

    # Present user with most likely commands
    commands = load_command_options(cmd_prompt)
    options = query_command_options(cmd_prompt, commands)
    _echo_command_options(options)

    option_num = _input("(Select command) >> ", int)
    num_options = len(options)
    if option_num == num_options + 1:
        return None

    selected_option: CommandOptions = options[option_num - 1][0]
    _echo(f"Selected command => {selected_option.name}")
    params = [pn for pn, _ in selected_option.params]
    if len(params) == 0:
        return Command.create_command(
            name=selected_option.name,
            prompt=cmd_prompt,
            action=selected_option.action,
            param_types={},
            param_values={},
            history=history,
        )

    # Prompt user for parameters
    param_types = {}
    param_values = {}
    keyphrases = query_keyphrases(selected_option)
    for param in params:
        _echo(f"Select value for '{param}'")
        param_options = query_param_options(param, keyphrases)
        _echo_param_options(param_options, keyphrases)

        param_option_num = _input("(Select value) >> ", int)
        num_param_options = len(keyphrases) + 1
        if param_option_num == num_param_options:
            value = _input(f"(Enter custom value for '{param}') >> ")
        else:
            value = param_options[param_option_num - 1][1]
        param_types[param] = str
        param_values[param] = value
        _echo(f"Selected param, value pair => ({param}, {value})")

    return Command.create_command(
        name=selected_option.name,
        prompt=cmd_prompt,
        action=selected_option.action,
        param_types=param_types,
        param_values=param_values,
        history=history,
    )


def query_param_options(
    param: str, keyphrases: T.List[T.Tuple[str, float]]
) -> T.List[T.Tuple[str, T.Any, float]]:
    options = []
    for keyphrase, _ in keyphrases:
        param_guess, similarity = get_most_similar_word(param, keyphrase)
        values = keyphrase.split()
        value_guess_idx = values.index(param_guess)
        value_guess = (
            values[value_guess_idx + 1] if value_guess_idx < len(values) - 1 else None
        )
        options.append((param_guess, value_guess, similarity))
    return options


def _echo(msg: str):
    click.echo(msg)


def _input(greeting: str = ">> ", prompt_type: T.Type = str) -> T.Any:
    return click.prompt(greeting, type=prompt_type, prompt_suffix="")


def _echo_command_options(results: T.List[T.Tuple[CommandOptions, float]]):
    for idx, (command, similarity) in enumerate(results):
        _echo(f"{idx+1}) {command.name} ({similarity:0.2f})")
    _echo(f"{len(results)+1}) Quit")


def _echo_param_options(
    param_options: T.List[T.Tuple[str, T.Any, float]],
    keyphrases: T.List[T.Tuple[str, float]],
):
    param_keyphrase_pairs = list(zip(param_options, keyphrases))
    for idx, pair in enumerate(param_keyphrase_pairs):
        (param_guess, value_guess, similarity), (keyphrase, keyphrase_similarity) = pair
        _echo(
            f"{idx+1}) (param, value):  '{param_guess}', '{value_guess}' "
            + f"({similarity:0.2f}) "
            + f"(keyphrase => '{keyphrase}' ({keyphrase_similarity:0.2f})"
        )
    _echo(f"{len(param_keyphrase_pairs)+1}) Enter custom value")
