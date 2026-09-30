from pathlib import Path

from core.index import load_index
from core.objects import hash_object


def status():
    """Show modified, deleted, and untracked files."""
    index = load_index()
    entries = index["entries"]

    for file_name, entry in sorted(entries.items()):
        path = Path(file_name)
        if not path.is_file():
            print(f"deleted: {file_name}")
            continue

        current_hash = hash_object(path.read_bytes(), write=False)
        if current_hash != entry["hash"]:
            print(f"modified: {file_name}")

    for path in sorted(Path(".").rglob("*")):
        if not path.is_file() or ".mygit" in path.parts:
            continue

        file_name = path.as_posix()
        if file_name not in entries:
            print(f"untracked: {file_name}")