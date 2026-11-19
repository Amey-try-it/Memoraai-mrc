from pathlib import Path
from docx import Document
from pptx import Presentation
from ..base import BaseParser
from ..models import EvidenceRecord, EvidenceLocation, Provenance


class DOCXParser(BaseParser):
    source_type = "docx"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        doc = Document(str(path))
        records = []
        section_title = "Document"
        paragraph_index = 0

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
            paragraph_index += 1
            style = getattr(paragraph.style, "name", "") if paragraph.style else ""
            if style.lower().startswith("heading"):
                section_title = text

            records.append(EvidenceRecord.create(
                document_id=document_id,
                source_name=path.name,
                source_type=self.source_type,
                content_type="text",
                content=text,
                location=EvidenceLocation(section=section_title),
                provenance=Provenance(parser="DOCXParser", extraction_method="paragraph"),
                metadata={"paragraph_index": paragraph_index, "style": style},
            ))

        # Extract tables as separate evidence records, retaining row/column structure.
        for table_index, table in enumerate(doc.tables, start=1):
            rows = []
            for row_index, row in enumerate(table.rows, start=1):
                cells = [cell.text.strip() for cell in row.cells]
                rows.append(" | ".join(cells))
            table_text = "\n".join(rows).strip()
            if table_text:
                records.append(EvidenceRecord.create(
                    document_id=document_id,
                    source_name=path.name,
                    source_type=self.source_type,
                    content_type="text/table",
                    content=table_text,
                    location=EvidenceLocation(section=section_title),
                    provenance=Provenance(parser="DOCXParser", extraction_method="table"),
                    metadata={"table_index": table_index, "rows": len(table.rows)},
                ))
        return records


class PPTXParser(BaseParser):
    source_type = "pptx"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        presentation = Presentation(str(path))
        records = []

        for slide_index, slide in enumerate(presentation.slides, start=1):
            pieces = []
            for shape in slide.shapes:
                if getattr(shape, "has_text_frame", False):
                    text = shape.text.strip()
                    if text:
                        pieces.append(text)
                if getattr(shape, "has_table", False):
                    table = shape.table
                    for row in table.rows:
                        pieces.append(" | ".join(cell.text.strip() for cell in row.cells))

            slide_text = "\n".join(pieces).strip()
            records.append(EvidenceRecord.create(
                document_id=document_id,
                source_name=path.name,
                source_type=self.source_type,
                content_type="text",
                content=slide_text,
                location=EvidenceLocation(slide=slide_index),
                provenance=Provenance(parser="PPTXParser", extraction_method="slide_text_and_tables"),
                metadata={"slide_index": slide_index, "shape_count": len(slide.shapes)},
            ))
        return records
