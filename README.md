# MyGit

MyGit is a small Git-like version control client written in Python. It uses SHA-256 content-addressed objects, a JSON staging index, commit history, branches, and checkout.

## Requirements

- Python 3.10 or newer
- Run commands from a directory that should be managed by MyGit

## Running the Client

From this directory, run:

```powershell
python mygit.py <command>
```

From another project directory, provide the path to `mygit.py`:

```powershell
python path\to\mygit\mygit.py <command>
```

## Commands

### Initialize a repository

```powershell
python mygit.py init
```

Creates:

```text
.mygit/
├── HEAD
├── objects/
└── refs/
    └── heads/
```

`HEAD` initially contains `ref: refs/heads/main`.

### Stage files

```powershell
python mygit.py add file.txt notes.txt
```

Each file is read as bytes, stored as a blob object, and added to `.mygit/index`. The index stores each relative path, blob hash, and file mode.

Only files are accepted by the current implementation. Directories must be expanded into individual file arguments.

### Create a commit

```powershell
python mygit.py commit -m "initial commit"
```

The command reads the index, creates a tree object, creates a commit object, and moves the current branch ref to the new commit.

A later commit records the previous commit as its parent.

### Show history

```powershell
python mygit.py log
```

Starts at the commit referenced by `HEAD` and follows each `parent` line backward, printing newest commits first.

### Show status

```powershell
python mygit.py status
```

Reports:

- `new file staged`: a file is staged for the first time
- `modified in index`: a committed file has staged changes
- `deleted from index`: a committed file is staged for removal
- `modified`: an indexed file has different content on disk
- `deleted`: an indexed file no longer exists on disk
- `untracked`: a file exists on disk but is not in the index

Status compares the last commit, the staging index, and the working directory.

### Create or list branches

Create a branch from the current commit:

```powershell
python mygit.py branch feature
```

List branches:

```powershell
python mygit.py branch
```

The current branch is marked with `*`.

Branches are files under `.mygit/refs/heads/`. Creating a branch copies the current commit hash into a new ref file.

### Checkout a branch

```powershell
python mygit.py checkout feature
```

Checkout restores the files and index from the selected branch's latest commit, then updates `HEAD`.

Checkout refuses to continue if tracked files have local changes that would be overwritten.

## Internal Design

### Objects

Objects are stored under `.mygit/objects/` using the first two characters of their SHA-256 hash as a directory name.

Each object is hashed using:

```text
<type> <content length>\0<content>
```

The complete object is compressed with zlib before being stored.

The implementation uses three object types:

- Blob: raw file contents
- Tree: hierarchical directory entries, where files reference blobs and directories reference trees
- Commit: tree hash, optional parent hash, author, committer, and message

### Index

The staging area is stored as JSON at `.mygit/index`. It maps file paths to blob hashes and modes. This is simpler than Git's binary index format while preserving the same staging concept.

### References

`HEAD` contains a symbolic reference such as:

```text
ref: refs/heads/main
```

The referenced branch file contains the latest commit hash:

```text
HEAD -> refs/heads/main -> commit hash
```

## Example Workflow

```powershell
mkdir demo
cd demo
python path\to\mygit\mygit.py init
Set-Content file.txt "hello"
python path\to\mygit\mygit.py add file.txt
python path\to\mygit\mygit.py commit -m "first commit"
python path\to\mygit\mygit.py status
python path\to\mygit\mygit.py log
python path\to\mygit\mygit.py branch feature
python path\to\mygit\mygit.py checkout feature
```

After changing a file, stage it again before committing:

```powershell
python path\to\mygit\mygit.py add file.txt
python path\to\mygit\mygit.py commit -m "update file"
```

## Current Limitations

- The CLI currently expects file paths for `add`; recursive directory staging is not implemented.
- Checkout supports named branches but not detached `HEAD` mode.
- Merge, conflict resolution, rename detection, and remote repositories are not implemented.

- The CLI currently expects file paths for `add`; recursive directory staging is not implemented.
- Tree objects are nested recursively for directory contents.
- Checkout supports switching branches but not detached HEAD mode.
- Merge, conflict resolution, rename detection, and remote repositories are not implemented.
