# MemoraAI Unified Ingestion — Milestone 1

Supported formats:

- TXT
- Markdown
- PDF
- DOCX
- PPTX
- HTML
- CSV
- JSON
- XLSX

## Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run ingestion

```powershell
python -m app.ingestion.cli path\to\file.pdf
```

Save output:

```powershell
python -m app.ingestion.cli path\to\file.xlsx --output ingestion-result.json
```

## Automated tests

```powershell
pytest -v
```

GitHub Actions also runs these tests on backend changes and pull requests.

## Output

Every parser emits the same `EvidenceRecord` schema. Format-specific location and metadata are preserved:

- PDF: page
- DOCX: section/paragraph and tables
- PPTX: slide
- Markdown/HTML: section
- CSV: row
- JSON: JSON path
- XLSX: sheet and row

This is the initial extraction layer. OCR, audio/video, WhatsApp, integrity scoring, storage, chunking, indexing, and retrieval are subsequent milestones.
