import hashlib
import zlib
from pathlib import Path


MYGIT_DIR = Path(".mygit")
OBJECTS_DIR = MYGIT_DIR / "objects"


def hash_object(data: bytes, obj_type: str = "blob", write: bool = True):
    """Hash an object and optionally store its compressed representation."""
    header = f"{obj_type} {len(data)}\0".encode()
    full_object = header + data
    object_hash = hashlib.sha256(full_object).hexdigest()

    if write:
        object_dir = OBJECTS_DIR / object_hash[:2]
        object_path = object_dir / object_hash[2:]
        if not object_path.exists():
            object_dir.mkdir(parents=True, exist_ok=True)
            object_path.write_bytes(zlib.compress(full_object))

    return object_hash


def read_object(object_hash: str):
    """Read an object and return its type and unwrapped content."""
    object_path = OBJECTS_DIR / object_hash[:2] / object_hash[2:]
    full_object = zlib.decompress(object_path.read_bytes())
    header, data = full_object.split(b"\0", 1)
    object_type = header.split(b" ", 1)[0].decode()
    return object_type, data
