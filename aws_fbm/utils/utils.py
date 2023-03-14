from pathlib import Path


def repo_path() -> Path:
    return Path(__file__).parent.parent.resolve()
