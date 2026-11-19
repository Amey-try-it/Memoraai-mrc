from pathlib import Path
import mimetypes


EXTENSION_MAP = {
    ".txt": "txt",
    ".md": "markdown",
    ".markdown": "markdown",
    ".pdf": "pdf",
    ".docx": "docx",
    ".pptx": "pptx",
    ".html": "html",
    ".htm": "html",
    ".csv": "csv",
    ".json": "json",
    ".xlsx": "xlsx",
}


def detect_type(path: str | Path) -> str:
    """Detect supported type using extension, with signature checks for binary formats."""
    path = Path(path)
    ext = path.suffix.lower()

    # ZIP-based Office formats are verified using their package signatures.
    if ext in {".docx", ".pptx", ".xlsx"}:
        if not _is_zip(path):
            raise ValueError(f"{ext} file does not have a valid ZIP container signature")
        return EXTENSION_MAP[ext]

    if ext == ".pdf":
        with path.open("rb") as f:
            if not f.read(5).startswith(b"%PDF-"):
                raise ValueError("PDF signature is missing or invalid")
        return "pdf"

    if ext in EXTENSION_MAP:
        return EXTENSION_MAP[ext]

    mime, _ = mimetypes.guess_type(str(path))
    raise ValueError(f"Unsupported file type: extension={ext!r}, mime={mime!r}")


def _is_zip(path: Path) -> bool:
    with path.open("rb") as f:
        return f.read(4) in {b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"}
