from pathlib import Path

import typing_extensions as T

from src.command import Result


def create_note(filename: str, history: T.List[Result]) -> T.Tuple[str, str]:
    note = Path(filename)
    if note.exists():
        raise RuntimeError(f"Note already exists at {filename}.")

    note.parent.mkdir(parents=True, exist_ok=True)
    note.touch()
    return filename, f"Created note at {filename}."


def record_note(
    note_path: str,
    notes: str,
    history: T.List[Result],
) -> T.Tuple[str, str]:
    note = Path(note_path)
    if not note.exists():
        raise RuntimeError(f"Note does not exist at {note_path}.")
    if not note.is_file():
        raise RuntimeError(f"Note is not a file at {note_path}.")

    note.write_text(f"{notes}\n", encoding="utf-8")
    return "Ok", f"Recorded notes at {note_path}."


_ACTION_MAPPING: T.Mapping[str, T.Callable] = {
    "create_note": create_note,
    "record_note": record_note,
}


def load_action(action: str) -> T.Callable:
    if action not in _ACTION_MAPPING:
        raise ValueError(f"Unknown action: {action}")
    return _ACTION_MAPPING[action]
