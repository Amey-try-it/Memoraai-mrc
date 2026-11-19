from pathlib import Path
from charset_normalizer import from_path
from ..base import BaseParser
from ..models import EvidenceRecord, EvidenceLocation, Provenance


def read_text_safely(path: Path) -> tuple[str, str]:
    """Decode text while retaining the detected encoding as metadata."""
    result = from_path(path).best()
    if result is not None:
        return str(result), result.encoding or "unknown"
    return path.read_text(encoding="utf-8", errors="replace"), "utf-8-replacement"


class TextParser(BaseParser):
    source_type = "txt"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        text, encoding = read_text_safely(path)
        return [EvidenceRecord.create(
            document_id=document_id,
            source_name=path.name,
            source_type=self.source_type,
            content_type="text",
            content=text,
            location=EvidenceLocation(),
            provenance=Provenance(parser="TextParser", extraction_method="text_decode"),
            metadata={"encoding": encoding},
        )]


class MarkdownParser(BaseParser):
    source_type = "markdown"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        text, encoding = read_text_safely(path)
        # Split on Markdown headings while preserving the heading in each section.
        sections: list[tuple[str, str]] = []
        current_title = "Document"
        current_lines: list[str] = []

        for line in text.splitlines():
            if line.lstrip().startswith("#"):
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines).strip()))
                current_title = line.strip().lstrip("#").strip() or "Untitled section"
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))

        records = []
        for index, (title, body) in enumerate(sections, start=1):
            if not body.strip():
                continue
            records.append(EvidenceRecord.create(
                document_id=document_id,
                source_name=path.name,
                source_type=self.source_type,
                content_type="text/markdown",
                content=body,
                location=EvidenceLocation(section=title),
                provenance=Provenance(parser="MarkdownParser", extraction_method="heading_sections"),
                metadata={"section_index": index, "encoding": encoding},
            ))
        return records or [EvidenceRecord.create(
            document_id=document_id, source_name=path.name, source_type=self.source_type,
            content_type="text/markdown", content=text,
            provenance=Provenance(parser="MarkdownParser", extraction_method="raw_markdown"),
            metadata={"encoding": encoding},
        )]
