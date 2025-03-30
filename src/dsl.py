from pathlib import Path

import typing_extensions as T
import yaml
from pke.unsupervised import TopicRank
from sentence_transformers import SentenceTransformer

from src.actions import load_action
from src.command import CommandOptions


def load_command_options(prompt: str = "") -> T.List[CommandOptions]:
    commands_path = Path(__file__).parent / "dsl" / "commands.yaml"
    with open(commands_path, encoding="utf-8") as fd:
        dsl = yaml.safe_load(fd)
    return [_create_command_options(cmd, prompt=prompt) for cmd in dsl["commands"]]


def _create_command_options(
    cmd: T.Mapping[str, T.Any],
    prompt: str = "",
    reserved_params: T.Optional[T.List[str]] = None,
) -> CommandOptions:
    if reserved_params is None:
        reserved_params = []
    reserved_params.append("history")
    reserved_params.append("return")

    action = load_action(cmd["action"])
    param_types = T.get_type_hints(action)
    params = [(pn, pt) for pn, pt in param_types.items() if pn not in reserved_params]
    return CommandOptions(
        name=cmd["name"],
        action=action,
        params=params,
        prompt=prompt,
    )


def get_most_similar_word(
    keyword: str,
    phrase: str,
    model_name: str = "all-MiniLM-L12-v2",
) -> T.Tuple[str, float]:
    model = SentenceTransformer(model_name)
    keyword_embedding = model.encode(keyword)

    similarities = []
    for word in phrase.split():
        word_embedding = model.encode(word)
        similarity = model.similarity(
            keyword_embedding,
            word_embedding,  # type: ignore
        )
        similarities.append((word, similarity.item()))
    return max(similarities, key=lambda x: x[1])


def query_command_options(
    prompt: str,
    commands: T.List[CommandOptions],
    model_name: str = "all-MiniLM-L12-v2",
) -> T.List[T.Tuple[CommandOptions, float]]:
    model = SentenceTransformer(model_name)
    prompt_embedding = model.encode(prompt)
    command_embeddings = model.encode([cmd.name for cmd in commands])
    similarities = model.similarity(
        prompt_embedding,
        command_embeddings,  # type: ignore
    )
    similarities = similarities.squeeze(0).tolist()
    return sorted(
        zip(commands, similarities),
        key=lambda x: x[1],
        reverse=True,
    )


def query_keyphrases(command: CommandOptions) -> T.List[T.Tuple[str, float]]:
    extractor = TopicRank()
    extractor.load_document(input=command.prompt, language="en")
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=5)
    return keyphrases
