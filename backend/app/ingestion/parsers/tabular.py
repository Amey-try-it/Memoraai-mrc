from pathlib import Path
import csv
from openpyxl import load_workbook
from ..base import BaseParser
from ..models import EvidenceRecord, EvidenceLocation, Provenance


class CSVParser(BaseParser):
    source_type = "csv"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        records = []
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as file:
            sample = file.read(8192)
            file.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(file, dialect)
            rows = list(reader)

        if not rows:
            return records

        headers = rows[0]
        records.append(EvidenceRecord.create(
            document_id=document_id,
            source_name=path.name,
            source_type=self.source_type,
            content_type="text/table",
            content="CSV columns: " + ", ".join(headers),
            location=EvidenceLocation(row=1),
            provenance=Provenance(parser="CSVParser", extraction_method="header"),
            metadata={"columns": headers},
        ))

        for row_index, row in enumerate(rows[1:], start=2):
            if not any(str(value).strip() for value in row):
                continue
            pairs = []
            for index, value in enumerate(row):
                column = headers[index] if index < len(headers) else f"column_{index + 1}"
                pairs.append(f"{column}: {value}")
            records.append(EvidenceRecord.create(
                document_id=document_id,
                source_name=path.name,
                source_type=self.source_type,
                content_type="text/table-row",
                content="; ".join(pairs),
                location=EvidenceLocation(row=row_index),
                provenance=Provenance(parser="CSVParser", extraction_method="row"),
                metadata={"row_index": row_index},
            ))
        return records


class XLSXParser(BaseParser):
    source_type = "xlsx"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        workbook = load_workbook(filename=str(path), read_only=True, data_only=False)
        records = []

        for sheet in workbook.worksheets:
            sheet_name = sheet.title
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                continue
            headers = [str(value) if value is not None else f"column_{i + 1}" for i, value in enumerate(rows[0])]

            records.append(EvidenceRecord.create(
                document_id=document_id,
                source_name=path.name,
                source_type=self.source_type,
                content_type="text/table",
                content=f"Sheet: {sheet_name}. Columns: " + ", ".join(headers),
                location=EvidenceLocation(sheet=sheet_name, row=1),
                provenance=Provenance(parser="XLSXParser", extraction_method="sheet_header"),
                metadata={"sheet": sheet_name, "columns": headers},
            ))

            for row_index, row in enumerate(rows[1:], start=2):
                if not any(value is not None and str(value).strip() for value in row):
                    continue
                pairs = []
                for col_index, value in enumerate(row):
                    header = headers[col_index] if col_index < len(headers) else f"column_{col_index + 1}"
                    cell_value = "" if value is None else str(value)
                    pairs.append(f"{header}: {cell_value}")
                records.append(EvidenceRecord.create(
                    document_id=document_id,
                    source_name=path.name,
                    source_type=self.source_type,
                    content_type="text/table-row",
                    content="; ".join(pairs),
                    location=EvidenceLocation(sheet=sheet_name, row=row_index),
                    provenance=Provenance(parser="XLSXParser", extraction_method="row"),
                    metadata={"sheet": sheet_name, "row_index": row_index},
                ))
        workbook.close()
        return records
