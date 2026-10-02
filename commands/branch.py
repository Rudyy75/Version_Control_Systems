from pathlib import Path

from core.refs import MYGIT_DIR, get_current_branch, get_head_commit, update_ref


HEADS_DIR = MYGIT_DIR / "refs" / "heads"


def branch(name: str | None = None):
    """Create a branch or list existing branches."""
    if name:
        if get_head_commit() is None:
            print("error: cannot create a branch before the first commit")
            return

        branch_path = f"refs/heads/{name}"
        if (MYGIT_DIR / branch_path).exists():
            print(f"error: branch already exists: {name}")
            return

        update_ref(branch_path, get_head_commit())
        print(f"created branch {name}")
        return

    current_branch = get_current_branch()
    for ref_path in sorted(HEADS_DIR.iterdir()):
        branch_name = ref_path.name
        marker = "*" if f"refs/heads/{branch_name}" == current_branch else " "
        print(f"{marker} {branch_name}")
