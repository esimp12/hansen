from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import typing_extensions as T
import yaml
from sentence_transformers import SentenceTransformer


class CommandType(Enum):
    INTAKE = "intake"
    PROCESS = "process"

    @classmethod
    def from_str(cls, value: str) -> CommandType:
        value = value.lower()
        return cls(value)


@dataclass
class Command:
    name: str
    command_type: CommandType
    action: T.Callable
    params: T.Mapping[str, T.Any]


def load_commands() -> T.List[Command]:
    commands_path = Path(__file__).parent / "dsl" / "commands.yaml"
    with open(commands_path, encoding="utf-8") as fd:
        dsl = yaml.safe_load(fd)
    return [_create_command(cmd) for cmd in dsl["commands"]]


def _create_command(cmd: T.Mapping[str, T.Any]) -> Command:
    return Command(
        name=cmd["name"],
        command_type=CommandType.from_str(cmd["type"]),
        action=cmd["action"],
        params=cmd["params"],
    )


def load_model(model_name: str = "all-MiniLM-L12-v2") -> SentenceTransformer:
    return SentenceTransformer(model_name)


def query_command_similarities(
    prompt: str,
    commands: T.List[Command],
    model_name: str = "all-MiniLM-L12-v2",
) -> T.List[T.Tuple[Command, float]]:
    model = load_model(model_name)

    prompt_embedding = model.encode(prompt)
    command_embeddings = model.encode([cmd.name for cmd in commands])
    similarities = model.similarity(prompt_embedding, command_embeddings)
    similarities = similarities.squeeze(0).tolist()
    return sorted(
        zip(commands, similarities),
        key=lambda x: x[1],
        reverse=True,
    )
