from abc import ABC, abstractmethod
from pathlib import Path
from .models import EvidenceRecord


class BaseParser(ABC):
    source_type: str = "unknown"

    @abstractmethod
    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        """Parse source file into normalized evidence records."""
        raise NotImplementedError
