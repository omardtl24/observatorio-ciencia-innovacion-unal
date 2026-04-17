import hashlib


def compute_sha256(path, chunk_size=8192):
    """
    Computes SHA256 checksum of a file on disk.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_sha256(path, expected_checksum):
    """
    Validates file integrity before persistence.
    """
    computed = compute_sha256(path)
    return computed == expected_checksum
