from pathlib import Path
import json
import csv

from app.ingestion.pipeline import IngestionPipeline


def test_txt(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("Hello MemoraAI", encoding="utf-8")
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "txt"
    assert result.evidence[0].content == "Hello MemoraAI"


def test_markdown(tmp_path):
    path = tmp_path / "sample.md"
    path.write_text("# Intro\nFirst section.\n\n## Next\nSecond section.", encoding="utf-8")
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "markdown"
    assert len(result.evidence) >= 2
    assert any("First section" in e.content for e in result.evidence)
    assert any("Second section" in e.content for e in result.evidence)


def test_pdf(tmp_path):
    from pypdf import PdfWriter
    path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    with path.open("wb") as f:
        writer.write(f)
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "pdf"
    assert len(result.evidence) == 1
    assert result.evidence[0].location.page == 1


def test_docx(tmp_path):
    from docx import Document
    path = tmp_path / "sample.docx"
    doc = Document()
    doc.add_heading("Heading", level=1)
    doc.add_paragraph("DOCX paragraph")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "A"
    table.cell(0, 1).text = "B"
    doc.save(path)
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "docx"
    assert any("DOCX paragraph" in e.content for e in result.evidence)
    assert any("A | B" in e.content for e in result.evidence)


def test_pptx(tmp_path):
    from pptx import Presentation
    from pptx.util import Inches
    path = tmp_path / "sample.pptx"
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
    box.text = "Slide text"
    prs.save(path)
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "pptx"
    assert result.evidence[0].location.slide == 1
    assert "Slide text" in result.evidence[0].content


def test_html(tmp_path):
    path = tmp_path / "sample.html"
    path.write_text("<html><head><title>Page</title></head><body><h1>Intro</h1><p>HTML text</p><script>bad()</script></body></html>", encoding="utf-8")
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "html"
    combined = "\n".join(e.content for e in result.evidence)
    assert "HTML text" in combined
    assert "bad()" not in combined


def test_csv(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text("name,age\nAlice,20\nBob,21\n", encoding="utf-8")
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "csv"
    assert any("name: Alice" in e.content for e in result.evidence)
    assert any(e.location.row == 2 for e in result.evidence)


def test_json(tmp_path):
    path = tmp_path / "sample.json"
    path.write_text(json.dumps({"person": {"name": "Alice", "age": 20}, "items": [1, 2]}), encoding="utf-8")
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "json"
    assert any(e.location.json_path == "$/person/name" and e.content == "Alice" for e in result.evidence)
    assert any(e.location.json_path == "$/items/0" and e.content == "1" for e in result.evidence)


def test_xlsx(tmp_path):
    from openpyxl import Workbook
    path = tmp_path / "sample.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "People"
    sheet.append(["name", "age"])
    sheet.append(["Alice", 20])
    workbook.save(path)
    result = IngestionPipeline().ingest(path)
    assert result.detected_type == "xlsx"
    assert any("name: Alice" in e.content for e in result.evidence)
    assert any(e.location.sheet == "People" and e.location.row == 2 for e in result.evidence)


def test_invalid_pdf_signature(tmp_path):
    path = tmp_path / "not_pdf.pdf"
    path.write_text("not a pdf", encoding="utf-8")
    try:
        IngestionPipeline().ingest(path)
    except ValueError as exc:
        assert "PDF signature" in str(exc)
    else:
        assert False, "Expected invalid PDF signature to be rejected"


def test_unsupported_format(tmp_path):
    path = tmp_path / "sample.unsupported"
    path.write_text("test", encoding="utf-8")
    try:
        IngestionPipeline().ingest(path)
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)
    else:
        assert False, "Expected unsupported format to be rejected"
