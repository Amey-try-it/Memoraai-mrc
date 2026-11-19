from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from uuid import uuid4


@dataclass
class EvidenceLocation:
    page: Optional[int] = None
    section: Optional[str] = None
    slide: Optional[int] = None
    sheet: Optional[str] = None
    row: Optional[int] = None
    cell: Optional[str] = None
    timestamp: Optional[str] = None
    json_path: Optional[str] = None


@dataclass
class Provenance:
    parser: str
    extraction_method: str
    parser_version: Optional[str] = None
    parent_evidence_id: Optional[str] = None


@dataclass
class IntegrityProfile:
    source_integrity: str = "NOT_ASSESSED"
    extraction_quality: str = "NOT_ASSESSED"
    structural_validity: str = "NOT_ASSESSED"
    degradation_flags: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class EvidenceRecord:
    evidence_id: str
    document_id: str
    source_name: str
    source_type: str
    content_type: str
    content: str
    location: EvidenceLocation
    provenance: Provenance
    integrity: IntegrityProfile = field(default_factory=IntegrityProfile)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        document_id: str,
        source_name: str,
        source_type: str,
        content_type: str,
        content: str,
        location: EvidenceLocation | None = None,
        provenance: Provenance | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "EvidenceRecord":
        return cls(
            evidence_id=str(uuid4()),
            document_id=document_id,
            source_name=source_name,
            source_type=source_type,
            content_type=content_type,
            content=content,
            location=location or EvidenceLocation(),
            provenance=provenance or Provenance(parser="unknown", extraction_method="unknown"),
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class IngestionResult:
    document_id: str
    source_name: str
    detected_type: str
    evidence: list[EvidenceRecord]
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "source_name": self.source_name,
            "detected_type": self.detected_type,
            "evidence": [item.to_dict() for item in self.evidence],
            "warnings": self.warnings,
            "metadata": self.metadata,
        }
