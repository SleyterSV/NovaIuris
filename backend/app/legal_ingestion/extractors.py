"""Page/order preserving extraction; no OCR or provider calls."""
from __future__ import annotations

import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from .models import Block, ExtractedDocument


class _LegalHTML(HTMLParser):
    BLOCK_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "li", "tr", "article", "section"}
    SKIP_TAGS = {"script", "style", "noscript", "svg"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self._text: list[str] = []
        self._links: list[str] = []
        self._active: str | None = None
        self._skip = 0
        self._href: str | None = None

    def _flush(self):
        content = re.sub(r"\s+", " ", " ".join(self._text)).strip()
        if content:
            self.blocks.append(Block(content, index=len(self.blocks), style=self._active,
                                     kind="heading" if self._active in {"h1","h2","h3","h4"} else "paragraph",
                                     links=list(dict.fromkeys(self._links))))
        self._text, self._links = [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self._skip += 1
            return
        if self._skip:
            return
        if tag in self.BLOCK_TAGS:
            self._flush()
            self._active = tag
        elif tag == "br":
            self._text.append("\n")
        elif tag == "a":
            href = dict(attrs).get("href")
            self._href = href if href and re.match(r"^https?://", href, re.I) else None

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS:
            self._skip = max(0, self._skip - 1)
            return
        if self._skip:
            return
        if tag == "a":
            self._href = None
        if tag in self.BLOCK_TAGS:
            self._flush()
            self._active = None

    def handle_data(self, data):
        if not self._skip and data.strip():
            self._text.append(data)
            if self._href:
                self._links.append(self._href)

    def finish(self):
        self._flush()
        return self.blocks


def _decode(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


def is_html_document(data: bytes) -> bool:
    start = data[:4096].lstrip().lower()
    return any(marker in start for marker in (b"<!doctype html", b"<html", b"<head", b"<body"))


def extract(path: str | Path) -> ExtractedDocument:
    path = Path(path)
    data = path.read_bytes()
    suffix = path.suffix.lower()
    file_hash = hashlib.sha256(data).hexdigest()
    if is_html_document(data):
        parser = _LegalHTML()
        parser.feed(_decode(data))
        blocks = parser.finish()
        source_format = "spij_html" if suffix == ".doc" else "html"
    elif suffix == ".pdf":
        from pypdf import PdfReader
        blocks = []
        reader = PdfReader(str(path))
        for page_number, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            for line in page_text.splitlines():
                if line.strip():
                    blocks.append(Block(line.strip(), page=page_number, index=len(blocks)))
        source_format = "pdf"
    elif suffix == ".docx":
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        doc = Document(str(path))
        blocks = []
        for element in doc.element.body.iterchildren():
            if element.tag.endswith("}p"):
                paragraph = Paragraph(element, doc)
                value = paragraph.text.strip()
                if value:
                    style = paragraph.style.name if paragraph.style else None
                    numbered = paragraph._p.pPr is not None and paragraph._p.pPr.numPr is not None
                    blocks.append(Block(value, index=len(blocks), style=style,
                                        kind="list" if numbered else "heading" if style and "heading" in style.lower() else "paragraph"))
            elif element.tag.endswith("}tbl"):
                table = Table(element, doc)
                for row in table.rows:
                    value = " | ".join(cell.text.strip() for cell in row.cells)
                    if value.strip(" |"):
                        blocks.append(Block(value, index=len(blocks), kind="table"))
        source_format = "docx"
    elif suffix in {".txt", ".md", ".markdown", ".html", ".htm"}:
        content = _decode(data)
        if suffix in {".html", ".htm"}:
            parser = _LegalHTML()
            parser.feed(content)
            blocks, source_format = parser.finish(), "html"
        else:
            blocks = [Block(line.strip(), index=i) for i, line in enumerate(content.splitlines()) if line.strip()]
            source_format = suffix.lstrip(".")
    else:
        raise ValueError(f"Unsupported legal source format: {suffix}")
    warnings = []
    replacement_count = sum(block.text.count("\ufffd") for block in blocks)
    pdf_pages = max((block.page or 0 for block in blocks), default=0)
    ocr_required = suffix == ".pdf" and (not blocks or sum(len(b.text) for b in blocks) / max(pdf_pages, 1) < 80)
    if replacement_count:
        warnings.append("replacement_characters")
    if ocr_required:
        warnings.append("ocr_required")
    return ExtractedDocument(path.name, source_format, blocks, file_hash, warnings, ocr_required)
