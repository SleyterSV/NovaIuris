"""Publication gate for staged public legal documents."""
import re
from .identity import search_normalize


def extraction_quality(blocks, ocr_required=False) -> str:
    if ocr_required:
        return "ocr_required"
    text = " ".join(block.text for block in blocks)
    if not text.strip():
        return "low"
    replacements = text.count("\ufffd")
    if replacements / max(len(text), 1) > .005:
        return "low"
    return "medium" if len(search_normalize(text)) < 300 else "high"


def validate_staged(document) -> list[str]:
    problems = []
    if not document.title.strip() or not document.document_hash:
        problems.append("document_metadata_invalid")
    if document.document_type in {"law", "code", "regulation"} and not document.metadata.get("number"):
        problems.append("normative_number_missing")
    if document.document_type in {"judgment", "order", "cassation", "precedent"}:
        if (document.metadata.get("sumilla") and
            re.search(r"\bPRECEDENTE\s+VINCULANTE\b", document.metadata["sumilla"], re.I) and
            document.metadata.get("precedent_binding") is not True):
            problems.append("precedent_claim_unverified")
        if not document.metadata.get("court") or not document.metadata.get("expediente"):
            problems.append("jurisprudence_identity_missing")
        if not document.metadata.get("resolution_type") or not document.metadata.get("resolution_date"):
            problems.append("jurisprudence_date_or_type_missing")
    if not document.units:
        problems.append("no_legal_units")
    if document.extraction_quality in {"low", "ocr_required"}:
        problems.append("extraction_review_required")
    if any(unit.unit_type in {"article", "disposition"} and
           re.search(r"\bNOTA\s+SPIJ\b|\bFE\s+DE\s+ERRATAS\b|En la presente edición de Normas Legales", unit.text, re.I)
           for unit in document.units):
        problems.append("editorial_material_mixed_with_law")
    if any(unit.unit_type in {"article", "disposition"} and
           re.search(r"\(\*\)\s*(?:[^\n]{0,90})?\b(?:modificad[oa]|incorporad[oa]|derogad[oa]|sustituid[oa])\s+por\b|\bTEXTO\s+INCORPORADO\s*:", unit.text, re.I)
           for unit in document.units):
        problems.append("versioned_amendment_mixed_with_law")
    numeric_articles = [(int(unit.unit_number), unit.book) for unit in document.units
                        if unit.unit_type == "article" and unit.unit_number and unit.unit_number.isdigit()
                        and unit.part_number in (None, 1)]
    highest_by_book = {}
    for number, book in numeric_articles:
        highest = highest_by_book.get(book, 0)
        if highest >= 50 and number < highest - 20:
            problems.append("article_numbering_restart_review_required")
            break
        highest_by_book[book] = max(highest, number)
    if document.document_type in {"judgment", "order", "cassation", "precedent"}:
        if any(unit.unit_type == "decision" and
               re.search(r"\bVOTO\s+(?:SINGULAR|EN\s+DISCORDIA|SEPARADO)\b", unit.text, re.I)
               for unit in document.units):
            problems.append("separate_opinion_mixed_with_decision")
        if any(unit.unit_type == "foundation" and
               re.search(r"\n(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[ÉE]PTIMO|S[ÉE]TIMO|OCTAVO|NOVENO|DÉCIMO\w*|DECIMO\w*|UNDÉCIMO|DUODÉCIMO|VIGÉSIMO(?:\s+\w+)?|TRIGÉSIMO(?:\s+\w+)?)[.°º)-]+", unit.text, re.I)
               for unit in document.units):
            problems.append("multiple_foundations_in_one_unit")
    if any((unit.part_count or 0) > 8 for unit in document.units):
        problems.append("oversized_structure_review_required")
    if any(unit.unit_type == "disposition" and (unit.token_count or 0) < 5
           for unit in document.units):
        problems.append("incomplete_disposition")
    if document.source_format == "pdf" and any(
        unit.part_count and (unit.page_start is None or unit.page_end is None or
                             unit.metadata.get("page_provenance") != "source_lines")
        for unit in document.units
    ):
        problems.append("split_page_provenance_review_required")
    numbered_foundations = [int(unit.unit_number) for unit in document.units
                            if unit.unit_type == "foundation" and unit.unit_number and unit.unit_number.isdigit()]
    if numbered_foundations and max(numbered_foundations) > max(100, len(document.units) * 5):
        problems.append("foundation_numbering_review_required")
    hashes = set()
    for index, unit in enumerate(document.units, 1):
        if not unit.text.strip() or not unit.normalized_text.strip():
            problems.append("empty_unit")
        if unit.sequence != index:
            problems.append("invalid_sequence")
        if unit.content_hash in hashes:
            problems.append("duplicate_unit_hash")
        hashes.add(unit.content_hash)
        if unit.page_start is not None and unit.page_end is not None and unit.page_end < unit.page_start:
            problems.append("invalid_page_range")
        if not unit.search_text.strip():
            problems.append("missing_search_text")
    return list(dict.fromkeys(problems))
