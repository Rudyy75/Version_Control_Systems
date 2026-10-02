from pathlib import Path

from core.index import load_index, save_index
from core.objects import read_object
from core.refs import HEAD_PATH, MYGIT_DIR


HEADS_DIR = MYGIT_DIR / "refs" / "heads"


def read_tree(commit_hash: str):
    object_type, commit_data = read_object(commit_hash)
    if object_type != "commit":
        raise ValueError(f"{commit_hash} is not a commit")

    tree_hash = next(
        line.removeprefix("tree ")
        for line in commit_data.decode().splitlines()
        if line.startswith("tree ")
    )
    object_type, tree_data = read_object(tree_hash)
    if object_type != "tree":
        raise ValueError(f"{tree_hash} is not a tree")

    entries = {}
    position = 0
    while position < len(tree_data):
        mode_end = tree_data.index(b" ", position)
        name_end = tree_data.index(b"\0", mode_end)
        hash_start = name_end + 1
        hash_end = hash_start + 32
        path = tree_data[mode_end + 1:name_end].decode()
        entries[path] = {
            "hash": tree_data[hash_start:hash_end].hex(),
            "mode": tree_data[position:mode_end].decode(),
        }
        position = hash_end

    return entries


def checkout(name: str):
    """Switch to a branch and restore its committed files."""
    branch_path = HEADS_DIR / name
    if not branch_path.is_file():
        print(f"error: branch does not exist: {name}")
        return

    target_commit = branch_path.read_text(encoding="utf-8").strip()
    current_index = load_index()
    current_entries = current_index["entries"]

    for path, entry in current_entries.items():
        file_path = Path(path)
        if not file_path.is_file():
            print(f"error: local changes would be overwritten: {path}")
            return
        if read_object(entry["hash"])[1] != file_path.read_bytes():
            print(f"error: local changes would be overwritten: {path}")
            return

    target_entries = read_tree(target_commit)
    for path in target_entries:
        if path not in current_entries and Path(path).exists():
            print(f"error: untracked file would be overwritten: {path}")
            return

    for path in current_entries:
        if path not in target_entries:
            Path(path).unlink(missing_ok=True)

    for path, entry in target_entries.items():
        object_type, data = read_object(entry["hash"])
        if object_type != "blob":
            print(f"error: {entry['hash']} is not a blob")
            return
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)

    save_index({"entries": target_entries})
    HEAD_PATH.write_text(f"ref: refs/heads/{name}\n", encoding="utf-8")
    print(f"switched to branch {name}")
