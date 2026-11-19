from pathlib import Path
import json
from ..base import BaseParser
from ..models import EvidenceRecord, EvidenceLocation, Provenance


class JSONParser(BaseParser):
    source_type = "json"

    def parse(self, path: Path, document_id: str) -> list[EvidenceRecord]:
        with path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        records = []
        for json_path, value in self._walk(data):
            if isinstance(value, (dict, list)):
                rendered = json.dumps(value, ensure_ascii=False, indent=2)
            else:
                rendered = "" if value is None else str(value)
            if not rendered.strip():
                continue
            records.append(EvidenceRecord.create(
                document_id=document_id,
                source_name=path.name,
                source_type=self.source_type,
                content_type="text/json-value",
                content=rendered,
                location=EvidenceLocation(json_path=json_path),
                provenance=Provenance(parser="JSONParser", extraction_method="recursive_path_extraction"),
                metadata={"json_path": json_path, "value_type": type(value).__name__},
            ))
        return records

    def _walk(self, value, path="$"):
        if isinstance(value, dict):
            # Emit leaf values; object paths are retained as metadata.
            if not value:
                yield path, value
            for key, child in value.items():
                safe_key = str(key).replace("~", "~0").replace("/", "~1")
                yield from self._walk(child, f"{path}/{safe_key}")
        elif isinstance(value, list):
            if not value:
                yield path, value
            for index, child in enumerate(value):
                yield from self._walk(child, f"{path}/{index}")
        else:
            yield path, value
