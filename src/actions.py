import typing_extensions as T


def create_note() -> str:
    return "Created note at /path/to/note."


def record_note(note_path: str, notes: T.List[str]) -> str:
    with open(note_path, "w") as fd:
        fd.write("\n".join(notes))
    return f"Recorded notes at {note_path}."


_ACTION_MAPPING: T.Mapping[str, T.Callable] = {
    "create_note": create_note,
    "record_note": record_note,
}


def load_action(action: str) -> T.Callable:
    if action not in _ACTION_MAPPING:
        raise ValueError(f"Unknown action: {action}")
    return _ACTION_MAPPING[action]
