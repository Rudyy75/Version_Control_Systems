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

## Demonstration Walkthrough

The following sequence can be used to demonstrate the implementation. Each step
shows a different part of the client:

1. Run `init` in an empty directory. This creates the `.mygit` metadata
   directory, including `HEAD`, object storage, and the `main` branch reference.
2. Create files in nested directories and run `add` on each file. MyGit hashes
   their contents as blobs and records the paths and hashes in the JSON index.
3. Run `status` before the first commit. The output `new file staged` confirms
   that the files are in the staging area.
4. Run `commit -m "initial nested commit"` and then `log`. The commit references
   a root tree, which references nested trees for directories such as `src` and
   `src/utils`.
5. Modify a tracked file without staging it and run `status`. The output
   `modified` identifies an unstaged working-directory change.
6. Run `add` again and run `status`. The output `modified in index` identifies a
   staged change. After committing, an empty status output means the working
   directory and index match the latest commit.
7. Create a branch with `branch feature`, list branches with `branch`, and switch
   using `checkout feature`. The `*` marker identifies the current branch.
8. Commit a different version of a file on the feature branch. Switching between
   `main` and `feature` restores the version belonging to each branch.
9. Make an unstaged change and try to checkout another branch. MyGit refuses with
   `local changes would be overwritten`. It also refuses checkout when staged
   changes have not been committed.
10. Delete a tracked file and run `status`. The output `deleted` reports the
    working-directory deletion. This simplified client detects the deletion but
    does not currently provide a separate `rm` command for staging it.

This walkthrough is also suitable as a screen-recording outline. The commands
may be run manually so that each output can be explained while demonstrating the
corresponding internal operation.

## Current Limitations

- The CLI currently expects file paths for `add`; recursive directory staging is not implemented.
- File deletion is detected by `status`, but there is no separate `rm` command for staging deletions.
- Checkout supports named branches but not detached `HEAD` mode.
- Merge, conflict resolution, rename detection, and remote repositories are not implemented.
