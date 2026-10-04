import hashlib


def calculate_document_id(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()