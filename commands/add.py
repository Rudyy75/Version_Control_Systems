import os
from pathlib import Path

from core.index import load_index, save_index
from core.objects import hash_object


def add(file_paths: list[str]) -> None:
    """Store files as blobs and add them to the staging area."""
    index = load_index()

    for file_name in file_paths:
        path = Path(file_name)
        if not path.is_file():
            print(f"error: path does not exist or is not a file: {file_name}")
            continue

        data = path.read_bytes()
        object_hash = hash_object(data)
        relative_path = Path(os.path.relpath(path, Path.cwd())).as_posix()
        index["entries"][relative_path] = {
            "hash": object_hash,
            "mode": "100644",
        }
        print(f"added: {relative_path}")

    save_index(index)
