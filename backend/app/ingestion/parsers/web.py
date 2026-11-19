from pathlib import Path
from bs4 import BeautifulSoup
from ..base import BaseParser
from ..models import EvidenceRecord, EvidenceLocation, Provenance


class HTMLParser(BaseParser):
    source_type = "html"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        raw = path.read_text(encoding="utf-8", errors="replace")
        soup = BeautifulSoup(raw, "html.parser")

        for tag in soup(["script", "style", "noscript", "template"]):
            tag.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else path.name
        records = []
        current_heading = title or "Document"
        section_parts = []

        body = soup.body or soup
        elements = body.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "blockquote", "pre", "table"],
            recursive=True,
        )

        for element in elements:
            if element.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                if section_parts:
                    records.append(self._record(path, document_id, current_heading, "\n".join(section_parts)))
                    section_parts = []
                current_heading = element.get_text(" ", strip=True) or "Untitled section"
            elif element.name == "table":
                rows = []
                for row in element.find_all("tr"):
                    cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["th", "td"])]
                    if cells:
                        rows.append(" | ".join(cells))
                if rows:
                    section_parts.append("\n".join(rows))
            else:
                text = element.get_text(" ", strip=True)
                if text:
                    section_parts.append(text)

        if section_parts:
            records.append(self._record(path, document_id, current_heading, "\n".join(section_parts)))

        if not records:
            text = soup.get_text("\n", strip=True)
            if text:
                records.append(self._record(path, document_id, title, text))
        return records

    def _record(self, path, document_id, heading, content):
        return EvidenceRecord.create(
            document_id=document_id,
            source_name=path.name,
            source_type=self.source_type,
            content_type="text/html",
            content=content,
            location=EvidenceLocation(section=heading),
            provenance=Provenance(parser="HTMLParser", extraction_method="heading_and_element_extraction"),
            metadata={"section_title": heading},
        )
