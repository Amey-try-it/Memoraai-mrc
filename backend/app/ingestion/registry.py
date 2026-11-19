from pathlib import Path
from .parsers import (
    TextParser, MarkdownParser, PDFParser, DOCXParser, PPTXParser,
    HTMLParser, CSVParser, XLSXParser, JSONParser,
)


class ParserRegistry:
    def __init__(self):
        self._parsers = {}

    def register(self, source_type: str, parser):
        self._parsers[source_type] = parser

    def get(self, source_type: str):
        parser = self._parsers.get(source_type)
        if parser is None:
            raise ValueError(f"No parser registered for type: {source_type}")
        return parser

    def supported_types(self):
        return sorted(self._parsers.keys())


def default_registry() -> ParserRegistry:
    registry = ParserRegistry()
    registry.register("txt", TextParser())
    registry.register("markdown", MarkdownParser())
    registry.register("pdf", PDFParser())
    registry.register("docx", DOCXParser())
    registry.register("pptx", PPTXParser())
    registry.register("html", HTMLParser())
    registry.register("csv", CSVParser())
    registry.register("json", JSONParser())
    registry.register("xlsx", XLSXParser())
    return registry
