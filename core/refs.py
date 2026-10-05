from pathlib import Path


MYGIT_DIR = Path(".mygit")
HEAD_PATH = MYGIT_DIR / "HEAD"


def require_repository() -> bool:
    """Report whether the current directory contains a MyGit repository."""
    if not HEAD_PATH.is_file() or not (MYGIT_DIR / "objects").is_dir():
        print("fatal: not a mygit repository")
        return False
    return True


def get_current_branch():
    """Return the ref path stored in HEAD."""
    head_contents = HEAD_PATH.read_text(encoding="utf-8").strip()
    return head_contents.removeprefix("ref: ")


def get_head_commit():
    """Return the current branch's commit hash, if one exists."""
    branch_path = MYGIT_DIR / get_current_branch()
    if not branch_path.exists():
        return None

    commit_hash = branch_path.read_text(encoding="utf-8").strip()
    return commit_hash or None


def update_ref(branch_path: str, commit_hash: str):
    """Move a branch ref to a commit hash."""
    ref_path = MYGIT_DIR / branch_path
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    ref_path.write_text(f"{commit_hash}\n", encoding="utf-8")
