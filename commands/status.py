from pathlib import Path

from core.index import load_index
from core.objects import hash_object
from core.refs import get_head_commit, require_repository
from core.trees import tree_from_commit


def status():
    """Show modified, deleted, and untracked files."""
    if not require_repository():
        return

    index = load_index()
    entries = index["entries"]
    head_entries = tree_from_commit(get_head_commit()) if get_head_commit() else {}

    all_tracked = sorted(set(head_entries) | set(entries))
    for file_name in all_tracked:
        head_entry = head_entries.get(file_name)
        index_entry = entries.get(file_name)
        path = Path(file_name)

        if head_entry != index_entry:
            if head_entry is None:
                print(f"new file staged: {file_name}")
            elif index_entry is None:
                print(f"deleted from index: {file_name}")
            else:
                print(f"modified in index: {file_name}")

        if not path.is_file():
            if index_entry is not None:
                print(f"deleted: {file_name}")
            continue

        current_hash = hash_object(path.read_bytes(), write=False)
        if index_entry is not None and current_hash != index_entry["hash"]:
            print(f"modified: {file_name}")

    for path in sorted(Path(".").rglob("*")):
        if not path.is_file() or ".mygit" in path.parts:
            continue

        file_name = path.as_posix()
        if file_name not in entries:
            print(f"untracked: {file_name}")