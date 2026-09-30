import getpass
import time
from datetime import datetime

from core.index import load_index
from core.objects import hash_object
from core.refs import get_current_branch, get_head_commit, update_ref


def signature() -> str:
    """Build the author and committer signature for this commit."""
    username = getpass.getuser()
    timestamp = int(time.time())
    timezone = datetime.now().astimezone().strftime("%z")
    return f"{username} <{username}@localhost> {timestamp} {timezone}"


def commit(message: str) -> str:
    """Create a tree and commit from the current staging area."""
    index = load_index()
    tree_entries = []

    for path, entry in sorted(index["entries"].items()):
        tree_entry = (
            entry["mode"].encode()
            + b" "
            + path.encode()
            + b"\0"
            + bytes.fromhex(entry["hash"])
        )
        tree_entries.append(tree_entry)

    tree_hash = hash_object(b"".join(tree_entries), "tree")
    parent_hash = get_head_commit()
    sig = signature()

    commit_lines = [f"tree {tree_hash}"]
    if parent_hash:
        commit_lines.append(f"parent {parent_hash}")
    commit_lines.extend(
        [
            f"author {sig}",
            f"committer {sig}",
            "",
            message.rstrip("\n"),
        ]
    )
    commit_data = ("\n".join(commit_lines) + "\n").encode()

    commit_hash = hash_object(commit_data, "commit")
    update_ref(get_current_branch(), commit_hash)
    print(f"[commit {commit_hash}] {message}")
    return commit_hash
