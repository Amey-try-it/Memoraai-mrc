from pathlib import Path
from uuid import uuid4
from .detection import detect_type
from .models import IngestionResult
from .registry import ParserRegistry, default_registry


class IngestionPipeline:
    def __init__(self, registry: ParserRegistry | None = None):
        self.registry = registry or default_registry()

    def ingest(self, path: str | Path, document_id: str | None = None) -> IngestionResult:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(path)
        if not path.is_file():
            raise ValueError(f"Expected a file, received: {path}")

        document_id = document_id or str(uuid4())
        source_type = detect_type(path)
        parser = self.registry.get(source_type)
        evidence = parser.parse(path, document_id)

        warnings = []
        if not evidence:
            warnings.append("Parser returned no evidence records.")
        empty_records = sum(not record.content.strip() for record in evidence)
        if empty_records:
            warnings.append(f"{empty_records} evidence record(s) contained empty content.")

        return IngestionResult(
            document_id=document_id,
            source_name=path.name,
            detected_type=source_type,
            evidence=evidence,
            warnings=warnings,
            metadata={
                "file_size_bytes": path.stat().st_size,
                "evidence_count": len(evidence),
                "parser": parser.__class__.__name__,
            },
        )
