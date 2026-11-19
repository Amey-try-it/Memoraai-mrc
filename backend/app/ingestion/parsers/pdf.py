from pathlib import Path
from pypdf import PdfReader
from ..base import BaseParser
from ..models import EvidenceRecord, EvidenceLocation, Provenance, IntegrityProfile


class PDFParser(BaseParser):
    source_type = "pdf"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        reader = PdfReader(str(path), strict=False)
        records = []
        warnings = []

        for page_index, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception as exc:
                text = ""
                warnings.append(f"Page {page_index} extraction failed: {type(exc).__name__}")

            record = EvidenceRecord.create(
                document_id=document_id,
                source_name=path.name,
                source_type=self.source_type,
                content_type="text",
                content=text,
                location=EvidenceLocation(page=page_index),
                provenance=Provenance(parser="PDFParser", extraction_method="native_text"),
                metadata={"page_count": len(reader.pages), "page_has_text": bool(text.strip())},
            )
            if not text.strip():
                record.integrity.degradation_flags.append("EMPTY_PAGE_EXTRACTION")
                record.integrity.notes.append("No native text extracted; OCR fallback is not implemented yet.")
            records.append(record)

        if warnings and records:
            records[0].metadata["parser_warnings"] = warnings
        return records
