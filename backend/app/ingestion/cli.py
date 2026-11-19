import argparse
import json
from pathlib import Path
from .pipeline import IngestionPipeline


def main():
    parser = argparse.ArgumentParser(description="MemoraAI local ingestion test CLI")
    parser.add_argument("file", help="File to ingest")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    result = IngestionPipeline().ingest(args.file)
    payload = result.to_dict()
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
