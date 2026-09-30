import json
from pathlib import Path


INDEX_PATH = Path(".mygit") / "index"


def load_index() -> dict:
    """Load the staging area, or return an empty one if it does not exist."""
    if not INDEX_PATH.exists():
        return {"entries": {}}

    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def save_index(index: dict) -> None:
    """Save the staging area as JSON."""
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(
        json.dumps(index, indent=2),
        encoding="utf-8",
    )
