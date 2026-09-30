from core.objects import read_object
from core.refs import get_head_commit


def log():
    """Print commits from the current branch, newest first."""
    current_hash = get_head_commit()

    while current_hash:
        object_type, object_data = read_object(current_hash)
        if object_type != "commit":
            print(f"error: {current_hash} is not a commit")
            return

        commit_text = object_data.decode()
        headers, message = commit_text.split("\n\n", 1)
        parent_hash = None

        for line in headers.splitlines():
            if line.startswith("parent "):
                parent_hash = line.removeprefix("parent ")
                break

        print(f"commit {current_hash}")
        print(message.strip())
        print()
        current_hash = parent_hash
