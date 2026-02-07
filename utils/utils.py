from pathlib import Path


def has_correct_suffix(path: Path, suffix: str):
    assert suffix[0] == "."
    return path.is_file() and path.suffix.lower() == suffix
