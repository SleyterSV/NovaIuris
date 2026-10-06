"""Small typed contracts for a provider-free ingestion preview."""
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Block:
    text: str
    page: int | None = None
    index: int = 0
    style: str | None = None
    kind: str = "paragraph"
    links: list[str] = field(default_factory=list)


@dataclass
class ExtractedDocument:
    filename: str
    source_format: str
    blocks: list[Block]
    source_file_hash: str
    warnings: list[str] = field(default_factory=list)
    ocr_required: bool = False


@dataclass
class LegalUnit:
    unit_type: str
    sequence: int
    text: str
    normalized_text: str
    content_hash: str
    unit_number: str | None = None
    heading: str | None = None
    page_start: int | None = None
    page_end: int | None = None
    parent_sequence: int | None = None
    part_number: int | None = None
    part_count: int | None = None
    book: str | None = None
    section: str | None = None
    title: str | None = None
    chapter: str | None = None
    excerpt: str | None = None
    token_count: int | None = None
    search_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class StagedDocument:
    title: str
    document_type: str
    document_hash: str
    source_file_name: str
    source_format: str
    parser_version: str
    extraction_quality: str
    ingestion_status: str
    ocr_required: bool
    metadata: dict[str, Any]
    units: list[LegalUnit]
    warnings: list[str] = field(default_factory=list)
    document_id: str | None = None

    def to_dict(self):
        return asdict(self)
