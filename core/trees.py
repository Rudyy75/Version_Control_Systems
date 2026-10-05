from pathlib import PurePosixPath

from core.objects import hash_object, read_object


def build_tree(entries: dict[str, dict]) -> str:
    """Build nested tree objects from flat index entries."""
    root: dict = {}
    for path, entry in entries.items():
        parts = PurePosixPath(path).parts
        current = root
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = {
            "hash": entry["hash"],
            "mode": entry["mode"],
        }

    def write_tree(directory: dict) -> str:
        tree_entries = []
        for name in sorted(directory):
            value = directory[name]
            if "hash" in value:
                object_hash = value["hash"]
                mode = value["mode"]
            else:
                object_hash = write_tree(value)
                mode = "040000"
            tree_entries.append(
                mode.encode()
                + b" "
                + name.encode()
                + b"\0"
                + bytes.fromhex(object_hash)
            )
        return hash_object(b"".join(tree_entries), "tree")

    return write_tree(root)


def tree_from_commit(commit_hash: str) -> dict[str, dict]:
    object_type, commit_data = read_object(commit_hash)
    if object_type != "commit":
        raise ValueError(f"{commit_hash} is not a commit")

    tree_hash = next(
        line.removeprefix("tree ")
        for line in commit_data.decode().splitlines()
        if line.startswith("tree ")
    )
    return flatten_tree(tree_hash)


def flatten_tree(tree_hash: str, prefix: str = "") -> dict[str, dict]:
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
        mode = tree_data[position:mode_end].decode()
        name = tree_data[mode_end + 1:name_end].decode()
        path = f"{prefix}/{name}" if prefix else name
        object_hash = tree_data[hash_start:hash_end].hex()

        if mode == "040000":
            entries.update(flatten_tree(object_hash, path))
        else:
            entries[path] = {"hash": object_hash, "mode": mode}
        position = hash_end

    return entries
