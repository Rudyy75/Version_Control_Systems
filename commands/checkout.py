from pathlib import Path

from core.index import load_index, save_index
from core.objects import read_object
from core.refs import HEAD_PATH, MYGIT_DIR, get_head_commit, require_repository
from core.trees import tree_from_commit


HEADS_DIR = MYGIT_DIR / "refs" / "heads"


def checkout(name: str):
    """Switch to a branch and restore its committed files."""
    if not require_repository():
        return

    branch_path = HEADS_DIR / name
    if not branch_path.is_file():
        print(f"error: branch does not exist: {name}")
        return

    target_commit = branch_path.read_text(encoding="utf-8").strip()
    current_index = load_index()
    current_entries = current_index["entries"]
    current_commit = get_head_commit()

    if current_commit:
        committed_entries = tree_from_commit(current_commit)
        if committed_entries != current_entries:
            print("error: local changes would be overwritten: staged changes")
            return

    for path, entry in current_entries.items():
        file_path = Path(path)
        if not file_path.is_file():
            print(f"error: local changes would be overwritten: {path}")
            return
        if read_object(entry["hash"])[1] != file_path.read_bytes():
            print(f"error: local changes would be overwritten: {path}")
            return

    target_entries = tree_from_commit(target_commit)
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
