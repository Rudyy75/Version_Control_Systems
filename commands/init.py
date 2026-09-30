from pathlib import Path


MYGIT_DIR = Path(".mygit")


def init() -> None:
    """Create the metadata directories and default branch pointer."""
    (MYGIT_DIR / "objects").mkdir(parents=True, exist_ok=True)
    (MYGIT_DIR / "refs" / "heads").mkdir(parents=True, exist_ok=True)
    (MYGIT_DIR / "HEAD").write_text(
        "ref: refs/heads/main\n",
        encoding="utf-8",
    )
    print("Initialized empty mygit repository in .mygit")
